from flask import Flask, session, request, redirect

app = Flask(__name__)
app.secret_key = "lab-secret-not-for-prod"

USERS = {"alice": 1, "bob": 2}

REVIEWS = {
    1: {"review_id": 1, "user_id": 1, "book": "Dune", "text": "Loved it."},
    2: {"review_id": 2, "user_id": 2, "book": "Project Hail Mary", "text": "Great twist."},
}


@app.get("/login/<username>")
def login(username):
    if username not in USERS:
        return "unknown user", 404
    session["user_id"] = USERS[username]
    return f"logged in as {username} (user_id={USERS[username]})"


@app.get("/reviews/edit-form/<int:review_id>")
def edit_form(review_id):
    if "user_id" not in session:
        return redirect("/login/alice")
    review = REVIEWS.get(review_id)
    if not review:
        return "not found", 404
    return f"""
    <form method="POST" action="/reviews/edit">
        <input type="hidden" name="review_id" value="{review_id}">
        <textarea name="text">{review['text']}</textarea>
        <button type="submit">Save</button>
    </form>
    """


@app.post("/reviews/edit")
def edit_review():
    if "user_id" not in session:
        return redirect("/login/alice")
    review_id = request.form.get("review_id", type=int)
    new_text = request.form.get("text", "")
    review = REVIEWS.get(review_id)
    if not review:
        return "not found", 404
    # VULN: review_id comes from a hidden field the client fully controls, ownership never checked
    review["text"] = new_text
    return f"saved: {review}"


@app.get("/")
def index():
    return (
        "Pagebound Books — review edit demo. "
        "Try /login/alice then /reviews/edit-form/1, then resubmit with a different hidden review_id"
    )


if __name__ == "__main__":
    app.run(port=5005, debug=True)
