"""迁移一致性校验（PLAN-011 S4/AC5）：空库 `alembic upgrade head` 与
`Base.metadata.create_all` 的表结构 diff 为空才退出 0。

本地跑（需 infra PG :5433），建两临时库、用后删除：
    PYTHONPATH=api uv run --project api python api/scripts/check_migration_parity.py
"""

import sys

from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url

import src.models  # noqa: F401 -- 注册全部表
from alembic import command
from src.config import settings
from src.db import Base

MIG_DB = "app_parity_mig"
DDL_DB = "app_parity_ddl"
SKIP_TABLES = {"alembic_version"}


def _admin_engine():  # type: ignore[no-untyped-def]
    url = make_url(settings.database_url).set(database="app")
    return create_engine(url, isolation_level="AUTOCOMMIT")


def snapshot(db_name: str) -> dict:  # type: ignore[no-untyped-def]
    url = make_url(settings.database_url).set(database=db_name)
    eng = create_engine(url)
    insp = inspect(eng)
    snap = {"tables": {}, "enums": {}}
    for table in sorted(insp.get_table_names()):
        if table in SKIP_TABLES:
            continue
        snap["tables"][table] = {
            "columns": [
                (c["name"], str(c["type"]), c["nullable"], str(c.get("default")))
                for c in insp.get_columns(table)
            ],
            "pk": tuple(insp.get_pk_constraint(table).get("constrained_columns") or []),
            "fks": sorted(
                (
                    tuple(fk.get("constrained_columns") or []),
                    fk.get("referred_table"),
                    tuple(fk.get("referred_columns") or []),
                )
                for fk in insp.get_foreign_keys(table)
            ),
            "uniques": sorted(
                tuple(sorted(u.get("column_names") or [])) for u in insp.get_unique_constraints(table)
            ),
            "indexes": sorted(
                (ix["name"], tuple(ix.get("column_names") or []), ix.get("unique"))
                for ix in insp.get_indexes(table)
            ),
        }
    with eng.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT t.typname, e.enumlabel FROM pg_enum e "
                "JOIN pg_type t ON t.oid = e.enumtypid ORDER BY 1, 2"
            )
        ).all()
    for typ, label in rows:
        snap["enums"].setdefault(typ, []).append(label)
    eng.dispose()
    return snap


def main() -> int:
    from pathlib import Path

    api_dir = Path(__file__).resolve().parents[1]
    admin = _admin_engine()
    try:
        with admin.connect() as conn:
            for db in (MIG_DB, DDL_DB):
                conn.execute(text(f'DROP DATABASE IF EXISTS "{db}"'))
                conn.execute(text(f'CREATE DATABASE "{db}"'))

        cfg = Config(str(api_dir / "alembic.ini"))
        # env.py 统一从 settings 取 url；此处进程内改写指向临时库（lifespan/CLI 走真实配置，不受影响）。
        settings.database_url = (
            make_url(settings.database_url).set(database=MIG_DB).render_as_string(hide_password=False)
        )
        cfg.set_main_option("sqlalchemy.url", settings.database_url)
        cfg.set_main_option("script_location", str(api_dir / "alembic"))
        command.upgrade(cfg, "head")

        ddl_url = make_url(settings.database_url).set(database=DDL_DB)
        ddl_eng = create_engine(ddl_url)
        with ddl_eng.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
        Base.metadata.create_all(ddl_eng)
        ddl_eng.dispose()

        mig, ddl = snapshot(MIG_DB), snapshot(DDL_DB)
        if mig == ddl:
            print("parity OK: upgrade head == create_all (10 tables, enums, indexes)")
            return 0
        print("parity MISMATCH")
        for key in ("tables", "enums"):
            for name in sorted(set(mig[key]) | set(ddl[key])):
                if mig[key].get(name) != ddl[key].get(name):
                    print(f"--- {key}.{name} ---")
                    print(f"  mig: {mig[key].get(name)}")
                    print(f"  ddl: {ddl[key].get(name)}")
        return 1
    finally:
        with admin.connect() as conn:
            for db in (MIG_DB, DDL_DB):
                conn.execute(text(f'DROP DATABASE IF EXISTS "{db}"'))
        admin.dispose()


if __name__ == "__main__":
    sys.exit(main())
