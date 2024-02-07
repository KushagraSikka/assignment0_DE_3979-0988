
# Assignment 0 - Data Engineering (DE_3979-0988)

## Description

This repository contains code for Assignment 0 in the Data Engineering course (DE_3979-0988). The assignment involves extracting data from Norman, Oklahoma Police Department incident PDFs, storing the data in a SQLite database, and analyzing the nature of incidents.

## Getting Started

To get started with this project, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/KushagraSikka/assignment0_DE_3979-0988.git
   ```
2. Navigate to the project directory:
   ```bash
   cd assignment0_DE_3979-0988
   ```

## How to Use

The `main.py` script is the entry point of the project. It accepts the `--incidents` argument, which specifies the URL of the incident PDF to process.

Example usage:
```bash
pipenv run python main.py --incidents URL
```
Replace `URL` with the actual URL of the incident PDF.

## Functions

- `download_pdf(url, local_filename='incident.pdf')`: Downloads a PDF from a given URL and saves it locally.
- `generate_random_data(start_date, end_date, number_of_links)`: Generates a list of random URLs for daily incident summary PDFs.
- `extract_incidents(pdf_path)`: Extracts incidents from a PDF file and returns a list of incident dictionaries.
- `createdb(db_filename="normanpd.db", resources_dir="resources")`: Creates a SQLite database with necessary tables for storing incident data.
- `populatedb(db, incidents)`: Populates the SQLite database with incident data.
- `status(conn)`: Displays the status of incidents in the database.
- `print_total_incidents_count(db)`: Prints the total count of incidents in the database.

## Tests

To ensure the correctness and reliability of the code, tests have been implemented using the pytest framework. To run the tests, execute the following command in the terminal:
```bash
pipenv run pytest
```
This command will automatically discover and execute all test files within the tests directory and its subdirectories.

## Bugs and Assumptions

- Assumption: The incident PDFs follow a consistent format.
- All edge cases are handled.

## Collaborators

- Kushagra Sikka | kushagrasikka@gmail.com | kushagrasikka@ufl.edu |

## Acknowledgments

- Stack Overflow community for resolving coding issues.
