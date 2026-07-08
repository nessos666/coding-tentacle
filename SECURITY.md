# Security Policy — Coding Tentacle

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 11.0.x  | ✅ Active support  |
| < 11.0  | ❌ End of life     |

## Safety Guarantees

Coding Tentacle is a **read-only safety layer**. It NEVER:

- Modifies files on disk
- Executes code outside sandbox (`/tmp/ct_sandbox_*`)
- Pushes, commits, or creates PRs
- Auto-applies patches without human approval

## Reporting a Vulnerability

Email: `nessos6666@gmail.com`

PGP: Not yet configured. Will be added.

Response time: 48 hours.

## Security Architecture

CT employs 5 defense layers:

1. **TrojanSourceScanner** — Detects Unicode Bidi, homoglyph, and zero-width attacks
2. **ASTSecurityAnalyzer** — Structural Python code analysis (eval, exec, dangerous imports)
3. **SecurityStore** — 10 CWE-mapped detection patterns (SQL injection, XSS, path traversal)
4. **InhibitoryControl** — 5-level safety gate: GO / HOLD / BLOCK / ESCALATE / ASK_CONTEXT
5. **ApprovalGate** — Human-in-the-loop final authorization

**Absolute VETO:** SafetyBrain BLOCK can NEVER be overridden by any other component.

## Known Limitations

- AST scan is Python-only (3.10+)
- No runtime sandbox escape detection (relies on OS process isolation)
- Droste code graph may be stale if not re-indexed after structural changes

## Responsible Disclosure

We follow the [Contributor Covenant](CODE_OF_CONDUCT.md). Please do NOT open public issues for security vulnerabilities.
