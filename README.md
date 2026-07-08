<p align="center">
  <img src="ct-logo.png" width="180" alt="Coding Tentacle">
  <img src="https://img.shields.io/badge/%2B-FUSION-orange?style=for-the-badge&logoWidth=30" alt="+">
  <a href="https://github.com/nessos666/droste-memory"><img src="https://img.shields.io/badge/DROSTE-v1.1.6-purple?style=for-the-badge" alt="Droste"></a>
</p>

<h1 align="center">Coding Tentacle 11</h1>
<p align="center"><strong>Secure Self-Learning Repair Agent — Droste Fusion</strong></p>

<p align="center">
  <img src="https://img.shields.io/badge/version-11.0.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/tests-14%2F14-brightgreen" alt="Tests">
  <img src="https://img.shields.io/badge/regression-10%2F10-brightgreen" alt="Regression">
  <img src="https://img.shields.io/badge/droste-v1.1.6-purple" alt="Droste">
  <a href="https://github.com/nessos666/droste-memory"><img src="https://img.shields.io/badge/Droste_Repo-→-lightgrey" alt="Droste Repo"></a>
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
</p>

---

CT sits **between you and the LLM**. OpenCode, Claude Code, and Codex generate code brilliantly — but with **zero safety guarantees**. They can emit `eval(user_input)`, `DROP TABLE`, or `rm -rf /` without hesitation. **CT is the safety layer that controls them.**

```
Bug → CT (classify → security scan → route → Droste context)
    → OpenCode/Claude/Ollama (generates fix)
    → CT (safety review → skeptic → impact → approval → REFLECTION)
    → Human approves → Fix applied → BLM learns WHY
```

## CT + Droste Fusion

CT uses **[Droste](https://github.com/nessos666/droste-memory)** — a causal code graph engine — to give every fix engine structural context. Instead of blind grep, the LLM sees which functions are **causally connected** to the bug.

```
CODING TENTACLE                    DROSTE v1.1.6
━━━━━━━━━━━━━━━━━         ┏━━━━━━━━━━━━━━━━━━━━━━━┓
Classifier (18 types)     ┃ 4.187 symbols          ┃
SecurityBrain (VETO)      ┃ 4.697 causal edges     ┃
EngineRouter (4 engines)  ┃ 98% budget efficiency  ┃
ReflectionEngine          ┃ "Which functions are   ┃
BLM + EngineLearning      ┃  causally connected?"  ┃
━━━━━━━━━━━━━━━━━         ┗━━━━━━━━━━━━━━━━━━━━━━━┛
         │                          │
         └──────── FUSION ──────────┘
                   │
         Causal Code Context in Engine Prompt
```

## Quick Start

```bash
git clone https://github.com/nessos666/coding-tentacle.git
cd coding-tentacle
pip install -e .
ct version
ct repair --title "NullPointer in payment.py" --body "NoneType has no attribute"
```

## Benchmark

| System | Score |
|--------|:-----:|
| **CT+OpenCode+Droste** | **9/10 (90%)** |
| Baseline (grep-only) | 3/10 (30%) |
| Security blocks | 2 (eval, API key) |

## Learning System V2

```
Run 1: Bug → Fix → REFLECTION: "Why did this work?"
Run 2: Bug → BLM: "I've seen this!" → LEARNED LESSONS enrich prompt
Run N: 92 experiences, 23 REFLECTION entries, trust calibrated
```

## Pipeline

```
BUG → Classifier → SecurityBrain(VETO) → REFLECTION RETRIEVAL
    → Droste Context → EngineRouter → OpenCode/Claude
    → Safety Scan → ImpactAnalyzer → SkepticBrain
    → Sandbox → Approval → BLM → REFLECTION ENGINE → Consolidator
```

## Engines

| Engine | Status | Type |
|--------|:------:|------|
| OpenCode (deepseek-v4) | Primary | Local, free |
| Claude Code (2.1.86) | Active | Top-tier |
| Ollama (granite3.2) | Fallback | Offline |
| Codex (GPT-5.x) | Disabled | API required |

## Requirements

Python 3.10+ • [Droste v1.1.6](https://github.com/nessos666/droste-memory) • OpenCode CLI • No API keys • No cloud

## Status

| Metric | Value |
|--------|------:|
| Modules | 27 production |
| LOC | 8.405 |
| Archived | 34 |
| Regression | 10/10 |
| pytest | 14/14 |
| Checkpoints | 28 |

## License

MIT — Built by David + Hermes. 2026.