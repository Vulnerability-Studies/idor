from flask import Flask, session, jsonify, request, redirect

app = Flask(__name__)
app.secret_key = "lab-secret-not-for-prod"

USERS = {
    "alice": {"user_id": 1, "org_id": 100},
    "bob": {"user_id": 2, "org_id": 200},
}

ORDERS = {
    (100, 1): {"org_id": 100, "order_id": 1, "book": "Dune", "total": 18.99},
    (200, 1): {"org_id": 200, "order_id": 1, "book": "Project Hail Mary", "total": 15.50},
}


@app.get("/login/<username>")
def login(username):
    if username not in USERS:
        return "unknown user", 404
    session["org_id"] = USERS[username]["org_id"]
    return f"logged in as {username} (org_id={USERS[username]['org_id']})"


@app.get("/orders/<int:order_id>")
def get_order(order_id):
    if "org_id" not in session:
        return redirect("/login/alice")
    # VULN: combo - session org_id is the default, but an "internal debugging" header that
    # was never meant to be client-reachable in production takes precedence when present
    org_id = request.headers.get("X-Debug-Org-Id", type=int) or session["org_id"]
    order = ORDERS.get((org_id, order_id))
    if not order:
        return "not found", 404
    return jsonify(order)


@app.get("/")
def index():
    return (
        "Pagebound Books - combo demo (composite id + header override). "
        "Try /login/alice then /orders/1 (yours), then again with header X-Debug-Org-Id: 200"
    )


if __name__ == "__main__":
    app.run(port=5014, debug=True)
