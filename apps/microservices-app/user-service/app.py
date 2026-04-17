"""User microservice."""
from flask import Flask, jsonify, request

app = Flask(__name__)

_users: list[dict] = []
_next_id = 1


@app.get("/users")
def list_users():
    return jsonify(_users)


@app.post("/users")
def create_user():
    global _next_id
    data = request.get_json(silent=True) or {}
    name = data.get("name", "anonymous")
    user = {"id": _next_id, "name": name}
    _next_id += 1
    _users.append(user)
    return jsonify(user), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
