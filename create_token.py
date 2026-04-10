import os
import secrets
import hashlib
from dotenv import load_dotenv

from app import create_app
from models import db, ApiToken

load_dotenv()

def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def main():
    label = os.getenv("TOKEN_LABEL", "default")
    token = secrets.token_urlsafe(32)  # plaintext bearer token
    token_hash = sha256_hex(token)

    app = create_app()
    with app.app_context():
        row = ApiToken(token_hash=token_hash, label=label, is_active=True)
        db.session.add(row)
        db.session.commit()

    print("Bearer token (store this securely; it won't be shown again):")
    print(token)
    print("\nUse it like: Authorization: Bearer <token>")

if __name__ == "__main__":
    main()