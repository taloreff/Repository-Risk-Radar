# Repo Risk Radar Engineering Rules

## Scope

These rules apply across the monorepo:

- `apps/client`: Next.js frontend.
- `apps/server`: NestJS API wrapper.
- `apps/agent`: Python dependency scanner and OpenAI narrative layer.

## Code Quality

- Prefer small files, small functions, and clear names.
- Do not create huge components or broad "god" modules.
- Separate business logic from UI rendering.
- Keep reusable formatting, mapping, and policy logic in utilities or services.
- Use typed models/interfaces for API payloads and shared contracts.
- Add tests for deterministic logic, especially scoring, policy, parsing, and validation.
- Run lint, tests, and builds after changes when commands exist.
- Ask before adding new production dependencies.

## Security And Public Website Constraints

- Never expose API keys to the frontend.
- Do not commit secrets, `.env`, tokens, generated credentials, or private scan output.
- Only analyze public GitHub repositories.
- Never execute arbitrary repository code.
- Never generate exploit code, attack payloads, or offensive instructions.
- Keep Nmap/OpenVAS-style scanning opt-in and only for assets the user owns or has permission to test.
- Handle external API failures gracefully and avoid leaking internal errors or secrets.

## Agent And Release Gate Boundaries

- Keep deterministic scan/security logic separate from OpenAI narrative generation.
- Deterministic services fetch, parse, enrich, score, and make release-gate decisions first.
- OpenAI may explain, prioritize, summarize, and format remediation text only from structured data.
- OpenAI must not invent CVEs, package versions, fixed versions, evidence, or security facts.
- Release gate `PASS`/`WARN`/`BLOCK` decisions must come from deterministic policy rules before AI explanation.

## Development Workflow

- Preserve existing behavior unless the task explicitly asks for behavior changes.
- Keep API contracts stable unless a contract change is necessary and documented.
- Prefer focused refactors over broad rewrites.
- Do not edit generated build output in `dist` directly.
- Do not modify unrelated user changes or revert work you did not make.
