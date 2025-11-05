from flask import Flask, jsonify,request
import requests
import os

app = Flask(__name__)
output = "Uploads"
os.makedirs(output, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])

def upload():
    if request.method == 'GET':
        return "GET method received"
    
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    filepath = os.path.join(output, file.filename)
    file.save(filepath)
    return jsonify({"message": "File uploaded successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)