"""密码哈希 + JWT（auth 领域，core owner）。"""

from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from src.config import settings

_password_hash = PasswordHash.recommended()


def hash_password(raw: str) -> str:
    """明文转哈希；每个分支语义：仅接受非空串（上层已校验长度）。"""
    return _password_hash.hash(raw)


def verify_password(raw: str, hashed: str) -> bool:
    return _password_hash.verify(raw, hashed)


def create_token(*, user_id: str, tenant_id: str, role: str) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": user_id,
        "tenant_id": tenant_id,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
