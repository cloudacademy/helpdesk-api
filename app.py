import os
from flask import Flask, jsonify

from config import Config
from models import db
from routes import bp as api_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    if not app.config["SQLALCHEMY_DATABASE_URI"]:
        raise RuntimeError(
            "DATABASE_URL is not set. Example: "
            "mysql+pymysql://user:pass@localhost:3306/helpdesk"
        )

    db.init_app(app)
    app.register_blueprint(api_bp)

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)