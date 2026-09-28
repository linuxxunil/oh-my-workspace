"""请求/响应模型分离命名（Pydantic v2）。后端拥有形状，前端生成客户端只消费。"""

from pydantic import BaseModel, EmailStr, Field

from src.models import Role


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    id: str
    tenant_id: str
    email: str
    role: Role


class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    role: Role = Role.MEMBER


class UserUpdateRequest(BaseModel):
    password: str | None = Field(default=None, min_length=8)
    role: Role | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: str
    tenant_id: str
    email: str
    role: Role
    is_active: bool


class PermissionResponse(BaseModel):
    code: str
    description: str


class RolePermissionsUpdateRequest(BaseModel):
    permission_codes: list[str]


class RolePermissionsResponse(BaseModel):
    role: Role
    permission_codes: list[str]


class SystemFeatureResponse(BaseModel):
    features: dict[str, bool]


class TestConnectionResponse(BaseModel):
    ok: bool
    status_code: int
    model_count: int
    error: str = ""
