"""Run the KalaSetu Flask application from the project root."""

from backend.app import app
from backend.config import Config


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=Config.DEBUG,
        use_reloader=False,
    )
