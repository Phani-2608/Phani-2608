"""Optional local MCP stdio server (install the official `mcp` package).

No network-hosted MCP endpoint is created. Credentials are checked by the same
policy gateway as the REST service. Do NOT expose tool tokens to untrusted users.
"""
from __future__ import annotations
import os
from .auth import load_credentials
from .store import CaseStore
from .tool_gateway import invoke_tool

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as e:
    raise ImportError('Install optional dependency: pip install "mcp>=1.8,<2"') from e

server=FastMCP('case-evidence-read-only')

def gateway(name,api_key,case_id,query=''):
    return invoke_tool(name,credential=api_key,credentials=load_credentials(),
                       store=CaseStore(os.getenv('DB_PATH','./runtime/cases.sqlite3')),
                       case_id=case_id,query=query)

@server.tool()
def search_case_evidence(case_id:str,query:str,api_key:str)->dict:
    """Search evidence belonging only to the authenticated tenant; read-only."""
    return gateway('search_case_evidence',api_key,case_id,query)

@server.tool()
def get_case_summary(case_id:str,api_key:str)->dict:
    """Read case metadata belonging only to the authenticated tenant; read-only."""
    return gateway('get_case_summary',api_key,case_id)

if __name__=='__main__':
    server.run(transport='stdio')
