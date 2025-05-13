# Import the QueryBase class
from .query_base import QueryBase  # As specified in the assignment

# Import pandas since it’s used below
import pandas as pd


# Create a subclass of QueryBase
# called `Team`
class Team(QueryBase):
    # Uses inheritance to add query-related methods from QueryBase/Mixin

    # Set the class attribute `name`
    # to the string "team"
    name = "team"

    # I added an __init__ method to set the database path
    def __init__(self, db_path=None):
        """
        Initialize the database path, allowing an override.
        QueryBase.__init__ will default if none given.
        """
        super().__init__(db_path=db_path)

    # Define a `names` method
    # that receives no arguments
    # This method should return
    # a list of tuples from an SQL execution
    def names(self):
        query = """
            SELECT team_name, team_id
            FROM team
        """
        return self.query(query)

    # Define a `username` method
    # that receives an ID argument
    # This method should return
    # a list of tuples from an SQL execution
    def username(self, id):
        query = """
            SELECT team_name
            FROM team
            WHERE team_id = ?
        """
        return self.query(query, (id,))

    # Below is a method with an SQL query
    # This SQL query generates the data needed for
    # the machine learning model.
    # Without editing the query, alter this method
    # so when it is called, a Pandas DataFrame
    # is returned containing the execution of
    # the SQL query
    def model_data(self, id):
        # SQL query string that will:
        # Join the 'team' and 'employee_events' tables on 'team_id'
        # Filter for a specific team_id (provided as parameter '?')
        # Group results by employee_id to aggregate event counts
        # Calculate SUM of positive_events and negative_events per employee
        query = """
            SELECT
                employee_id,
                SUM(positive_events)   AS positive_events,
                SUM(negative_events)   AS negative_events
            FROM employee_events
            WHERE team_id = ?
            GROUP BY employee_id
        """
        # Return the query results as a cleaned pandas DataFrame
        return self.pandas_query(query, (id,))
