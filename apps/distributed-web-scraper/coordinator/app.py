"""Coordinator: enqueue URLs in Redis; expose aggregated scrape results."""
import json
import os
import uuid

import redis
from flask import Flask, jsonify, request

app = Flask(__name__)

REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0")
QUEUE_KEY = "scraper:url_queue"
RESULTS_KEY = "scraper:results"


def _r() -> redis.Redis:
    return redis.from_url(REDIS_URL, decode_responses=True)


@app.post("/jobs")
def add_jobs():
    body = request.get_json(silent=True) or {}
    urls = body.get("urls")
    if urls is None and body.get("url"):
        urls = [body["url"]]
    if not urls or not isinstance(urls, list):
        return jsonify({"error": "Provide 'urls' (list) or 'url' (string)"}), 400
    job_id = str(uuid.uuid4())
    r = _r()
    pipe = r.pipeline()
    queued = 0
    for u in urls:
        if not isinstance(u, str) or not u.strip():
            continue
        pipe.rpush(QUEUE_KEY, json.dumps({"job_id": job_id, "url": u.strip()}))
        queued += 1
    pipe.execute()
    return jsonify({"job_id": job_id, "queued": queued}), 202


@app.get("/jobs")
def list_jobs():
    r = _r()
    raw = r.hgetall(RESULTS_KEY)
    out = []
    for k, v in raw.items():
        try:
            row = json.loads(v)
            row["key"] = k
            out.append(row)
        except json.JSONDecodeError:
            out.append({"key": k, "raw": v})
    return jsonify(out)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
