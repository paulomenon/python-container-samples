import time
import os
from flask import Flask, jsonify

app = Flask(__name__)
start_time = time.time()


@app.route("/")
def index():
    return jsonify({"service": "Health Check Demo", "endpoints": ["/health", "/ready", "/info"]})


@app.route("/health")
def health():
    """Liveness probe — is the process running?"""
    return jsonify({"status": "healthy"}), 200


@app.route("/ready")
def ready():
    """Readiness probe — is the app ready to serve traffic?"""
    uptime = time.time() - start_time
    # Simulate a warmup period of 5 seconds
    if uptime < 5:
        return jsonify({"status": "not ready", "reason": "warming up", "uptime_seconds": round(uptime, 1)}), 503
    return jsonify({"status": "ready", "uptime_seconds": round(uptime, 1)}), 200


@app.route("/info")
def info():
    return jsonify({
        "service": "health-check-endpoint",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "hostname": os.getenv("HOSTNAME", "unknown"),
        "uptime_seconds": round(time.time() - start_time, 1),
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
