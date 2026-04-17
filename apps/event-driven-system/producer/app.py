"""Publish events to Redis Pub/Sub channel ``events``."""
import json
import os

import redis
from flask import Flask, jsonify, request

app = Flask(__name__)

REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0")
CHANNEL = "events"


def _client() -> redis.Redis:
    return redis.from_url(REDIS_URL, decode_responses=True)


@app.post("/events")
def publish_event():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "JSON body required"}), 400
    payload = json.dumps(data)
    r = _client()
    n = r.publish(CHANNEL, payload)
    return jsonify({"published": True, "subscribers": n}), 202


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
