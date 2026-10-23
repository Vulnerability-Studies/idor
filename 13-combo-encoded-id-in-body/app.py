import base64
from flask import Flask, session, jsonify, request, redirect

app = Flask(__name__)
app.secret_key = "lab-secret-not-for-prod"

USERS = {"alice": 1, "bob": 2}

ORDERS = {
    1: {"id": 1, "user_id": 1, "book": "Dune", "status": "placed"},
    2: {"id": 2, "user_id": 2, "book": "Project Hail Mary", "status": "placed"},
}


def encode_id(raw_id: int) -> str:
    return base64.urlsafe_b64encode(str(raw_id).encode()).decode()


def decode_id(token: str) -> int:
    return int(base64.urlsafe_b64decode(token.encode()).decode())


@app.get("/login/<username>")
def login(username):
    if username not in USERS:
        return "unknown user", 404
    session["user_id"] = USERS[username]
    return f"logged in as {username} (user_id={USERS[username]})"


@app.get("/my-order-token")
def my_order_token():
    if "user_id" not in session:
        return redirect("/login/alice")
    my_order = next(o for o in ORDERS.values() if o["user_id"] == session["user_id"])
    return jsonify({"order_token": encode_id(my_order["id"])})


@app.post("/api/orders/cancel")
def cancel_order():
    if "user_id" not in session:
        return redirect("/login/alice")
    body = request.get_json(force=True, silent=True) or {}
    token = body.get("order_token", "")
    try:
        order_id = decode_id(token)
    except Exception:
        return "bad token", 400
    order = ORDERS.get(order_id)
    if not order:
        return "not found", 404
    # VULN: combo - id is obscured by encoding and hidden inside a POST body, with no ownership check either way
    order["status"] = "cancelled"
    return jsonify(order)


@app.get("/")
def index():
    return (
        "Pagebound Books - combo demo (encoded id + body field). "
        "Try /login/alice then /my-order-token, decode it, re-encode order id 2, "
        "then POST /api/orders/cancel with JSON body {\"order_token\": \"<token for id 2>\"}"
    )


if __name__ == "__main__":
    app.run(port=5013, debug=True)
