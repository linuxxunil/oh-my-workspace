"""供应商 controller（薄层）；api_key 只收不返。"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.controllers.deps import current_user, require
from src.db import get_db
from src.errors import Conflict, NotFound
from src.models import ModelProvider, ProviderType, User
from src.schemas import TestConnectionResponse
from src.services import provider_service

router = APIRouter(prefix="/models/providers", tags=["models"])


class ProviderCreateRequest(BaseModel):
    type: ProviderType
    name: str = Field(min_length=1, max_length=128)
    base_url: str = Field(min_length=8, max_length=512)
    api_key: str = Field(default="", max_length=1024)
    extra_headers: dict[str, str] = Field(default_factory=dict)


class ProviderResponse(BaseModel):
    id: str
    type: ProviderType
    name: str
    base_url: str
    is_active: bool


class ProviderUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    base_url: str | None = Field(default=None, min_length=8, max_length=512)
    # 空（None/'')= 保持原 Key（只收不返）；要换 Key 必须传非空值。
    api_key: str | None = Field(default=None, max_length=1024)
    extra_headers: dict[str, str] | None = None


def _to(p: ModelProvider) -> ProviderResponse:
    return ProviderResponse(
        id=p.id, type=p.type, name=p.name, base_url=p.base_url, is_active=p.is_active
    )


@router.get("", response_model=list[ProviderResponse])
def list_providers(
    _: User = Depends(require("models:read")),
    db: Session = Depends(get_db),
    me: User = Depends(current_user),
):
    return [_to(p) for p in provider_service.list_providers(db, tenant_id=me.tenant_id)]


@router.post("", response_model=ProviderResponse, status_code=status.HTTP_201_CREATED)
def create_provider(
    payload: ProviderCreateRequest,
    _: User = Depends(require("models:write")),
    db: Session = Depends(get_db),
    me: User = Depends(current_user),
):
    try:
        return _to(
            provider_service.create_provider(
                db,
                tenant_id=me.tenant_id,
                type=payload.type,
                name=payload.name,
                base_url=payload.base_url,
                api_key=payload.api_key,
                extra_headers=payload.extra_headers,
            )
        )
    except (Conflict, ValueError) as e:
        code = status.HTTP_409_CONFLICT if isinstance(e, Conflict) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(e))


@router.patch("/{provider_id}", response_model=ProviderResponse)
def update_provider(
    provider_id: str,
    payload: ProviderUpdateRequest,
    _: User = Depends(require("models:write")),
    db: Session = Depends(get_db),
    me: User = Depends(current_user),
):
    try:
        return _to(
            provider_service.update_provider(
                db,
                tenant_id=me.tenant_id,
                provider_id=provider_id,
                name=payload.name,
                base_url=payload.base_url,
                api_key=payload.api_key,
                extra_headers=payload.extra_headers,
            )
        )
    except NotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Conflict as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_provider(
    provider_id: str,
    _: User = Depends(require("models:write")),
    db: Session = Depends(get_db),
    me: User = Depends(current_user),
):
    try:
        provider_service.delete_provider(db, tenant_id=me.tenant_id, provider_id=provider_id)
    except NotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{provider_id}/models", response_model=list[str])
def fetch_models(
    provider_id: str,
    _: User = Depends(require("models:read")),
    db: Session = Depends(get_db),
    me: User = Depends(current_user),
):
    try:
        return provider_service.fetch_models(db, tenant_id=me.tenant_id, provider_id=provider_id)
    except NotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{provider_id}/test", response_model=TestConnectionResponse)
def test_connection(
    provider_id: str,
    _: User = Depends(require("models:read")),
    db: Session = Depends(get_db),
    me: User = Depends(current_user),
):
    try:
        return provider_service.test_connection(db, tenant_id=me.tenant_id, provider_id=provider_id)
    except NotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
