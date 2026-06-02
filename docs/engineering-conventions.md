# Engineering Conventions

## Architecture Overview

Repo Risk Radar is a monorepo with three application layers:

- `apps/client`: Next.js UI for repository scans and release-gate results.
- `apps/server`: NestJS API that validates scan requests and invokes the Python agent.
- `apps/agent`: Python scanner that fetches public GitHub manifests, checks OSV, enriches CVEs with NVD/EPSS, ranks findings, evaluates release policy, and optionally asks OpenAI to explain structured results.

The Python agent is the source of truth for dependency/security facts. The server is a process/API boundary. The client renders typed payloads and should not reimplement security policy.

## Folder And Module Boundaries

- `apps/client/src/components/ui`: generic reusable UI primitives.
- `apps/client/src/features/*`: feature-specific sections, utilities, hooks, and types.
- `apps/client/src/lib`: shared client services and low-level helpers.
- `apps/server/src/modules`: NestJS controllers, DTOs, and services.
- `apps/agent/src/repo_risk_radar/services`: external API clients.
- `apps/agent/src/repo_risk_radar/analyzers`: deterministic parsing and scoring.
- `apps/agent/src/repo_risk_radar/release_policy.py`: deterministic release-gate policy.
- `apps/agent/src/repo_risk_radar/agent.py`: OpenAI explanation and narrative formatting.

## Frontend Component Conventions

- Keep components ideally under about 100 lines.
- Keep one React component per file, and match the exported component name to the filename.
- Move secondary UI pieces into their own component files and non-UI helpers into utilities.
- Prefer presentational sections with typed props.
- Keep scan/result API calls in services or hooks.
- Extract chart data mapping, risk colors, severity labels, and formatting into utilities.
- Avoid repeating long Tailwind strings when a component or helper would make intent clearer.
- Preserve responsive behavior and existing visual style during refactors.

Suggested scan-results structure:

```text
apps/client/src/features/scan-results/
  components/
  hooks/
  types/
  utils/
```

## Backend And Service Conventions

- Controllers should stay thin.
- Services should own process execution, caching, and integration details.
- DTOs should validate public inputs.
- API errors should be user-safe and must not leak secrets, stack traces, or filesystem details.
- The server should not duplicate release-gate policy that already lives in the agent.

## AI Agent Conventions

- Deterministic code fetches, parses, enriches, scores, and decides release gates first.
- OpenAI only explains structured scan data and deterministic policy outputs.
- AI must not invent CVEs, packages, fixed versions, evidence, or release decisions.
- AI output should include unknowns when data is incomplete.
- All AI behavior must remain defensive and remediation-focused.

## Testing Expectations

- Add unit tests for deterministic logic.
- Do not call OpenAI or external networks from unit tests.
- Run available checks after changes:

```bash
npm run lint
npm run build
cd apps/agent && ../../.venv/bin/python -m ruff check .
cd apps/agent && ../../.venv/bin/python -m pytest
npm audit --omit=dev
```

## Security And Public Website Constraints

- Analyze public GitHub repositories only.
- Never execute arbitrary repository code.
- Never expose API keys to the frontend.
- Never commit `.env`, secrets, tokens, or private scan output.
- Never generate exploit code, attack payloads, or offensive instructions.
- Keep Nmap/OpenVAS-style scanning opt-in and limited to assets the user owns or has permission to test.

## Code Review Checklist

- Are files and functions small enough to understand quickly?
- Is business/security logic separated from UI?
- Are API payloads typed?
- Are deterministic security decisions outside OpenAI prompts?
- Are failures handled safely without leaking secrets?
- Are formatter/mapping/style utilities reused rather than duplicated?
- Were relevant lint, build, and tests run?
