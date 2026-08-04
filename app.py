from flask import Flask, request, redirect, jsonify
import string
import random

app = Flask(__name__)

# In-memory "database" — a plain dict.
# Key = short code, Value = {"url": ..., "clicks": int}
# This disappears every time the process restarts. That's expected for now.
url_store = {}

def generate_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.route("/shorten", methods=["POST"])
def shorten():
    data = request.get_json()
    if not data or "url" not in data:
        return jsonify({"error": "missing 'url' in request body"}), 400

    long_url = data["url"]
    code = generate_code()
    while code in url_store:          # avoid collisions
        code = generate_code()

    url_store[code] = {"url": long_url, "clicks": 0}
    return jsonify({"short_code": code, "url": long_url}), 201

@app.route("/<code>", methods=["GET"])
def redirect_to_url(code):
    entry = url_store.get(code)
    if entry is None:
        return jsonify({"error": "short code not found"}), 404

    entry["clicks"] += 1
    return redirect(entry["url"], code=302)

@app.route("/stats/<code>", methods=["GET"])
def stats(code):
    entry = url_store.get(code)
    if entry is None:
        return jsonify({"error": "short code not found"}), 404

    return jsonify({"url": entry["url"], "clicks": entry["clicks"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)