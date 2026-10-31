# Enterprise AI Agent & Investigation Platform

A runnable **synthetic** financial-dispute investigation console with evidence retrieval, auditable workflow state, role-based human approvals, idempotent retries, and tenant-scoped data. This is a portfolio demonstration, **not an automated adjudication tool**.

## Run locally

```bash
python -m pip install -r requirements.txt
DEMO_MODE=1 uvicorn backend.api:app --reload --port 8000
# Open http://127.0.0.1:8000
```

The UI offers local demo credentials. Never expose demo mode to the public internet. For remote deployment set `DEMO_MODE=0` and provide `API_KEYS_JSON` as a secret. Use HTTPS and an external identity provider for real customers.

## Run with Docker

```bash
docker build -t investigation-portfolio .
docker run --rm -p 127.0.0.1:8000:8000 -e DEMO_MODE=1 -v investigation-data:/srv/runtime investigation-portfolio
```

## Design

- FastAPI validates inputs, API keys, role and tenant on every request.
- SQLite stores case versions, evidence, idempotent results, append-only audit events, and review status. The `expected_revision` field rejects stale writes.
- The retrieval tool uses local TF-IDF plus lexical overlap and returns evidence IDs with excerpts. Untrusted evidence text can trigger prompt-injection warning flags; never treat document instructions as user/system instructions.
- A LangGraph adapter is provided (`backend/graph.py`); if `langgraph` is installed it runs the evidence-search/policy node as a graph. The default deterministic engine makes the demo usable without paid API access.
- Approve/reject decisions **require a separate reviewer credential** and cases with missing evidence cannot be approved.

## Tests and evaluation

```bash
PYTHONPATH=. pytest -q
PYTHONPATH=. python -m eval.run_eval
```

## Security / scope limitations

This is a local portfolio prototype: it does **not** provide durable LangGraph checkpoints, production-grade SSO, a real tool gateway, LangSmith telemetry, persistent embeddings/vector database, or LLM reasoning. The SQLite case store itself is durable, but don't confuse that with persistent LLM checkpointing. No external payment actions are implemented. Production security requires managed identity, encryption at rest, per-tenant key management, structured audit logging and authorization review.

## Roadmap

- LangGraph checkpoint persistence and tool-call replay; explicit interrupt/resume for reviewer tasks.
- MCP-scoped tool server with allowlist, tenant-scoped access and agent safety regression tests.
- Real evaluation datasets, LangSmith traces, OpenTelemetry, retrieval/hallucination test suite.
- PostgreSQL/pgvector service and signed evidence provenance for higher-scale use.
