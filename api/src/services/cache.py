"""redis 缓存 owner；连不上时退化为进程内存（开发/单测可用，行为一致）。"""

import json
import time

from src.config import settings

_mem: dict[str, tuple[float, str]] = {}


def _client():
    try:
        import redis

        c = redis.Redis.from_url(settings.redis_url, socket_connect_timeout=2)
        c.ping()
        return c
    except Exception:
        return None


def get_json(key: str) -> object | None:
    c = _client()
    if c is not None:
        try:
            raw = c.get(key)
            return json.loads(raw) if raw else None
        except Exception:
            return None
    item = _mem.get(key)
    if item is None or item[0] < time.time():
        return None
    return json.loads(item[1])


def set_json(key: str, value: object, ttl_s: int = 300) -> None:
    raw = json.dumps(value)
    c = _client()
    if c is not None:
        try:
            c.set(key, raw, ex=ttl_s)
            return
        except Exception:
            pass
    _mem[key] = (time.time() + ttl_s, raw)


def provider_models_key(tenant_id: str, provider_id: str) -> str:
    return f"models:{tenant_id}:{provider_id}"
