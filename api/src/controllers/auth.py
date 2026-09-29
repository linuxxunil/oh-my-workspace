"""Auth controller（薄层）：登录/me，领域异常在边界翻译。"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.controllers.deps import current_user
from src.db import get_db
from src.errors import BadRequest, Unauthorized
from src.models import User
from src.schemas import LoginRequest, MeResponse, PasswordChangeRequest, TokenResponse
from src.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        token = auth_service.login(db, email=payload.email, password=payload.password)
    except Unauthorized as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return TokenResponse(access_token=token)


@router.get("/me", response_model=MeResponse)
def me(user: User = Depends(current_user)):
    return MeResponse(id=user.id, tenant_id=user.tenant_id, email=user.email, role=user.role)


@router.post("/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    payload: PasswordChangeRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    """本人自改密码：仅需登录（authn-only，无新权限码），验旧密码。"""
    try:
        auth_service.change_password(
            db, user=user, old_password=payload.old_password, new_password=payload.new_password
        )
    except BadRequest as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
