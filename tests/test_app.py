from fastapi.testclient import TestClient
from application.core.processing import results_storage
from application.main import app

client = TestClient(app)


def test_upload_file():
    file_path = "/data/TEM3.png"
    with open(file_path, "rb") as file:
        response = client.post("/upload/", files={"file": ("TEM3.png", file, "application/data")})

    assert response.status_code == 200
    result_id = response.json()
    assert isinstance(result_id, str)


def test_get_result():
    result_id = "test_result_id"
    results_storage[result_id] = {
        "date_of_shipment": "2023-01-01",
        "bill_of_landing_number": "BL123456",
        "master_bill_of_landing_number": "MBL654321",
        "customer_po": "PO987654",
        "reference": "REF1234",
        "delivery": "Delivery Info",
        "shipment": "Shipment Info",
        "name": "John Doe",
        "trailer_number": "TR123",
        "qty_order": "100",
        "bottles_shipped": "200",
        "cases_shipped": "50",
        "pallets_shipped": "10",
        "upc_code": "UPC123456",
        "total_weight": "500kg"
    }

    response = client.get(f"/result/{result_id}")
    assert response.status_code == 200
    result = response.json()
    assert result["bill_of_landing_number"] == "BL123456"

