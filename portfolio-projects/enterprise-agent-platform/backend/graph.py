"""Optional multi-step LangGraph orchestration; local policy baseline otherwise.

When the LangGraph package is available, a graph runs evidence discovery,
policy classification, and a safe routing decision. Case persistence, audit and
human resume are provided separately by the SQLite store/API.
"""
from __future__ import annotations
from typing import Any, TypedDict
from .engine import analyze,has_instruction_attack
from .retrieval import retrieve

class InvestigationState(TypedDict, total=False):
    case: dict[str, Any]
    citations: list[dict[str,Any]]
    flags: list[str]
    recommendation: str
    result: dict[str, Any]

def build_graph():
    try:
        from langgraph.graph import StateGraph, START, END
    except ImportError:
        return None
    workflow=StateGraph(InvestigationState)
    def evidence_search(state:InvestigationState):
        return {'citations':retrieve(state['case'].get('description',''),state['case'].get('evidence',[]))}
    def policy_check(state:InvestigationState):
        case=state['case'];flags=[]
        if case['amount']>=500:flags.append('high_value_case')
        if not case.get('evidence'):flags.append('missing_evidence')
        if any(has_instruction_attack(d['text']) for d in case.get('evidence',[])):
            flags.append('suspicious_document_instructions')
        return {'flags':flags}
    def classify(state:InvestigationState):
        return {'recommendation':'request_evidence' if not state['case'].get('evidence') else 'send_to_human_review'}
    def finish(state:InvestigationState):
        matches=state.get('citations',[])
        return {'result':{'recommendation':state['recommendation'],
                          'reasons':state.get('flags',[]) or ['evidence_available_for_review'],
                          'citations':matches,'requires_human_approval':True,
                          'tool_calls':[{'tool':'search_case_evidence','status':'completed','results':len(matches)}],
                          'model_used':'deterministic_safety_graph'}}
    workflow.add_node('retrieve_evidence',evidence_search)
    workflow.add_node('check_policy',policy_check)
    workflow.add_node('decide_next_step',classify)
    workflow.add_node('assemble_review_packet',finish)
    workflow.add_edge(START,'retrieve_evidence')
    workflow.add_edge('retrieve_evidence','check_policy')
    workflow.add_edge('check_policy','decide_next_step')
    workflow.add_edge('decide_next_step','assemble_review_packet')
    workflow.add_edge('assemble_review_packet',END)
    return workflow.compile()

def run_case(case:dict[str,Any])->dict[str,Any]:
    graph=build_graph()
    if graph is None:
        return analyze(case)
    return graph.invoke({'case':case})['result']
