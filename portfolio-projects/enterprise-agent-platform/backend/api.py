"""REST API with tenant-scoped access, reviewer authorization and audit logging."""
from __future__ import annotations
from pathlib import Path
import os
from fastapi import Depends, FastAPI, HTTPException, Header
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from .store import CaseStore, ConflictError
from .auth import load_credentials, authenticate, Principal
from .graph import run_case

class CreateCase(BaseModel):
    case_id: str = Field(min_length=1, max_length=72, pattern=r'^[a-zA-Z0-9_-]+$')
    customer_id: str = Field(min_length=1, max_length=72)
    amount: float = Field(ge=0, le=100000000)
    description: str = Field(min_length=4, max_length=5000)

class AddEvidence(BaseModel):
    evidence_id: str = Field(min_length=1, max_length=72, pattern=r'^[a-zA-Z0-9_-]+$')
    text: str = Field(min_length=3, max_length=10000)
    expected_revision: int = Field(ge=1)

class RevisionRequest(BaseModel):
    expected_revision: int = Field(ge=1)

class HumanDecision(RevisionRequest):
    decision: str = Field(pattern='^(approve|reject)$')


def create_app(db_path: str | None = None, demo_mode: bool | None = None) -> FastAPI:
    credentials = load_credentials(demo_mode)
    store = CaseStore(db_path or os.getenv('DB_PATH', './runtime/cases.sqlite3'))
    app = FastAPI(title='Enterprise AI Investigation Platform', version='1.0.0',
                  description='Synthetic-data demonstration. Human authorization always required.')
    app.state.store = store

    def principal(x_api_key: str | None = Header(default=None)) -> Principal:
        who = authenticate(x_api_key, credentials)
        if who is None:
            raise HTTPException(401, 'invalid API credentials')
        return who

    def investigator(who: Principal = Depends(principal)):
        if who.role != 'investigator':
            raise HTTPException(403, 'investigator role required')
        return who

    def reviewer(who: Principal = Depends(principal)):
        if who.role != 'reviewer':
            raise HTTPException(403, 'reviewer role required')
        return who

    def get_case(tenant, case_id):
        record = store.get(tenant, case_id)
        if not record:
            raise HTTPException(404, 'case not found')
        return record

    @app.get('/health')
    def health():
        return {'status': 'ok', 'environment': 'demo' if demo_mode or os.getenv('DEMO_MODE') == '1' else 'configured'}

    @app.get('/')
    def dashboard():
        return FileResponse(Path(__file__).parent.parent / 'frontend' / 'index.html')

    @app.get('/cases')
    def cases(who: Principal = Depends(principal)):
        return store.list_cases(who.tenant)

    @app.post('/cases', status_code=201)
    def create_case(body: CreateCase, who: Principal = Depends(investigator)):
        try:
            return store.create(who.tenant, body.case_id, body.customer_id, body.amount, body.description, who.role)
        except ConflictError as exc:
            raise HTTPException(409, str(exc)) from exc

    @app.get('/cases/{case_id}')
    def case_detail(case_id: str, who: Principal = Depends(principal)):
        return get_case(who.tenant, case_id)

    @app.post('/cases/{case_id}/evidence')
    def evidence(case_id: str, body: AddEvidence, who: Principal = Depends(investigator)):
        try:
            result = store.append_evidence(who.tenant, case_id, body.evidence_id, body.text, who.role, body.expected_revision)
        except ConflictError as exc:
            raise HTTPException(409, str(exc)) from exc
        if result is None:
            raise HTTPException(404, 'case not found')
        return result

    def replay_if_identical(tenant: str, case_id: str, token: str, action: str, revision: int, decision: str | None = None):
        # Reusing a token with different request arguments is a conflict, never a replay.
        import json
        with store.connect() as db:
            row = db.execute('SELECT action,response FROM idempotency WHERE tenant=? AND case_id=? AND token=?',
                             (tenant, case_id, token)).fetchone()
        if row is None:
            return None
        if row['action'] != action:
            raise HTTPException(409, 'idempotency key already used for another action')
        previous = json.loads(row['response'])
        if previous['revision'] != revision + 1:
            raise HTTPException(409, 'idempotency key already used with a different revision')
        if decision is not None and previous['status'] != ('approved' if decision == 'approve' else 'rejected'):
            raise HTTPException(409, 'idempotency key already used with a different decision')
        return previous

    @app.post('/cases/{case_id}/investigate')
    def investigate(case_id: str, body: RevisionRequest,
                    idempotency_key: str | None = Header(default=None, max_length=120),
                    who: Principal = Depends(investigator)):
        case = get_case(who.tenant, case_id)
        if idempotency_key:
            previous = replay_if_identical(who.tenant, case_id, idempotency_key, 'investigate', body.expected_revision)
            if previous is not None:
                return previous
        if case['revision'] != body.expected_revision:
            raise HTTPException(409, 'revision mismatch; refresh case')
        analysis = run_case(case)
        try:
            result = store.investigate(who.tenant, case_id, analysis, who.role, body.expected_revision, idempotency_key)
        except ConflictError as exc:
            raise HTTPException(409, str(exc)) from exc
        return result

    @app.post('/cases/{case_id}/decision')
    def decision(case_id: str, body: HumanDecision,
                 idempotency_key: str | None = Header(default=None, max_length=120),
                 who: Principal = Depends(reviewer)):
        if idempotency_key:
            previous = replay_if_identical(who.tenant, case_id, idempotency_key, 'decide', body.expected_revision, body.decision)
            if previous is not None:
                return previous
        try:
            result = store.decide(who.tenant, case_id, body.decision, who.role, body.expected_revision, idempotency_key)
        except ConflictError as exc:
            raise HTTPException(409, str(exc)) from exc
        if result is None:
            raise HTTPException(404, 'case not found')
        return result

    @app.get('/cases/{case_id}/audit')
    def audit(case_id: str, who: Principal = Depends(principal)):
        get_case(who.tenant, case_id)
        return store.audit(who.tenant, case_id)

    return app

# Production fails closed without configured API keys. Local dev: DEMO_MODE=1 uvicorn backend.api:app
if os.getenv('PORTFOLIO_SKIP_APP', '') == '1':
    app = None
else:
    app = create_app()
