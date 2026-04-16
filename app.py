import os
from flask import Flask, jsonify

from config import Config
from models import db
from routes import bp as api_bp

from flasgger import Swagger

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


app = create_app()

swagger_config = {
    "swagger": "2.0",
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,  # include all routes
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Helpdesk Ticketing API",
        "description": "CRUD Helpdesk Ticketing API with Bearer-token authentication",
        "version": "1.0.0",
    },
    "basePath": "/",
    "schemes": ["http"],
    "securityDefinitions": {
        "BearerAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Authorization: Bearer <token>",
        }
    },
    "definitions": {
        "ErrorResponse": {
            "type": "object",
            "properties": {
                "error": {"type": "string"},
                "errors": {
                    "type": "array",
                    "items": {"type": "string"}
                },
            },
        },
        "Ticket": {
            "type": "object",
            "required": [
                "id",
                "title",
                "status",
                "priority",
                "created_at",
                "updated_at",
            ],
            "properties": {
                "id": {"type": "integer", "example": 1},
                "title": {"type": "string", "example": "VPN not connecting"},
                "description": {"type": "string"},
                "status": {
                    "type": "string",
                    "enum": ["open", "in_progress", "resolved", "closed"],
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "urgent"],
                },
                "requester_email": {"type": "string"},
                "assigned_to": {"type": "string"},
                "created_at": {"type": "string", "format": "date-time"},
                "updated_at": {"type": "string", "format": "date-time"},
            },
        },
        "TicketCreateRequest": {
            "type": "object",
            "required": ["title"],
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "status": {
                    "type": "string",
                    "enum": ["open", "in_progress", "resolved", "closed"],
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "urgent"],
                },
                "requester_email": {"type": "string"},
                "assigned_to": {"type": "string"},
            },
        },
        "TicketReplaceRequest": {
            "type": "object",
            "required": ["title"],
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "status": {
                    "type": "string",
                    "enum": ["open", "in_progress", "resolved", "closed"],
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "urgent"],
                },
                "requester_email": {"type": "string"},
                "assigned_to": {"type": "string"},
            },
        },
        "TicketPatchRequest": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "status": {
                    "type": "string",
                    "enum": ["open", "in_progress", "resolved", "closed"],
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "urgent"],
                },
                "requester_email": {"type": "string"},
                "assigned_to": {"type": "string"},
            },
            "additionalProperties": False,
        },
    },
}

Swagger(app, config=swagger_config, template=swagger_template)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)