"""Small Task API used to demonstrate deployment, metrics, logs and alerts."""
import logging
import time

from flask import Flask, Response, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("task-api")

REQUESTS = Counter("app_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
LATENCY = Histogram("app_request_latency_seconds", "Request latency in seconds", ["endpoint"])
TASKS = []


@app.before_request
def _start_timer():
    request.environ["start_time"] = time.time()


@app.after_request
def _record_metrics(response):
    endpoint = request.url_rule.rule if request.url_rule else "unmatched"
    if endpoint != "/metrics":
        elapsed = time.time() - request.environ.get("start_time", time.time())
        REQUESTS.labels(request.method, endpoint, str(response.status_code)).inc()
        LATENCY.labels(endpoint).observe(elapsed)
        log.info("%s %s -> %s (%.1f ms)", request.method, request.path, response.status_code, elapsed * 1000)
    return response


@app.get("/")
def index():
    return jsonify(service="task-api", status="running")


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/tasks")
def list_tasks():
    return jsonify(TASKS)


@app.post("/tasks")
def create_task():
    data = request.get_json(silent=True) or {}
    title = data.get("title", "").strip()
    if not title:
        return jsonify(error="title is required"), 400
    task = {"id": len(TASKS) + 1, "title": title}
    TASKS.append(task)
    return jsonify(task), 201


@app.get("/boom")
def boom():
    """Deliberate error endpoint to demonstrate the high-error-rate alert and error logs."""
    log.error("Deliberate failure triggered on /boom")
    return jsonify(error="deliberate failure"), 500


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
