# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| latest  | Yes                |

## Reporting a Vulnerability

If you discover a security vulnerability in Jarvis Orb, please report it responsibly.

**Do not open a public issue for security vulnerabilities.**

Instead, please email: **security@thestack.ai**

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## Response Timeline

- **Acknowledgment:** within 48 hours
- **Assessment:** within 7 days
- **Fix release:** as soon as practical, depending on severity

## Scope

Jarvis Orb runs entirely local. The brain database (`~/.jarvis-orb/brain.db`) and WebSocket communication (`localhost:9321`) are local-only by design. Security concerns we take seriously include:

- **SQLite injection** via FTS5 search queries (mitigated with input sanitization)
- **File permission** issues on the brain directory (enforced as `0700`)
- **Dependency vulnerabilities** in Python or Tauri/Rust packages
- **WebSocket** unauthorized access from non-local origins

## Security Design

- All data stays on your machine. Zero cloud dependencies.
- Brain directory permissions are restricted to owner-only (`0700`).
- FTS5 queries are sanitized to prevent injection.
- Database queries use parameterized statements exclusively.
