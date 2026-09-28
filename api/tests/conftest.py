"""pytest 隔离：sqlite 内存库 + seed 三角色；每个测试函数重建。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db import Base, get_db
from src.main import app
from src.services.seed import seed

CREDS = {
    "super_admin": ("root@example.com", "Root12345"),
    "admin": ("admin@example.com", "Admin12345"),
    "member": ("member@example.com", "Member12345"),
}


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    # 与 postgres 语义对齐：强制外键，否则删主留子只在测试里静默通过。
    event.listen(engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with factory() as db:
        seed(db)

    def _override():
        db = factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override
    # deps.current_user 内部直接 Depends(get_db)，override 生效，无需再 patch。
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def login(client: TestClient, role: str) -> str:
    email, password = CREDS[role]
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
