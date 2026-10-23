from flask import Flask, session, jsonify, request, redirect

app = Flask(__name__)
app.secret_key = "lab-secret-not-for-prod"

USERS = {"alice": 1, "bob": 2}

PROFILES = {
    1: {"user_id": 1, "name": "Alice", "reading_list": ["Dune", "The Hobbit"], "email": "alice@example.com"},
    2: {"user_id": 2, "name": "Bob", "reading_list": ["Project Hail Mary"], "email": "bob@example.com"},
}


@app.get("/login/<username>")
def login(username):
    if username not in USERS:
        return "unknown user", 404
    session["user_id"] = USERS[username]
    return f"logged in as {username} (user_id={USERS[username]})"


@app.get("/profile")
def profile():
    if "user_id" not in session:
        return redirect("/login/alice")
    # VULN: X-User-Id header takes precedence over the session, with no check that it matches
    header_user_id = request.headers.get("X-User-Id", type=int)
    effective_id = header_user_id if header_user_id is not None else session["user_id"]
    data = PROFILES.get(effective_id)
    if not data:
        return "not found", 404
    return jsonify(data)


@app.get("/")
def index():
    return (
        "Pagebound Books - profile demo. "
        "Try /login/alice then GET /profile, then again with header X-User-Id: 2"
    )


if __name__ == "__main__":
    app.run(port=5004, debug=True)
