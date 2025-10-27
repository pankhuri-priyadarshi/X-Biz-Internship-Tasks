from flask import Flask, request, jsonify
from db import insert_log

app = Flask(__name__)

@app.route('/', methods=['POST'])
def operations():
    data = request.get_json() or {}
    data1 = data.get("data1")
    data2 = data.get("data2")

    if not all(isinstance(x, (int, float)) for x in [data1, data2]):
        return jsonify({"error": "data1 and data2 must be numbers"}), 400

    big, small = max(data1, data2), min(data1, data2)
    results = {
        "+": data1 + data2,
        "-": big - small,
        "*": data1 * data2,
        "/": round(big / small, 2) if small != 0 else "Infinity"
    }

    api_request = {"data1": data1, "data2": data2}
    api_response = results

    try:
        insert_log("SECOND", data1, data2, None, api_request, api_response)
    except Exception as e:
        return jsonify({"warning": "logging failed", "error": str(e)}), 500

    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
