<p align="center">
  <img src="https://raw.githubusercontent.com/nessos666/coding-tentacle/main/ct-logo.png" width="500" alt="Coding Tentacle v11"><br>
  <h1 align="center">🦑 Coding Tentacle 11</h1>
  <p align="center"><strong>Secure Self-Learning Repair Agent</strong></p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-11.0.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/tests-14%2F14-brightgreen" alt="Tests">
  <img src="https://img.shields.io/badge/regression-10%2F10-brightgreen" alt="Regression">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
</p>

---

CT sits **between you and the LLM**. OpenCode, Claude Code, and Codex generate code brilliantly — but with **zero safety guarantees**. They can emit `eval(user_input)`, `DROP TABLE`, or `rm -rf /` without hesitation. **CT is the safety layer that controls them.**

```
Bug -> CT (classify -> security scan -> route -> Droste context)
    -> OpenCode/Claude/Ollama (generates fix)
    -> CT (safety review -> skeptic -> impact -> approval -> REFLECTION)
    -> Human approves -> Fix applied -> BLM learns WHY
```

## Architecture: CT + Droste Fusion

```
CODING TENTACLE
  Classifier(18 types) | SecurityBrain | MetaBrain | EngineRouter
  ImpactAnalyzer | SkepticBrain | ApprovalGate | Sandbox
  BLM | EngineLearning | REFLECTION ENGINE | Decision Trace

  DROSTE FUSION (v1.1.6)
    Causal Code Graph -> Engine Prompt
    4.187 symbols, 4.697 edges, 98% budget efficiency
    "Which functions are causally connected to this bug?"

  ENGINES: OpenCode(deepseek-v4) | Claude Code(2.1.86) | Ollama(granite3.2)
```

## Quick Start

```bash
git clone https://github.com/nessos666/coding-tentacle.git
cd coding-tentacle
pip install -e .

# CLI
ct version
ct repair --title "NullPointer in payment.py" --body "NoneType has no attribute"
```

## Benchmark

```
CT v11.0.0 + OpenCode + Droste + Reflection
CT+OpenCode:  9/10 (90%)
Baseline:     3/10 (30%)
Delta:        +6 bugs
Security:     2 blocks (eval, API key) — Baseline "fixed" unsafely
```

## Learning System V2

CT doesn't just store experiences. It **understands WHY**:

```
Run 1: Bug -> Fix -> REFLECTION: "Why did this work? Droste helpful? Root cause correct?"
Run 2: Bug -> BLM: "I've seen this!" -> LEARNED LESSONS enrich prompt -> BETTER fix
Run N: 92 experiences, 23 REFLECTION entries, trust calibrated, rules consolidated
```

## Pipeline (16 Steps)

```
BUG -> Classifier -> SecurityBrain(VETO) -> REFLECTION RETRIEVAL ->
Droste Context -> EngineRouter -> OpenCode/Claude -> Safety Scan ->
ImpactAnalyzer -> SkepticBrain -> Sandbox -> Approval ->
BLM Record -> REFLECTION ENGINE -> Consolidator -> Recommendation
```

## Engines

| Engine | Status | Notes |
|--------|:------:|-------|
| OpenCode (deepseek-v4) | Primary | Local, free |
| Claude Code (2.1.86) | Active | Top-tier |
| Ollama (granite3.2) | Fallback | Offline |
| Codex (GPT-5.x) | Disabled | Needs API key |

## Requirements

Python 3.10+ | Droste v1.1.6 (auto-init) | OpenCode CLI | No API keys | No cloud

## Project Status

27 modules (8.405 LOC) | 34 archived | 10/10 Regression | 14/14 pytest | 28 Checkpoints | Tag: v11.0.0

## License

MIT — free, open source, no restrictions. Built by David + Hermes. June–July 2026.