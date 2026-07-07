# ARCHIVE: CT Islands (31 Module, ~7.500 LOC)

**Archiviert am:** 5. Juli 2026
**Grund:** Gebaut + getestet, aber nie in die Produktions-Pipeline (shadow_mode.py) verdrahtet.

## Wiederherstellung

Jedes Modul kann einzeln zurückgeholt werden:
```bash
cp archive/islands/MODUL_PATH src/coding_tentacle/MODUL_PATH
```

## Kategorien

### KLASSIFIZIERER (2)
- `classifier/semantic_classifier.py` — Weighted keyword fallback
- `classifier/unified_classifier.py` — 18 Typen, 8 Sprachen
- **Warum archiviert:** shadow_mode.py nutzt eigenes `_classify_bug_type()`

### KNOWLEDGE STORES (2)
- `knowledge/bug_pattern_store.py` — 50 Bug-Patterns (534 LOC)
- `knowledge/library_store.py` — 50 Library-Patterns (489 LOC)
- **Warum archiviert:** Nie von Pipeline abgefragt

### SPRACHEN (8)
- `languages/*_support.py` — C++, Go, Java, JS, Ruby, Rust, Shell (1.678 LOC)
- **Warum archiviert:** Klassifizieren ja, reparieren nein. 0 Fixes in Nicht-Python.

### MEMORY (5)
- `memory/bug_type_hybrid.py` — FTS5+TF-IDF Hybrid
- `memory/hypothesis_feedback.py` — BR→BLM
- `memory/hybrid_retrieval.py` — TF-IDF Store
- `memory/rare_procedures.py` — 11 rare bug types
- `memory/skill_compiler.py` — Procedure→Skill

### ORCHESTRATOR (4)
- `orchestrator/engine_ensemble.py` — Multi-Engine Ensemble
- `orchestrator/metacognitive_evaluator.py` — Bayesian+Kálmán
- `orchestrator/minimal_orchestrator.py` — Legacy Pipeline
- `orchestrator/outcome_learning.py` — Outcome-Analyse

### SONSTIGE (10)
- `brains/sg_brain.py` — BQ Grounding (628 LOC)
- `config.py` — YAML Config System
- `reasoning/br_scientific_method.py` — Scientific Method
- `safety/escalation_logic.py` — EL Routing
- `tentacles/*.py` — 6 Tentacle-Module (1.581 LOC)

## Statistik

- **31 Module archiviert**
- **~7.500 LOC aus Produktion entfernt**
- **Codebase jetzt: 25 Module, ~8.500 LOC (von 56 → 25)**
- **Produktions-Quote: 17/25 = 68% (vorher 17/56 = 30%)**
