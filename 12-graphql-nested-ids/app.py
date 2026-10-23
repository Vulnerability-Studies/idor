from flask import Flask, session, jsonify, request, redirect
import graphene

app = Flask(__name__)
app.secret_key = "lab-secret-not-for-prod"

USERS = {"alice": 1, "bob": 2}

ORDERS_BY_USER = {
    1: [{"id": 1, "book": "Dune", "total": 18.99}],
    2: [{"id": 2, "book": "Project Hail Mary", "total": 15.50}],
}

NAMES = {1: "Alice", 2: "Bob"}


class Order(graphene.ObjectType):
    id = graphene.Int()
    book = graphene.String()
    total = graphene.Float()


class User(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()
    orders = graphene.List(Order)

    def resolve_orders(parent, info):
        return ORDERS_BY_USER.get(parent.id, [])


class Query(graphene.ObjectType):
    user = graphene.Field(User, id=graphene.Int(required=True))

    def resolve_user(root, info, id):
        # VULN: resolves any user id requested, nested orders included, no ownership/session check at all
        if id not in NAMES:
            return None
        return User(id=id, name=NAMES[id])


schema = graphene.Schema(query=Query)


@app.get("/login/<username>")
def login(username):
    if username not in USERS:
        return "unknown user", 404
    session["user_id"] = USERS[username]
    return f"logged in as {username} (user_id={USERS[username]})"


@app.post("/graphql")
def graphql_endpoint():
    if "user_id" not in session:
        return redirect("/login/alice")
    body = request.get_json(force=True, silent=True) or {}
    query = body.get("query", "")
    result = schema.execute(query)
    return jsonify({"data": result.data, "errors": [str(e) for e in result.errors] if result.errors else None})


@app.get("/")
def index():
    return (
        "Pagebound Books — GraphQL demo. "
        "Try /login/alice then POST /graphql with JSON body "
        '{"query": "{ user(id: 2) { name orders { id book total } } }"}'
    )


if __name__ == "__main__":
    app.run(port=5012, debug=True)
