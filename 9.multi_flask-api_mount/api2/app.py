from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['POST'])
def operations():
    data = request.get_json()
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
    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
