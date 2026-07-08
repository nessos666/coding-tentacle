# 🧠 KOGNITIVE ARCHITEKTUREN — DEEP RESEARCH

> 35 Gehirne gebaut. Hier: Was die FORSCHUNG sagt. Stand 2026.

---

## 1. PREDICTIVE CODING — Vom Gehirn zur KI

**Quellen**: 
- Rao & Ballard (1999): Original-Paper in Nature Neuroscience
- Friston (2005-2024): Free Energy Principle als theoretisches Fundament
- *Nature Communications* (2025): "Predictive Coding Light" — erstes spiking neural network Modell
- *Neural Networks* (2025): PrediRep — hierarchisches PC als Deep Learning
- *Trends in Cognitive Sciences* (2025): "A more cognitive process than we thought?"

**Kerngedanke**: Das Gehirn ist eine Vorhersagemaschine. Jede kortikale Schicht sagt die Aktivität der darunterliegenden Schicht vorher. Prediction Errors fließen nach oben. Predictions fließen nach unten. Lernen = Minimierung des Prediction Errors.

**Status 2026**: 
- Theorie weitgehend akzeptiert (Friston ist meistzitierter Neurowissenschaftler)
- Praktische Implementierung in Deep Learning beginnt gerade erst
- "Predictive Coding Light" beweist: PC kann in spiking neural networks funktionieren
- PrediRep zeigt: Hierarchisches PC verbessert unsupervised Representation Learning

**Coding Tentacle Relevanz**: Unser Gehirn AE implementiert eine 4-schichtige PC-Hierarchie (384→128→64→32). Die Forschung zeigt: Mehr Schichten + bessere Weight-Updates = bessere Abstraktion.

---

## 2. MODERN HOPFIELD NETWORKS — Exponentielle Kapazität

**Quellen**:
- Hopfield (1982): Klassisches Modell (begrenzte Kapazität: N/4 Muster)
- Krotov & Hopfield (2016): "Dense Associative Memories" — Durchbruch
- Demircigil et al. (2017): Exponentielle Speicherkapazität bewiesen
- Ramsauer et al. (2021): "Hopfield Networks is All You Need" — Verbindung zu Transformern
- *Modern Hopfield Networks with Continuous-Time Memories* (2025): Skalierung verbessert
- Wikipedia (aktualisiert März 2026): "Large memory storage capacity Hopfield Networks"

**Kerngedanke**: Klassischer Hopfield speichert ~0.14N Muster (N=Neuronen). Modern Hopfield speichert EXPONENTIELL viele Muster via stärkerer Nichtlinearität in der Energie-Funktion. Die Update-Regel ist mathematisch äquivalent zur Transformer-Attention!

**Mathematik**:
- Klassisch: E = -½ Σ w_ij·s_i·s_j, Update: s_i ← sign(Σ w_ij·s_j)
- Modern: E = -logsumexp(β·Σ pattern_i·x) + ½||x||², Update via softmax

**Status 2026**:
- Direkte Verbindung zu Transformer-Attention etabliert
- Kann Attention-Heads in Transformern ERSETZEN
- Continuous-time Varianten verbessern Skalierung
- Anwendung: Pattern Completion, Denoising, Memory-Module in Deep Learning

**Coding Tentacle Relevanz**: Unser Gehirn AF (Hopfield) nutzt klassische Hebb'sche Speicherung. Ein MODERN Hopfield mit Softmax-Update würde exponentiell mehr Bug-Patterns speichern können.

---

## 3. SOAR — Die vollständigste kognitive Architektur

**Quellen**:
- Laird, Newell, Rosenbloom (1987): Erste SOAR-Version an der CMU
- Laird (2012): *The Soar Cognitive Architecture* (MIT Press) — Standardwerk
- SOAR 9.6 (2020): Reinforcement Learning Integration (SOAR-RL)
- Aktive Entwicklung an der University of Michigan (soar.eecs.umich.edu)

