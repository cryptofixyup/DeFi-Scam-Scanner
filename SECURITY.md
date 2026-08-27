# Security Policy

## Supported Versions

Security fixes target the default branch and the latest released version.

## Reporting a Vulnerability

Do not open a public issue for a security vulnerability.

Report privately through the repository's GitHub Security Advisories feature when available. Include:

- affected component and version/commit
- reproduction steps or proof of concept
- security impact
- suggested mitigation, when known

Do not include secrets, private keys, seed phrases, credentials, or real user data in a report.

## Security Rules

- Never submit private keys, seed phrases, API keys, database credentials, or payment credentials to this repository.
- Never embed backend secrets or blockchain RPC credentials in the Android application.
- Server-side entitlement checks are authoritative.
- Risk results must distinguish `NO_KNOWN_RISK` from `INSUFFICIENT_DATA`.
- Security fixes must include regression tests where practical.
