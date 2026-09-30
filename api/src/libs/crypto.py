"""provider api_key 加解密 owner（REQ-012，libs 保持业务无关，只读 settings）。

Fernet 对称：写一律加密，读双兼容（新密文解密，老明文原样兜底）。
空串直通（无 Key 语义）；`gAAAA` 起始才视为 Fernet 形态，误判不透传。
"""

from cryptography.fernet import Fernet, InvalidToken

from src.config import settings

_FERNET_PREFIX = "gAAAA"


def _fernet() -> Fernet:
    try:
        return Fernet(settings.api_master_key.encode())
    except Exception as e:
        raise ValueError("主密钥无效") from e


def is_encrypted(v: str) -> bool:
    """是否为 Fernet 密文形态（前缀判定，不做解密）。"""
    return isinstance(v, str) and v.startswith(_FERNET_PREFIX)


def encrypt(plaintext: str) -> str:
    """明文转密文；空串直通。"""
    if not plaintext:
        return ""
    return _fernet().encrypt(plaintext.encode()).decode()


def decrypt(stored: str) -> str:
    """密文转明文；空串直通；老明文行原样兜底（非 Fernet 形态）。

    Fernet 形态但解密失败则上抛 InvalidToken（调用方不得透传脏密文）。
    """
    if not stored:
        return ""
    try:
        return _fernet().decrypt(stored.encode()).decode()
    except InvalidToken:
        if is_encrypted(stored):
            raise
        return stored
