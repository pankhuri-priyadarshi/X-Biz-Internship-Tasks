from flask import Flask
import requests
app=Flask(__name__)

@app.route('/data2')
def get_data():
    try:
        response = requests.get("http://img1:5000/data")

        if response.status_code == 200:
            print(f"Hello from Flask-Image2! \nResponse from Image1 - {response.text}")
            return f"Hello from Flask-Image2! \nResponse from Image1 - {response.text}"

    except requests.exceptions.RequestException:
        print("Finding Error in connection with Image1")
        return "Error: Could not connect to Image1"

if __name__=="__main__":
    app.run(host="0.0.0.0",port=8000,debug=True)

