"""权限管理 controller（薄层）。读权限放宽到 admin，写仅 super_admin。"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.controllers.deps import require
from src.db import get_db
from src.errors import Forbidden, NotFound
from src.models import Role, User
from src.schemas import (
    PermissionResponse,
    RolePermissionsResponse,
    RolePermissionsUpdateRequest,
)
from src.services import permission_service

router = APIRouter(tags=["permissions"])


@router.get("/permissions", response_model=list[PermissionResponse])
def list_permissions(_: User = Depends(require("permissions:read")), db: Session = Depends(get_db)):
    return [
        PermissionResponse(code=p.code, description=p.description)
        for p in permission_service.list_permissions(db)
    ]


@router.get("/roles/{role}/permissions", response_model=RolePermissionsResponse)
def get_role_permissions(
    role: Role, _: User = Depends(require("permissions:read")), db: Session = Depends(get_db)
):
    return RolePermissionsResponse(
        role=role, permission_codes=permission_service.get_role_permissions(db, role=role)
    )


@router.put("/roles/{role}/permissions", response_model=RolePermissionsResponse)
def update_role_permissions(
    role: Role,
    payload: RolePermissionsUpdateRequest,
    _: User = Depends(require("permissions:write")),
    db: Session = Depends(get_db),
):
    try:
        codes = permission_service.update_role_permissions(
            db, role=role, codes=payload.permission_codes
        )
    except NotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Forbidden as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    return RolePermissionsResponse(role=role, permission_codes=codes)
