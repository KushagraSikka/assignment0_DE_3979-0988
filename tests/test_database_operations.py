# test_database_operations.py

import pytest
import sqlite3
import os
from assignment0.main import createdb, populatedb


def test_createdb():
    db_conn = createdb(db_filename="testdb")
    assert db_conn is not None
    assert isinstance(db_conn, sqlite3.Connection)
# this test checks if the database is created and if it is a sqlite3 connection object
# if the database is created and the connection object is a sqlite3 connection object, the test passes


def test_populatedb():
    db_conn = createdb(db_filename="testdb")
    sample_data = [{
        'Date/Time': '2024-01-01 12:00',
        'Incident Number': '12345',
        'Location': 'Test Location',
        'Nature': 'Test Nature',
        'Incident ORI': 'Test ORI'
    }]
    populatedb(db_conn, sample_data)
    cursor = db_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM incidents")
    count = cursor.fetchone()[0]
    assert count == len(sample_data)
    os.remove("resources/testdb")
