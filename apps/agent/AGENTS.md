# AI Agent Engineering Rules

## Deterministic First

- AI must not decide raw security facts.
- Deterministic services fetch repositories, parse manifests, query OSV/NVD/EPSS, score findings, and evaluate release policy first.
- Keep deterministic policy logic testable without network or OpenAI calls.

## OpenAI Usage

- AI only explains, prioritizes, and writes human-friendly remediation text from structured scan data.
- AI must not invent CVEs, fixed versions, package versions, affected versions, or evidence.
- AI must not override deterministic release-gate decisions.
- Always include unknowns when data is incomplete.

## Safety

- Defensive-security-only behavior.
- Do not generate exploit code, payloads, offensive workflows, or instructions for unauthorized testing.
- Suggested commands must be safe remediation commands and only pin exact versions when fixed-version data exists.
- Do not put API keys or secrets in tests, docs, fixtures, or source code.
