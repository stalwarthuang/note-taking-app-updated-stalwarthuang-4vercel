import os
import sys
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.note import note_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), "static"))
app.config["SECRET_KEY"] = "asdf#FGSgvasgf$5$WGT"

# Enable CORS for all routes
CORS(app)

# register blueprints
app.register_blueprint(user_bp, url_prefix="/api")
app.register_blueprint(note_bp, url_prefix="/api")

# Database configuration - support both PostgreSQL (production) and SQLite (development)
DATABASE_URL = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")

if DATABASE_URL:
    # Using PostgreSQL (for Vercel deployment)
    # Vercel Postgres URLs might use 'postgres://' but SQLAlchemy requires 'postgresql://'
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    # Clean up URL parameters that psycopg2 doesn't support
    parsed = urlparse(DATABASE_URL)
    if parsed.query:
        # Parse query parameters
        params = parse_qs(parsed.query)
        # Keep only standard PostgreSQL parameters
        allowed_params = {"sslmode", "connect_timeout", "application_name", "options"}
        cleaned_params = {k: v for k, v in params.items() if k in allowed_params}
        # Reconstruct URL with cleaned parameters
        query_string = urlencode(cleaned_params, doseq=True) if cleaned_params else ""
        DATABASE_URL = urlunparse(
            (
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                query_string,
                parsed.fragment,
            )
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
else:
    # Fallback to SQLite for local development
    ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    DB_PATH = os.path.join(ROOT_DIR, "database", "app.db")
    # ensure database directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
with app.app_context():
    db.create_all()


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, "index.html")
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, "index.html")
        else:
            return "index.html not found", 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
