# Contributing

## Development principles

Keep the product small, deterministic, secure, and inexpensive to operate.

Do not add Kafka, Kubernetes, Redis, graph databases, ML, or additional services unless a measured production bottleneck justifies the change.

## API rules

- All public endpoints use `/v1`.
- Validate all external input with typed Pydantic models.
- Never trust client-side subscription or usage state.
- Never expose provider credentials or internal infrastructure details.
- Expensive external calls require bounded timeouts and bounded retries.
- Security-sensitive behavior requires regression coverage.

## Risk-result rules

A missing intelligence record is not evidence of safety. Use explicit states such as `NO_KNOWN_RISK` and `INSUFFICIENT_DATA`.

Every risk result should remain reproducible through an engine version and its evidence/findings.

## Pull requests

PRs should explain the user problem, security impact, performance impact, and test coverage. Keep changes narrowly scoped.
