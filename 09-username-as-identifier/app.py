from flask import Flask, session, jsonify, redirect

app = Flask(__name__)
app.secret_key = "lab-secret-not-for-prod"

USERS = {"alice": 1, "bob": 2}

WISHLISTS = {
    "alice": ["Dune", "The Hobbit"],
    "bob": ["Project Hail Mary", "Foundation"],
}


@app.get("/login/<username>")
def login(username):
    if username not in USERS:
        return "unknown user", 404
    session["user"] = username
    return f"logged in as {username}"


@app.get("/users/<username>/wishlist")
def wishlist(username):
    if "user" not in session:
        return redirect("/login/alice")
    items = WISHLISTS.get(username)
    if items is None:
        return "not found", 404
    # VULN: username in the path is used directly as the lookup key, never compared to session["user"]
    return jsonify({"username": username, "wishlist": items})


@app.get("/")
def index():
    return (
        "Pagebound Books — wishlist demo. "
        "Try /login/alice then /users/alice/wishlist, then /users/bob/wishlist"
    )


if __name__ == "__main__":
    app.run(port=5009, debug=True)
