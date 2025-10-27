from flask import Flask, jsonify
import os, requests

app = Flask(__name__)

# Get App1 URL from env variable
APP1_URL = os.getenv("APP1_HOST", "http://app1:5000") + "/data"

@app.route('/')
def home():
    return jsonify({
        "service": "app2",
        "message": "Hello from App2 - I consume App1 API"
    })

@app.route('/consume')
def consume():
    try:
        r = requests.get(APP1_URL)
        r.raise_for_status()
        return jsonify({
            "service": "app2",
            "data_from_app1": r.json()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
