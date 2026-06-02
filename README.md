# Repo Risk Radar

Repo Risk Radar is a defensive fullstack dependency-risk scanner for public GitHub repositories. The monorepo contains:

- `apps/client`: Next.js, React, Tailwind, shadcn-style components, and a 21st.dev-inspired agent input surface.
- `apps/server`: NestJS API that runs the Python agent and returns structured scan JSON.
- `apps/agent`: Python OpenAI Agents SDK scanner that fetches manifests, checks OSV.dev, enriches CVEs with NVD and EPSS, ranks risk, and writes reports.

The project is defensive only. It focuses on vulnerability awareness, prioritization, and remediation. It does not generate exploit code, attack payloads, or offensive instructions.

## What It Does

1. The user pastes a public GitHub repo URL into the web app.
2. The NestJS server calls the Python agent.
3. The agent downloads only supported dependency manifests.
4. Dependencies with exact versions are matched against OSV.dev.
5. CVE aliases are enriched with NVD data and FIRST EPSS probability data.
6. Findings are ranked with CVSS, severity, EPSS, CISA KEV, dependency directness, and fix availability.
7. A deterministic AI Release Gate returns `PASS`, `WARN`, or `BLOCK` for production release readiness.
8. The client displays a dark dashboard with scan coverage, CVEs, CVSS, EPSS, risk scores, release gate evidence, and remediation steps.

## AI Release Gate

The AI Release Gate answers: "Can this repository be safely released to production today?"

The decision is deterministic. The Python policy engine returns:

- `BLOCK` for known exploited vulnerabilities, critical direct dependencies with fixes, direct CVSS >= 9.0 findings, overall risk score >= 85, or more than two critical findings.
- `WARN` for high severity findings, critical findings without fixes, overall risk score from 50 to 84, multiple medium runtime findings, or incomplete enrichment for important findings.
- `PASS` when no high/critical/KEV findings exist and overall risk is below 50.

OpenAI is used only to explain the already-computed decision, create a developer-friendly fix plan, and format a developer ticket. It must not override the deterministic decision, invent vulnerabilities, invent CVEs, invent fixed versions, or provide offensive instructions. If `OPENAI_API_KEY` is missing or AI is disabled, the gate uses deterministic fallback text and a deterministic developer ticket.

Public website safety constraints:

- Only public GitHub repository URLs are analyzed.
- Repository code is not executed.
- API keys stay server-side and must never be exposed to the frontend.
- Reports and logs must not include secrets.
- The feature is defensive and remediation-focused only.
- OpenAI calls are skipped when AI is disabled or when there are no findings.

## Setup

```bash
npm install
python -m venv .venv
source .venv/bin/activate
python -m pip install -e "apps/agent[dev]"
cp .env.example .env
```

Optional environment variables:

```bash
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
GITHUB_TOKEN=
NVD_API_KEY=
NEXT_PUBLIC_API_BASE_URL=http://localhost:4000/api
PORT=4000
SCAN_CACHE_TTL_SECONDS=900
```

`GITHUB_TOKEN` and `NVD_API_KEY` are optional but help with public API rate limits. If `OPENAI_API_KEY` is missing, the agent automatically produces a deterministic report.

Without `GITHUB_TOKEN`, GitHub public API calls are limited heavily per IP address. Create a fine-grained or classic GitHub personal access token with public repository read access, put it in the root `.env`, then restart the server:

```bash
GITHUB_TOKEN=github_pat_...
```

The NestJS server also caches successful scans for `SCAN_CACHE_TTL_SECONDS` so repeated scans of the same repo do not keep spending GitHub API quota.

## Run The Fullstack App

```bash
npm run dev
```

Or run apps separately:

```bash
npm run dev --workspace @repo-risk-radar/server
npm run dev --workspace @repo-risk-radar/client -- --port 3000
```

Open [http://localhost:3000](http://localhost:3000). The API runs at [http://localhost:4000/api](http://localhost:4000/api).

## Agent CLI

```bash
cd apps/agent
../../.venv/bin/python -m repo_risk_radar analyze https://github.com/owner/repo
../../.venv/bin/python -m repo_risk_radar analyze https://github.com/owner/repo/tree/branch-name --json
../../.venv/bin/python -m repo_risk_radar analyze https://github.com/owner/repo --release-gate
../../.venv/bin/python -m repo_risk_radar analyze https://github.com/owner/repo --ticket
../../.venv/bin/python -m repo_risk_radar analyze https://github.com/owner/repo --output ../../reports/example.md
../../.venv/bin/python -m repo_risk_radar self-test
```

## API

```bash
curl -X POST http://localhost:4000/api/scans \
  -H 'Content-Type: application/json' \
  -d '{"repoUrl":"https://github.com/owner/repo","noAi":true}'
```

The scan response includes `findings`, `narrative`, and `release_gate`. `release_gate` contains the deterministic decision, risk score, reasons, required actions, unknowns, pass conditions, evidence, and a developer ticket.

Demo dashboard data is available without external API calls:

```bash
curl http://localhost:4000/api/scans/demo
```

## Confidence Checks

```bash
npm run build
npm run lint --workspace @repo-risk-radar/client
npm run lint --workspace @repo-risk-radar/server
cd apps/agent && ../../.venv/bin/python -m ruff check . && ../../.venv/bin/python -m pytest
cd apps/agent && ../../.venv/bin/python -m repo_risk_radar self-test
npm audit --omit=dev
```

Normal scans include coverage lines like:

```text
OSV checked: 21/110 dependencies with exact versions
Skipped without exact versions: 89
```

OSV version matching requires exact resolved versions. Lockfiles and pinned requirements create stronger scans than broad ranges such as `^1.2.3` or `>=2.0`.

## About Nmap And OpenVAS

Nmap and OpenVAS are useful defensive tools for network and host exposure assessment, but they are not a natural default for public repository dependency analysis. They should only be run against assets the user owns or has explicit permission to test. This app keeps dependency-risk scanning as the default path and leaves Nmap/OpenVAS as future opt-in integrations for owned infrastructure.

## Roadmap

1. Persist scan history and compare drift over time.
2. Add authenticated GitHub token setup in the UI.
3. Add Trivy or Grype as an optional local open-source dependency/container scanner.
4. Add opt-in OpenVAS/Nmap jobs for owned targets only.
5. Add PDF export and GitHub issue generation.
