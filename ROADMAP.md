# Production MVP Roadmap

## P0 — Release blocker

- [ ] Complete Android onboarding in EN/PL/DE.
- [ ] Complete authentication and refresh-token lifecycle.
- [ ] Enforce Free/Pro quotas server-side with atomic usage reservation.
- [ ] Add Google Play subscription verification on the server.
- [ ] Connect the real EVM wallet risk engine.
- [ ] Add strict wallet/token validation and `INSUFFICIENT_DATA` handling.
- [ ] Add request IDs, bounded external-call timeouts, and structured errors.
- [ ] Add regression tests for authentication, authorization, and entitlement bypasses.

## P1 — Public beta

- [ ] Add scan analytics: install, onboarding completion, first scan, repeat scan, limit reached, checkout, paid.
- [ ] Add scan history.
- [ ] Add lightweight abuse/rate limiting.
- [ ] Add production health/readiness checks and minimal metrics.
- [ ] Add curated scam intelligence import workflow.
- [ ] Publish Android closed beta.

## P2 — Growth

- [ ] Telegram scanner using the same API.
- [ ] Referral/share-scan flow.
- [ ] SEO landing pages for high-intent scanner searches.
- [ ] Pro conversion experiments based on real usage data.

## Architecture guardrail

Do not add distributed infrastructure merely for completeness. Introduce Kafka, Redis, Kubernetes, graph databases, ML, or additional services only after measured user volume or a concrete production requirement justifies them.
