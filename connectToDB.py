import os
import cx_Oracle
from flask import Flask, render_template, request
from dotenv import load_dotenv

load_dotenv()

# Get environment variables to access the database
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
SID = os.getenv("SID")

# Connect to database and retrieve the cursor object to execute queries
dsn_tns = cx_Oracle.makedsn(HOST, PORT, SID)
conn = cx_Oracle.connect(user=USER, password=PASSWORD, dsn=dsn_tns)
c = conn.cursor()

tableNames = [
    "APPOINTMENT",
    "MEDICAL_HISTORY",
    "PATIENT",
    "FULL_TIME_STAFF",
    "PART_TIME_STAFF",
    "STAFF",
    "INSURANCE",
    "ADDRESS",
    "PROCEDURES",
]

# Initialize Flask app
app = Flask(__name__)


# Results route
@app.route("/result", methods=["GET", "POST"])
def result_page():
    if request.method == "POST":
        # Get submitted information
        form_input = request.form.to_dict()
        action = form_input["action"]
        output = {}

        # Handle user input
        if action == "reset":
            drop_tables()
            create_tables()
            populate_tables()
            output["return_code"] = 0
        elif action == "drop":
            output = drop_tables()
        elif action == "create":
            output = create_tables()
        elif action == "populate":
            output = populate_tables()
        elif action == "close":
            conn.close()
        elif action == "query":
            query = form_input["specific_query"].replace(";", "")
            output = executeQuery(query)

        return render_template("result.html", input=form_input, output=output)
    else:
        # Redirect to form if request method is not POST
        return render_template("action.html")


# Load form
@app.route("/action")
def action_page():
    return render_template("action.html")


# Load About page
@app.route("/about")
def about_page():
    return render_template("about.html")


# Load main page
@app.route("/")
def index_page():
    # Get table data
    data = get_tables()

    return render_template("index.html", rowData=data)


def executeQuery(query):
    status_code = {"return_code": 0, "return_values": []}

    try:
        c.execute(query)
        result = c.fetchall()
        # Save returned rows from query, if any
        if len(result) > 0:
            for row in result:
                status_code["return_values"].append(row)
    except Exception as e:
        # Catches errors
        status_code["return_values"].append(e.args[0])
        if status_code["return_code"] == 0:
            status_code["return_code"] = -1

    return status_code


def checkIfTablesExist():
    # Check if tables exist by table count
    numTables = 0
    for name in tableNames:
        c.execute(
            f"SELECT count(*) FROM all_objects WHERE object_type IN ('TABLE') AND object_name = '{name}'"
        )
        numTables += c.fetchall()[0][0]
    return numTables > 0


def create_tables():
    # Read query commands from file (all in 1 line)
    with open("createTables.txt", "r") as file:
        sql_queries = file.read().rstrip()
    query_arr = [i.strip() for i in sql_queries.split(";") if len(i) > 0]

    status_code = {"return_code": 0, "error_msgs": []}

    for query in query_arr:
        try:
            c.execute(query)
        except Exception as e:
            # Catches errors (mainly ORA-00955: Table already exists)
            status_code["error_msgs"].append((query, e.args[0]))
            if status_code["return_code"] == 0:
                status_code["return_code"] = -1

    return status_code


def populate_tables():
    # Read query commands from file (all on separate lines)
    with open("populateTables.txt", "r") as file:
        sql_queries = file.read().replace("\n", "")
    query_arr = [i.strip() for i in sql_queries.split(";") if len(i) > 0]

    status_code = {"return_code": 0, "error_msgs": []}

    for query in query_arr:
        try:
            c.execute(query)
        except Exception as e:
            # Catches errors (Mainly ORA-00001: non-unique value in unique column)
            status_code["error_msgs"].append((query, e.args[0]))
            if status_code["return_code"] == 0:
                status_code["return_code"] = -1

    return status_code


def drop_tables():
    status_code = {"return_code": 0, "error_msgs": []}

    for name in tableNames:
        query = f"DROP TABLE {name}"
        try:
            c.execute(query)
        except Exception as e:
            # Catches errors (mainly ORA-00942: Table doesn't exist error)
            status_code["error_msgs"].append((query, e.args[0]))
            if status_code["return_code"] == 0:
                status_code["return_code"] = -1

    return status_code


def get_tables():
    allTableRows = {}
    allTableCols = {}

    tablesExist = checkIfTablesExist()

    if tablesExist:
        for name in tableNames:
            # Get columns names
            c.execute(
                f"SELECT COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE TABLE_NAME='{name}' ORDER BY COLUMN_ID"
            )
            cols = []
            for row in c:
                cols.append(row[0].replace("_", " ").title())
            allTableCols[name] = tuple(cols)

            # Get table rows
            c.execute(f"SELECT * FROM {name}")
            allTableRows[name] = [row for row in c]

        # Fixing CLOB Objects to be readable
        old_staff_array = allTableRows["STAFF"]
        new_staff_array = []
        for staff in old_staff_array:
            temp = list(staff)
            temp[6] = temp[6].read() if temp[6] is not None else temp[6]
            temp2 = tuple(temp)
            new_staff_array.append(temp2)
        allTableRows["STAFF"] = new_staff_array

        # Fixing Datetime.Datetime Objects to be readable
        old_app_array = allTableRows["APPOINTMENT"]
        new_app_array = []
        for app in old_app_array:
            temp = list(app)
            temp[4] = temp[4].strftime("%m/%d/%Y, %H:%M:%S")
            temp2 = tuple(temp)
            new_app_array.append(temp2)
        allTableRows["APPOINTMENT"] = new_app_array

        # Add column names to data
        for tableName in allTableCols:
            allTableRows[tableName].insert(0, allTableCols[tableName])

    return allTableRows


if __name__ == "__main__":
    app.run()
