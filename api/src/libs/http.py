"""出站 HTTP 统一 owner（SSRF-safe 通道占位，S3/S5 落实解析与拦截）。"""

from urllib.parse import urlparse


def assert_safe_url(url: str) -> None:
    """仅允许 http/https 且禁止内网/元数据地址直连（S3 补全 IP 展开检查）。"""
    parts = urlparse(url)
    if parts.scheme not in ("http", "https"):
        raise ValueError("仅允许 http/https")
    host = (parts.hostname or "").lower()
    if host in ("localhost", "127.0.0.1", "::1", "169.254.169.254") or host.endswith(".internal"):
        raise ValueError("禁止内网地址")
