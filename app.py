from flask import Flask, request, Response
from threading import Lock
import os
import requests
import time

app = Flask(__name__)

GROUP_ID = 66492435
REQUIRED_RANK = 254

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable not set!")

global_text = ""
lock = Lock()

last_request_time = {}
RATE_LIMIT_SECONDS = 2

def verify_group_rank(user_id: int) -> bool:
    try:
        url = f"https://groups.roblox.com/v1/users/{user_id}/groups/roles"
        r = requests.get(url, timeout=5)

        if r.status_code != 200:
            return False

        data = r.json()
        for group in data.get("data", []):
            if group["group"]["id"] == GROUP_ID:
                rank = group["role"]["rank"]
                return rank >= REQUIRED_RANK

        return False

    except Exception:
        return False

def validate_request(require_body=False):
    auth = request.headers.get("X-Auth")
    if auth != SECRET_KEY:
        return None, Response("Forbidden", status=403)

    user_id = request.values.get("userId")
    if not user_id:
        return None, Response("Missing userId", status=400)

    try:
        user_id = int(user_id)
    except ValueError:
        return None, Response("Invalid userId", status=400)

    now = time.time()
    last = last_request_time.get(user_id, 0)
    if now - last < RATE_LIMIT_SECONDS:
        return None, Response("Too Many Requests", status=429)
    last_request_time[user_id] = now

    if not verify_group_rank(user_id):
        return None, Response("Unauthorized (Group rank too low)", status=403)

    return user_id, None

@app.route("/", methods=["GET"])
def get_text():
    user_id, error = validate_request()
    if error:
        return error

    global global_text
    with lock:
        if not global_text:
            return Response("", status=204)

        text = global_text
        global_text = ""
        return Response(text, mimetype="text/plain")

@app.route("/set", methods=["POST"])
def set_text():
    user_id, error = validate_request(require_body=True)
    if error:
        return error

    new_text = request.form.get("text")
    if not new_text:
        return Response("No text provided", status=400)

    if new_text.lower().startswith("exec:"):
        return Response("Exec disabled for security", status=403)

    global global_text
    with lock:
        global_text = new_text

    return Response("OK", status=200)

@app.route("/health", methods=["GET"])
def health():
    return "OK", 200

if __name__ == "__main__":
    app.run()
