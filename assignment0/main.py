# -*- coding: utf-8 -*-
import fitz
import fitz  # Ensure fitz is imported
import random
import datetime
import argparse
import requests
import pandas as pd
import fitz  # Import PyMuPDF
import re
import os
import sqlite3
from PyPDF2 import PdfReader

# Function to download a PDF from a given URL and save it locally


def download_pdf(url, local_filename='incident.pdf'):
    response = requests.get(url)
    with open(local_filename, 'wb') as file:
        file.write(response.content)
    return local_filename

# Function to generate random URLs for daily incident summary PDFs


def generate_random_data(start_date, end_date, number_of_links):
    """
    Generate a list of random URLs for daily incident summary PDFs.

    :param start_date: The start date in the format 'YYYY-MM-DD'.
    :param end_date: The end date in the format 'YYYY-MM-DD', should be before '2024-02-05'.
    :param number_of_links: The number of random URLs to generate.
    :return: A list of random URLs.
    """
    start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    date_range = (end - start).days
    random_dates = set()

    # Ensure that we don't generate more dates than what is available in the range
    max_links = min(number_of_links, date_range)

    while len(random_dates) < max_links:
        random_days = random.randrange(date_range)
        random_date = start + datetime.timedelta(days=random_days)
        random_dates.add(random_date)

    base_url = 'https://www.normanok.gov/sites/default/files/documents/{year}-{month:02d}/{date}_daily_incident_summary.pdf'
    random_urls = [
        base_url.format(year=date.year, month=date.month, date=date.strftime('%Y-%m-%d')) for date in random_dates
    ]

    return random_urls

# Function to extract incidents from a PDF file


def extract_incidents(pdf_path):
    # Open the PDF file to read its contents
    with fitz.open(pdf_path) as doc:
        all_text = ''.join(page.get_text() for page in doc)

    # Split the combined text into individual lines
    lines = all_text.split('\n')

    incidents = []

    for i in range(len(lines)):
        if 'Date / Time' in lines[i]:
            continue  # Skip header line

        if i + 4 < len(lines) and '/' in lines[i] and ':' in lines[i]:
            edge_case_temp = lines[i + 3].strip()
            if edge_case_temp == "RAMP":
                edge_case_temp = lines[i + 4].strip()
            incident_data = {
                'Date/Time': lines[i].strip(),
                'Incident Number': lines[i + 1].strip(),
                'Location': lines[i + 2].strip(),
                'Nature': edge_case_temp if ':' not in lines[i + 3].strip() else "NULLVALUE",
                'Incident ORI': lines[i + 4].strip()
            }
            incidents.append(incident_data)

    return incidents


# Function to create a SQLite database with necessary tables


def createdb(db_filename="normanpd.db", resources_dir="resources"):
    """
    Create a SQLite database with the necessary table if it doesn't exist, in the parent directory's 'resources' folder.

    Parameters:
    - db_filename: Name of the SQLite database file.
    - resources_dir: Directory name to store the SQLite database file, relative to the parent directory of this script.

    Returns:
    - Connection object to the SQLite database.
    """
    # Calculate the parent directory of this script
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Construct the full path to the resources directory in the parent directory
    resources_full_path = os.path.join(parent_dir, resources_dir)

    # Ensure the resources directory exists
    if not os.path.exists(resources_full_path):
        os.makedirs(resources_full_path)

    # Construct the full path to the database file
    db_path = os.path.join(resources_full_path, db_filename)

    # Connect to the SQLite database at the specified path
    try:
        conn = sqlite3.connect(db_path)
        # Create the incidents table if it doesn't exist
        with conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS incidents (
                    incident_time TEXT,
                    incident_number TEXT UNIQUE,
                    incident_location TEXT,
                    nature TEXT,
                    incident_ori TEXT
                );
            ''')
        # print(f"Database created at: {db_path}")
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

# Function to populate the SQLite database with incident data


def populatedb(db, incidents):
    c = db.cursor()
    for incident in incidents:
        # Check if the incident number already exists
        c.execute('SELECT incident_number FROM incidents WHERE incident_number = ?',
                  (incident['Incident Number'],))  # Use 'Incident Number' key
        if c.fetchone() is None:
            # Only insert if the incident does not exist
            c.execute('INSERT INTO incidents (incident_time, incident_number, incident_location, nature, incident_ori) VALUES (?,?,?,?,?)',
                      (incident['Date/Time'], incident['Incident Number'], incident['Location'], incident['Nature'], incident['Incident ORI']))  # Use keys accordingly
    db.commit()

# Function to display the status of incidents in the database


def status(conn):
    c = conn.cursor()
    query = '''
    SELECT nature, COUNT(nature) AS cnt
    FROM incidents
    GROUP BY nature
    ORDER BY cnt DESC, nature ASC;
    '''
    c.execute(query)
    results = c.fetchall()

    for nature, count in results:
        if (nature == "NULLVALUE"):
            print(f'|{count}')

        else:
            print(f'{nature}|{count}')

# Function to print the total count of incidents in the database


def print_total_incidents_count(db):
    # Connect to the SQLite database
    conn = sqlite3.connect(db)
    c = conn.cursor()

    # Query to count the total number of incidents
    query = 'SELECT COUNT(*) FROM incidents;'
    c.execute(query)
    count = c.fetchone()[0]  # Fetch the first (and only) row of the result

    # Print the total number of incidents
    print(f'Total incidents in database: {count}')

    # Close the connection to the database
    conn.close()

# Main function to orchestrate the entire process


def main(url):
    # Remove the existing 'normanpd.db' database if it exists
    if os.path.exists('../resources/normanpd.db'):
        os.remove('../resources/normanpd.db')

    # Create or connect to the database
    db = createdb()
    if db is None:
        print("Failed to create or connect to the database.")
        return

    # Proceed with downloading PDF, extracting incidents, and populating the database
    pdf_path = download_pdf(url)
    incidents = extract_incidents(pdf_path)
    populatedb(db, incidents)
    status(db)

    # Close the database connection
    db.close()

    # Optional: Remove the PDF file after processing
    os.remove(pdf_path)


# Entry point of the script
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Download and process police incident PDFs.')
    parser.add_argument('--incidents', type=str, required=True,
                        help='URL of the incident PDF to process.')
    args = parser.parse_args()
    main(args.incidents)
