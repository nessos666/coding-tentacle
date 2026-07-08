# 🧠 10 GEHIRNE — Passende Benchmark-Tests

> Jedes Gehirn braucht den RICHTIGEN Test. Nicht alle BugsInPy.
> Hier: Der etablierte Standard-Test für jeden mathematischen Typ.

---

## ÜBERSICHT

| # | Gehirn | Mathematik | Benchmark | Typ |
|---|--------|-----------|-----------|-----|
| A | Bayesian | ⟨f,c⟩ NARS | **BLInD** — Bayesian Linguistic Inference Dataset | Probabilistisches Schließen |
| B | Shannon | -log₂ p(bug) | **ADBench** — Anomaly Detection Benchmark | Neuheitserkennung |
| C | Graph | BFS + PageRank | **OGB** — Open Graph Benchmark (ogbn-arxiv) | Knoten-Klassifikation |
| D | RL | Q(s,a) + ε-greedy | **Gymnasium Taxi-v3** — Tabular Q-Learning | Reinforcement Learning |
| E | Kybernetisch | A+B+C+D | **BugsInPy** — 31 reale Python-Bugs | Bug-Fixing SE |
| F | ACT-R | Base-Level + Spreading | **Human Memory Retrieval** — Serial Recall Task | Kognitive Modellierung |
| G | Friston | Free Energy ∇F | **Active Inference Grid World** — FEPS Benchmark | Aktive Inferenz |
| H | Causal | do-Kalkül | **CausalBench / DoWhy IHDP** | Kausale Inferenz |
| I | Kolmogorov | K(x) NCD | **Calgary Corpus** — Text Compression Standard | Kompression |
| J | Mandelbrot | Hurst + Power-Law | **UCR Time Series Archive** — 128 Datasets | Fraktale Klassifikation |

---

## A — Bayesian: BLInD (Bayesian Linguistic Inference Dataset)

**Quelle**: arXiv:2402.09614 (2024)
**Was**: Text-basierte probabilistische Inferenz. Natürlichsprachliche Bayesian-Updates.
**Metrik**: Accuracy der Wahrscheinlichkeitsschätzung (30% besser mit BIRD-Framework)
**Warum**: Testet ⟨f,c⟩-Logik direkt — update belief mit neuer Evidenz.
**Größe**: ~1000 probabilistische Text-Queries

```
Test:     "Wenn P(A)=0.3 und P(B|A)=0.8, was ist P(A|B)?"
Gehirn:   frequency=0.3, confidence=... → Update nach Bayes
```

---

## B — Shannon: ADBench (Anomaly Detection Benchmark)

**Quelle**: arXiv:2206.09426, pyod library (yzhao062/pyod)
**Was**: 57 Anomaly-Detection-Algorithmen auf 50+ Datasets.
**Metrik**: ROC-AUC, Precision@N für Neuheitserkennung
**Warum**: Shannon misst Überraschung. ADBench misst, WIE GUT Überraschung erkannt wird.
**Größe**: 50+ Datasets, 57 Algorithmen als Baseline

```
Test:     Normal-Daten trainieren → Anomalien erkennen
Gehirn:   Surprisal = -log₂ p(x). Hoher Surprisal = Anomalie.
```

---

## C — Graph: OGB (Open Graph Benchmark)

**Quelle**: snap-stanford.github.io/ogb-web (Stanford, NeurIPS 2021)
**Was**: Große, realistische Graph-Datasets. ogbn-arxiv: 169K Paper, 1.1M Kanten.
**Metrik**: Node Classification Accuracy
**Warum**: Graph Brain traversiert Knoten. OGB testet Knoten-Klassifikation auf Gigantischen Graphen.
**Größe**: 169,343 Knoten, 1,166,243 Kanten

```
Test:     Paper in 40 Kategorien klassifizieren via Graph-Traversal
Gehirn:   BFS über 2 Hops → ähnliche Bugs/Knoten finden
```

---

## D — RL: Gymnasium Taxi-v3

**Quelle**: gymnasium.farama.org (OpenAI Gym Nachfolger)
**Was**: Tabular Q-Learning Environment. Taxi muss Passagier abholen + absetzen.
**Metrik**: Average Reward über 100 Episoden, Steps-to-Solve
**Warum**: RL Brain = Q(s,a). Taxi-v3 IST der Standard-Test für tabulares Q-Learning.
**Größe**: 500 Zustände, 6 Aktionen

```
Test:     Taxi lernt optimale Route via Q-Learning
Gehirn:   Q(s,a) ← Q(s,a) + α[r + γ·max Q - Q]
```

---

## E — Kybernetisch: BugsInPy (31 Python Bugs)

**Quelle**: github.com/soarsmu/BugsInPy, arXiv:2401.15481
**Was**: 31 reale Bugs aus 17 Python-Projekten. Jeder mit Test-Suite.
**Metrik**: Fix-Rate (bug gefixed / total), Time-to-Fix, Memory-Hit-Rate
**Warum**: Das EINZIGE Gehirn, das ALLE Mechanismen für Bug-Fixing vereint.
**Größe**: 31 Bugs, 17 Projekte (thefuck, ansible, cookiecutter...)

