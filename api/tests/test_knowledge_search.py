"""S1 验收：知识检索混合语义（REQ-013 AC1/AC3/AC5）。sqlite 独立库，不碰 conftest/PG。"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db import Base
from src.models import Tenant
from src.services import knowledge_service as ks


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with factory() as s:
        t = Tenant(name="t1")
        s.add(t)
        s.flush()
        yield s, t.id


def _seed(db, tenant_id, title, content):
    return ks.create_document(db, tenant_id=tenant_id, title=title, content=content)


def test_hybrid_ranking_prefers_keyword_overlap(db):
    s, tid = db
    _seed(s, tid, "d1", "苹果 香蕉 橙子 葡萄 " * 40)
    _seed(s, tid, "d2", "退款 政策 七天 无理由 " * 40)
    hits = ks.search(s, tenant_id=tid, query="退款政策", top_k=1)
    assert len(hits) == 1 and "退款" in hits[0]


def test_top_k_truncation_and_empty(db):
    s, tid = db
    assert ks.search(s, tenant_id=tid, query="anything", top_k=3) == []
    for i in range(5):
        _seed(s, tid, f"d{i}", f"内容{i} 关键词 " * 40)
    hits = ks.search(s, tenant_id=tid, query="关键词", top_k=2)
    assert len(hits) == 2


def test_tenant_isolation(db):
    from src.models import Tenant as T

    s, tid = db
    other = T(name="t2")
    s.add(other)
    s.flush()
    _seed(s, other.id, "do", "隔离词 秘密 " * 40)
    _seed(s, tid, "dm", "公开词 普通 " * 40)
    hits = ks.search(s, tenant_id=tid, query="隔离词", top_k=5)
    assert all("隔离词" not in h for h in hits)


def test_sqlite_path_equals_shared_ranking(db):
    s, tid = db
    _seed(s, tid, "d1", "alpha beta gamma " * 40)
    _seed(s, tid, "d2", "delta epsilon zeta " * 40)
    assert s.bind.dialect.name == "sqlite"  # sqlite 永不触 pgvector 算子
    assert ks.search(s, tenant_id=tid, query="alpha", top_k=2) == ks._search_python(
        s, tenant_id=tid, query="alpha", top_k=2
    )
