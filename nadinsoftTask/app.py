from flask import Flask, jsonify
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import time

app = Flask(__name__)
REQUESTS = Counter("app_requests_total", "Total HTTP requests", ["endpoint"])

@app.route("/")
def home():
    REQUESTS.labels(endpoint="/").inc()
    return "Hello from Dockerized Flask App with Metrics!"

@app.route("/healthz")
def healthz():
    REQUESTS.labels(endpoint="/healthz").inc()
    return jsonify(status="ok", ts=time.time())

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
