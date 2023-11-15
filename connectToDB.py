import sys
import os
import cx_Oracle
from flask import Flask, render_template, url_for, request
from dotenv import load_dotenv
import datetime

load_dotenv()

USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
SID = os.getenv("SID")

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

app = Flask(__name__)


@app.route("/result", methods=["GET", "POST"])
def result_page():
    output = request.form.to_dict()
    action = output["action"]
    query = output["query"]
    return render_template("result.html", result=output)


@app.route("/action", methods=["GET"])
def action_page():
    return render_template("action.html")


@app.route("/")
def index_page():
    data = get_tables()

    return render_template("index.html", rowData=data)


def checkIfTablesExist():
    # Checking if tables exist by table count
    numTables = 0
    for name in tableNames:
        c.execute(
            f"SELECT count(*) FROM all_objects WHERE object_type IN ('TABLE') AND object_name = '{name}'"
        )
        numTables += c.fetchall()[0][0]
    return numTables > 0


def create_tables():
    tablesExist = checkIfTablesExist()

    # Prevent repeated creation of tables
    if tablesExist:
        drop_tables()

    with open("createTables.txt", "r") as file:
        sql_queries = file.read().rstrip()
    query_arr = [i.strip() for i in sql_queries.split(";") if len(i) > 0]

    for query in query_arr:
        c.execute(query)


def populate_tables():
    tablesExist = checkIfTablesExist()

    # Prevent repeated creation of tables
    if not tablesExist:
        create_tables()

    with open("populateTables.txt", "r") as file:
        sql_queries = file.read().replace("\n", "")
    query_arr = [i.strip() for i in sql_queries.split(";") if len(i) > 0]

    for query in query_arr:
        c.execute(query)


def drop_tables():
    for name in tableNames:
        try:
            c.execute(f"DROP TABLE {name}")
        except Exception as e:
            # Catches errors (mainly ORA-00942: Table doesn't exist error)
            print(e.args[0])


def get_tables():
    allTableRows = {}
    allTableCols = {}

    tablesExist = checkIfTablesExist()

    if tablesExist:
        for name in tableNames:
            c.execute(
                f"SELECT COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE TABLE_NAME='{name}' ORDER BY COLUMN_ID"
            )
            cols = []
            for row in c:
                cols.append(row[0].replace("_", " ").title())
            allTableCols[name] = tuple(cols)
            c.execute(f"SELECT * FROM {name}")
            allTableRows[name] = [row for row in c]

        # Fixing CLOB Objects
        old_staff_array = allTableRows["STAFF"]
        new_staff_array = []
        for staff in old_staff_array:
            temp = list(staff)
            temp[6] = temp[6].read() if temp[6] is not None else temp[6]
            temp2 = tuple(temp)
            new_staff_array.append(temp2)
        allTableRows["STAFF"] = new_staff_array

        # Fixing Datetime.Datetime Objects
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
