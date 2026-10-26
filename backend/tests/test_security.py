import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import jwt
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials


@pytest.fixture
def security(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://test:test@127.0.0.1/test")
    monkeypatch.setenv("JWT_SECRET", "test-only-secret-0123456789abcdef0123456789abcdef")
    from app import security

    monkeypatch.setattr(security.settings, "jwt_secret", "test-only-secret-0123456789abcdef0123456789abcdef")
    return security


def credentials(token):
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


@pytest.mark.parametrize("claim", ["exp", "iat", "sub"])
def test_rejects_incomplete_access_token(security, claim):
    now = datetime.now(timezone.utc)
    payload = {"sub": str(uuid4()), "iat": now, "exp": now + timedelta(minutes=5)}
    del payload[claim]
    token = jwt.encode(payload, security.settings.jwt_secret, algorithm="HS256")
    session = AsyncMock()
    with pytest.raises(HTTPException) as error:
        asyncio.run(security.current_user(credentials(token), session))
    assert error.value.status_code == 401
    session.scalar.assert_not_awaited()


def test_accepts_server_issued_access_token(security):
    from app.db import User

    user = User(id=uuid4(), email="audit@example.com", password_hash="unused")
    session = AsyncMock()
    session.scalar.return_value = user
    token = security.create_access_token(user.id)
    assert asyncio.run(security.current_user(credentials(token), session)) is user
    session.scalar.assert_awaited_once()


@pytest.mark.parametrize("invalid", ["expired", "signature"])
def test_rejects_invalid_access_token(security, invalid):
    now = datetime.now(timezone.utc)
    payload = {"sub": str(uuid4()), "iat": now - timedelta(minutes=2), "exp": now + timedelta(minutes=5)}
    if invalid == "expired":
        payload["exp"] = now - timedelta(minutes=1)
    key = "other-test-secret-0123456789abcdef0123456789abcdef" if invalid == "signature" else security.settings.jwt_secret
    token = jwt.encode(payload, key, algorithm="HS256")
    session = AsyncMock()
    with pytest.raises(HTTPException) as error:
        asyncio.run(security.current_user(credentials(token), session))
    assert error.value.status_code == 401
    session.scalar.assert_not_awaited()
