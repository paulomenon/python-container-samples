import os
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", "/app/uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)


@app.get("/")
def index():
    return jsonify(
        {
            "service": "file-upload-service",
            "endpoints": {
                "POST /upload": "multipart file field 'file'",
                "GET /files": "list files",
                "GET /files/<filename>": "download",
            },
        }
    )


@app.post("/upload")
def upload():
    if "file" not in request.files:
        return jsonify({"error": "Missing file field"}), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify({"error": "Empty filename"}), 400
    name = secure_filename(f.filename)
    if not name:
        return jsonify({"error": "Invalid filename"}), 400
    dest = UPLOAD_DIR / name
    f.save(dest)
    return jsonify({"filename": name, "size": dest.stat().st_size}), 201


@app.get("/files")
def list_files():
    names = sorted(p.name for p in UPLOAD_DIR.iterdir() if p.is_file())
    return jsonify({"files": names})


@app.get("/files/<path:filename>")
def download(filename):
    safe = secure_filename(filename)
    if safe != filename or not safe:
        return jsonify({"error": "Invalid filename"}), 400
    path = UPLOAD_DIR / safe
    if not path.is_file():
        return jsonify({"error": "Not found"}), 404
    return send_from_directory(UPLOAD_DIR, safe, as_attachment=True)
