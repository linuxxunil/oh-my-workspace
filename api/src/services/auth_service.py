"""Auth 编排（service owner）。"""

from sqlalchemy.orm import Session

from src.core.security import create_token, hash_password, verify_password
from src.errors import BadRequest, Unauthorized
from src.models import User


def login(db: Session, *, email: str, password: str) -> str:
    """邮箱+密码换 JWT；失败统一 Unauthorized（不泄露是账号还是密码错，防枚举细节除外）。"""
    user = db.query(User).filter(User.email == email, User.is_active.is_(True)).first()
    if user is None or not verify_password(password, user.password_hash):
        raise Unauthorized("账号或密码错误")
    return create_token(user_id=user.id, tenant_id=user.tenant_id, role=user.role.value)


def change_password(db: Session, *, user: User, old_password: str, new_password: str) -> None:
    """本人自改：验旧 hash，对换新 hash；旧密码错→400（BadRequest），与登录 401 区分。"""
    fresh = db.query(User).filter(User.id == user.id).first()
    if fresh is None or not verify_password(old_password, fresh.password_hash):
        raise BadRequest("旧密码不正确")
    fresh.password_hash = hash_password(new_password)
    db.commit()
