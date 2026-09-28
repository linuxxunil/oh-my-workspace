"""最小未鉴权启动白名单（不当通用配置中心用，见 API_SCHEMA_GUIDE）。"""

from fastapi import APIRouter

from src.schemas import SystemFeatureResponse

router = APIRouter(tags=["system"])


@router.get("/system-features", response_model=SystemFeatureResponse)
def system_features():
    return SystemFeatureResponse(features={"auth": True, "rbac": True, "workflows": True})
