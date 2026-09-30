"""PG parity（REQ-013 S2）：临时库内对比 _search_pg vs _search_python top_k；用后删库。

重跑：uv run --project api python api/scripts/check_vector_parity.py（需 infra-up 的 PG :5433）
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import sqlalchemy as sa
from sqlalchemy.orm import Session

from src.config import settings
from src.db import Base
from src.models import Tenant
from src.services import knowledge_service as ks

TMP_DB = "app_vector_parity"


def _admin_url(dbname: str) -> str:
    base = settings.database_url.rsplit("/", 1)[0]
    return f"{base}/{dbname}"


def main() -> None:
    from sqlalchemy import create_engine

    admin = create_engine(_admin_url("postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as c:
        c.execute(sa.text("DROP DATABASE IF EXISTS " + TMP_DB))
        c.execute(sa.text(f"CREATE DATABASE {TMP_DB}"))
    eng = None
    try:
        eng = create_engine(_admin_url(TMP_DB))
        with eng.connect() as c:
            c.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector"))
            c.commit()
        Base.metadata.create_all(eng)
        with Session(eng) as db:
            assert eng.dialect.name == "postgresql"
            t1 = Tenant(name="t1")
            t2 = Tenant(name="t2")
            db.add_all([t1, t2])
            db.flush()
            fixtures = [
                ("退款政策", "本店支持七天无理由退款，退款流程详见说明。" * 20),
                ("水果", "苹果 香蕉 橙子 葡萄 西瓜 " * 20),
                ("物流", "下单后三天内发货，支持上门取件。" * 20),
                ("混合", "退款 水果 物流 混合文档关键词。" * 20),
            ]
            for title, content in fixtures:
                ks.create_document(db, tenant_id=t1.id, title=title, content=content)
            ks.create_document(db, tenant_id=t2.id, title="iso", content="隔离租户秘密词。" * 20)
            mismatches = 0
            for q, k in [("退款", 2), ("水果物流", 3), ("关键词", 1), ("不存在的词xyz", 3)]:
                a = ks._search_pg(db, tenant_id=t1.id, query=q, top_k=k)
                b = ks._search_python(db, tenant_id=t1.id, query=q, top_k=k)
                status = "OK " if a == b else "DIFF"
                if a != b:
                    mismatches += 1
                print(f"[{status}] q={q!r} k={k} pg={len(a)} py={len(b)}")
                # 租户隔离：t2 数据永不出现在 t1 结果
                assert all("隔离租户" not in h for h in a)
            # t2 自查可用
            assert ks._search_pg(db, tenant_id=t2.id, query="隔离租户", top_k=2)
            if mismatches:
                raise SystemExit(f"parity FAILED: {mismatches} mismatches")
            print("parity OK: _search_pg == _search_python on fixture set")
    finally:
        if eng is not None:
            eng.dispose()
        admin.dispose()
        with create_engine(_admin_url("postgres"), isolation_level="AUTOCOMMIT").connect() as c:
            c.execute(sa.text("DROP DATABASE IF EXISTS " + TMP_DB))


if __name__ == "__main__":
    main()
