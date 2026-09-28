"""Workflow 编排（service owner）：CRUD + 版本/发布 + 运行历史。写事务显式有界。"""

from sqlalchemy.orm import Session

from src.core.graph import compile_and_run
from src.dag import Dag, WorkflowCreateRequest
from src.errors import Conflict, NotFound
from src.models import Workflow, WorkflowRun, WorkflowVersion


def create_workflow(
    db: Session, *, tenant_id: str, user_id: str, payload: WorkflowCreateRequest
) -> tuple[Workflow, WorkflowVersion]:
    exists = (
        db.query(Workflow)
        .filter(Workflow.tenant_id == tenant_id, Workflow.name == payload.name)
        .first()
    )
    if exists is not None:
        raise Conflict("同名流程已存在")
    wf = Workflow(
        tenant_id=tenant_id,
        name=payload.name,
        description=payload.description,
        created_by=user_id,
    )
    db.add(wf)
    db.flush()
    ver = WorkflowVersion(workflow_id=wf.id, version_no=1, dag=payload.dag.model_dump())
    db.add(ver)
    db.commit()
    db.refresh(wf)
    db.refresh(ver)
    return wf, ver


def list_workflows(db: Session, *, tenant_id: str) -> list[Workflow]:
    return db.query(Workflow).filter(Workflow.tenant_id == tenant_id).order_by(Workflow.name).all()


def latest_version(db: Session, *, workflow_id: str) -> WorkflowVersion:
    ver = (
        db.query(WorkflowVersion)
        .filter(WorkflowVersion.workflow_id == workflow_id)
        .order_by(WorkflowVersion.version_no.desc())
        .first()
    )
    if ver is None:
        raise NotFound("版本不存在")
    return ver


def publish_version(db: Session, *, tenant_id: str, workflow_id: str) -> WorkflowVersion:
    get_workflow(db, tenant_id=tenant_id, workflow_id=workflow_id)
    ver = latest_version(db, workflow_id=workflow_id)
    ver.is_published = True
    db.commit()
    db.refresh(ver)
    return ver


def new_version(db: Session, *, tenant_id: str, workflow_id: str, dag: Dag) -> WorkflowVersion:
    """画布保存：冻结旧版，新增一版（发布态不继承，需重发布）。"""
    get_workflow(db, tenant_id=tenant_id, workflow_id=workflow_id)
    cur = latest_version(db, workflow_id=workflow_id)
    ver = WorkflowVersion(
        workflow_id=workflow_id, version_no=cur.version_no + 1, dag=dag.model_dump()
    )
    db.add(ver)
    db.commit()
    db.refresh(ver)
    return ver


def run_workflow(db: Session, *, tenant_id: str, workflow_id: str, inputs: dict) -> WorkflowRun:
    wf = get_workflow(db, tenant_id=tenant_id, workflow_id=workflow_id)
    ver = latest_version(db, workflow_id=wf.id)
    dag = Dag.model_validate(ver.dag)
    try:
        outputs = compile_and_run(dag, db=db, tenant_id=tenant_id, inputs=inputs)
        run = WorkflowRun(
            workflow_id=wf.id, version_id=ver.id, status="succeeded", inputs=inputs, outputs=outputs
        )
    except Exception as e:  # noqa: BLE001 -- 运行失败必须落库为 failed 记录而非 500，宽捕获为契约
        run = WorkflowRun(
            workflow_id=wf.id,
            version_id=ver.id,
            status="failed",
            inputs=inputs,
            outputs={},
            error=str(e)[:2000],
        )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def list_runs(db: Session, *, tenant_id: str, workflow_id: str) -> list[WorkflowRun]:
    get_workflow(db, tenant_id=tenant_id, workflow_id=workflow_id)
    return (
        db.query(WorkflowRun)
        .filter(WorkflowRun.workflow_id == workflow_id)
        .order_by(WorkflowRun.created_at.desc())
        .all()
    )


def get_workflow(db: Session, *, tenant_id: str, workflow_id: str) -> Workflow:
    wf = (
        db.query(Workflow)
        .filter(Workflow.tenant_id == tenant_id, Workflow.id == workflow_id)
        .first()
    )
    if wf is None:
        raise NotFound("流程不存在")
    return wf


def delete_workflow(db: Session, *, tenant_id: str, workflow_id: str) -> None:
    """删流程：先子（runs→versions）后主，一次有界事务提交。"""
    wf = get_workflow(db, tenant_id=tenant_id, workflow_id=workflow_id)
    db.query(WorkflowRun).filter(WorkflowRun.workflow_id == wf.id).delete(
        synchronize_session=False
    )
    db.query(WorkflowVersion).filter(WorkflowVersion.workflow_id == wf.id).delete(
        synchronize_session=False
    )
    db.delete(wf)
    db.commit()
