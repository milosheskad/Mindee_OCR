import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.core.processing import results_storage

client = TestClient(app)


@pytest.fixture
def mock_process_pdf():
    with patch('app.core.processing.process_pdf') as mock:
        yield mock


# Test the upload_file endpoint
@pytest.mark.asyncio
async def test_upload_file(mock_process_pdf):
    # Mock the response from process_pdf
    mock_process_pdf.return_value = {'key': 'value'}

    # Create a mock UploadFile
    file_content = b"Test file content"
    file = UploadFile(filename="test.pdf", file=MagicMock(read=MagicMock(return_value=file_content)))

    response = await client.post("/upload/", files={"file": ("test.pdf", file_content, "application/pdf")})

    assert response.status_code == 200

    result_id = response.json()
    assert len(result_id) == 36

    # check if the result is stored in results_storage
    assert result_id in results_storage
    assert results_storage[result_id] == {'key': 'value'}
