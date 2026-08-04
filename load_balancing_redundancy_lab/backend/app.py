from flask import Flask, jsonify
import platform
import os

app = Flask(__name__)

count = 0
is_healthy = True

port = int(os.environ.get("PORT", 5000))
host = os.environ.get("HOST", "127.0.0.1")


@app.route("/", methods=["GET"])
def greeting():
    global count

    count += 1

    return jsonify(
        hostname=platform.node(),
        count=count,
    ), 200


@app.route("/health", methods=["GET"])
def check_health():
    if is_healthy:
        return jsonify(status="healthy"), 200

    return jsonify(status="unhealthy"), 503


@app.route("/kill", methods=["GET"])
def make_it_unhealthy():
    global is_healthy

    is_healthy = False

    return jsonify(
        message="Server marked as unhealthy",
        status="unhealthy",
    ), 200


@app.route("/recover", methods=["GET"])
def make_it_healthy():
    global is_healthy

    is_healthy = True

    return jsonify(
        message="Server marked as healthy",
        status="healthy",
    ), 200


if __name__ == "__main__":
    app.run(host=host, port=port)
