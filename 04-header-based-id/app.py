from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

USERS = {"alice": 1, "bob": 2}

PROFILES = {
    1: {"user_id": 1, "name": "Alice", "reading_list": ["Dune", "The Hobbit"], "email": "alice@example.com"},
    2: {"user_id": 2, "name": "Bob", "reading_list": ["Project Hail Mary"], "email": "bob@example.com"},
}


@app.get("/login/<username>")
def login(username):
    if username not in USERS:
        return "unknown user", 404
    user_id = USERS[username]
    resp = make_response(f"logged in as {username}. Send the X-User-Id header on subsequent requests.")
    # VULN: the server hands the client its own user id in a header and trusts
    # whatever value the client echoes back, with no server-side session or signature.
    resp.headers["X-User-Id"] = str(user_id)
    return resp


@app.get("/profile")
def profile():
    header_user_id = request.headers.get("X-User-Id", type=int)
    if header_user_id is None:
        return "missing X-User-Id header, log in first", 401
    data = PROFILES.get(header_user_id)
    if not data:
        return "not found", 404
    return jsonify(data)


@app.get("/")
def index():
    return (
        "Pagebound Books - profile demo. "
        "Try /login/alice, note the X-User-Id response header, "
        "then GET /profile sending that header back."
    )


if __name__ == "__main__":
    app.run(port=5004, debug=True)
