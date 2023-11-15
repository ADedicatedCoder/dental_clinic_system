import sys
import os
import cx_Oracle
from flask import Flask, render_template
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


@app.route("/")
def index_page():
    data = get_tables()

    return render_template("index.html", rowData=data)


def get_tables():
    allTableRows = {}
    allTableCols = {}

    # Checking if tables exist
    numTables = 0
    for name in tableNames:
        c.execute(f"select count(*) from all_objects where object_type in ('TABLE','VIEW') and object_name = '{name}'")
        numTables += c.fetchall()[0][0]

    if numTables > 0:
        for name in tableNames:
            c.execute(f"select COLUMN_NAME from ALL_TAB_COLUMNS where TABLE_NAME='{name}' ORDER BY COLUMN_ID")
            cols = []
            for row in c:
                cols.append(row[0].replace("_", " ").title())
            allTableCols[name] = tuple(cols)
            c.execute(f"select * from {name}")
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
