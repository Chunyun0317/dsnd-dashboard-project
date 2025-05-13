from fasthtml import FastHTML, serve
from fasthtml.common import Select, Label, Div, H1, Option, RedirectResponse
import matplotlib.pyplot as plt  # import pyplot for visuals
import pandas as pd  # Import pandas for DataFrame manipulation
import sqlite3  # import sqlite3 for database connections
from pathlib import Path
import sys, os  # import modules for system and OS interactions

# Ensure correct absolute path for the database employee_events.db
# db_file is used whenever connecting to sqlite in this script
project_root = Path(__file__).resolve().parent.parent
db_file = project_root / "python-package" / "employee_events" / "employee_events.db"
# If needed, extend sys.path to import local modules
# sys.path.append(str(project_root / 'python-package'))

# Import SQL models
from employee_events.employee import Employee  # As defined in assignment
from employee_events.team import Team        # As defined in assignment

# import the load_model function from the utils.py file
from report.utils import load_model

# Below, we import the parent classes you will use for subclassing
from report.base_components import Dropdown, BaseComponent, Radio, MatplotlibViz, DataTable
from report.combined_components import FormGroup, CombinedComponent

# FastHTML app
app = FastHTML()

# Create a subclass of base_components/dropdown called `ReportDropdown`
class ReportDropdown(Dropdown):
    # Overwrite the build_component method
    # ensuring it has the same parameters as the parent class's method
    def build_component(self, entity_id, model):
        # Set the `label` attribute so it is set to the `name` attribute for the model
        self.label = model.name
        # Return the output from the parent class's build_component method
        return super().build_component(entity_id, model)

    # Overwrite the `component_data` method
    # Ensure the method uses the same parameters as the parent class
    def component_data(self, entity_id, model):
        # Using the model argument call the method that returns names and ids
        return model.names()

# Create a subclass of base_components/BaseComponent called `Header`
class Header(BaseComponent):
    # Overwrite the `build_component` method
    # Ensure the method has the same parameters as the parent class
    def build_component(self, entity_id, model):
        # return an H1 containing the model's name attribute + ' performance'
        return H1(f"{model.name} performance")

# Create a subclass of base_components/MatplotlibViz called `LineChart`
class LineChart(MatplotlibViz):
    # Overwrite the parent class's `visualization` method
    # Use the same parameters as the parent
    def visualization(self, entity_id, model):
        # Pass entity_id to model.event_counts to receive counts
        data = model.event_counts(entity_id)
        # fill nulls with 0 and set date index
        data = data.fillna(0)
        data['event_date'] = pd.to_datetime(data['event_date'])
        data.set_index('event_date', inplace=True)
        data = data.sort_index()
        # rename columns for readability
        data.rename(columns={"positive_events": "Positive", "negative_events": "Negative"}, inplace=True)
        # Validate required columns
        if not set(["Positive", "Negative"]).issubset(data.columns):
            raise KeyError("ERROR: Missing required columns in DataFrame before cumulative sum.")
        # ensure numeric
        data[["Positive", "Negative"]] = data[["Positive", "Negative"]].apply(pd.to_numeric, errors="coerce")
        # cumulative sum
        data = data.cumsum()
        # Initialize plot
        fig, ax = plt.subplots()
        if data.empty:
            raise ValueError("ERROR: No numeric data available to plot.")
        data.plot(ax=ax)
        # style and labels
        self.set_axis_styling(ax, bordercolor='black', fontcolor='black')
        ax.set_title("Event Counts Over Time")
        ax.set_xlabel("")
        ax.set_ylabel("Event Count")
        return fig

# Create a subclass of base_components/MatplotlibViz called `BarChart`
class BarChart(MatplotlibViz):
    # predictor for ML risk
    predictor = load_model()

    def visualization(self, entity_id, model):
        # 1) load the full DataFrame (includes employee_id)
        data = model.model_data(entity_id)

        # 2) select only the numeric features your model expects
        X = data[["positive_events", "negative_events"]]

        # 3) predict
        proba = self.predictor.predict_proba(X)[:, 1]
        pred = proba.mean() if model.name == "team" else proba[0]

        # 4) plotting
        fig, ax = plt.subplots()
        ax.barh(["Risk"], [pred])
        ax.set_xlim(0, 1)
        ax.set_title("Risk of being recruited by another company")
        ax.set_xlabel("Probability of losing the employee")
        self.set_axis_styling(ax, bordercolor="black", fontcolor="black")
        return fig

# Create a subclass of combined_components/CombinedComponent called Visualizations
class Visualizations(CombinedComponent):
    # children components
    children = [LineChart(), BarChart()]
    # layout container
    outer_div_type = Div(cls='grid')

# Create a subclass of base_components/DataTable called `NotesTable`
class NotesTable(DataTable):
    # Overwrite the `component_data` method
    def component_data(self, entity_id, model):
        # return the notes DataFrame
        return model.notes(entity_id)

# Filters form
class DashboardFilters(FormGroup):
    id = "top-filters"
    action = "/update_data"
    method = "POST"
    children = [
        Radio(
            values=["Employee", "Team"],
            name='profile_type',
            hx_get='/update_dropdown',
            hx_target='#selector'
        ),
        ReportDropdown(
            id="selector",
            name="user-selection"
        )
    ]

# Combined report
class Report(CombinedComponent):
    children = [Header(), DashboardFilters(), Visualizations(), NotesTable()]

# instantiate report
report = Report()

# --- Routes ---
@app.get('/')
def homepage():
    # default to Employee ID 1
    return report('1', Employee(db_file))

@app.get('/employee/{id}')
def employee_page(id: str):
    return report(id, Employee(db_file))

@app.get('/team/{id}')
def team_page(id: str):
    return report(id, Team(db_file))

@app.get('/update_dropdown')
def update_dropdown(r):
    # dynamic dropdown update
    profile = r.query_params.get('profile_type', 'Employee')
    model = Team(db_file) if profile == 'Team' else Employee(db_file)
    return DashboardFilters.children[1].build_component(None, model)

@app.post('/update_data')
async def update_data(r):
    data = await r.form()
    profile = data.get('profile_type')
    selected = data.get('user-selection')
    path = '/team/' if profile == 'Team' else '/employee/'
    return RedirectResponse(f"{path}{selected}", status_code=303)

# Start the app
if __name__ == '__main__':
    serve()
