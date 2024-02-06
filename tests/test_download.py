import os
import pytest
import requests
from unittest.mock import Mock, patch
from assignment0.main import download_pdf

# Define a directory for test files, which you will need to create and populate with test PDFs.
TEST_DIR = os.path.join(os.path.dirname(__file__), 'test_data')

# Sample URLs for test PDFs
TEST_PDF_URLS = [
    'https://www.normanok.gov/sites/default/files/documents/2024-01/2024-01-16_daily_incident_summary.pdf',
    'https://www.normanok.gov/sites/default/files/documents/2024-01/2024-01-17_daily_incident_summary.pdf',
    'https://www.normanok.gov/sites/default/files/documents/2024-01/2024-01-18_daily_incident_summary.pdf'
]


@pytest.fixture(scope='function')
def mock_request_response():
    # Mock the requests.get function to return a response with a status code of 200 and some content.
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.content = b'Test PDF content'
    with patch('requests.get', return_value=mock_resp):
        yield


@pytest.mark.parametrize('test_pdf_url', TEST_PDF_URLS)
def test_download_pdf_success(test_pdf_url, tmp_path, mock_request_response):
    # Test the download_pdf function for successful download
    local_filename = download_pdf(
        test_pdf_url, local_filename=tmp_path / 'test_incident.pdf')
    assert os.path.exists(local_filename)
    assert os.path.getsize(local_filename) > 0  # The file should not be empty


def test_download_pdf_failure(tmp_path, mock_request_response):
    # Test the download_pdf function for a failed download due to a bad URL
    with patch('requests.get') as mocked_get:
        mocked_get.side_effect = requests.exceptions.RequestException
        with pytest.raises(requests.exceptions.RequestException):
            download_pdf('http://example.com/invalid.pdf',
                         local_filename=tmp_path / 'invalid.pdf')

# Additional tests for specific edge cases and error handling can be added here.
