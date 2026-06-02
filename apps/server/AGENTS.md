# Backend Engineering Rules

## API Boundaries

- Controllers should stay thin and delegate work to services.
- Keep API integrations and process execution in services.
- Validate request inputs before doing work.
- Preserve API response contracts unless a contract change is necessary and documented.

## Error Handling

- Handle GitHub, OSV, NVD, EPSS, Python process, and timeout failures gracefully.
- Never leak internal stack traces, filesystem details, tokens, or secrets to clients.
- Keep cache behavior explicit and safe for public scan requests.

## Security Logic

- Keep release policy deterministic and testable in the Python agent layer.
- The server should act as a boundary around the agent, not duplicate security decisions.
- Do not execute arbitrary repository code.
