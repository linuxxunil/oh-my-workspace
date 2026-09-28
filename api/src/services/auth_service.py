"""Auth 编排（service owner）。"""

from sqlalchemy.orm import Session

from src.core.security import create_token, verify_password
from src.errors import Unauthorized
from src.models import User


def login(db: Session, *, email: str, password: str) -> str:
    """邮箱+密码换 JWT；失败统一 Unauthorized（不泄露是账号还是密码错，防枚举细节除外）。"""
    user = db.query(User).filter(User.email == email, User.is_active.is_(True)).first()
    if user is None or not verify_password(password, user.password_hash):
        raise Unauthorized("账号或密码错误")
    return create_token(user_id=user.id, tenant_id=user.tenant_id, role=user.role.value)
