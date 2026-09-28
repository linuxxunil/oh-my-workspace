"""领域表：单租户（tenant_id 谓词），三角色，功能权限码。"""

import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, DateTime, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import TypeDecorator

from src.db import Base


def _uid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(UTC)


EMBED_DIM = 32


class Role(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MEMBER = "member"


class Tenant(Base):
    __tablename__ = "tenants"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uid)
    name: Mapped[str] = mapped_column(String(128), default="default")


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    email: Mapped[str] = mapped_column(String(320), index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.MEMBER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),)


class Permission(Base):
    """功能权限码（permission 管理 API 的读写对象）。"""

    __tablename__ = "permissions"
    code: Mapped[str] = mapped_column(String(64), primary_key=True)
    description: Mapped[str] = mapped_column(String(255), default="")


class RolePermission(Base):
    __tablename__ = "role_permissions"
    role: Mapped[Role] = mapped_column(Enum(Role), primary_key=True)
    permission_code: Mapped[str] = mapped_column(ForeignKey("permissions.code"), primary_key=True)


class ProviderType(str, enum.Enum):
    OPENAI_COMPATIBLE = "openai_compatible"
    OPENCODE_GO = "opencode_go"


class ModelProvider(Base):
    """模型供应商；api_key 永不经 API 返回（加密存 KMS 为二期，见 PLAN-001 R1）。"""

    __tablename__ = "model_providers"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    type: Mapped[ProviderType] = mapped_column(Enum(ProviderType))
    name: Mapped[str] = mapped_column(String(128))
    base_url: Mapped[str] = mapped_column(String(512))
    api_key: Mapped[str] = mapped_column(String(1024), default="")
    extra_headers: Mapped[dict] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    __table_args__ = (UniqueConstraint("tenant_id", "name", name="uq_providers_tenant_name"),)


class EmbeddingVector(TypeDecorator):
    """pgvector 同库：postgres 用原生 Vector(32)，其他方言退 JSON（单测 sqlite 可用）。

    生产 embedding 模型在此处替换 embed 实现即可，维度同步改 Vector(n)。
    """

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):  # type: ignore[no-untyped-def]
        if dialect.name == "postgresql":
            from pgvector.sqlalchemy import Vector

            return dialect.type_descriptor(Vector(32))
        return dialect.type_descriptor(JSON())

    def process_bind_param(self, value, dialect):  # type: ignore[no-untyped-def]
        return list(value) if value is not None else None

    def process_result_value(self, value, dialect):  # type: ignore[no-untyped-def]
        return list(value) if value is not None else None


class Workflow(Base):
    __tablename__ = "workflows"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    name: Mapped[str] = mapped_column(String(128))
    description: Mapped[str] = mapped_column(String(512), default="")
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    __table_args__ = (UniqueConstraint("tenant_id", "name", name="uq_wf_tenant_name"),)


class WorkflowVersion(Base):
    """发布版本不可变：publish 后 dag 冻结，只新增版本。"""

    __tablename__ = "workflow_versions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uid)
    workflow_id: Mapped[str] = mapped_column(ForeignKey("workflows.id"), index=True)
    version_no: Mapped[int] = mapped_column(default=1)
    dag: Mapped[dict] = mapped_column(JSON)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uid)
    workflow_id: Mapped[str] = mapped_column(ForeignKey("workflows.id"), index=True)
    version_id: Mapped[str] = mapped_column(ForeignKey("workflow_versions.id"))
    status: Mapped[str] = mapped_column(String(16), default="succeeded")
    inputs: Mapped[dict] = mapped_column(JSON, default=dict)
    outputs: Mapped[dict] = mapped_column(JSON, default=dict)
    error: Mapped[str] = mapped_column(String(2048), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Document(Base):
    __tablename__ = "documents"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    title: Mapped[str] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Chunk(Base):
    __tablename__ = "chunks"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), index=True)
    content: Mapped[str] = mapped_column(String(4000))
    embedding: Mapped[list | None] = mapped_column(EmbeddingVector, nullable=True)


# 默认权限码种子（与 core/rbac.py 矩阵保持一致，见 seed_permissions）。
DEFAULT_PERMISSIONS: tuple[tuple[str, str], ...] = (
    ("users:read", "查看用户"),
    ("users:write", "管理用户"),
    ("permissions:read", "查看权限"),
    ("permissions:write", "分配权限"),
    ("models:read", "查看模型"),
    ("models:write", "配置模型"),
    ("workflows:read", "查看流程"),
    ("workflows:write", "编排/发布流程"),
    ("workflows:run", "运行流程"),
)
