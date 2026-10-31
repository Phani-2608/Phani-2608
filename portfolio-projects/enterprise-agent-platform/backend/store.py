"""SQLite-backed multi-tenant case state and append-only audit events."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from contextlib import contextmanager
from typing import Any

class ConflictError(ValueError):
    pass

class CaseStore:
    def __init__(self, path: str):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS cases (
                    tenant TEXT NOT NULL, id TEXT NOT NULL, customer TEXT NOT NULL,
                    amount REAL NOT NULL, description TEXT NOT NULL, evidence TEXT NOT NULL,
                    analysis TEXT, status TEXT NOT NULL, revision INTEGER NOT NULL,
                    PRIMARY KEY (tenant, id)
                );
                CREATE TABLE IF NOT EXISTS audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant TEXT NOT NULL,
                    case_id TEXT NOT NULL, actor TEXT NOT NULL, event TEXT NOT NULL,
                    payload TEXT NOT NULL, timestamp TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_audit_case ON audit(tenant, case_id, id);
                CREATE TABLE IF NOT EXISTS idempotency (
                    tenant TEXT NOT NULL, case_id TEXT NOT NULL, token TEXT NOT NULL,
                    action TEXT NOT NULL, response TEXT NOT NULL,
                    PRIMARY KEY (tenant, case_id, token)
                );
            """)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            db.execute('PRAGMA foreign_keys=ON')
            db.execute('PRAGMA busy_timeout=10000')
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def _decode(row) -> dict[str, Any] | None:
        if row is None:
            return None
        data = dict(row)
        data['evidence'] = json.loads(data['evidence'])
        data['analysis'] = json.loads(data['analysis']) if data['analysis'] else None
        return data

    @staticmethod
    def _event(db, tenant, case_id, actor, event, payload):
        db.execute('INSERT INTO audit(tenant, case_id, actor, event, payload, timestamp) VALUES(?,?,?,?,?,?)',
                   (tenant, case_id, actor, event, json.dumps(payload, sort_keys=True), datetime.now(timezone.utc).isoformat()))

    def create(self, tenant, case_id, customer, amount, description, actor):
        with self.connect() as db:
            try:
                db.execute('INSERT INTO cases VALUES(?,?,?,?,?,?,?,?,?)',
                           (tenant, case_id, customer, amount, description, '[]', None, 'new', 1))
            except sqlite3.IntegrityError as e:
                raise ConflictError('case_id already exists in this tenant') from e
            self._event(db, tenant, case_id, actor, 'created', {'amount': amount})
        return self.get(tenant, case_id)

    def get(self, tenant, case_id):
        with self.connect() as db:
            return self._decode(db.execute('SELECT * FROM cases WHERE tenant=? AND id=?', (tenant, case_id)).fetchone())

    def append_evidence(self, tenant, case_id, evidence_id, text, actor, expected_revision):
        with self.connect() as db:
            row = db.execute('SELECT * FROM cases WHERE tenant=? AND id=?', (tenant, case_id)).fetchone()
            if row is None:
                return None
            if row['revision'] != expected_revision:
                raise ConflictError('revision mismatch; refresh case')
            if row['status'] in ('approved', 'rejected'):
                raise ConflictError('finalized case cannot be changed')
            items = json.loads(row['evidence'])
            if evidence_id in {item['id'] for item in items}:
                raise ConflictError('duplicate evidence id')
            items.append({'id': evidence_id, 'text': text})
            db.execute('UPDATE cases SET evidence=?, analysis=NULL, status=?, revision=revision+1 WHERE tenant=? AND id=?',
                       (json.dumps(items), 'new', tenant, case_id))
            self._event(db, tenant, case_id, actor, 'evidence_added', {'evidence_id': evidence_id})
        return self.get(tenant, case_id)

    def investigate(self, tenant, case_id, analysis, actor, expected_revision, token):
        with self.connect() as db:
            if token:
                previous = db.execute('SELECT action,response FROM idempotency WHERE tenant=? AND case_id=? AND token=?',
                                      (tenant, case_id, token)).fetchone()
                if previous:
                    if previous['action'] != 'investigate':
                        raise ConflictError('idempotency key reused for different action')
                    return json.loads(previous['response'])
            row = db.execute('SELECT * FROM cases WHERE tenant=? AND id=?', (tenant, case_id)).fetchone()
            if row is None:
                return None
            if row['revision'] != expected_revision:
                raise ConflictError('revision mismatch; refresh case')
            if row['status'] in ('approved', 'rejected'):
                raise ConflictError('finalized case cannot be reinvestigated')
            status = 'needs_evidence' if analysis['recommendation'] == 'request_evidence' else 'awaiting_review'
            db.execute('UPDATE cases SET analysis=?, status=?, revision=revision+1 WHERE tenant=? AND id=?',
                       (json.dumps(analysis), status, tenant, case_id))
            self._event(db, tenant, case_id, actor, 'investigated', {'recommendation': analysis['recommendation'], 'citations': [c['evidence_id'] for c in analysis['citations']]})
            updated = db.execute('SELECT * FROM cases WHERE tenant=? AND id=?', (tenant, case_id)).fetchone()
            response = self._decode(updated)
            if token:
                db.execute('INSERT INTO idempotency VALUES(?,?,?,?,?)', (tenant, case_id, token, 'investigate', json.dumps(response)))
            return response

    def decide(self, tenant, case_id, decision, actor, expected_revision, token):
        with self.connect() as db:
            if token:
                previous = db.execute('SELECT action,response FROM idempotency WHERE tenant=? AND case_id=? AND token=?',
                                      (tenant, case_id, token)).fetchone()
                if previous:
                    if previous['action'] != 'decide':
                        raise ConflictError('idempotency key reused for different action')
                    return json.loads(previous['response'])
            row = db.execute('SELECT * FROM cases WHERE tenant=? AND id=?', (tenant, case_id)).fetchone()
            if row is None:
                return None
            if row['revision'] != expected_revision:
                raise ConflictError('revision mismatch; refresh case')
            if row['status'] != 'awaiting_review':
                raise ConflictError('only cases awaiting review can be finalized')
            status = 'approved' if decision == 'approve' else 'rejected'
            db.execute('UPDATE cases SET status=?, revision=revision+1 WHERE tenant=? AND id=?', (status, tenant, case_id))
            self._event(db, tenant, case_id, actor, 'human_decision', {'decision': decision})
            response = self._decode(db.execute('SELECT * FROM cases WHERE tenant=? AND id=?', (tenant, case_id)).fetchone())
            if token:
                db.execute('INSERT INTO idempotency VALUES(?,?,?,?,?)', (tenant, case_id, token, 'decide', json.dumps(response)))
            return response

    def audit(self, tenant, case_id):
        with self.connect() as db:
            rows = db.execute('SELECT id,actor,event,payload,timestamp FROM audit WHERE tenant=? AND case_id=? ORDER BY id',
                              (tenant, case_id)).fetchall()
            return [{**dict(row), 'payload': json.loads(row['payload'])} for row in rows]

    def list_cases(self, tenant):
        with self.connect() as db:
            return [self._decode(row) for row in db.execute('SELECT * FROM cases WHERE tenant=? ORDER BY id', (tenant,)).fetchall()]
