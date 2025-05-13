from sqlite3 import connect
from pathlib import Path
from functools import wraps
import pandas as pd

class QueryMixin:
    # Initialize with an optional path, defaulting to the adjacent DB file
    def __init__(self, db_path: Path = None):
        # If no path passed, point at employee_events.db beside this file
        self.db_path = db_path or (Path(__file__).resolve().parent / "employee_events.db")

    # Define a method that runs a SQL query and returns a pandas DataFrame
    def pandas_query(self, sql_query, params=()):
        try:
            # Connect using the instance's db_path
            with connect(self.db_path) as connection:
                # run the SQL query and convert results to a pandas DataFrame
                return pd.read_sql_query(sql_query, connection, params=params)
        except Exception as e:
            # print any error and return an empty DataFrame if it fails
            print(f"Error executing pandas_query: {e}")
            return pd.DataFrame()

    # Define a method that runs a SQL query and returns raw tuples
    def query(self, sql_query, params=()):
        try:
            with connect(self.db_path) as connection:
                cursor = connection.cursor()       # get a cursor to interact with DB
                cursor.execute(sql_query, params)  # execute safely with parameters
                return cursor.fetchall()           # return all results as list of tuples
        except Exception as e:
            print(f"Error executing query: {e}")
            return []


def query(func):
    """
    Decorator that runs a standard SQL execution
    and returns a list of tuples.

    The wrapped function may return either:
      - a plain SQL string, or
      - a tuple (sql_string, params_tuple)
    """
    @wraps(func)
    def run_query(*args, **kwargs):
        # Call the original to get SQL (and possibly params)
        res = func(*args, **kwargs)
        if isinstance(res, tuple) and len(res) == 2:
            sql, params = res
        else:
            sql, params = res, ()

        # Determine which db_path to use:
        # if first arg is a QueryMixin instance, use its .db_path
        if args and hasattr(args[0], "db_path"):
            db = args[0].db_path
        else:
            # fallback to the default file next to this code
            db = Path(__file__).resolve().parent / "employee_events.db"

        conn = connect(db)
        try:
            cursor = conn.execute(sql, params)
            return cursor.fetchall()
        finally:
            conn.close()
    return run_query
