"""知识库最小 RAG（service owner）。
embed 为确定性占位实现（32 维哈希向量）；生产替换为真实 embedding 模型即可，
维度同步改 models.EmbeddingVector。检索=关键词重合为主 + 余弦为辅，保证无语义模型时可用。
"""

import hashlib
import math
import re

from sqlalchemy.orm import Session

from src.models import Chunk, Document

_TOKEN = re.compile(r"[A-Za-z0-9\u4e00-\u9fff]+")


def tokens(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN.findall(text)}


def embed(text: str, dim: int = 32) -> list[float]:
    vec = [0.0] * dim
    for tok in tokens(text):
        h = int(hashlib.sha256(tok.encode()).hexdigest(), 16)
        vec[h % dim] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def split_text(content: str, size: int = 500) -> list[str]:
    return [content[i : i + size] for i in range(0, len(content), size)] or [""]


def create_document(
    db: Session, *, tenant_id: str, title: str, content: str
) -> tuple[Document, int]:
    doc = Document(tenant_id=tenant_id, title=title)
    db.add(doc)
    db.flush()
    chunks = split_text(content)
    for c in chunks:
        db.add(
            Chunk(
                tenant_id=tenant_id,
                document_id=doc.id,
                content=c,
                embedding=embed(c),
            )
        )
    db.commit()
    return doc, len(chunks)


def cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def _ranked(qv: list[float], qt: set[str], rows: list[Chunk], top_k: int) -> list[str]:
    """共享终排：0.7 关键词重合 + 0.3 余弦（两检索路径共用，语义单点）。"""
    scored: list[tuple[float, str]] = []
    for ch in rows:
        kw = len(qt & tokens(ch.content)) / max(len(qt | tokens(ch.content)), 1)
        cos = cosine(qv, ch.embedding or [0.0] * 32)
        scored.append((0.7 * kw + 0.3 * cos, ch.content))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:top_k]]


def _search_python(db: Session, *, tenant_id: str, query: str, top_k: int) -> list[str]:
    """非 PG 路径（sqlite 单测）：全量 load 后 Python 重排（REQ-013 前行为原样下沉）。"""
    qv = embed(query)
    qt = tokens(query)
    rows = db.query(Chunk).filter(Chunk.tenant_id == tenant_id).all()
    return _ranked(qv, qt, rows, top_k)


def _search_pg(db: Session, *, tenant_id: str, query: str, top_k: int) -> list[str]:
    """PG 路径：向量排序下推（`ORDER BY embedding <=> :qv LIMIT candidate`）后 Python 重排。

    候选集 `max(top_k*10, 50)` 覆盖常规数据全量重排的 top_k；终排与 `_search_python` 同一 `_ranked`。
    """
    qv = embed(query)
    qt = tokens(query)
    candidate = max(top_k * 10, 50)
    rows = (
        db.query(Chunk)
        .filter(Chunk.tenant_id == tenant_id)
        .order_by(Chunk.embedding.op("<=>")(qv))
        .limit(candidate)
        .all()
    )
    return _ranked(qv, qt, rows, top_k)


def search(db: Session, *, tenant_id: str, query: str, top_k: int = 3) -> list[str]:
    """知识检索入口：按方言分发（PG 下推向量排序，sqlite 全量；混合公式两边一致）。"""
    bind = db.bind
    if bind is not None and bind.dialect.name == "postgresql":
        return _search_pg(db, tenant_id=tenant_id, query=query, top_k=top_k)
    return _search_python(db, tenant_id=tenant_id, query=query, top_k=top_k)
