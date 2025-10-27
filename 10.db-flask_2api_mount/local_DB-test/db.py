import pyodbc
import json
from datetime import datetime


SERVER = r'DESKTOP-0CBMBC2\SQL2022EXPRESS'  
DATABASE = 'API_testing'
UID = 'sa'
PWD = 'pankhuri2608'

CONN_STR = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={SERVER};DATABASE={DATABASE};UID={UID};PWD={PWD};"
    "TrustServerCertificate=yes;"
)
def get_conn():
    return pyodbc.connect(CONN_STR, autocommit=True)

def insert_log(ms_name, value1, value2, perform, api_request_obj, api_response_obj):
    
    req_text = json.dumps(api_request_obj, ensure_ascii=False)
    resp_text = json.dumps(api_response_obj, ensure_ascii=False)
    created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  

    sql = """
    INSERT INTO api_logs (MS_NAME, VALUE1, VALUE2, PERFORM, API_REQUEST, API_RESPONSE, CREATED_DATE)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql, ms_name, value1, value2, perform, req_text, resp_text, created_date)
    finally:
        conn.close()
