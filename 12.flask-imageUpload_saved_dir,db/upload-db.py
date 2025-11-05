import pyodbc
import json
from datetime import datetime
import flask
import os

app = flask.Flask(__name__)

SERVER = r'DESKTOP-0CBMBC2\SQL2022EXPRESS'
DATABASE = 'testing'
UID = 'sa'
PWD = 'Pankhuri@2608X'

Conn_str=(
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={SERVER};DATABASE={DATABASE};UID={UID};PWD={PWD};"
    "TrustServerCertificate=yes;"
    "Encrypt=no;"
)

def get_conn():
    return pyodbc.connect(Conn_str, autocommit=True)    

def insert_log(filename, filesize, file_extension):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
                    INSERT INTO upload (filename, filesize, file_extension) VALUES (?, ?, ?)
                    """, (filename, filesize, file_extension))
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"Error inserting log: {e}")
        raise
    finally:
        conn.close()

output_dir=r"C:\Users\Pankhuri Priyadarshi\Desktop\xbiz-Projects\12.flask-image_upload_&_db\Upload_sample"
os.makedirs(output_dir, exist_ok=True)

@app.route('/health')
def health_check():
    return "OK", 200

@app.route('/',methods=['GET','POST'])
def upload_file():

    if flask.request.method == 'GET':
        return "Use POST with a file in form-data to upload."
    
    if 'file' not in flask.request.files:
        return "No file part", 400
    
    file = flask.request.files['file']
    if file.filename == '':
        return "No selected file", 400

    filename = file.filename
    file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    file.seek(0, 2)  
    filesize = file.tell() 
    file.seek(0) 

    file.save(os.path.join(output_dir, filename))
    insert_log(filename, filesize, file_extension)

    return f"File {filename} uploaded successfully with size {filesize} bytes and extension {file_extension}", 200
   

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",port=8000)