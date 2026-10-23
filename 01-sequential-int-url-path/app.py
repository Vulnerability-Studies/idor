from flask import Flask, session, jsonify, redirect

app = Flask(__name__)
app.secret_key = "lab-secret-not-for-prod"

USERS = {"alice": 1, "bob": 2}

ORDERS = {
    1: {"id": 1, "user_id": 1, "book": "Dune", "total": 18.99},
    2: {"id": 2, "user_id": 2, "book": "Project Hail Mary", "total": 15.50},
    3: {"id": 3, "user_id": 1, "book": "The Hobbit", "total": 9.99},
}


@app.get("/login/<username>")
def login(username):
    if username not in USERS:
        return "unknown user", 404
    session["user_id"] = USERS[username]
    return f"logged in as {username} (user_id={USERS[username]})"


@app.get("/orders/<int:order_id>")
def get_order(order_id):
    if "user_id" not in session:
        return redirect("/login/alice")
    order = ORDERS.get(order_id)
    if not order:
        return "not found", 404
    # VULN: never checks order["user_id"] == session["user_id"]
    return jsonify(order)


@app.get("/")
def index():
    return "Pagebound Books — order lookup demo. Try /login/alice then /orders/1"


if __name__ == "__main__":
    app.run(port=5001, debug=True)
