# Security and data handling

This prototype is for **synthetic, non-sensitive** examples. Never store real cardholder data, patient records, credentials or secrets in the local SQLite database.

## Controls exercised in code

- Default non-demo startup requires `API_KEYS_JSON` with long keys and tenant/role associations. Only `DEMO_MODE=1` enables intentionally public example keys.
- API requests authenticate using an API key, and tenant identity is derived from the credential rather than a user-provided tenant header.
- Only a reviewer credential can finalize a case. Evidence upload and investigation require investigator credentials.
- Untrusted evidence cannot trigger an approval tool call; no external payment actions exist.
- `expected_revision` provides optimistic concurrency checks. Idempotency keys avoid repeating investigation/decision commits.
- Case lookup, tool results, case listing and audit history are tenant-scoped.

## Controls not provided

This does not implement SSO, rate limiting, rotation/revocation workflows, encrypted database storage, legal retention controls, immutable signed logs, hosted MCP authentication, prompt-injection proofing, per-user audit identities, or production-grade secret storage. The local demo credentials are **not** secure, and demo mode must never be publicly deployed. The local MCP stdio protocol passes credentials as tool arguments; in a production integration use an identity-aware tool gateway rather than allowing agents to handle credentials as ordinary text.
