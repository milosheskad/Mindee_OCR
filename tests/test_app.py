import os
import pytest
import json
import tempfile
from fastapi.testclient import TestClient
from da import app, results_storage

client = TestClient(app)

@pytest.fixture(scope="module")
def test_app():
    # Code that sets up your FastAPI application before tests run
    yield app  # Yield the application to the tests
    # Code that runs after the tests have completed (if needed)

@pytest.fixture()
def temp_file():
    # Create a temporary directory and return the path
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

# def test_upload_file(test_app, temp_file):
#     filename = "C:\\Users\Dragana\PycharmProjects\Laigo\data\TEMPL_A.pdf"
#     file_path = os.path.join(temp_file, filename)
#
#     # Simulate file upload
#     with open(file_path, "wb") as f:
#         f.write(b"dummy content")
#
#     # Send a POST request to /upload/ endpoint
#     response = client.post("/upload/", files={"file": (filename, open(file_path, "rb"))})
#     assert response.status_code == 200
#
#     # Verify the response JSON structure or specific keys
#     result_id = response.json()
#
#     # Clean up (optional as temp directory will be cleaned up automatically)
#     # os.remove(file_path)
#
#     assert result_id in results_storage

def test_upload_file(test_app, temp_file):
    filename = "C:\\Users\Dragana\PycharmProjects\Laigo\data\TEMPL_A.pdf"


    file_path = os.path.join(temp_file, filename)

    # Simulate file upload
    with open(file_path, "wb") as f:
        f.write(b"dummy content")

    # Simulate incorrect JSON data (missing 'document' key)
    invalid_data = {
        "incorrect_key": "value"
    }

    # Send a POST request to /upload/ endpoint with invalid data
    response = client.post("/upload/", files={"file": (filename, open(file_path, "rb"))}, data=invalid_data)
    assert response.status_code == 400

# def test_get_result(test_app):
#     # Simulate a request to fetch the result
#     result_id = "dummy_result_id"
#
#     # Add dummy data to results_storage
#     results_storage[result_id] = {
#         "name": "Buy groceries",
#         "completed": False
#     }
#
#     # Send a GET request to /result/{result_id} endpoint
#     response = client.get(f"/result/{result_id}")
#     assert response.status_code == 200
#
#     # Verify the response JSON structure or specific keys
#     result_data = response.json()
#     assert result_data["name"] == "Buy groceries"
#     assert result_data["completed"] == False
