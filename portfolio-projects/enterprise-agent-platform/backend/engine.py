"""Policy-constrained investigation: evidence is data, not instructions."""
from __future__ import annotations
from typing import Any
import re
from .retrieval import retrieve

INJECTION_PATTERNS = (
    r'ignore (?:all |previous |your )?(?:instructions|rules|policies)',
    r'(?:system|developer) (?:message|prompt)',
    r'bypass (?:approval|security|policy)',
    r'approve (?:this |the )?(?:claim|dispute) (?:automatically|without review)',
)


def has_instruction_attack(text: str) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in INJECTION_PATTERNS)


def analyze(case: dict[str, Any]) -> dict[str, Any]:
    """Recommend next workflow state, NEVER finalize financial claims."""
    evidence = case.get('evidence', [])
    matches = retrieve(case.get('description', ''), evidence)
    flags = []
    if case['amount'] >= 500:
        flags.append('high_value_case')
    if not evidence:
        flags.append('missing_evidence')
    if any(has_instruction_attack(d['text']) for d in evidence):
        flags.append('suspicious_document_instructions')
    if evidence and not matches:
        flags.append('no_relevant_evidence')
    # A document's prose can NEVER authorize financial action.
    recommendation = 'request_evidence' if not evidence else 'send_to_human_review'
    return {
        'recommendation': recommendation,
        'reasons': flags or ['evidence_available_for_review'],
        'citations': matches,
        'requires_human_approval': True,
        'tool_calls': [{'tool': 'search_case_evidence', 'status': 'completed', 'results': len(matches)}],
        'model_used': 'deterministic_safety_baseline',
    }
