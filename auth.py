import hashlib
from functools import wraps
from flask import request, jsonify
from models import db, ApiToken

def _sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def require_bearer_token(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        token = auth_header.removeprefix("Bearer ").strip()
        if not token:
            return jsonify({"error": "Missing bearer token"}), 401

        token_hash = _sha256_hex(token)

        token_row = ApiToken.query.filter_by(token_hash=token_hash, is_active=True).first()
        if not token_row:
            return jsonify({"error": "Invalid or inactive token"}), 401

        # If you later want to attach identity/roles, you can set g.user here
        return fn(*args, **kwargs)

    return wrapper