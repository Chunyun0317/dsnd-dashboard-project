import sqlite3
import pandas as pd  # To return data as DataFrame when needed
from .sql_execution import QueryMixin

# Define a class called QueryBase
# Use inheritance to add methods
# for querying the employee_events database.
class QueryBase(QueryMixin):

    # Create a class attribute called `name`
    # set the attribute to an empty string
    name = ""  # initialize an empty string variable called 'name'

    # Initialize with the database path for connecting
    def __init__(self, db_path="python-package/employee_events/employee_events.db"):
        # we put in parameter the path
        self.db_path = db_path  # Database file path

    # Define a helper to open a connection
    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    # Define a `names` method that receives
    # no passed arguments
    def names(self):
        # Return an empty list
        return []

    # Define an `event_counts` method
    # that receives an `id` argument
    # This method should return a pandas dataframe
    def event_counts(self, id):
        # QUERY 1
        # Write an SQL query that groups by `event_date`
        # and sums the number of positive and negative events
        # Use parameter placeholders for safety
        query = """
            SELECT event_date, 
                   SUM(positive_events) AS positive_events, 
                   SUM(negative_events) AS negative_events
            FROM employee_events
            WHERE {}_id = ?
            GROUP BY event_date
            ORDER BY event_date
        """.format(self.name)
        # Query contains the SQL to get date of events, total good/bad events
        # Filtered by ID (team_id or employee_id), grouped by date

        # Execute the query and return as DataFrame
        with self._get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=(id,))
        return df

    # Define a `notes` method that receives an id argument
    # This function should return a pandas dataframe
    def notes(self, id):
        # QUERY 2
        # Write an SQL query that returns `note_date`, and `note`
        # from the `notes` table
        # Use parameter placeholders for safety
        query = f"""
            SELECT note_date, note
            FROM notes
            WHERE {self.name}_id = ?
        """
        # Get the date of note creation and note content

        # Execute the query and return as DataFrame
        with self._get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=(id,))
        return df.rename(columns={"note_date": "Note date", "note": "Note"})

    # utility method to execute an SQL query.
    # Centralized SQL execution; subclasses can reuse this.
    def execute_query(self, query, params=()):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchall()  # Return results as a list of tuples
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
