# Repo Risk Radar Agent

Python dependency-risk scanner used by the monorepo server. It can still run as a standalone CLI.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m repo_risk_radar analyze https://github.com/owner/repo --json
python -m repo_risk_radar analyze https://github.com/owner/repo --release-gate
python -m repo_risk_radar analyze https://github.com/owner/repo --ticket
python -m repo_risk_radar self-test
```

The CLI response includes an AI Release Gate. The PASS/WARN/BLOCK decision is deterministic; OpenAI only explains the decision and formats remediation/ticket text when `OPENAI_API_KEY` is available. Use `--no-ai` for deterministic fallback mode.
