# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Coding Tentacle, please report it via GitHub issue or contact the maintainer directly.

**Do NOT open a public issue for security vulnerabilities.** Instead, use the "Report a vulnerability" button on the Security tab.

## Safety VETO

Coding Tentacle's Safety VETO is the primary security mechanism. It:

1. Scans all bug reports for dangerous patterns (SQL injection, eval(), shell commands)
2. Scans all engine-generated diffs before they reach sandbox
3. Decodes Base64 and HTML entities to catch obfuscated patterns
4. BLOCKS execution of any dangerous code — no override possible

## Supported Versions

| Version | Supported |
|---------|-----------|
| v0.9.0  | ✅ Active (shadow release) |
| < v0.9.0 | ❌ No longer supported |

## Known Limitations

- Safety scanning is keyword-based with Base64/HTML decode
- Semantic analysis of code behavior is not implemented
- See SECURITY.md for full details
