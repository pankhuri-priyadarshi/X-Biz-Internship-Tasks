from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/', methods=['POST'])
def calculate():
    data = request.get_json()
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

    # If merge=True, call API2
    if merge:
        try:
            response = requests.post("http://api2:5002/",
                                     json={"data1": data1, "data2": data2})
            api2_result = response.json()
        except Exception as e:
            return jsonify({"error": f"API2 connection failed: {str(e)}"}), 500

        return jsonify({
            "api1Result": result,
            "api2Result": api2_result
        })

    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
