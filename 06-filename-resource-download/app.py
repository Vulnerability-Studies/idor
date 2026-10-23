from flask import Flask, session, Response, redirect

app = Flask(__name__)
app.secret_key = "lab-secret-not-for-prod"

USERS = {"alice": 1, "bob": 2}

RECEIPTS = {
    "receipt-1001.txt": {"user_id": 1, "contents": "Receipt #1001 - Dune - $18.99 - Alice"},
    "receipt-1002.txt": {"user_id": 2, "contents": "Receipt #1002 - Project Hail Mary - $15.50 - Bob"},
}


@app.get("/login/<username>")
def login(username):
    if username not in USERS:
        return "unknown user", 404
    session["user_id"] = USERS[username]
    return f"logged in as {username} (user_id={USERS[username]})"


@app.get("/downloads/<filename>")
def download(filename):
    if "user_id" not in session:
        return redirect("/login/alice")
    receipt = RECEIPTS.get(filename)
    if not receipt:
        return "not found", 404
    # VULN: filename alone determines the resource served, with no ownership check
    return Response(receipt["contents"], mimetype="text/plain")


@app.get("/")
def index():
    return (
        "Pagebound Books - receipt download demo. "
        "Try /login/alice then /downloads/receipt-1001.txt, then /downloads/receipt-1002.txt"
    )


if __name__ == "__main__":
    app.run(port=5006, debug=True)
