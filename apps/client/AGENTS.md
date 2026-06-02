# Frontend Engineering Rules

## Component Boundaries

- Components should ideally stay under about 100 lines.
- Keep one React component per file; the exported component name should match the filename.
- Move secondary UI pieces into their own component files and move non-UI helpers into utilities.
- Split large dashboard components into presentational sections.
- Prefer feature folders such as `src/features/scan-results`.
- Use typed props for every exported component.
- Keep API calls in services or hooks, not inside large UI components.

## Scan Results UI

- Prefer named sections such as `ReleaseGateCard`, `RiskMetricsGrid`, `ExploitabilityMap`, `PrioritizedFindingsTable`, `CveIntelligencePanel`, and `RemediationBriefCard`.
- Extract mapping, formatting, severity, risk-color, and chart data logic into utilities.
- Avoid duplicated Tailwind/className strings when a small component would be clearer.
- Preserve the current cyber/intelligence cockpit visual style.
- Do not change API payload shapes from the frontend.

## Safety

- Never expose server-only environment variables or API keys.
- Keep public-site messaging defensive and remediation-focused.
- Do not add frontend dependencies without asking first unless the user explicitly requested them.
