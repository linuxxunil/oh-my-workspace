"""RBAC 判定（core owner）。单租户三角色，权限码走 DB（role_permissions）。"""

from src.errors import Forbidden
from src.models import Role

# 角色默认矩阵（seed 用；运行时以 DB 为准，DB 为空时回退此矩阵保证可用）。
DEFAULT_MATRIX: dict[Role, set[str]] = {
    Role.SUPER_ADMIN: {
        "users:read",
        "users:write",
        "permissions:read",
        "permissions:write",
        "models:read",
        "models:write",
        "workflows:read",
        "workflows:write",
        "workflows:run",
    },
    Role.ADMIN: {
        "users:read",
        "users:write",
        "permissions:read",
        "models:read",
        "models:write",
        "workflows:read",
        "workflows:write",
        "workflows:run",
    },
    Role.MEMBER: {"workflows:read", "workflows:run", "models:read"},
}

# admin 不可触碰的红线（即使 DB 被改也强制）。
ADMIN_FORBIDDEN = {"permissions:write"}


def check(role: Role, permission: str, granted: set[str] | None) -> None:
    """无权限则抛 Forbidden；granted 为 None 时用默认矩阵。"""
    allowed = granted if granted is not None else DEFAULT_MATRIX[role]
    if role == Role.ADMIN and permission in ADMIN_FORBIDDEN:
        raise Forbidden(f"admin 不可拥有 {permission}")
    if permission not in allowed:
        raise Forbidden(f"缺少权限 {permission}")


def can_manage_actor(*, actor_role: Role, target_role: Role | None, is_self: bool) -> None:
    """用户管理红线：admin 不可删/改 super_admin，不可授 super_admin；member 不可管人。"""
    if actor_role == Role.MEMBER:
        raise Forbidden("member 不可管理用户")
    if actor_role == Role.ADMIN and target_role == Role.SUPER_ADMIN:
        raise Forbidden("admin 不可操作 super_admin")
