"""Order microservice."""
from flask import Flask, jsonify, request

app = Flask(__name__)

_orders: list[dict] = []
_next_id = 1


@app.get("/orders")
def list_orders():
    return jsonify(_orders)


@app.post("/orders")
def create_order():
    global _next_id
    data = request.get_json(silent=True) or {}
    item = data.get("item", "unknown")
    order = {"id": _next_id, "item": item}
    _next_id += 1
    _orders.append(order)
    return jsonify(order), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
