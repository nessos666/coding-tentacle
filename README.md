# 🐙 Coding Tentacle v0.7.0

**Safety-First Multi-Language Bug Analysis & Patch Suggestion System**
*8 Sprachen | 78+ Bug-Typen | 41+ Procedures | 40+ Module | 8.000+ LOC*

Coding Tentacle analyzes bugs using a tentacle architecture with a strict safety gate. It **proposes patches**, **sandbox-tests them**, but **NEVER modifies files without human approval**. Every dangerous action is BLOCKED.

---

## What It Does

```
✅ Classifies 13+ bug types (NullPointer, TypeError, ImportError, ...)
✅ Generates unified diffs (6 languages: Py/Rust/Go/C++/Ruby/Shell)
✅ Sandbox-tests patches in isolated temp directories
✅ Learns from every fix (11 learning bridges: WM→BLM→Rules→Skills→Procedures)
✅ Safety VETO blocks dangerous patterns (DROP TABLE, eval(), rm -rf, API_KEY)
✅ Octopus architecture: 4 MetaBrains + Dynamic Tentacle Activation
✅ Shadow Mode: analyze GitHub issues without touching originals
✅ Parallel tentacle execution (Codex-inspired, Safety-first)
```

## What It Does NOT Do

```
❌ NO auto-apply patches to real files
❌ NO git commit/push/PR without human approval  
❌ NO shell execution without Safety VETO
❌ NOT a replacement for Devin or Codex
❌ NOT an autonomous agent (yet — architecture supports it)
```

## Supported Languages

```
Python  █████ 5/5  13 Bug-Typen  10 Procedures
Shell   █████ 5/5  12 SC-Rules   8 Procedures
Rust    ████░ 4/5  7 Bug-Typen   2 Procedures
Ruby    ████░ 4/5  9 Bug-Typen   4 Procedures
C++     ████░ 4/5  9 Bug-Typen   5 Procedures
Go      ████░ 4/5  9 Bug-Typen   4 Procedures
JS/TS   ████░ 4/5  10 Bug-Typen  4 Procedures
Java    ████░ 4/5  9 Bug-Typen   4 Procedures
```

## Quickstart

```bash
cd GEHIRN_BIBLIOTHEK
pip install -e .

# Demo (5 curated issues, SHADOW MODE only)
python scripts/public_demo.py

# Regression
python scripts/full_regression.py

# Integration test (10 pipeline cases)
python scripts/integration_test.py
```

## Architecture (RC16)

```
MetaBrain (4 Sub-Brains)
  ├── Safety Brain   (VETO — blocks dangerous ops)
  ├── Teacher Brain  (analyzes, plans)
  ├── Planning Brain (selects procedures & skills)
  └── Learning Brain (collects feedback)

Pipeline:
  Issue → MetaBrain → Teacher → DiffGenerator → Sandbox → TestRunner → HumanGate
  
11 Learning Bridges (all active):
  WM→BLM→EC→RuleMemory→ProceduralMemory→SkillStore→Teacher
```

## Safety Guarantees

```
DROP TABLE        → BLOCK (Safety VETO)
eval(user_input)  → BLOCK  
API_KEY='***'     → BLOCK
os.system(...)    → BLOCK
rm -rf /          → BLOCK
guard_clause      → GO (after Safety check)
```

## Honest Limitations

```
⚠️  Classifier: keyword-based (13 types, ~80% accuracy)
⚠️  No real GitHub cloning (simulated in Shadow Mode)
⚠️  No Docker/SWE-bench integration yet
⚠️  Public demo uses curated examples — real-world accuracy varies
```

## License

MIT — Copyright (c) 2026 Coding Tentacle
