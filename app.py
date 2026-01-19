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
	# AUTH SECRET
# ===============================
	# BEST PRACTICE:
	# Put SECRET_KEY in Render Environment Variables
#
# FALLBACK (ONLY FOR TESTING):
	# If no env var exists, this string will be used.
	#
# ⚠️ CHANGE THIS STRING TO YOUR OWN RANDOM KEY
# ===============================
	SECRET_KEY = os.environ.get(
		"SECRET_KEY",
		"WINFX_91fA3cX9KQ72mP"
	)

# ===============================
	# ROUTES
# ===============================
	@app.route("/", methods=["GET"])
def get_text():
	auth = request.headers.get("X-Auth")
if auth != SECRET_KEY:
	return Response("Forbidden", status=403)

	global global_text
	with lock:
		if not global_text:
			return Response("", status=204)

			text = global_text
			global_text = ""  # delete after send
			return Response(text, mimetype="text/plain")


			@app.route("/set", methods=["POST"])
			def set_text():
			auth = request.headers.get("X-Auth")
			if auth != SECRET_KEY:
				return "Forbidden", 403

				global global_text
				new_text = request.form.get("text")
				if not new_text:
					return "No text provided", 400

					with lock:
					global_text = new_text

					return "OK", 200
