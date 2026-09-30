"""模型双通道编排（service owner）。
wire 结论（PLAN-001 R1 spike，PLAN-014 S1 2026-09-30 复核）：
opencode-go 远端（https://opencode.ai/zen/go/v1）实测仅通 OpenAI-compatible wire——
GET {base}/models 200 标准 list 形态（30 模型），候选原生形态 /api/models、/api/v1/models 均为 404
（base 以 /v1 结尾时 /v1/models 候选被脚本去重跳过）；
故首版按 OpenAI-compatible wire 承载 + 独立 type/headers 钩子，维持 downgrade，不写推测性原生 client。
spike 脚手架见 api/scripts/spike_opencode_go.py（PLAN-002 S2，只读探测，无凭证时结论为 downgrade）。
"""

import re

import httpx
from pydantic import ValidationError
from sqlalchemy.orm import Session

from src.dag import Dag
from src.errors import Conflict, NotFound
from src.libs import crypto
from src.libs.http import assert_safe_url
from src.models import ModelProvider, ProviderType, Workflow, WorkflowVersion
from src.services import cache as cache_svc


def _http_get(url: str, headers: dict, timeout_s: float = 10.0) -> httpx.Response:
    assert_safe_url(url)
    return httpx.get(url, headers=headers, timeout=timeout_s)


def _http_post(url: str, headers: dict, payload: dict, timeout_s: float = 60.0) -> httpx.Response:
    assert_safe_url(url)
    return httpx.post(url, headers=headers, json=payload, timeout=timeout_s)


def _auth_headers(p: ModelProvider) -> dict[str, str]:
    """出站鉴权头：DB 密文经 crypto.decrypt 还原后拼 Bearer（老明文行兜底，见 libs/crypto）。"""
    plain = crypto.decrypt(p.api_key) if p.api_key else ""
    h = {"Authorization": f"Bearer {plain}"} if plain else {}
    h.update(p.extra_headers or {})
    return h


def _models_url(p: ModelProvider) -> str:
    return p.base_url.rstrip("/") + "/models"


def _chat_url(p: ModelProvider) -> str:
    return p.base_url.rstrip("/") + "/chat/completions"


_HEADER_NAME_RE = re.compile(r"^[A-Za-z0-9-]+$")
_MAX_EXTRA_HEADERS = 20
_MAX_HEADER_VALUE_LEN = 1024


def _check_extra_headers(headers: dict) -> None:
    """校验自定义头；非法抛 ValueError（controller 译 400）。
    禁止覆盖 Authorization（大小写不敏感），防 Bearer 被顶掉。"""
    if len(headers) > _MAX_EXTRA_HEADERS:
        raise ValueError(f"自定义头最多 {_MAX_EXTRA_HEADERS} 条")
    for k, v in headers.items():
        if not isinstance(k, str) or not _HEADER_NAME_RE.match(k):
            raise ValueError(f"非法头名：{k}")
        if k.lower() == "authorization":
            raise ValueError("不允许覆盖 Authorization 头")
        if not isinstance(v, str) or len(v) > _MAX_HEADER_VALUE_LEN:
            raise ValueError(f"头值非法或过长：{k}")


def list_providers(db: Session, *, tenant_id: str) -> list[ModelProvider]:
    return (
        db.query(ModelProvider)
        .filter(ModelProvider.tenant_id == tenant_id)
        .order_by(ModelProvider.name)
        .all()
    )


