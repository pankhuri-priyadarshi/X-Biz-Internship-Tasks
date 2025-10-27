from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Flask app!"

@app.route('/ABOUT')
def about():
    return "This is the ABOUT page."

@app.route('/CONTACT')
def contact():
    return "This is the CONTACT page."

if __name__ == '__main__':
    app.run(debug=True)

print(app.url_map)

