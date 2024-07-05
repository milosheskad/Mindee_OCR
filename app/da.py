import os
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import aiofiles
import json
from typing import Optional
from mindee import Client, product

app = FastAPI()
results_storage = {}

mindee_client = Client(api_key="2bdd35a8bdc998a2835f0baa79d5e3ad")
my_endpoint = mindee_client.create_endpoint(
    account_name="dmilo6",
    endpoint_name="bill_of_landing",
    version="1"
)
TEMP_DIR = "/tmp/"
IMAGEDIR = "images/"

if not os.path.exists(TEMP_DIR):
    try:
        os.makedirs(TEMP_DIR)
    except OSError as e:
        print(f"Error creating temporary directory {TEMP_DIR}: {e}")
        raise


def process_items(items: dict) -> dict:
    processed_item = {}
    try:
        # Verify the expected structure
        if not isinstance(items, dict) or 'document' not in items:
            raise ValueError("Invalid input structure: 'document' key is missing.")

        document = items['document']

        if not isinstance(document, dict) or 'inference' not in document:
            raise ValueError("Invalid input structure: 'inference' key is missing.")

        inference = document['inference']

        if not isinstance(inference, dict) or 'prediction' not in inference:
            raise ValueError("Invalid input structure: 'prediction' key is missing.")

        prediction = inference['prediction']

        if not isinstance(prediction, dict):
            raise ValueError("Invalid input structure: 'prediction' is not a dictionary.")

        # Extract the required fields
        processed_item['date_of_shipment'] = prediction['date_of_shipment']['value']
        processed_item['bill_of_landing_number'] = prediction['bill_of_landing_number']['value']
        processed_item['master_bill_of_landing_number'] = prediction['master_bill_of_landing_number']['value']
        processed_item['customer_po'] = prediction['customer_po']['value']
        processed_item['reference'] = prediction['reference']['value']
        processed_item['delivery'] = prediction['delivery']['value']
        processed_item['shipment'] = prediction['shipment']['value']
        processed_item['name'] = prediction['name']['value']
        processed_item['trailer_number'] = prediction['trailer_number']['value']
        processed_item['qty_order'] = prediction['qty_order']['value']
        processed_item['bottles_shipped'] = prediction['bottles_shipped']['value']
        processed_item['cases_shipped'] = prediction['cases_shipped']['value']
        processed_item['pallets_shipped'] = prediction['pallets_shipped']['value']
        processed_item['upc_code'] = prediction['customer_item_id']['value']
        processed_item['total_weight'] = prediction['total_weight']['value']

        print(processed_item)

    except KeyError as e:
        print(f"KeyError: {e}")
        raise HTTPException(status_code=500, detail=f"Missing key in document structure: {e}")

    except ValueError as e:
        print(f"ValueError: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        print(f"Unhandled Exception: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing the items.")

    return processed_item


async def process_file(file_path: str) -> Optional[dict]:
    try:
        # Load file from disk
        print(f"Loading file from path: {file_path}")
        input_doc = mindee_client.source_from_path(file_path)

        # Parse the file
        print(f"Sending file to Mindee API for processing...")
        result = mindee_client.enqueue_and_parse(
            product.GeneratedV1,
            input_doc,
            endpoint=my_endpoint
        )

        parsed_json = json.loads(result.raw_http)
        clean_data = process_items(parsed_json)
        return clean_data
    except Exception as e:
        print(f"Error in process_pdf: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {e}")


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file.filename = f"{uuid.uuid4()}.jpg"
    contents = await file.read()

    # save the file
    with open(f"{IMAGEDIR}{file.filename}", "wb") as f:
        f.write(contents)

    return {"filename": file.filename}
    # try:
    #     file_location = f"/tmp/{file.filename}"
    #     async with aiofiles.open(file_location, 'wb') as out_file:
    #         content = await file.read()
    #         await out_file.write(content)
    #
    #     # json_data = await process_pdf(file_location)
    #
    #     if file.content_type in ["application/pdf", "image/jpeg", "image/png"]:
    #         json_data = await process_file(file_location)
    #     else:
    #         raise HTTPException(status_code=400, detail="Unsupported file type")
    #
    #     result_id = str(uuid.uuid4())
    #     print(result_id)
    #     results_storage[result_id] = json_data
    #
    #     # Remove the temporary file after processing
    #     os.remove(file_location)
    #
    #     return result_id
    # except Exception as e:
    #     print(f"Error in upload_file: {e}")
    #     raise HTTPException(status_code=500, detail=str(e))


@app.get("/result/{result_id}")
async def get_result(result_id: str):
    try:
        result = results_storage.get(result_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Result not found")
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
