import os
from flask import Flask, jsonify

app = Flask(__name__)

config = {
    "APP_NAME": os.getenv("APP_NAME", "env-config-app"),
    "APP_ENV": os.getenv("APP_ENV", "development"),
    "APP_DEBUG": os.getenv("APP_DEBUG", "false").lower() == "true",
    "APP_PORT": int(os.getenv("APP_PORT", "5000")),
    "DB_HOST": os.getenv("DB_HOST", "localhost"),
    "DB_PORT": int(os.getenv("DB_PORT", "5432")),
    "DB_NAME": os.getenv("DB_NAME", "mydb"),
    "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
    "SECRET_KEY": os.getenv("SECRET_KEY", "change-me-in-production"),
}


@app.route("/")
def index():
    return jsonify({"service": config["APP_NAME"], "environment": config["APP_ENV"]})


@app.route("/config")
def show_config():
    """Show all configuration (redact sensitive values)."""
    safe = {k: v for k, v in config.items()}
    safe["SECRET_KEY"] = "***REDACTED***"
    return jsonify(safe)


@app.route("/env")
def show_env():
    """Show all environment variables (for debugging — disable in production)."""
    if not config["APP_DEBUG"]:
        return jsonify({"error": "Debug mode is off. Set APP_DEBUG=true to view env vars."}), 403
    return jsonify(dict(os.environ))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config["APP_PORT"], debug=config["APP_DEBUG"])
