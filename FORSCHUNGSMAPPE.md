# 🧠 GEHIRN BIBLIOTHEK — Forschungs-Mappe

> Coding Tentacle | 20 Gehirne | 4 Generationen | 42 Kybernetiker | 10+ Benchmarks
> Verknüpft mit Hermes via Qdrant (knowledge_nuggets, Port 6335)

---

## 📂 ORDNERSTRUKTUR

```
~/GEHIRN_BIBLIOTHEK/
├── README.md                          ← START HIER
├── 00_UEBERSICHT_6_GEHIRN_ARTEN.md    ← Gen1+Gen2: Mathematik + Forschung
├── 09_kybernetiker_liste.md           ← 42 Kybernetiker, 4 Epochen
├── 10_kybernetiker_nach_themen.md     ← Nach 10 Themenbereichen
├── 12_benchmark_tests.md              ← 10 spezifische Standard-Tests
│
├── 01_bayesian/        Gehirn A:  ⟨f,c⟩ NARS-Konfidenz
├── 02_shannon_entropie/ Gehirn B:  -log₂ p(bug) Entropie
├── 03_graph_struktur/  Gehirn C:  BFS + PageRank
├── 04_reinforcement/   Gehirn D:  Q(s,a) + ε-greedy
├── 05_kybernetisch/     Gehirn E:  A+B+C+D + 4 Regelkreise
├── 06_act_r_spreading/  Gehirn F:  ACT-R Base-Level    Gehirn G: Friston ∇F
│                        Gehirn H:  Causal do-Kalkül    Gehirn I: K(x) NCD
│                        Gehirn J:  Mandelbrot Hurst
├── 07_experimente/     ALLE Benchmarks & Ergebnisse
├── 08_fusion_mit_qdrant/ Gehirn ↔ Qdrant Integration
├── 11_hebbian/         Gehirn K:  Δw = η·x_i·x_j
├── 12_genetisch/       Gehirn L:  Evolution (Holland)
├── 13_attention/       Gehirn M:  Q·K^T → Softmax (Vaswani)
├── 14_fuzzy/           Gehirn N:  μ(x) ∈ [0,1] (Zadeh)
├── 15_ensemble/        Gehirn O:  Σ w_i · vote_i
├── 16_game_theory/     Gehirn P:  Minimax/Nash
├── 17_gradient/        Gehirn Q:  Adam-Optimierung
├── 18_nearest_neighbor/ Gehirn R:  k-NN Case-Based
├── 19_markov/          Gehirn S:  MDP Value-Iteration
├── 20_contrastive/     Gehirn T:  InfoNCE Loss
```

---

## 🧠 20 GEHIRNE — ÜBERSICHT

| # | Name | Mathematik | Kybernetiker | Generation |
|---|------|-----------|-------------|------------|
| A | Bayesian | ⟨f,c⟩ NARS | Pei Wang | 1: Kybernetik |
| B | Shannon | -log₂ p(bug) | Claude Shannon | 1: Kybernetik |
| C | Graph | BFS + PageRank | Euler/Barabási | 1: Kybernetik |
| D | RL | Q(s,a) + ε | Sutton/Barto | 1: Kybernetik |
| E | Kybernetisch | A+B+C+D | Ashby/Wiener | 1: Kybernetik |
| F | ACT-R | B = ln(Σ t^(-d)) | John Anderson | 2: Moderne |
| G | Friston | ∇F Free Energy | Karl Friston | 2: Moderne |
| H | Causal | do-Kalkül | Judea Pearl | 2: Moderne |
| I | Kolmogorov | K(x) = min\|p\| | A. Kolmogorov | 2: Moderne |
| J | Mandelbrot | Hurst/Power-Law | B. Mandelbrot | 2: Moderne |
| K | Hebbian | Δw = η·x·y | Donald Hebb | 3: KI |
| L | Genetisch | Selektion/Crossover | John Holland | 3: KI |
| M | Attention | Q·K^T/√d_k | Vaswani et al. | 3: KI |
| N | Fuzzy | μ(x) ∈ [0,1] | Lotfi Zadeh | 3: KI |
| O | Ensemble | Σ w_i·vote_i | Dietterich | 3: KI |
| P | GameTheory | Minimax/Nash | von Neumann | 4: Strategie |
| Q | Gradient | Adam (β1,β2) | Kingma/Ba | 4: Strategie |
| R | NearestNeighbor | k-NN | Cover/Hart | 4: Strategie |
| S | Markov | V(s)=max_a ΣP·(R+γV) | Bellman | 4: Strategie |
| T | Contrastive | InfoNCE Loss | Hadsell/LeCun | 4: Strategie |

---

## 📊 BENCHMARK-ERGEBNISSE

