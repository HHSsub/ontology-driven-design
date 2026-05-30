# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | ✅ Yes    |

## Reporting a Vulnerability

If you discover a security issue in ODD — particularly in hook scripts that execute Python code or interact with the filesystem — please report it privately:

**Email:** hhoesun@gmail.com  
**Subject:** `[ODD Security] <brief description>`

Please include:
- A description of the vulnerability
- Steps to reproduce
- Potential impact

Do **not** open a public GitHub issue for security vulnerabilities.

## Scope

ODD hooks run as Python subprocesses triggered by Claude Code's hook system. Security considerations include:

- Hook scripts read/write only to paths explicitly referenced in code
- No network requests are made by any hook (except websearch_yearguard which reads stdin)
- violation_registry.json is read-only at hook runtime
- No credentials or secrets are accessed by any hook
