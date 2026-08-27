# Crypto Safety Scanner

Android-first crypto wallet/token risk scanner.

## Current release foundation

- FastAPI authentication with Argon2 password hashing
- Short-lived JWT access tokens
- PostgreSQL users, plans, subscriptions and atomic daily usage counters
- Server-side Free/Pro entitlement enforcement
- EN / PL / DE localization foundation
- Secure Android token storage dependency
- Non-root backend container
- CI dependency security gate

## Plans

| Plan | Price | Daily | Monthly |
|---|---:|---:|---:|
| Free | EUR 0 | 10 | 300 |
| Pro | EUR 9.99 | 50 | 500 |

## Local backend

1. Create `backend/.env` from `backend/.env.example`.
2. Start PostgreSQL.
3. Apply `backend/schema.sql`.
4. Install `backend/requirements.txt`.
5. Run:

```bash
uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

The scan endpoint currently returns a readiness response until the real risk engine is connected. It deliberately does not fabricate a safety score.

## Security boundary

The Android client never decides plan access. The API authenticates the user and enforces scan limits transactionally before expensive scan work. Payment integration should subsequently verify Google Play purchases server-side before changing a subscription to Pro.

## Localization

Supported locales:

- English (`en`)
- Polish (`pl`)
- German (`de`)
