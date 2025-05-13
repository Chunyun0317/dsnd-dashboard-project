import pytest
from pathlib import Path
from sqlite3 import connect

# Using pathlib create a project_root
# variable set to the absolute path
# for the root of this project
project_root = Path(__file__).resolve().parent.parent

# apply the pytest fixture decorator
# to a `db_path` function
@pytest.fixture
def db_path():
    # Using the `project_root` variable
    # return a pathlib object for the `employee_events.db` file
    return project_root / "python-package" / "employee_events" / "employee_events.db"

# Fixture: Database connection (ensures proper close)
@pytest.fixture
def db_conn(db_path):
    conn = connect(db_path)
    yield conn
    conn.close()

# Fixture: Table names in the database
@pytest.fixture
def table_names(db_conn):
    rows = db_conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchall()
    # normalize to lowercase
    return [row[0].lower() for row in rows]

# Test: Database file exists
def test_db_exists(db_path):
    # using the pathlib `.is_file` method
    # assert that the sqlite database file exists
    assert db_path.is_file(), f"Database file not found at {db_path}"

# Test: Employee table exists
def test_employee_table_exists(table_names):
    # Assert that the string 'employee' is in the table_names list
    assert "employee" in table_names, "Table 'employee' does not exist in the database"

# Test: Team table exists
def test_team_table_exists(table_names):
    # Assert that the string 'team' is in the table_names list
    assert "team" in table_names, "Table 'team' does not exist in the database"

# Test: Employee events table exists
def test_employee_events_table_exists(table_names):
    # Assert that the string 'employee_events' is in the table_names list
    assert "employee_events" in table_names, "Table 'employee_events' does not exist in the database"

# Test: Notes table exists
def test_notes_table_exists(table_names):
    # Assert that the string 'notes' is in the table_names list
    assert "notes" in table_names, "Table 'notes' does not exist in the database"