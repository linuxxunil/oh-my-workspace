"""统一 config 入口（api 内唯一配置 owner）。"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置；环境变量优先，本地默认连 workspace2 infra 端口。"""

    model_config = SettingsConfigDict(env_prefix="API_", extra="ignore")

    database_url: str = "postgresql+psycopg://app:app@localhost:5433/app"
    redis_url: str = "redis://localhost:6380/0"
    jwt_secret: str = "change-me-in-local-env-only-32bytes-min"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 8
    # 为空则 code 节点本地执行（开发直跑）；S5 起 sandbox 服务后配 http://localhost:18091。
    sandbox_url: str = ""
    # dev 自举建表开关；单测默认关（不碰真实 PG），本地直跑时置 1。
    auto_migrate: bool = False


settings = Settings()
