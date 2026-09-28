"""权限管理编排（service owner）。"""

from sqlalchemy.orm import Session

from src.core.rbac import ADMIN_FORBIDDEN
from src.errors import Forbidden, NotFound
from src.models import Permission, Role, RolePermission


def list_permissions(db: Session) -> list[Permission]:
    return db.query(Permission).order_by(Permission.code).all()


def get_role_permissions(db: Session, *, role: Role) -> list[str]:
    rows = db.query(RolePermission).filter(RolePermission.role == role).all()
    return sorted(r.permission_code for r in rows)


def update_role_permissions(db: Session, *, role: Role, codes: list[str]) -> list[str]:
    """仅 super_admin 可调（controller 已鉴权）；admin 红线权限不可授。"""
    known = {p.code for p in db.query(Permission).all()}
    for code in codes:
        if code not in known:
            raise NotFound(f"未知权限 {code}")
    if role == Role.ADMIN and any(c in ADMIN_FORBIDDEN for c in codes):
        raise Forbidden("admin 不可拥有 permissions:write")
    db.query(RolePermission).filter(RolePermission.role == role).delete()
    for code in sorted(set(codes)):
        db.add(RolePermission(role=role, permission_code=code))
    db.commit()
    return sorted(set(codes))
