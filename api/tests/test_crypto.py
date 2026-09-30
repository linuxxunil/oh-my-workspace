"""S1 验收：crypto owner（REQ-012 AC1/AC2）。纯函数，不碰 DB/网络。"""

import pytest
from cryptography.fernet import Fernet

from src.libs import crypto


def test_roundtrip_and_empty_passthrough():
    assert crypto.encrypt("") == ""
    assert crypto.decrypt("") == ""
    assert crypto.decrypt(crypto.encrypt("sk-live-123")) == "sk-live-123"


def test_is_encrypted_prefix():
    assert crypto.is_encrypted(crypto.encrypt("x")) is True
    assert crypto.is_encrypted("plain-old-key") is False
    assert crypto.is_encrypted("") is False


def test_legacy_plaintext_fallback():
    assert crypto.decrypt("old-plain-key") == "old-plain-key"


def test_fernet_shape_but_wrong_key_raises(monkeypatch):
    from cryptography.fernet import InvalidToken

    token = crypto.encrypt("k")
    monkeypatch.setattr("src.libs.crypto.settings.api_master_key", Fernet.generate_key().decode())
    with pytest.raises(InvalidToken):
        crypto.decrypt(token)


def test_invalid_master_key_raises_value_error(monkeypatch):
    monkeypatch.setattr("src.libs.crypto.settings.api_master_key", "not-a-key")
    with pytest.raises(ValueError, match="主密钥无效"):
        crypto.encrypt("k")
