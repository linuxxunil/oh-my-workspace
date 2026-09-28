"""种子数据（显式有界事务，S2 初始化用）。"""

from sqlalchemy.orm import Session

from src.core.rbac import DEFAULT_MATRIX
from src.core.security import hash_password
from src.models import DEFAULT_PERMISSIONS, Permission, Role, RolePermission, Tenant, User


def seed(db: Session) -> dict[str, str]:
    """建默认租户+权限+角色映射+三个用户；返回三角色邮箱→密码（仅本地/测试）。"""
    tenant = db.query(Tenant).first()
    if tenant is None:
        tenant = Tenant(name="default")
        db.add(tenant)
        db.flush()
    for code, desc in DEFAULT_PERMISSIONS:
        if db.get(Permission, code) is None:
            db.add(Permission(code=code, description=desc))
    db.flush()
    for role, codes in DEFAULT_MATRIX.items():
        for code in codes:
            exists = (
                db.query(RolePermission)
                .filter(RolePermission.role == role, RolePermission.permission_code == code)
                .first()
            )
            if exists is None:
                db.add(RolePermission(role=role, permission_code=code))
    users = {
        Role.SUPER_ADMIN: ("root@example.com", "Root12345"),
        Role.ADMIN: ("admin@example.com", "Admin12345"),
        Role.MEMBER: ("member@example.com", "Member12345"),
    }
    for role, (email, raw) in users.items():
        user_exists = (
            db.query(User).filter(User.tenant_id == tenant.id, User.email == email).first()
        )
        if user_exists is None:
            db.add(
                User(
                    tenant_id=tenant.id,
                    email=email,
                    password_hash=hash_password(raw),
                    role=role,
                    is_active=True,
                )
            )
    db.commit()
    return {role.value: email for role, (email, _) in users.items()}
