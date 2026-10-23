from flask import Flask, session, jsonify, request, redirect

app = Flask(__name__)
app.secret_key = "lab-secret-not-for-prod"

USERS = {"alice": 1, "bob": 2}

INVOICES = {
    101: {"invoice_id": 101, "user_id": 1, "book": "Dune", "amount": 18.99},
    102: {"invoice_id": 102, "user_id": 2, "book": "Project Hail Mary", "amount": 15.50},
}


@app.get("/login/<username>")
def login(username):
    if username not in USERS:
        return "unknown user", 404
    session["user_id"] = USERS[username]
    return f"logged in as {username} (user_id={USERS[username]})"


@app.get("/invoice")
def get_invoice():
    if "user_id" not in session:
        return redirect("/login/alice")
    invoice_id = request.args.get("invoice_id", type=int)
    invoice = INVOICES.get(invoice_id)
    if not invoice:
        return "not found", 404
    # VULN: id comes from query string, no ownership check
    return jsonify(invoice)


@app.get("/")
def index():
    return "Pagebound Books - invoice lookup demo. Try /login/alice then /invoice?invoice_id=101"


if __name__ == "__main__":
    app.run(port=5002, debug=True)
