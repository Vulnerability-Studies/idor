from flask import Flask, session, jsonify, redirect

app = Flask(__name__)
app.secret_key = "lab-secret-not-for-prod"

# Pagebound Books Marketplace: independent seller orgs, each with their own orders
USERS = {
    "alice": {"user_id": 1, "org_id": 100},  # Alice sells for org 100
    "bob": {"user_id": 2, "org_id": 200},    # Bob sells for org 200
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


@app.get("/org/<int:org_id>/orders/<int:order_id>")
def get_order(org_id, order_id):
    if "org_id" not in session:
        return redirect("/login/alice")
    order = ORDERS.get((org_id, order_id))
    if not order:
        return "not found", 404
    # VULN: org_id is taken straight from the URL instead of session["org_id"] — the composite
    # key *looks* safe (order_id 1 alone isn't enough) but the org half isn't actually validated
    return jsonify(order)


@app.get("/")
def index():
    return (
        "Pagebound Books Marketplace — composite id demo. "
        "Try /login/alice then /org/100/orders/1 (yours), then /org/200/orders/1 (not yours)"
    )


if __name__ == "__main__":
    app.run(port=5010, debug=True)
