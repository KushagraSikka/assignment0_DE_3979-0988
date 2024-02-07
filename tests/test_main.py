# test_main.py

import pytest
from unittest.mock import patch, mock_open
import os
from assignment0.main import download_pdf, extract_incidents


@patch('requests.get')
def test_download_pdf(mock_get):
    mock_get.return_value.content = b'%PDF-1.4 sample PDF content'
    test_filename = 'test_download.pdf'

    result_filename = download_pdf(
        'https://www.normanok.gov/sites/default/files/documents/2024-01/2024-01-25_daily_incident_summary.pdf', test_filename)
    assert os.path.exists(result_filename)
    os.remove(result_filename)  # Cleanup after test
