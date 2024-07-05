import os
import uuid
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import aiofiles
from app.core.processing import process_pdf, results_storage

router = APIRouter()

TEMP_DIR = "/tmp/"
if not os.path.exists(TEMP_DIR):
    try:
        os.makedirs(TEMP_DIR)
    except OSError as e:
        print(f"Error creating temporary directory {TEMP_DIR}: {e}")
        raise


@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_location = f"/tmp/{file.filename}"
        async with aiofiles.open(file_location, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)

        json_data = await process_pdf(file_location)

        result_id = str(uuid.uuid4())
        # print(result_id)
        results_storage[result_id] = json_data
        os.remove(file_location)

        return result_id
    except Exception as e:
        print(f"Error in upload_file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/result/{result_id}")
async def get_result(result_id: str):
    try:
        result = results_storage.get(result_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Result not found")
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