def create_provider(
    db: Session,
    *,
    tenant_id: str,
    type: ProviderType,
    name: str,
    base_url: str,
    api_key: str = "",
    extra_headers: dict | None = None,
) -> ModelProvider:
    assert_safe_url(base_url)
    _check_extra_headers(extra_headers or {})
    exists = (
        db.query(ModelProvider)
        .filter(ModelProvider.tenant_id == tenant_id, ModelProvider.name == name)
        .first()
    )
    if exists is not None:
        raise Conflict("同名供应商已存在")
    p = ModelProvider(
        tenant_id=tenant_id,
        type=type,
        name=name,
        base_url=base_url.rstrip("/"),
        api_key=crypto.encrypt(api_key) if api_key else "",
        extra_headers=extra_headers or {},
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def delete_provider(db: Session, *, tenant_id: str, provider_id: str) -> None:
    p = _get(db, tenant_id=tenant_id, provider_id=provider_id)
    bound = _referencing_workflows(db, tenant_id=tenant_id, provider_id=provider_id)
    if bound:
        raise Conflict(f"已被以下流程引用：{'、'.join(bound)}")
    db.delete(p)
    db.commit()


def _referencing_workflows(db: Session, *, tenant_id: str, provider_id: str) -> list[str]:
    """查各流程最新版本 DAG 的 llm 节点引用；脏版本跳过（只认合法 llm 节点）。"""
    names: list[str] = []
    workflows = (
        db.query(Workflow).filter(Workflow.tenant_id == tenant_id).order_by(Workflow.name).all()
    )
    for wf in workflows:
        dag = _latest_dag(db, workflow_id=wf.id)
        if dag is None:
            continue
        for n in dag.nodes:
            if n.type == "llm" and str(n.config.get("provider_id") or "") == provider_id:
                names.append(wf.name)
                break
    return names


def _latest_dag(db: Session, *, workflow_id: str) -> Dag | None:
    """取最新版本 DAG；脏版本返回 None（不挡删除判定）。"""
    ver = (
        db.query(WorkflowVersion)
        .filter(WorkflowVersion.workflow_id == workflow_id)
        .order_by(WorkflowVersion.version_no.desc())
        .first()
    )
    if ver is None:
        return None
    try:
        return Dag.model_validate(ver.dag)
    except ValidationError:  # 脏版本不挡删除判定
        return None


def update_provider(
    db: Session,
    *,
    tenant_id: str,
    provider_id: str,
    name: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    extra_headers: dict | None = None,
) -> ModelProvider:
    """改供应商；api_key 空（None/''）= 保持（Key 只收不返，无法回显确认）。"""
    p = _get(db, tenant_id=tenant_id, provider_id=provider_id)
    if name is not None and name != p.name:
        exists = (
            db.query(ModelProvider)
            .filter(ModelProvider.tenant_id == tenant_id, ModelProvider.name == name)
            .first()
        )
        if exists is not None:
            raise Conflict("同名供应商已存在")
        p.name = name
    if base_url is not None:
        assert_safe_url(base_url)
        p.base_url = base_url.rstrip("/")
    if api_key:
        p.api_key = crypto.encrypt(api_key)
    if extra_headers is not None:
        _check_extra_headers(extra_headers)
        p.extra_headers = extra_headers
    db.commit()
    db.refresh(p)
    return p


def fetch_models(db: Session, *, tenant_id: str, provider_id: str) -> list[str]:
    """模型列表（redis 缓存 5 分钟）；两通道同 wire，opencode_go 失败时回退空列表不抛错。"""
    p = _get(db, tenant_id=tenant_id, provider_id=provider_id)
    key = cache_svc.provider_models_key(tenant_id, provider_id)
    cached = cache_svc.get_json(key)
    if isinstance(cached, list):
        return [str(x) for x in cached]
    try:
        r = _http_get(_models_url(p), _auth_headers(p))
        r.raise_for_status()
        data = r.json().get("data", [])
        names = [str(x.get("id")) for x in data if isinstance(x, dict) and x.get("id")]
    except (httpx.HTTPError, ValueError, KeyError):
        return []
    if names:
        cache_svc.set_json(key, names, ttl_s=300)
    return names


def test_connection(db: Session, *, tenant_id: str, provider_id: str) -> dict:
    """连通性检查：调 /models，2xx 即 ok，返回模型数。"""
    p = _get(db, tenant_id=tenant_id, provider_id=provider_id)
    try:
        r = _http_get(_models_url(p), _auth_headers(p))
        ok = 200 <= r.status_code < 300
        count = len(r.json().get("data", [])) if ok else 0
        return {"ok": ok, "status_code": r.status_code, "model_count": count}
    except (httpx.HTTPError, ValueError, KeyError) as e:
        return {"ok": False, "status_code": 0, "model_count": 0, "error": str(e)}


def chat(
    db: Session,
    *,
    tenant_id: str,
    provider_id: str,
    model: str,
    messages: list[dict],
) -> str:
    """LLM 对话（workflow llm 节点调用）；返回 content 文本。"""
    p = _get(db, tenant_id=tenant_id, provider_id=provider_id)
    r = _http_post(_chat_url(p), _auth_headers(p), {"model": model, "messages": messages})
    r.raise_for_status()
    return str(r.json()["choices"][0]["message"]["content"])


def _get(db: Session, *, tenant_id: str, provider_id: str) -> ModelProvider:
    p = (
        db.query(ModelProvider)
        .filter(ModelProvider.tenant_id == tenant_id, ModelProvider.id == provider_id)
        .first()
    )
    if p is None:
        raise NotFound("供应商不存在")
    return p
