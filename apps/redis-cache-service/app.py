import json
import os
import time

from flask import Flask, jsonify, request
from redis import Redis

REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0")
KEY_PREFIX = "cache:data:"
STATS_HITS = "cache:stats:hits"
STATS_MISSES = "cache:stats:misses"

redis_conn = Redis.from_url(REDIS_URL, decode_responses=True)

app = Flask(__name__)


def cache_key(k: str) -> str:
    return f"{KEY_PREFIX}{k}"


def fresh_value(key: str) -> str:
    """Simulate expensive fetch (not stored until caller sets TTL)."""
    return json.dumps(
        {
            "key": key,
            "fetched_at": time.time(),
            "payload": f"generated-for-{key}",
        }
    )


@app.get("/")
def index():
    return jsonify(
        {
            "service": "redis-cache-service",
            "endpoints": {
                "GET /data/<key>": "get cached or fetch fresh",
                "POST /data": '{"key","value","ttl"}',
                "DELETE /data/<key>": "invalidate",
                "GET /cache/stats": "hit/miss counts",
            },
        }
    )


@app.get("/data/<key>")
def get_data(key: str):
    if not key:
        return jsonify({"error": "Invalid key"}), 400
    ck = cache_key(key)
    raw = redis_conn.get(ck)
    if raw is not None:
        redis_conn.incr(STATS_HITS)
        return jsonify({"source": "cache", "key": key, "value": raw})
    redis_conn.incr(STATS_MISSES)
    value = fresh_value(key)
    redis_conn.setex(ck, 60, value)
    return jsonify({"source": "origin", "key": key, "value": value, "ttl_applied": 60})


@app.post("/data")
def set_data():
    data = request.get_json(silent=True) or {}
    key = (data.get("key") or "").strip()
    value = data.get("value")
    ttl = int(data.get("ttl", 60))
    if not key or value is None:
        return jsonify({"error": "key and value are required"}), 400
    if ttl <= 0 or ttl > 86400:
        return jsonify({"error": "ttl must be 1..86400"}), 400
    if not isinstance(value, str):
        value = json.dumps(value)
    redis_conn.setex(cache_key(key), ttl, value)
    return jsonify({"ok": True, "key": key, "ttl": ttl})


@app.delete("/data/<key>")
def delete_data(key: str):
    if not key:
        return jsonify({"error": "Invalid key"}), 400
    deleted = redis_conn.delete(cache_key(key))
    return jsonify({"deleted": bool(deleted)})


@app.get("/cache/stats")
def cache_stats():
    hits = int(redis_conn.get(STATS_HITS) or 0)
    misses = int(redis_conn.get(STATS_MISSES) or 0)
    return jsonify({"hits": hits, "misses": misses, "total": hits + misses})