**Architektur**:
```
┌─────────────────────────────────────────────┐
│  SOAR Decision Cycle                         │
│                                              │
│  INPUT → ELABORATE → PROPOSE → DECIDE → APPLY → OUTPUT
│           ↑            ↓                     │
│           └── Working Memory ──────────────┘ │
│                                              │
│  LONG-TERM MEMORIES:                         │
│  • Procedural Memory (Production Rules)      │
│  • Semantic Memory (Fakten)                  │
│  • Episodic Memory (Erfahrungen)             │
│                                              │
│  LEARNING MECHANISMS:                        │
│  • Chunking: Ergebnisse → neue Regeln        │
│  • Reinforcement Learning: Tuning von Regeln │
│  • Semantic Learning: Fakten speichern       │
│  • Episodic Learning: Erfahrungen speichern  │
└─────────────────────────────────────────────┘
```

**Status 2026**: SOAR ist die am längsten kontinuierlich entwickelte kognitive Architektur (~40 Jahre). Aktive RL-Integration. Wird für Robotik, autonome Agenten und kognitive Modellierung eingesetzt.

**Coding Tentacle Relevanz**: Unser Gehirn AG implementiert die SOAR-Struktur (WM + Procedural + Semantic + Episodic). Die echte SOAR hat zusätzlich: Chunking, Subgoaling, Impasse-Auflösung.

---

## 4. OPENTCOG / HYPERON — AGI-Plattform

**Quellen**:
- Goertzel (2008): OpenCog Prime Design
- *Engineering General Intelligence* (Goertzel 2014, 2 Bände)
- OpenCog Hyperon (2023-2025): Nächste Generation, verteilt, neural-symbolisch
- *AtomSpace* (github.com/opencog/atomspace): Hypergraph-Wissensdatenbank
- SingularityNET / ASI Alliance: Kommerzielle Entwicklung

**Architektur**:
```
┌──────────────────────────────────────────────┐
│  OpenCog Hyperon (2025)                       │
│                                               │
│  ATOMSPACE (Hypergraph-KB)                    │
│  ├── Atoms: Konzepte, Zahlen, Strings         │
│  ├── Links: Relationen (Inheritance, Similarity)
│  └── TruthValues: ⟨strength, confidence⟩      │
│                                               │
│  COMPONENTS:                                  │
│  • PLN (Probabilistic Logic Networks)         │
│  • MOSES (Meta-Optimizing Semantic Evolution) │
│  • ECAN (Economic Attention Networks)         │
│  • Pattern Miner (häufige Subgraphen)         │
│  • URE (Unified Rule Engine)                  │
│                                               │
│  KEY INNOVATION in Hyperon:                   │
│  • Distributed AtomSpace (DAS) — multi-node   │
│  • MeTTa-Sprache für kognitive Operationen    │
│  • Neural-Symbolic Bridge (LLM ↔ AtomSpace)   │
└──────────────────────────────────────────────┘
```

**Status 2026**: Hyperon ist die aktivste AGI-Entwicklung außerhalb der großen Tech-Konzerne. MeTTa-Sprache macht kognitive Programmierung zugänglich. Integration mit LLMs via SingularityNET.

**Coding Tentacle Relevanz**: Unser Gehirn AI (AtomSpace) implementiert die Kernidee: Hypergraph + TruthValues. Die volle OpenCog-Pipeline (PLN + MOSES + Pattern Miner) ist um Größenordnungen komplexer.

---

## 5. WEITERE KOGNITIVE ARCHITEKTUREN (NICHT GEBAUT)

