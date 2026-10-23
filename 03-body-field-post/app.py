from flask import Flask, session, jsonify, request, redirect

app = Flask(__name__)
app.secret_key = "lab-secret-not-for-prod"

USERS = {"alice": 1, "bob": 2}

ACCOUNTS = {
    1: {"account_id": 1, "name": "Alice", "shipping_address": "1 Reader Ln", "saved_card": "**** 1111"},
    2: {"account_id": 2, "name": "Bob", "shipping_address": "2 Bookworm Ave", "saved_card": "**** 2222"},
}


@app.get("/login/<username>")
def login(username):
    if username not in USERS:
        return "unknown user", 404
    session["user_id"] = USERS[username]
    return f"logged in as {username} (user_id={USERS[username]})"


@app.post("/api/account/details")
def account_details():
    if "user_id" not in session:
        return redirect("/login/alice")
    body = request.get_json(force=True, silent=True) or {}
    account_id = body.get("account_id")
    account = ACCOUNTS.get(account_id)
    if not account:
        return "not found", 404
    # VULN: account_id taken from JSON body, never compared to session user_id
    return jsonify(account)


@app.get("/")
def index():
    return (
        "Pagebound Books — account details demo. "
        "Try /login/alice then POST /api/account/details with JSON body {\"account_id\": 2}"
    )


if __name__ == "__main__":
    app.run(port=5003, debug=True)
