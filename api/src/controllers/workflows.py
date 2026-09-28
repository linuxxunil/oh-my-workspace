"""Workflow/KB controller（薄层）。"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.controllers.deps import current_user, require
from src.dag import (
    DocumentCreateRequest,
    DocumentResponse,
    RunRequest,
    RunResponse,
    VersionCreateRequest,
    VersionResponse,
    WorkflowCreateRequest,
    WorkflowResponse,
)
from src.db import get_db
from src.errors import Conflict, NotFound
from src.models import User
from src.services import knowledge_service, workflow_service

router = APIRouter(tags=["workflows"])


def _to_run(r) -> RunResponse:  # type: ignore[no-untyped-def]
    return RunResponse(id=r.id, status=r.status, outputs=r.outputs, error=r.error)


@router.post("/workflows", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
def create_workflow(
    payload: WorkflowCreateRequest,
    _: User = Depends(require("workflows:write")),
    db: Session = Depends(get_db),
    me: User = Depends(current_user),
):
    try:
        wf, _ver = workflow_service.create_workflow(
            db, tenant_id=me.tenant_id, user_id=me.id, payload=payload
        )
    except Conflict as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return WorkflowResponse(id=wf.id, name=wf.name, description=wf.description)


@router.get("/workflows", response_model=list[WorkflowResponse])
def list_workflows(
    _: User = Depends(require("workflows:read")),
    db: Session = Depends(get_db),
    me: User = Depends(current_user),
):
    return [
        WorkflowResponse(id=w.id, name=w.name, description=w.description)
        for w in workflow_service.list_workflows(db, tenant_id=me.tenant_id)
    ]


@router.delete("/workflows/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workflow(
    workflow_id: str,
    _: User = Depends(require("workflows:write")),
    db: Session = Depends(get_db),
    me: User = Depends(current_user),
):
    try:
        workflow_service.delete_workflow(db, tenant_id=me.tenant_id, workflow_id=workflow_id)
    except NotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/workflows/{workflow_id}/versions/latest", response_model=VersionResponse)
def latest_version(
    workflow_id: str,
    _: User = Depends(require("workflows:read")),
    db: Session = Depends(get_db),
    me: User = Depends(current_user),
):
    try:
        workflow_service.get_workflow(db, tenant_id=me.tenant_id, workflow_id=workflow_id)
        ver = workflow_service.latest_version(db, workflow_id=workflow_id)
    except NotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return VersionResponse(
        id=ver.id,
        workflow_id=ver.workflow_id,
        version_no=ver.version_no,
        dag=ver.dag,
        is_published=ver.is_published,
    )


@router.post("/workflows/{workflow_id}/publish", response_model=VersionResponse)
def publish(
    workflow_id: str,
    _: User = Depends(require("workflows:write")),
    db: Session = Depends(get_db),
    me: User = Depends(current_user),
):
    try:
        ver = workflow_service.publish_version(db, tenant_id=me.tenant_id, workflow_id=workflow_id)
    except NotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return VersionResponse(
        id=ver.id,
        workflow_id=ver.workflow_id,
        version_no=ver.version_no,
        dag=ver.dag,
        is_published=ver.is_published,
    )


@router.post(
    "/workflows/{workflow_id}/versions",
    response_model=VersionResponse,
    status_code=status.HTTP_201_CREATED,
)
def new_version(
    workflow_id: str,
    payload: VersionCreateRequest,
    _: User = Depends(require("workflows:write")),
    db: Session = Depends(get_db),
    me: User = Depends(current_user),
):
    try:
        ver = workflow_service.new_version(
            db, tenant_id=me.tenant_id, workflow_id=workflow_id, dag=payload.dag
        )
    except NotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return VersionResponse(
        id=ver.id,
        workflow_id=ver.workflow_id,
        version_no=ver.version_no,
        dag=ver.dag,
        is_published=ver.is_published,
    )


@router.post("/workflows/{workflow_id}/run", response_model=RunResponse)
def run_workflow(
    workflow_id: str,
    payload: RunRequest,
    _: User = Depends(require("workflows:run")),
    db: Session = Depends(get_db),
    me: User = Depends(current_user),
):
    try:
        run = workflow_service.run_workflow(
            db, tenant_id=me.tenant_id, workflow_id=workflow_id, inputs=payload.inputs
        )
    except NotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return _to_run(run)


@router.get("/workflows/{workflow_id}/runs", response_model=list[RunResponse])
def list_runs(
    workflow_id: str,
    _: User = Depends(require("workflows:read")),
    db: Session = Depends(get_db),
    me: User = Depends(current_user),
):
    try:
        runs = workflow_service.list_runs(db, tenant_id=me.tenant_id, workflow_id=workflow_id)
    except NotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return [_to_run(r) for r in runs]


@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    payload: DocumentCreateRequest,
    _: User = Depends(require("workflows:write")),
    db: Session = Depends(get_db),
    me: User = Depends(current_user),
):
    doc, n = knowledge_service.create_document(
        db, tenant_id=me.tenant_id, title=payload.title, content=payload.content
    )
    return DocumentResponse(id=doc.id, title=doc.title, chunk_count=n)
