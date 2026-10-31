import os
os.environ['PORTFOLIO_SKIP_APP']='1'
import pytest
from backend.tool_gateway import invoke_tool,ToolUnauthorized
from backend.auth import load_credentials
from backend.store import CaseStore


def test_allowlisted_tools_and_tenant_isolation(tmp_path):
    store=CaseStore(str(tmp_path/'cases.db'))
    credentials=load_credentials(demo_mode=True)
    record=store.create('alpha','c1','u1',30,'Disputed card payment','investigator')
    store.append_evidence('alpha','c1','e1','Payment receipt for disputed card charge','investigator',record['revision'])
    result=invoke_tool('search_case_evidence',credential='alpha-investigator-demo-key',credentials=credentials,store=store,case_id='c1',query='card receipt')
    assert result['citations'][0]['evidence_id']=='e1'
    summary=invoke_tool('get_case_summary',credential='alpha-reviewer-demo-key',credentials=credentials,store=store,case_id='c1')
    assert summary['evidence_count']==1
    for token in ['beta-investigator-demo-key','garbage']:
        with pytest.raises(ToolUnauthorized):
            invoke_tool('search_case_evidence',credential=token,credentials=credentials,store=store,case_id='c1',query='card')
    with pytest.raises(ToolUnauthorized):
        invoke_tool('delete_all_transactions',credential='alpha-investigator-demo-key',credentials=credentials,store=store,case_id='c1')
