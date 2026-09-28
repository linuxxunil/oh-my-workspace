"""FastAPI 装配（controller 只挂载，逻辑在 service/core）。"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.controllers import auth, models, permissions, system_features, users, workflows


@asynccontextmanager
async def lifespan(_app: FastAPI):  # type: ignore[no-untyped-def]
    """dev 自举建表+种子（含 pgvector 扩展，需 API_AUTO_MIGRATE=1）；发布迁移走 alembic（后续）。
    种子幂等：users 表已有数据则跳过。"""
    from src.config import settings

    if settings.auto_migrate:
        from sqlalchemy import text

        import src.models  # noqa: F401 -- 注册全部表
        from src.db import Base, engine
        from src.models import User
        from src.services.seed import seed

        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
        Base.metadata.create_all(engine)
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