```
Test:     Bug-Repository klonen → Bug-Snapshot auschecken → Fix finden
Gehirn:   Alle 4 Regelkreise: Entropie→Explore/Exploit, Bayesian→Konfidenz,
          Graph→Zusammenhänge, RL→Memory-Aktion
```

---

## F — ACT-R: Human Memory Retrieval (Serial Recall)

**Quelle**: ACT-R Standalone, ACM DL (2025: Human-Like Remembering in LLM Agents)
**Was**: Simulation menschlicher Gedächtnisabrufe. Liste lernen → Items abrufen.
**Metrik**: Korrelation mit humanen Recall-Daten (Pearson's r), Retrieval-Wkeit
**Warum**: ACT-R wurde gebaut, um MENSCHLICHES Gedächtnis zu simulieren.
**Größe**: Standard-Experimente: 20-Item Lists, Serial Position Curves

```
Test:     Liste von 20 Wörtern → Welche werden erinnert?
Gehirn:   Base-Level B = ln(Σ t_j^(-d)). Spreading Activation.
          Primacy/Recency-Effekt vorhersagen.
```

---

## G — Friston: Active Inference Grid World (FEPS)

**Quelle**: PLOS ONE (2025): Free Energy Projective Simulation, arXiv:2412.10425
**Was**: Agent in Grid World. Kein Reward! Nur Free Energy Minimization.
**Metrik**: Goal-Reaching Rate, Steps-to-Goal, Free Energy über Zeit
**Warum**: Friston-Gehirn minimiert F = D_KL - E_Q[ln P]. Kein Reward nötig.
**Größe**: 5×5 bis 20×20 Grid Worlds

```
Test:     Agent findet Ziel OHNE Belohnungssignal
Gehirn:   a* = argmin_a F(o, a, s). Free Energy sinkt → Agent lernt.
```

---

## H — Causal: CausalBench / DoWhy IHDP

**Quelle**: causalbench.org, py-why/dowhy (Microsoft), IHDP Dataset
**Was**: Infant Health and Development Program. Kausaler Effekt von Interventionen.
**Metrik**: ATE (Average Treatment Effect) Error, Precision in Effect Estimation
**Warum**: Causal Brain nutzt do-Kalkül. IHDP ist DER Standard-Test für kausale Inferenz.
**Größe**: 747 Samples, 25 Covariates, binäre Treatment/Outcome

```
Test:     "Was ist der kausale Effekt von Frühförderung auf IQ?"
Gehirn:   P(Y|do(X)) = Σ_z P(Y|X,Z)·P(Z). Backdoor-Adjustierung.
```

---

## I — Kolmogorov: Calgary Corpus

**Quelle**: data-compression.info/Corpora/CalgaryCorpus (Bell, Witten, Cleary 1987)
**Was**: DE-FACTO Standard für Text-Kompression. 18 Dateien, 9 Text-Typen.
**Metrik**: Kompressionsrate (Bits pro Zeichen), NCD-Präzision
**Warum**: Kolmogorov-Gehirn = NCD. Calgary Corpus = DAS Maß für Kompression.
**Größe**: ~3.2 MB, 18 Dateien (bib, book1, book2, news, paper1-6...)

```
Test:     Datei komprimieren → NCD zwischen Dateien berechnen
Gehirn:   K(x) ~ len(zlib.compress(x)). NCD(a,b) = (C(ab)-min)/(max)
```

---

## J — Mandelbrot: UCR Time Series Archive

**Quelle**: timeseriesclassification.com, cs.ucr.edu/~eamonn/time_series_data
**Was**: 128 Zeitreihen-Datasets. DER Standard für Zeitreihen-Klassifikation.
**Metrik**: Classification Accuracy, Hurst-Exponent-Präzision
**Warum**: Mandelbrot misst Hurst + Power-Law. UCR = 1000+ Zeitreihen zum Testen.
**Größe**: 128 Datasets, ~1000 Zeitreihen pro Dataset

```
Test:     Zeitreihe klassifizieren → Hurst-Exponent berechnen
Gehirn:   H > 0.5 = Trend. P(X>x) ~ x^(-α). Selbstähnlichkeit erkennen.
```

---

## PRIORITÄT FÜR CODING TENTACLE

```
1. E — BugsInPy       (DIREKT relevant: Bug-Fixing)
2. H — CausalBench    (Kausalität von Fixes messen)
3. B — ADBench        (Neue Bug-Typen erkennen)
4. I — Calgary Corpus (Pattern-Kompression messen)
5. A — BLInD           (Konfidenz kalibrieren)
```

---

## Quellen

- BLInD: https://arxiv.org/abs/2402.09614
- ADBench: https://github.com/yzhao062/pyod
- OGB: https://snap-stanford.github.io/ogb-web
- Gymnasium: https://gymnasium.farama.org
- BugsInPy: https://github.com/soarsmu/BugsInPy
- ACT-R Memory: https://dl.acm.org/doi/10.1145/3765766.3765803
- FEPS Active Inference: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0331047
- CausalBench: https://causalbench.org
- Calgary Corpus: https://data-compression.info/Corpora/CalgaryCorpus
- UCR Archive: https://timeseriesclassification.com
