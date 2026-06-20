# 🧠 GEHIRN BIBLIOTHEK

## Status: 5 Gehirne gebaut, alle eigenständig lauffähig

| Gehirn | Datei | Zeilen | Demo | Mathematik |
|--------|-------|--------|------|------------|
| **A** Bayesian | `01_bayesian/bayesian_brain.py` | 200 | ✅ | ⟨f,c⟩ Konfidenz |
| **B** Shannon | `02_shannon_entropie/shannon_brain.py` | 230 | ✅ | -log₂ p(bug) |
| **C** Graph | `03_graph_struktur/graph_brain.py` | 210 | ✅ | BFS + PageRank |
| **D** RL | `04_reinforcement/rl_brain.py` | 190 | ✅ | Q(s,a) + ε-greedy |
| **E** Kybernetisch | `05_kybernetisch/kybernetisch_brain.py` | 260 | ✅ | A+B+C+D + Regelkreise |
| **F** ACT-R | `06_act_r_spreading/` | ❌ | — | Später |

## Interface (alle Gehirne)

```python
brain.think(signature, embedding) → {'action', 'pattern', 'confidence', 'reasoning'}
brain.learn(signature, pattern, success, embedding) → None
brain.stats() → dict
```

## Nächster Schritt

Phase 1 Experiment: Gehirn A + B gegen 50 BugsInPy-Bugs testen.
→ Ergebnisse in `07_experimente/`
