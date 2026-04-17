import os

from flask import Flask, jsonify, request
from redis import Redis
from rq import Queue
from rq.exceptions import NoSuchJobError
from rq.job import Job

from worker import simulate_task

REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0")

redis_conn = Redis.from_url(REDIS_URL)
queue = Queue("default", connection=redis_conn)

app = Flask(__name__)


@app.get("/")
def index():
    return jsonify(
        {
            "service": "task-queue-worker",
            "endpoints": {
                "POST /tasks": '{"seconds": 3}',
                "GET /tasks/<job_id>": "job status",
            },
            "worker_hint": "Run: rq worker default",
        }
    )


@app.post("/tasks")
def submit_task():
    data = request.get_json(silent=True) or {}
    seconds = float(data.get("seconds", 3))
    if seconds < 0 or seconds > 300:
        return jsonify({"error": "seconds must be between 0 and 300"}), 400
    job = queue.enqueue(simulate_task, seconds, job_timeout=max(int(seconds) + 30, 60))
    return jsonify({"job_id": job.id, "status": job.get_status()}), 202


@app.get("/tasks/<job_id>")
def task_status(job_id):
    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except NoSuchJobError:
        return jsonify({"error": "Job not found"}), 404

    payload = {
        "job_id": job.id,
        "status": job.get_status(),
        "result": job.result if job.is_finished else None,
        "exc_info": job.exc_info,
    }
    return jsonify(payload)
