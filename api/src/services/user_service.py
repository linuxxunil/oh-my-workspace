"""用户管理编排（service owner）。读写沿 tenant_id 约束。"""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.core.rbac import can_manage_actor
from src.core.security import hash_password
from src.errors import Conflict, NotFound
from src.models import Role, User
from src.schemas import UserCreateRequest, UserUpdateRequest


def list_users(db: Session, *, tenant_id: str) -> list[User]:
    return db.query(User).filter(User.tenant_id == tenant_id).order_by(User.email).all()


def create_user(
    db: Session, *, tenant_id: str, actor_role: Role, payload: UserCreateRequest
) -> User:
    """admin 不可授 super_admin（红线）；同租户邮箱唯一。"""
    can_manage_actor(actor_role=actor_role, target_role=payload.role, is_self=False)
    if payload.role == Role.SUPER_ADMIN and actor_role != Role.SUPER_ADMIN:
        from src.errors import Forbidden

        raise Forbidden("仅 super_admin 可授 super_admin")
    exists = db.query(User).filter(User.tenant_id == tenant_id, User.email == payload.email).first()
    if exists is not None:
        raise Conflict("邮箱已存在")
    user = User(
        tenant_id=tenant_id,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(
    db: Session, *, tenant_id: str, actor_role: Role, user_id: str, payload: UserUpdateRequest
) -> User:
    user = _get(db, tenant_id=tenant_id, user_id=user_id)
    can_manage_actor(actor_role=actor_role, target_role=user.role, is_self=False)
    if payload.role is not None:
        can_manage_actor(actor_role=actor_role, target_role=payload.role, is_self=False)
        if payload.role == Role.SUPER_ADMIN and actor_role != Role.SUPER_ADMIN:
            from src.errors import Forbidden

            raise Forbidden("仅 super_admin 可授 super_admin")
        user.role = payload.role
    if payload.password is not None:
        user.password_hash = hash_password(payload.password)
    if payload.is_active is not None:
        user.is_active = payload.is_active
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, *, tenant_id: str, actor_role: Role, user_id: str) -> None:
    user = _get(db, tenant_id=tenant_id, user_id=user_id)
    can_manage_actor(actor_role=actor_role, target_role=user.role, is_self=False)
    db.delete(user)
    try:
        db.commit()
    except IntegrityError as e:  # FK 残留（名下仍有流程等）收敛为 Conflict，不透 500
        db.rollback()
        raise Conflict("用户仍有未清理资源，先删除其名下资源") from e


def _get(db: Session, *, tenant_id: str, user_id: str) -> User:
    user = db.query(User).filter(User.tenant_id == tenant_id, User.id == user_id).first()
    if user is None:
        raise NotFound("用户不存在")
    return user
