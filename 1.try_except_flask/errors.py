from flask import Flask, request

app = Flask(__name__)

# 400 Bad Request
@app.route('/badrequest', methods=['POST'])
def bad_request():
    data = request.form.get("name")
    if not data:
        return "400 Bad Request: Name is required", 400
    return f"Submitted: {data}"


# 401 Unauthorized
@app.route('/unauthorized')
def unauthorized():
    logged_in = False  
    if not logged_in:
        return "401 Unauthorized: Please log in first", 401
    return "Welcome to Dashboard"


# 403 Forbidden
@app.route('/forbidden')
def forbidden():
    user_role = "guest"  
    if user_role != "admin":
        return "403 Forbidden: You don’t have access", 403
    return "Welcome Admin"


# 404 Not Found
@app.errorhandler(404)
def not_found(e):
    return "404 Not Found: Page does not exist", 404


# 405 Method Not Allowed
@app.errorhandler(405)
def method_not_allowed(e):
    return "405 Method Not Allowed: Wrong HTTP method", 405


# 500 Internal Server Error
@app.route('/servererror')
def server_error():
    return 1 / 0  

@app.errorhandler(500)
def internal_error(e):
    return "500 Internal Server Error", 500


if __name__ == "__main__":
    app.run(debug=True)
