from flask import Flask, request, Response
from threading import Lock
import os

app = Flask(__name__)

# ===============================
# GLOBAL STATE
# ===============================
global_text = ""
lock = Lock()

# ===============================
# ENV VARIABLES
# ===============================
SECRET_KEY = os.environ.get("SECRET_KEY")
ALLOWED_IPS = os.environ.get("ALLOWED_IPS", "")
ALLOWED_IPS = [ip.strip() for ip in ALLOWED_IPS.split(",") if ip.strip()]

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY not set in environment variables!")

# ===============================
# HELPER FUNCTION: CHECK AUTH
# ===============================
def is_authorized(req):
    auth = req.headers.get("X-Auth")

    # Only POST requests require IP check (C# client)
    if req.method == "POST":
        ip = req.remote_addr
        if ip not in ALLOWED_IPS:
            print(f"[Unauthorized POST IP] {ip}")
            return False

    # All requests require correct secret key
    if auth != SECRET_KEY:
        print(f"[Unauthorized key] {req.remote_addr}")
        return False

    return True

# ===============================
# ROUTES
# ===============================
@app.route("/", methods=["GET"])
def get_text():
    if not is_authorized(request):
        return Response("Forbidden", status=403)

    global global_text
    with lock:
        if not global_text:
            return Response("", status=204)
        text = global_text
        global_text = ""  # delete after sending
        return Response(text, mimetype="text/plain")

@app.route("/set", methods=["POST"])
def set_text():
    if not is_authorized(request):
        return "Forbidden", 403

    global global_text
    new_text = request.form.get("text")
    if not new_text:
        return "No text provided", 400

    with lock:
        global_text = new_text

    return "OK", 200

# ===============================
# MAIN ENTRY
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
