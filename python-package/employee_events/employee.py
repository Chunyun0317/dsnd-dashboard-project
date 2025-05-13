import pandas as pd

# Import the QueryBase class (which includes the QueryMixin logic)
from .query_base import QueryBase  


# Modifications performed in this employee.py file  
# - Imports the necessary modules (QueryBase)  
# - Defines the Employee class, inheriting from QueryBase  
# - Implements username(id) to return an employee's full name using an ID  
# - Converts RAW SQL results into a Pandas DataFrame  
class Employee(QueryBase):
    # Set the class attribute `name` to match the table prefix
    name = "employee"

    def __init__(self, db_path=None):
        """
        Initialize the database path and allow an override from the argument.
        If no path is provided, QueryBase.__init__ will use its default.
        """
        super().__init__(db_path=db_path)

    # Define a method called `names`
    # This method returns a list of tuples from an SQL execution
    def names(self):
        query = """
            SELECT first_name || ' ' || last_name AS full_name,
                   employee_id
            FROM employee
        """
        return self.query(query)  # raw list of (full_name, employee_id) tuples

    # Define a method called `username`
    # Retrieves an employee's full name using an ID
    def username(self, id):
        query = """
            SELECT first_name || ' ' || last_name AS full_name
            FROM employee
            WHERE employee_id = ?
        """
        results = self.query(query, (id,))
        # Return the single name or an empty string if not found
        return results[0][0] if results else ""

    # This method retrieves SQL data for the machine learning model
    # and converts the result into a Pandas DataFrame
    def model_data(self, id):
        query = """
            SELECT
                SUM(e.positive_events)    AS positive_events,
                SUM(e.negative_events)    AS negative_events
            FROM employee_events e
            WHERE e.employee_id = ?
        """
        return self.pandas_query(query, (id,))


# Example instantiation
if __name__ == "__main__":
    employee = Employee()
    print(employee.names())
