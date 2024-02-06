import pytest
from assignment0.main import generate_random_data
import datetime
import re

# Define the pattern to match the generated URLs
URL_PATTERN = r'https://www.normanok.gov/sites/default/files/documents/\d{4}-\d{2}/\d{4}-\d{2}-\d{2}_daily_incident_summary.pdf'


def is_date_in_range(date_text, start_date, end_date):
    """
    Check if the date in the URL is within the specified range.

    :param date_text: The date string from the URL.
    :param start_date: The start date as a datetime object.
    :param end_date: The end date as a datetime object.
    :return: Boolean indicating if the date is in the range.
    """
    url_date = datetime.datetime.strptime(date_text, '%Y-%m-%d')
    return start_date <= url_date <= end_date


def test_generate_random_data():
    start_date = '2024-01-01'
    end_date = '2024-02-04'
    number_of_links = 5

    # Convert string dates to datetime objects
    start_date_obj = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    # Generate the random URLs
    random_urls = generate_random_data(start_date, end_date, number_of_links)

    # Check that the correct number of URLs have been generated
    assert len(random_urls) == number_of_links

    # Check that each URL matches the expected format and date range
    for url in random_urls:
        assert re.match(URL_PATTERN, url) is not None
        date_match = re.search(r'\d{4}-\d{2}-\d{2}', url)
        assert date_match is not None
        date_text = date_match.group()
        assert is_date_in_range(date_text, start_date_obj, end_date_obj)
