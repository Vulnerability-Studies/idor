from flask import Flask, session, jsonify, Response, redirect

app = Flask(__name__)
app.secret_key = "lab-secret-not-for-prod"

USERS = {"alice": 1, "bob": 2}

ORDERS_BY_UUID = {
    "a1a1a1a1-aaaa-aaaa-aaaa-a1a1a1a1a1a1": {"user_id": 1, "book": "Dune"},
    "b2b2b2b2-bbbb-bbbb-bbbb-b2b2b2b2b2b2": {"user_id": 2, "book": "Project Hail Mary"},
}

INVOICE_FILES = {
    "a1a1a1a1-aaaa-aaaa-aaaa-a1a1a1a1a1a1": "Invoice — Dune — Alice — $18.99",
    "b2b2b2b2-bbbb-bbbb-bbbb-b2b2b2b2b2b2": "Invoice — Project Hail Mary — Bob — $15.50",
}


@app.get("/login/<username>")
def login(username):
    if username not in USERS:
        return "unknown user", 404
    session["user_id"] = USERS[username]
    return f"logged in as {username} (user_id={USERS[username]})"


@app.get("/api/my-recent-orders")
def my_recent_orders():
    if "user_id" not in session:
        return redirect("/login/alice")
    # VULN (leak half of the combo): meant to be "my" orders, but actually returns everyone's UUIDs
    return jsonify({"all_order_uuids": list(ORDERS_BY_UUID.keys())})


@app.get("/invoices/<uuid>.txt")
def invoice_download(uuid):
    if "user_id" not in session:
        return redirect("/login/alice")
    contents = INVOICE_FILES.get(uuid)
    if not contents:
        return "not found", 404
    # VULN (download half of the combo): filename is the whole access control, no ownership check
    return Response(contents, mimetype="text/plain")


@app.get("/")
def index():
    return (
        "Pagebound Books — combo demo (leaked uuid + filename download). "
        "Try /login/alice then /api/my-recent-orders to see every uuid, "
        "then /invoices/<someone else's uuid>.txt"
    )


if __name__ == "__main__":
    app.run(port=5015, debug=True)
