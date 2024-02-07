import unittest
import sqlite3
from assignment0.main import createdb, populatedb, status


class TestStatusFunction(unittest.TestCase):

    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.conn = sqlite3.connect('testdb_status')
        self.db = createdb(db_filename='testdb_status', resources_dir='.')
        self.assertIsNotNone(self.db)

        # Sample incidents data for testing
        self.incidents = [
            {
                'Date/Time': '2024-01-01 12:00:00',
                'Incident Number': '12345',
                'Location': 'Sample Location 1',
                'Nature': 'Nature A',
                'Incident ORI': '123456'
            },
            {
                'Date/Time': '2024-01-02 14:00:00',
                'Incident Number': '67890',
                'Location': 'Sample Location 2',
                'Nature': 'Nature B',
                'Incident ORI': '789012'
            },
            {
                'Date/Time': '2024-01-03 15:30:00',
                'Incident Number': '54321',
                'Location': 'Sample Location 3',
                'Nature': 'Nature A',
                'Incident ORI': '654321'
            }
        ]

        # Populate the database with sample incidents data
        populatedb(self.db, self.incidents)

    def tearDown(self):
        # Close the database connection
        self.db.close()

    def test_status_function(self):
        # Call the status function and capture its output
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output
        status(self.db)
        sys.stdout = sys.__stdout__  # Reset the standard output

        # Check the captured output to verify the status function's behavior
        expected_output = "Nature A|2\nNature B|1\n"
        self.assertEqual(captured_output.getvalue(), expected_output)


if __name__ == '__main__':
    unittest.main()
