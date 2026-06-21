# 🐙 Coding Tentacle v0.5.0

**Safety-First Bug Analysis & Patch Suggestion System**

Coding Tentacle analyzes bugs in your codebase using a tentacle architecture with a strict safety gate. It **proposes patches** but **never modifies files automatically**. Every dangerous action is BLOCKED before execution.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org)

---

## What Coding Tentacle IS

- ✅ A **bug analysis system** that reads code and identifies root causes
- ✅ A **patch suggestion engine** with multi-language templates (Python, Rust, Go, C++, Ruby, Shell)
- ✅ A **safety-gate** that BLOCKs dangerous operations (DROP TABLE, rm -rf, deploy, credential exposure)
- ✅ A **knowledge-based** system with 3 read-only stores (Bug Patterns, Security, Library APIs)
- ✅ A **project-aware** system with AST-based import/call graph analysis

## What Coding Tentacle is NOT

- ❌ An **auto-patching agent** — it will NOT modify your files
- ❌ A **replacement for Claude Code or Devin** — it prioritizes safety over autonomy
- ❌ A **shell executor** — it only analyzes and suggests

---

## Architecture

```
Bug Report + Stack Trace
    │
    ▼
┌──────────────┐
│ CodeContext  │ ← Extracts file, line, function
└──────┬───────┘
    │
    ▼
┌──────────────┐
│ BQ Grounding │ ← Symbol meaning (87% NullPointer, 97% TypeError accuracy)
└──────┬───────┘
    │
    ▼
┌──────────────┐
│ BR Scientific│ ← Hypothesis generation (4 templates per bug type)
└──────┬───────┘
    │
    ▼
┌──────────────┐     ┌─────────────────┐
│ Knowledge    │ ←── │ Bug Pattern Store│ (50 entries)
│ Stores       │ ←── │ Security Store   │ (10 CWE patterns)
│              │ ←── │ Library Store    │ (50 entries)
└──────┬───────┘     └─────────────────┘
    │
    ▼
┌──────────────┐
│ Patch        │ ← Multi-language templates (Python, Rust, Go, C++, Ruby, Shell)
│ Suggestion   │
└──────┬───────┘
    │
    ▼
┌──────────────┐
│ IC/EL Safety │ ← **HARD GATE** — BLOCKs dangerous patterns
│ Gate         │    ESCALATEs complex cases
└──────┬───────┘    GO only for safe, simple, tested patches
    │
    ▼
┌──────────────┐
│ Output       │ ← Patch suggestion + Safety decision + Project context
└──────────────┘
```

---

## Safety Guarantees

Coding Tentacle will **NEVER**:

- 🔴 Modify files directly (no write access to project files)
- 🔴 Execute `DROP TABLE`, `DELETE FROM`, or similar destructive SQL
- 🔴 Run `rm -rf`, `systemctl restart`, or `kubectl apply`
- 🔴 Deploy to production or execute infrastructure changes
- 🔴 Expose credentials (`API_KEY`, `SECRET`, `password`)
- 🔴 Access `~/.ssh`, `/etc/passwd`, `/etc/shadow`

All stores are **read-only** — `actions_executed = 0`.

---

## Quickstart

```bash
# Install
git clone https://github.com/your-org/coding-tentacle.git
cd coding-tentacle
pip install -e .

# Quick test
python examples/example_nullpointer.py

# Expected output:
# BUG REPORT: "NullPointerException in payment.py:42"
# GROUNDING:  NullPointer (confidence: 0.35)
# PATCH:      guard_clause: if self.field is not None: ...
# SAFETY:     GO — safe analysis

# Full regression
python scripts/full_regression.py
# ✅ RC2 ALL TESTS PASSED
```

---

## Project Structure

```
src/coding_tentacle/
├── brains/sg_brain.py              # BQ Symbol Grounding
├── reasoning/br_scientific_method.py # BR Scientific Method
├── safety/
│   ├── inhibitory_control.py       # IC Safety Gate (BLOCK/ESCALATE/GO)
│   └── escalation_logic.py         # EL Routing
├── knowledge/
│   ├── bug_pattern_store.py         # 50 bug patterns
│   ├── security_store.py            # 10 security patterns (CWE)
│   ├── library_store.py             # 50 library patterns
│   └── project_map.py               # AST-based import/call graph
├── patch/patch_suggestion.py        # Multi-language templates
├── tentacles/mini_tentacle_system.py # 4-tentacle pipeline
└── orchestrator/minimal_orchestrator.py
examples/example_nullpointer.py
scripts/full_regression.py
```

---

## Benchmark Status (100 Real-World Bugs)

| Bug Type | Score |
|----------|-------|
| NullPointer | 0.87 ✅ |
| TypeError | 0.97 ✅ |
| AttributeError | 0.68 ✅ |
| Logic | 0.55 ⚠️ |
| Security | 0.49 ⚠️ (blocks correctly, scoring artifact) |
| **Overall** | **0.70** |

---

## Known Limitations

- Currently proposes patches but does NOT automatically modify project files
- Logic/algorithm bugs score 0.55 (templates are generic)
- No container/sandbox isolation for test execution
- No CI/CD integration
- ProjectMap enrichment visible in 20% of cases (path resolution WIP)

---

## Roadmap

| Version | Feature | Status |
|---------|---------|--------|
| v0.5.0 | Safety-first release | ✅ Current |
| v0.6.0 | Atomic Diff Generator | 🔵 Next |
| v0.6.1 | Sandbox + Test Runner | 🔵 Planned |
| v0.6.2 | Quality-Gate Loop | 🔵 Planned |
| v0.7.0 | Full Repair Loop with Human Gate | ⚪ Research |
| v1.0.0 | Production-ready safety gate for enterprises | ⚪ Future |

---

## License

MIT — See [LICENSE](LICENSE)

## Authors

**Hermes + David** — Coding Tentacle 2026

*"Analyze first. Suggest second. NEVER execute without human consent."*
