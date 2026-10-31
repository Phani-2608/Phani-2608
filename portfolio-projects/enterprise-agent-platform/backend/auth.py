"""Demo-mode credentials are explicitly disabled unless DEMO_MODE=1."""
from __future__ import annotations
from dataclasses import dataclass
import json
import os
import secrets

@dataclass(frozen=True)
class Principal:
    tenant: str
    role: str

DEMO_KEYS = {
    'alpha-investigator-demo-key': Principal('alpha', 'investigator'),
    'alpha-reviewer-demo-key': Principal('alpha', 'reviewer'),
    'beta-investigator-demo-key': Principal('beta', 'investigator'),
}

def load_credentials(demo_mode: bool | None = None) -> dict[str, Principal]:
    demo = os.environ.get('DEMO_MODE', '0') == '1' if demo_mode is None else demo_mode
    if demo:
        return DEMO_KEYS.copy()
    raw = os.environ.get('API_KEYS_JSON', '')
    if not raw:
        raise RuntimeError('API_KEYS_JSON is required when DEMO_MODE is disabled')
    obj = json.loads(raw)
    if not isinstance(obj, dict) or not obj:
        raise RuntimeError('API_KEYS_JSON must map tokens to {tenant,role}')
    keys = {}
    for token, identity in obj.items():
        if len(token) < 24 or identity.get('role') not in ('investigator', 'reviewer') or not identity.get('tenant'):
            raise RuntimeError('invalid credential configuration')
        keys[token] = Principal(identity['tenant'], identity['role'])
    return keys

def authenticate(key: str | None, credentials: dict[str, Principal]) -> Principal | None:
    if not key:
        return None
    for actual, principal in credentials.items():
        if secrets.compare_digest(key, actual):
            return principal
    return None