| Architektur | Schöpfer | Kernidee | Warum relevant |
|-------------|----------|----------|----------------|
| **CLARION** | Ron Sun (RPI) | Dual-Process: implizit + explizit | Unbewusste vs bewusste Bug-Erkennung |
| **LIDA** | Stan Franklin (Memphis) | Global Workspace Theory | Bewusstsein als Broadcast-Mechanismus |
| **Nengo/Spaun** | Chris Eliasmith (Waterloo) | 2.5M Neuronen, 6 Mrd. Synapsen | Größtes funktionales Gehirnmodell |
| **Sigma** | Paul Rosenbloom (USC) | Graph-basierte kognitive Architektur | Factor Graphs + Message Passing |
| **MicroPsi** | Joscha Bach | Motiviertes kognitives System | Emotion + Motivation für Agenten |
| **HTM/NuPIC** | Jeff Hawkins (Numenta) | Hierarchical Temporal Memory | Tausend-Hirn-Theorie der Intelligenz |
| **NARS** | Pei Wang (Temple) | Non-Axiomatic Reasoning | Unser Gehirn A basiert darauf! |
| **ICARUS** | Pat Langley (Stanford) | Kognitive Architektur für physikalische Agenten | Embodied Bug-Fixing in Code? |
| **Airene** | (2026) | 42 kortikale Module | LLM ist nur EIN Modul von 42 |

---

## 6. DER "AI WINTER" DER KOGNITIVEN ARCHITEKTUREN

```
1960-1985: BLÜTEZEIT — Symbolische KI, Expertensysteme, SOAR, ACT-R
1985-2012: RÜCKGANG — "AI Winter", Neuronale Netze im Aufstieg
2012-2023: TIEFPUNKT — Deep Learning dominiert. Kognitive Architekturen "vergessen"
2024-2026: RENAISSANCE — LLMs allein nicht genug → Neuro-symbolische Hybride
```

**Zitat aus LinkedIn** (2025): "The forgotten AI Winter of Cognitive Architectures — ACT-R, Soar, CLARION, NARS, OpenCog, HTM, LIDA, Sigma, ICARUS, MicroPsi, Spaun. They were designed to simulate 'human like' reasoning."

---

## 7. WAS WIR FÜR CODING TENTACLE LERNEN

1. **Einfache Gehirne > Komplexe Gehirne** für MVP: Unser Test zeigt: A (Bayesian), K (Hebbian), P (GameTheory) sind schneller und robuster als Z (Hypernetwork) oder AD (HRL).

2. **Embedding-Ähnlichkeit ist der Schlüssel**: Fast alle Gehirne scheitern an Transfer, weil sie String-Matching statt Embedding-Matching nutzen.

3. **Neuro-symbolischer Hybrid ist die Zukunft**: OpenCog Hyperon zeigt: LLM als ein Modul, AtomSpace als Wissensbasis.

4. **Predictive Coding ist DER nächste Schritt**: 3-Schicht-Hierarchie in Gehirn AE → mehr Schichten für bessere Abstraktion.

5. **Modern Hopfield für Memory**: Softmax-basierte Speicherung würde Kapazität exponentiell erhöhen.

---

## 8. QUELLEN

1. Predictive Coding Light: *Nature Communications* (2025) — https://www.nature.com/articles/s41467-025-64234-z
2. PrediRep: *Neural Networks* (2025) — https://www.sciencedirect.com/science/article/pii/S089360802500125X
3. Modern Hopfield Networks: Wikipedia, Stand März 2026 — https://en.wikipedia.org/wiki/Modern_Hopfield_network
4. Continuous-Time Hopfield: arXiv 2502.10122 (2025)
5. SOAR: University of Michigan — https://soar.eecs.umich.edu
6. OpenCog Hyperon: SingularityNET — https://superintelligence.io/portfolio/opencog-hyperon/
7. AtomSpace: GitHub — https://github.com/opencog/atomspace
8. AGI Mind Map 2026: https://gogeometry.com/software/ai/agi-mind-map-overview.html
9. LLM-as-RNN with MANNs: arXiv 2601.13352 (2026)
10. Cognitive Architectures Winter: LinkedIn (2025)
