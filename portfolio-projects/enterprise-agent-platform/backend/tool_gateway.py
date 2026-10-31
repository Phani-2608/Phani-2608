"""Read-only tool gateway with an explicit allowlist and tenant-scoped credentials."""
from __future__ import annotations
from .auth import authenticate,Principal
from .store import CaseStore
from .retrieval import retrieve

ALLOWED_TOOLS=frozenset({'search_case_evidence','get_case_summary'})

class ToolUnauthorized(PermissionError):
    pass


def invoke_tool(name:str, *, credential:str, credentials:dict[str,Principal],store:CaseStore,
                case_id:str,query:str='') -> dict:
    if name not in ALLOWED_TOOLS:
        raise ToolUnauthorized('tool not allowlisted')
    identity=authenticate(credential,credentials)
    if identity is None:
        raise ToolUnauthorized('invalid tool credentials')
    record=store.get(identity.tenant,case_id)
    if record is None:
        raise ToolUnauthorized('case missing or outside tenant scope')
    if name=='search_case_evidence':
        return {'tool':name,'case_id':case_id,'citations':retrieve(query,record['evidence'])}
    return {'tool':name,'case_id':case_id,'amount':record['amount'],
            'status':record['status'],'evidence_count':len(record['evidence'])}
