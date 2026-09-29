"""FastAPI 装配（controller 只挂载，逻辑在 service/core）。"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.controllers import auth, models, permissions, system_features, users, workflows


@asynccontextmanager
async def lifespan(_app: FastAPI):  # type: ignore[no-untyped-def]
    """dev 自举迁移+种子（需 API_AUTO_MIGRATE=1）：alembic upgrade head 管 schema
    （含 pgvector 扩展，见 api/alembic/versions/0001_baseline.py），seed 幂等；
    发布启动前同样先 upgrade head（见 docs/release.md）。
    种子幂等：users 表已有数据则跳过。"""
    from src.config import settings

    if settings.auto_migrate:
        from pathlib import Path

        from alembic.config import Config

        import src.models  # noqa: F401 -- 注册全部表
        from alembic import command
        from src.db import engine
        from src.models import User
        from src.services.seed import seed

        api_dir = Path(__file__).resolve().parents[1]
        cfg = Config(str(api_dir / "alembic.ini"))
        cfg.set_main_option("sqlalchemy.url", settings.database_url)
        cfg.set_main_option("script_location", str(api_dir / "alembic"))
        command.upgrade(cfg, "head")
        from sqlalchemy.orm import Session

        with Session(engine) as db:
            if db.query(User).count() == 0:
                seed(db)
    yield


app = FastAPI(title="workspace2-api", version="0.1.0", lifespan=lifespan)
app.include_router(system_features.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(permissions.router)
app.include_router(models.router)
app.include_router(workflows.router)


@app.get("/health")
def health():
    return {"ok": True}
