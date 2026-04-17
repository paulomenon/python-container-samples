import hashlib
import sqlite3
from urllib.parse import urlparse

from flask import Flask, g, jsonify, redirect, request

DATABASE = "urls.db"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS urls (
            short_code TEXT PRIMARY KEY,
            original_url TEXT NOT NULL,
            visits INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    db.commit()
    db.close()


def generate_short_code(url: str, salt: int = 0) -> str:
    payload = f"{url}:{salt}".encode()
    return hashlib.sha256(payload).hexdigest()[:6]


def is_valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


app = Flask(__name__)
app.teardown_appcontext(close_db)
init_db()


@app.post("/shorten")
def shorten():
    data = request.get_json(silent=True) or {}
    url = data.get("url", "").strip()
    if not url or not is_valid_url(url):
        return jsonify({"error": "Invalid or missing url"}), 400

    db = get_db()
    salt = 0
    short_code = generate_short_code(url, salt)
    while True:
        row = db.execute(
            "SELECT short_code FROM urls WHERE short_code = ?", (short_code,)
        ).fetchone()
        if not row:
            break
        existing = db.execute(
            "SELECT original_url FROM urls WHERE short_code = ?", (short_code,)
        ).fetchone()
        if existing and existing["original_url"] == url:
            break
        salt += 1
        short_code = generate_short_code(url, salt)

    db.execute(
        """
        INSERT INTO urls (short_code, original_url, visits)
        VALUES (?, ?, 0)
        ON CONFLICT(short_code) DO UPDATE SET original_url = excluded.original_url
        """,
        (short_code, url),
    )
    db.commit()

    base = request.host_url.rstrip("/")
    short_url = f"{base}/{short_code}"
    return jsonify({"short_code": short_code, "short_url": short_url})


@app.get("/stats/<short_code>")
def stats(short_code):
    db = get_db()
    row = db.execute(
        "SELECT visits, original_url FROM urls WHERE short_code = ?", (short_code,)
    ).fetchone()
    if not row:
        return jsonify({"error": "Not found"}), 404
    return jsonify(
        {
            "short_code": short_code,
            "visits": row["visits"],
            "original_url": row["original_url"],
        }
    )


@app.get("/<short_code>")
def resolve(short_code):
    if short_code in ("shorten", "stats") or short_code.startswith("favicon"):
        return jsonify({"error": "Not found"}), 404
    db = get_db()
    row = db.execute(
        "SELECT original_url FROM urls WHERE short_code = ?", (short_code,)
    ).fetchone()
    if not row:
        return jsonify({"error": "Not found"}), 404
    db.execute(
        "UPDATE urls SET visits = visits + 1 WHERE short_code = ?", (short_code,)
    )
    db.commit()
    return redirect(row["original_url"], code=302)


@app.get("/")
def index():
    return jsonify(
        {
            "service": "url-shortener-api",
            "endpoints": {
                "POST /shorten": '{"url": "https://example.com"}',
                "GET /<short_code>": "redirect",
                "GET /stats/<short_code>": "visit count",
            },
        }
    )
