"""DB owner：engine/session/建表。写事务保持显式有界。"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    """FastAPI dependency：每请求一 session，结束关闭。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
