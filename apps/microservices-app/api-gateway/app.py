"""API gateway: proxies /users and /orders to downstream services."""
import os

import requests
from flask import Flask, Response, request

app = Flask(__name__)

USER_SERVICE = os.environ.get("SERVICE_USER_URL", "http://127.0.0.1:5001").rstrip("/")
ORDER_SERVICE = os.environ.get("SERVICE_ORDER_URL", "http://127.0.0.1:5002").rstrip("/")


def _proxy(base: str, path: str) -> Response:
    url = f"{base}{path}"
    if request.query_string:
        url = f"{url}?{request.query_string.decode()}"
    resp = requests.request(
        method=request.method,
        url=url,
        headers={k: v for k, v in request.headers if k.lower() != "host"},
        data=request.get_data(),
        cookies=request.cookies,
        timeout=30,
    )
    excluded = {"content-encoding", "content-length", "transfer-encoding", "connection"}
    headers = [(k, v) for k, v in resp.raw.headers.items() if k.lower() not in excluded]
    return Response(resp.content, resp.status_code, headers)


@app.route("/users", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@app.route("/users/<path:sub>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
def users_proxy(sub: str | None = None):
    path = "/users" if sub is None else f"/users/{sub}"
    return _proxy(USER_SERVICE, path)


@app.route("/orders", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@app.route("/orders/<path:sub>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
def orders_proxy(sub: str | None = None):
    path = "/orders" if sub is None else f"/orders/{sub}"
    return _proxy(ORDER_SERVICE, path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
