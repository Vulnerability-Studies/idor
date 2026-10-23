from flask import Flask, session, jsonify, redirect

app = Flask(__name__)
app.secret_key = "lab-secret-not-for-prod"

USERS = {"alice": 1, "bob": 2}

ORDERS_BY_UUID = {
    "a1a1a1a1-aaaa-aaaa-aaaa-a1a1a1a1a1a1": {"user_id": 1, "book": "Dune", "total": 18.99},
    "b2b2b2b2-bbbb-bbbb-bbbb-b2b2b2b2b2b2": {"user_id": 2, "book": "Project Hail Mary", "total": 15.50},
}

# Simulates a "site activity" widget that shows recent order UUIDs platform-wide, unauthenticated
RECENT_ACTIVITY_FEED = list(ORDERS_BY_UUID.keys())


@app.get("/login/<username>")
def login(username):
    if username not in USERS:
        return "unknown user", 404
    session["user_id"] = USERS[username]
    return f"logged in as {username} (user_id={USERS[username]})"


@app.get("/api/public/recent-activity")
def recent_activity():
    # leaks every order's "unguessable" UUID to anyone, logged in or not
    return jsonify({"recent_order_uuids": RECENT_ACTIVITY_FEED})


@app.get("/orders/by-uuid/<uuid>")
def order_by_uuid(uuid):
    if "user_id" not in session:
        return redirect("/login/alice")
    order = ORDERS_BY_UUID.get(uuid)
    if not order:
        return "not found", 404
    # VULN: UUID is unguessable on its own, but it leaked via recent-activity AND ownership is never checked here
    return jsonify(order)


@app.get("/")
def index():
    return (
        "Pagebound Books — order-by-uuid demo. "
        "Try GET /api/public/recent-activity to find UUIDs, then /login/alice then /orders/by-uuid/<uuid>"
    )


if __name__ == "__main__":
    app.run(port=5007, debug=True)
