from assignment0.main import extract_incidents


def test_extract_incidents():
    # Path to a test PDF file within the tests/resources directory
    test_pdf_path = "docs/test_pdf.pdf"

    # Execute the function
    incidents = extract_incidents(test_pdf_path)

    # Verify that the extracted data matches expected values
    assert len(incidents) > 0, "No incidents were extracted"
    # this checks if the length of the incidents is greater than 0
    assert incidents[0]['Nature'] == 'Traffic Stop', "Extracted data does not match expected values"
    # this checks if the nature of the first incident is 'Traffic Stop'
