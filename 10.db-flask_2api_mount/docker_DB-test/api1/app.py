from flask import Flask, request, jsonify
import requests
from db import insert_log

app = Flask(__name__)

@app.route('/', methods=['POST'])
def calculate():
    data = request.get_json() or {}
    data1 = data.get("data1")
    data2 = data.get("data2")
    perform = data.get("perform")
    merge = data.get("merge", False)

    if not all(isinstance(x, (int, float)) for x in [data1, data2]):
        return jsonify({"error": "data1 and data2 must be numbers"}), 400

    big, small = max(data1, data2), min(data1, data2)

    if perform == '+':
        result = data1 + data2
    elif perform == '-':
        result = big - small
    elif perform == '*':
        result = data1 * data2
    elif perform == '/':
        if small == 0:
            return jsonify({"error": "Division by zero"}), 400
        result = round(big / small, 2)
    else:
        return jsonify({"error": "Invalid operation"}), 400

    api_request = {"data1": data1, "data2": data2, "perform": perform, "merge": merge}
    api_response = {"api1Result": result}

    if merge:
        try:
            response = requests.post("http://api2:5002/", json={"data1": data1, "data2": data2}, timeout=5)
            api2_result = response.json()
            api_response["api2Result"] = api2_result
        except Exception as e:
            api_response["api2Result"] = {"error": f"API2 connection failed: {str(e)}"}

    try:
        insert_log("FIRST", data1, data2, perform, api_request, api_response)
    except Exception as e:
        return jsonify({"warning": "logging failed", "error": str(e)}), 500

    return jsonify(api_response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
