import json
import logging
import random
import sys
import time
from datetime import datetime, timezone

from flask import Flask, Response, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("http")

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "path"],
)

app = Flask(__name__)


def log_request_json(method, path, status, duration_ms):
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "method": method,
        "path": path,
        "status": status,
        "duration_ms": round(duration_ms, 3),
    }
    log.info(json.dumps(record))


@app.before_request
def start_timer():
    request._t0 = time.perf_counter()


@app.after_request
def after_request(response):
    t0 = getattr(request, "_t0", None)
    duration_ms = (time.perf_counter() - t0) * 1000 if t0 is not None else 0.0
    path = request.path
    log_request_json(request.method, path, response.status_code, duration_ms)
    if path != "/metrics":
        REQUEST_COUNT.labels(request.method, path, str(response.status_code)).inc()
        REQUEST_LATENCY.labels(request.method, path).observe(duration_ms / 1000.0)
    return response


@app.get("/")
def root():
    return {"service": "logging-monitoring-app", "ok": True}


@app.get("/compute")
def compute():
    # Simulate variable work
    n = random.randint(50_000, 200_000)
    _ = sum(i * i for i in range(n))
    return {"result": n, "checksum": _ % 10000}


@app.get("/metrics")
def metrics():
    data = generate_latest()
    return Response(data, mimetype=CONTENT_TYPE_LATEST)
