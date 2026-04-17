from flask import Flask, jsonify, request

app = Flask(__name__)

items = [
    {"id": 1, "name": "Laptop", "price": 999.99},
    {"id": 2, "name": "Mouse", "price": 29.99},
    {"id": 3, "name": "Keyboard", "price": 59.99},
]


@app.route("/")
def index():
    return jsonify({"message": "Flask Web API", "endpoints": ["/items", "/items/<id>"]})


@app.route("/items", methods=["GET"])
def get_items():
    return jsonify(items)


@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = next((i for i in items if i["id"] == item_id), None)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item)


@app.route("/items", methods=["POST"])
def create_item():
    data = request.get_json()
    new_item = {
        "id": max(i["id"] for i in items) + 1 if items else 1,
        "name": data.get("name", "Unnamed"),
        "price": data.get("price", 0.0),
    }
    items.append(new_item)
    return jsonify(new_item), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
