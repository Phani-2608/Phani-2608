"""Optional LangGraph orchestration; deterministic fallback requires no model key."""
from __future__ import annotations
from typing import Any, TypedDict
from .engine import analyze

class InvestigationState(TypedDict, total=False):
    case: dict[str, Any]
    result: dict[str, Any]

def build_graph():
    try:
        from langgraph.graph import StateGraph, START, END
    except ImportError:
        return None
    workflow = StateGraph(InvestigationState)
    def investigation_node(state: InvestigationState):
        return {'result': analyze(state['case'])}
    workflow.add_node('evidence_search_and_policy_review', investigation_node)
    workflow.add_edge(START, 'evidence_search_and_policy_review')
    workflow.add_edge('evidence_search_and_policy_review', END)
    return workflow.compile()

def run_case(case: dict[str, Any]) -> dict[str, Any]:
    graph = build_graph()
    if graph is None:
        return analyze(case)
    return graph.invoke({'case': case})['result']
