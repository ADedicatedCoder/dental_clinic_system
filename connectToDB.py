import os
import cx_Oracle
from flask import Flask, render_template
from dotenv import load_dotenv
import datetime

load_dotenv()

USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')

dsn_tns = cx_Oracle.makedsn('oracle.scs.ryerson.ca', '1521', 'orcl')
conn = cx_Oracle.connect(user=USER, password=PASSWORD, dsn=dsn_tns)
c = conn.cursor()

app = Flask(__name__)

@app.route("/")
def hello_world():
   allData = {}

   tableNames = ["APPOINTMENT", "MEDICAL_HISTORY", "PATIENT", "FULL_TIME_STAFF", "PART_TIME_STAFF", "STAFF", "INSURANCE", "ADDRESS", "PROCEDURES"]

   for name in tableNames:
      c.execute(f"select * from {name}")
      allData[name] = [row for row in c]

   # Fixing CLOB Objects
   old_staff_array = allData["STAFF"]
   new_staff_array = []
   for staff in old_staff_array:
      temp = list(staff)
      temp[6] = temp[6].read() if temp[6] is not None else temp[6]
      temp2 = tuple(temp)
      new_staff_array.append(temp2)
   allData["STAFF"] = new_staff_array

   # Fixing Datetime.Datetime Objects
   old_app_array = allData["APPOINTMENT"]
   new_app_array = []
   for app in old_app_array:
      temp = list(app)
      temp[4] = temp[4].strftime("%m/%d/%Y, %H:%M:%S")
      temp2 = tuple(temp)
      new_app_array.append(temp2)
   allData["APPOINTMENT"] = new_app_array


   return render_template('index.html', data=allData)

if (__name__ == '__main__'):
    app.run(debug=True)