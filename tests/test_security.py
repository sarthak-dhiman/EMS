from datetime import timedelta
import importlib

import app.core.security as security
from jose import jwt
from passlib.context import CryptContext


def test_password_hash_and_verify():
    # Use a PBKDF2 context for tests to avoid system bcrypt/backends issues
    security.pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

    password = "strong-password-123"
    hashed = security.get_password_hash(password)
    assert hashed != password
    assert security.verify_password(password, hashed)
    assert not security.verify_password("wrong", hashed)


def test_create_and_decode_access_token():
    # Use known secret + algorithm for deterministic decode
    security.SECRET_KEY = "test-secret-key"
    security.ALGORITHM = "HS256"

    token = security.create_access_token({"sub": "alice@example.com"}, expires_delta=timedelta(minutes=5))
    assert isinstance(token, str)

    decoded = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    assert decoded.get("sub") == "alice@example.com"
    assert "exp" in decoded
