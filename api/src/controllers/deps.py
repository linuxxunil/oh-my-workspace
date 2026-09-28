"""Controller 依赖：当前用户 + 权限检查（薄层，只解析与鉴权）。"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from src.core.rbac import check
from src.core.security import decode_token
from src.db import get_db
from src.errors import Forbidden
from src.models import Role, RolePermission, User

_bearer = HTTPBearer(auto_error=False)


def current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    """无 token→401；token 无效/用户不存在或停用→401。"""
    if creds is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录")
    try:
        payload = decode_token(creds.credentials)
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录已过期")
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录已失效")
    return user


def require(permission: str):
    """权限依赖工厂：DB 授权集合为空时回退默认矩阵（见 core/rbac）。"""

    def _dep(user: User = Depends(current_user), db: Session = Depends(get_db)) -> User:
        rows = db.query(RolePermission).filter(RolePermission.role == user.role).all()
        granted = {r.permission_code for r in rows} if rows else None
        try:
            check(Role(user.role), permission, granted)
        except Forbidden as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        return user

    return _dep
