from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "service": "app1",
        "message": "Hello from App1 - I provide data!"
    })

@app.route('/data')
def get_data():
    return jsonify({
        "service": "app1",
        "data": "This is data from App1"
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
