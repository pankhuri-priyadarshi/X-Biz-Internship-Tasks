import pyodbc

from db import CONN_STR

try:
    conn = pyodbc.connect(CONN_STR)
    print("Connected Successfully!")
    conn.close()
except Exception as e:
    print("Failed:", e)
