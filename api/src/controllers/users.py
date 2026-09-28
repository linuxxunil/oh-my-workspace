"""用户管理 controller（薄层）。"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.controllers.deps import current_user, require
from src.db import get_db
from src.errors import Conflict, Forbidden, NotFound
from src.models import User
from src.schemas import UserCreateRequest, UserResponse, UserUpdateRequest
from src.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


def _to(u: User) -> UserResponse:
    return UserResponse(
        id=u.id, tenant_id=u.tenant_id, email=u.email, role=u.role, is_active=u.is_active
    )


@router.get("", response_model=list[UserResponse])
def list_users(
    _: User = Depends(require("users:read")),
    db: Session = Depends(get_db),
    me: User = Depends(current_user),
):
    return [_to(u) for u in user_service.list_users(db, tenant_id=me.tenant_id)]


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreateRequest,
    _: User = Depends(require("users:write")),
    db: Session = Depends(get_db),
    me: User = Depends(current_user),
):
    try:
        return _to(
            user_service.create_user(
                db, tenant_id=me.tenant_id, actor_role=me.role, payload=payload
            )
        )
    except (Forbidden, Conflict) as e:
        code = status.HTTP_403_FORBIDDEN if isinstance(e, Forbidden) else status.HTTP_409_CONFLICT
        raise HTTPException(status_code=code, detail=str(e))


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    payload: UserUpdateRequest,
    _: User = Depends(require("users:write")),
    db: Session = Depends(get_db),
    me: User = Depends(current_user),
):
    try:
        return _to(
            user_service.update_user(
                db, tenant_id=me.tenant_id, actor_role=me.role, user_id=user_id, payload=payload
            )
        )
    except NotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Forbidden as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    _: User = Depends(require("users:write")),
    db: Session = Depends(get_db),
    me: User = Depends(current_user),
):
    try:
        user_service.delete_user(db, tenant_id=me.tenant_id, actor_role=me.role, user_id=user_id)
    except NotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Forbidden as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Conflict as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
