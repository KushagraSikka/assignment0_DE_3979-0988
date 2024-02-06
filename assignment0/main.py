# -*- coding: utf-8 -*-
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


def download_pdf(url, local_filename='incident.pdf'):
    response = requests.get(url)
    with open(local_filename, 'wb') as file:
        file.write(response.content)
    return local_filename


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


def extract_incidents(pdf_path):
    doc = fitz.open(pdf_path)
    incidents = []
    is_header = True  # Flag to identify the header line

    for page in doc:
        text = page.get_text("text")
        lines = text.split('\n')

        for i in range(len(lines)):
            if is_header:
                if 'Date / Time' in lines[i]:
                    is_header = False
                continue  # Skip header line

            # Check if the line is empty (no characters at all)
            if not lines[i].strip():
                date_time = "NULL"
                incident_number = "NULL"
                location = "NULL"
                nature = "NULL"
                incident_ori = "NULL"
            else:
                if i + 4 < len(lines) and '/' in lines[i] and ':' in lines[i]:
                    date_time = lines[i].strip()
                    incident_number = lines[i + 1].strip()
                    location = lines[i + 2].strip()
                    nature = lines[i + 3].strip()
                    incident_ori = lines[i + 4].strip()
                else:
                    # Handle cases where there are not enough lines for a complete entry
                    date_time = "NULL"
                    incident_number = "NULL"
                    location = "NULL"
                    nature = "NULL"
                    incident_ori = "NULL"

            incident_data = {
                'Date/Time': date_time,
                'Incident Number': incident_number,
                'Location': location,
                'Nature': nature,
                'Incident ORI': incident_ori
            }
            # incidents.append(incident_data)
            # if i + 4 < len(lines) and '/' in lines[i] and ':' in lines[i]:
            #     date_times.append(lines[i].strip()) if checkdatetime(
            #         lines[i].strip()) else natures.append(" ")
            #     incident_numbers.append(
            #         lines[i + 1].strip()) if "-" in lines[i+1].strip() else natures.append(" ")
            #     locations.append(
            #         lines[i + 2].strip()) if " " in lines[i+2] else natures.append(" ")
            # if checkdatetime(lines[i+3].strip()):
            #     natures.append(" ")
            # else:
            #     natures.append(lines[i + 3].strip())
            # # natures.append(lines[i + 3].strip()) if " " in lines[i+3] else " "
            # incident_oris.append(
            #     lines[i + 4].strip()) if lines[i+4].isalnum() else " "

    doc.close()
    return incidents


# def createdb():
#     # Define the database path to be in the 'resources' folder of the parent directory
#     parent_dir = os.path.dirname(os.getcwd())
#     db_path = os.path.join(parent_dir, 'resources', 'normanpd.db')

#     # Make sure the 'resources' directory exists, create if it does not
#     os.makedirs(os.path.dirname(db_path), exist_ok=True)

#     # Connect to the SQLite database at the specified path
#     conn = sqlite3.connect(db_path)
#     c = conn.cursor()
#     c.execute('''CREATE TABLE IF NOT EXISTS incidents
#                  (incident_time TEXT, incident_number TEXT UNIQUE, incident_location TEXT, nature TEXT, incident_ori TEXT)''')
#     return conn


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


# def populate_db(db_path, df):
#     """Insert DataFrame records into the SQLite database, excluding rows with null Incident Numbers."""
#     # Filter out rows where 'Incident Number' is null or empty
#     filtered_df = df[pd.notnull(df['Incident Number']) & (
#         df['Incident Number'] != '')]

#     # Connect to the SQLite database
#     conn = sqlite3.connect(db_path)
#     # Replace 'if_exists='replace'' with 'if_exists='append'' to keep existing data and add new non-null records
#     filtered_df.to_sql('incidents', conn, if_exists='append', index=False)
#     conn.commit()
#     conn.close()


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
        print(f'{nature}|{count}')


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Download and process police incident PDFs.')
    parser.add_argument('--incidents', type=str, required=True,
                        help='URL of the incident PDF to process.')
    args = parser.parse_args()
    main(args.incidents)
