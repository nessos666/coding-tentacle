# 🐙 Coding Tentacle v0.9.0

![Coding Tentacle Banner](https://raw.githubusercontent.com/nessos666/coding-tentacle/main/banner.png)

**Safety-First Guardian Layer for LLM-Based Code Fixing**

[![Status](https://img.shields.io/badge/status-research%20%2F%20shadow-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Tests](https://img.shields.io/badge/tests-10%2F10-brightgreen)]()

---

## What is Coding Tentacle?

Coding Tentacle does NOT try to replace coding agents like OpenCode, Codex, or Claude Code.

Instead, it **controls** them.

```
                    ┌─────────────────────────┐
                    │    Coding Tentacle       │
                    │    ┌───────────────────┐ │
  Bug Report ──────►│    │  Safety VETO 🛡️   │ │
                    │    │  SkepticBrain 🔍  │ │
                    │    │  ImpactAnalyzer 📊 │ │
                    │    │  Trust Calibration │ │
                    │    │  Learning Loop 🧠  │ │
                    │    └───────┬───────────┘ │
                    │            │             │
                    │    APPROVE / REJECT      │
                    │    / REQUEST_CHANGES     │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Fix Engines            │
                    │   ┌──────┐ ┌──────────┐ │
                    │   │OpenCode│ │ Ollama  │ │
                    │   │deepseek│ │granite  │ │
                    │   └───┬──┘ └────┬─────┘ │
                    │       │         │       │
                    │   Unified Diff Output   │
                    └─────────────────────────┘
```

---

## Architecture: Two Tentacles

```
┌───────────────────────────────────┐  ┌─────────────────────────────┐
│      TENTACLE A: ANALYZE          │  │     TENTACLE B: FIX         │
│      Safety + Learning            │  │     Code Generation         │
│                                   │  │                             │
│  ✅ Bug Classification (18 types) │  │  ✅ OpenCode (deepseek-v4)  │
│  ✅ Safety VETO (absolute block)  │  │  ✅ Ollama (granite3.2)     │
│  ✅ SkepticBrain (adversarial)    │  │  ✅ Template Fallback       │
│  ✅ ImpactAnalyzer                │  │                             │
│  ✅ Engine Router                 │  │  ❌ NO direct file access   │
│  ✅ Human Approval Gate           │  │  ❌ NO commits / PRs        │
│  ✅ BLM Learning Loop             │  │  ❌ NO safety bypass        │
│  ✅ Engine Trust Calibration      │  │                             │
│  ✅ Outcome Learning              │  │  Sandbox + TestRunner only  │
│                                   │  │                             │
│  CAN block any fix.               │  │  CANNOT act without A.      │
│  CAN learn from every run.        │  │  CAN be replaced/upgraded.  │
└───────────────────────────────────┘  └─────────────────────────────┘
              │                                      │
              └────────── A controls B ──────────────┘
```

---

## Learning Loop

```
  ┌──────────────────────────────────────────────────────────────┐
  │                     LEARNING FLOW                             │
  │                                                               │
  │  Run #1: Bug → CT → OpenCode → Fix → BLM stores experience   │
  │                                          ↓                    │
  │  Run #2: Bug → CT → BLM: "I've seen this!" → EnginePrompt    │
  │                     → "SIMILAR: NullPointer fixed by opencode"│
  │                     → OpenCode gets CONTEXT → BETTER fix      │
  │                                          ↓                    │
  │  Run #N: BLM: 500+ experiences                               │
  │          EngineLearning: trust=0.95 for opencode+NullPointer  │
  │          OutcomeLearning: "OpenCode excels at NullPointer"    │
  │          → Automatic routing to best engine                   │
  │          → Higher fix quality                                 │
  └──────────────────────────────────────────────────────────────┘
```

---

## ShadowMode Pipeline

```
  GitHub Issue
      │
      ▼
  ┌─────────────┐
  │ Classifier   │ ← UnifiedBugClassifier (18 types, 100% accuracy)
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │ SafetyBrain  │ ← VETO: DROP TABLE, eval(), system() → BLOCKED
  └──────┬──────┘         (Base64/HTML/string-concat decoded)
         │ GO
         ▼
  ┌─────────────┐
  │ EngineRouter │ ← OpenCode primary, Ollama fallback
  └──────┬──────┘    Bug-type-specific trust routing
         │
         ▼
  ┌─────────────┐
  │ OpenCode     │ ← Generates real code fix (unified diff)
  └──────┬──────┘    Template-fallback if engine unavailable
         │
         ▼
  ┌─────────────┐
  │ Safety scan  │ ← Scans ENGINE OUTPUT for dangerous patterns
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │ SkepticBrain │ ← "Why could this fix be WRONG?"
  └──────┬──────┘    risk_score + objections + recommendation
         │
         ▼
  ┌─────────────┐
  │ Sandbox      │ ← Isolated test environment
  └──────┬──────┘    Original files NEVER touched
         │
         ▼
  ┌─────────────┐
  │ TestRunner   │ ← pytest / shellcheck
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │ ApprovalGate │ ← APPROVE / REJECT / REQUEST_CHANGES
  └──────┬──────┘    Safety BLOCK can NEVER be overridden
         │
         ▼
  ┌─────────────┐
  │ BLM + EL     │ ← Store experience + update engine trust
  └─────────────┘
```

---

## Quick Start

```bash
# Clone
git clone https://github.com/nessos666/mmrp-research.git
cd mmrp-research

# Run a single bug through the full pipeline
python3 -c "
from coding_tentacle.orchestrator.shadow_mode import ShadowModeRunner, GitHubIssueRun
from coding_tentacle.orchestrator.metabrain import MetaBrain, SafetyBrain
from coding_tentacle.safety.inhibitory_control import InhibitoryControl
from coding_tentacle.knowledge.security_store import create_seed_security_store
from coding_tentacle.orchestrator.engine_router import EngineRouter
from coding_tentacle.orchestrator.skeptic_brain import SkepticBrain
from coding_tentacle.safety.approval_gate import ApprovalGate

sec = create_seed_security_store()
ic = InhibitoryControl(security_store=sec)
safety = SafetyBrain(ic=ic, security_store=sec)
mb = MetaBrain(safety=safety)
er = EngineRouter(); er.check_health()
sb = SkepticBrain(); ag = ApprovalGate()

runner = ShadowModeRunner(meta_brain=mb, engine_router=er,
                          approval_gate=ag, skeptic_brain=sb,
                          safety_brain=safety)

r = runner.analyze_issue(GitHubIssueRun(
    'https://github.com/user/repo', '#1',
    'NullPointer in views.py',
    'NoneType has no attribute at line 42'))

print(f'Bug Type: {r.detected_bug_type}')
print(f'Engine:   {r.engine_used}')
print(f'Diff:     {r.generated_diff[:200]}...')
print(f'Safety:   {\"BLOCKED\" if r.safety_events else \"OK\"}')
print(f'Skeptic:  risk={r.skeptic_risk:.2f} {r.skeptic_recommendation}')
print(f'Approval: {r.approval_status}')
"
```

---

## Requirements

- Python 3.10+
- OpenCode CLI (`opencode`) — for actual code fixing
- Ollama + granite3.2-vision — for local fallback
- No API keys required
- No cloud dependencies

---

## What CT Is Not

- ❌ Not a replacement for Codex, Devin, or Claude Code
- ❌ Not an autonomous bug fixer without an LLM engine
- ❌ Not a product — research/shadow release

## What CT Is

- ✅ Safety-first guardian layer for LLM-generated code
- ✅ Self-learning bug analysis system
- ✅ Engine router with trust calibration
- ✅ Human-in-the-loop approval gate
- ✅ The ONLY coding agent with Safety VETO + SkepticBrain + Bayesian Trust

---

## License

MIT — free, open source, no restrictions.

---

*Built by David + Hermes. June 2026.*