### Standard-Tests (15 spezifische Benchmarks)

| Rang | Gehirn | Test | Score |
|------|--------|------|-------|
| 1 | B_Shannon | ADBench Novelty | 1.000 |
| 1 | F_ACTR | Serial Position | 1.000 |
| 1 | L_Genetisch | Evolution Fitness | 1.000 |
| 1 | M_Attention | QKV Attention | 1.000 |
| 1 | K_Hebbian | Hebb Δw | 1.000 |
| 1 | N_Fuzzy | Fuzzy μ(x) | 1.000 |
| 1 | O_Ensemble | Meta Voting | 1.000 |
| 1 | P_GameTheory | Minimax | 1.000 |
| 1 | Q_Gradient | Adam | 1.000 |
| 1 | R_NearestNeighbor | k-NN | 1.000 |
| 1 | S_Markov | MDP | 1.000 |
| 1 | T_Contrastive | InfoNCE | 1.000 |
| 13 | H_Causal | Causal Backdoor | 0.930 |
| 13 | C_Graph | OGB Karate Club | 0.950 |

**Schnitt: 0.870 | 18/20 ≥ 0.5 | 14 ≥ 0.8**

### Neue Test-Arten (10 Kategorien, Research-basiert)

| Test | Ergebnis | Standard |
|------|----------|----------|
| BWT (Forgetting) | 18/20 | AgentMemoryBench 2026 |
| Persistenz | 19/20 | Continual Learning |
| Interferenz | 18/20 | CL Benchmarks |
| Skalierbarkeit | 18/20 | Scale ML |
| Recovery | 18/20 | Repair Mode |
| OOD Detection | 14/20 | OpenOOD Standard |
| ECE Kalibrierung | μ=0.129 | NeurIPS 2025 |
| Cross-Modal | 13/20 | Multi-Modal Transfer |
| Transfer (FWT) | 6/20 | Forward Transfer |

---

## 🔗 VERKNÜPFUNG MIT HERMES

### Qdrant (Port 6335): Collection `knowledge_nuggets`

```bash
# Gehirn-Forschung in Qdrant finden
python3 ~/.hermes/scripts/qdrant_search.py "Gehirn Bibliothek Bayesian Friston"

# Coding Tentacle Memory-Design
python3 ~/.hermes/scripts/qdrant_search.py "CodingTentacle Memory 3-Schicht"

# Kybernetiker Papers
python3 ~/.hermes/scripts/qdrant_search.py "Mandelbrot Fraktale Kybernetik"
```

### Session-Suche (Hermes intern)

```
@session:default/XXXX  → Direktlink zu Coding-Tentacle-Sessions
"Gehirn Bibliothek"    → Findet alle Sessions mit Gehirn-Bau
```

### Desktop

```
~/Schreibtisch/
├── GEHIRN_BENCHMARKS.md              ← 10 Standard-Tests
├── KYBERNETIKER_NACH_THEMEN.md       ← 42 Kybernetiker × 10 Themen
├── KYBERNETIKER_PAPERS_GLEICHUNGEN.md ← 69 KB Papers + Gleichungen
└── GEHIRN_BIBLIOTHEK_6_Arten.md      ← Gen1+Gen2 Übersicht
```

---

## 🎯 FÜR CODING TENTACLE

### Empfohlene Gehirn-Kombination (MVP)

1. **P_GameTheory** (0.889) — Sicherster Fix via Minimax
2. **C_Graph** (0.950) — Strukturelle Zusammenhänge
3. **M_Attention** (1.000) — Ähnlichste Bugs finden
4. **H_Causal** (0.930) — Kausale Effekte von Fixes

### Integration

```python
from coding_tentacle import CodingTentacle
tentacle = CodingTentacle(
    brains=[GameTheoryBrain(), GraphBrain(), AttentionBrain(), CausalBrain()],
    memory=HybridMemory(qdrant_port=6335, sqlite_path="tentacle.db")
)
```

---

## 📚 FORSCHUNGS-QUELLEN

- Wiener: Cybernetics (1948)
- Shannon: Mathematical Theory of Communication (1948)  
- Ashby: Introduction to Cybernetics (1956)
- Mandelbrot: Fractal Geometry of Nature (1977)
- Friston: Free Energy Principle (2005-2024)
- Pearl: Causality (2000), do-Kalkül (1995)
- Vaswani: Attention Is All You Need (2017)
- Holland: Adaptation in Natural and Artificial Systems (1975)
- Zadeh: Fuzzy Sets (1965)
- Hebb: Organization of Behavior (1949)
- AgentMemoryBench: OpenReview (March 2026)
- Agentic Confidence Calibration: arXiv 2601.15778 (2026)

---

*Letzte Aktualisierung: 19. Juni 2026 | Hermes + David*
