# CT Research TODO — Aus der Gehirn-Landschafts-Analyse (23.06.2026)
## Was Coding Tentacle noch braucht, untersuchen oder verbessern sollte

---

## 🔴 PRIORITÄT 1 — FUNDAMENTALE LÜCKEN SCHLIESSEN

### 1. Kolmogorov-Komplexität als Metrik integrieren
- **Was:** Prüfen ob ein Fix "minimal" ist — die kürzeste Beschreibung ist die beste
- **Warum:** CIv8r und Agent Cybernetics Paper fordern dies explizit
- **Aktion:** `SkepticBrain.check_minimality(diff)` — misst Diff-Komplexität, warnt bei Over-Engineering
- **Quelle:** arXiv:2605.10754 (Agent Cybernetics), CIv8r (Algoplexity)

### 2. Prigogine-Dissipationsstrukturen für BLM V2
- **Was:** Lernen als dissipativer Prozess fern vom Gleichgewicht
- **Warum:** BLM läuft aktuell als einfaches SQLite+Keyword-Matching, nicht als strukturelles Lernen
- **Aktion:** BLM V2 mit "Edge of Chaos"-Dynamik — Feedback Dampener ist schon da, aber nicht genug
- **Quelle:** CIv8r (Algoplexity), Prigogine's Dissipative Strukturen

### 3. Formale Ashby-Ableitung des IC-Gates
- **Was:** Mathematischer Beweis dass IC 5-Level NÖTIG sind (nicht 2, nicht 10)
- **Warum:** Agent Cybernetics Paper validiert Ansatz, aber CT hat keinen formalen Beweis
- **Aktion:** Paper/Whitepaper: "Warum 5-Level? — Ashby's Law auf Code-Sicherheit angewandt"
- **Quelle:** Ashby's Law of Requisite Variety

---

## 🟡 PRIORITÄT 2 — PRAKTISCHE VERBESSERUNGEN

### 4. OpenParallax-Integration prüfen
- **Was:** OpenParallax hat 4-Tier-Shield mit OS-Level-Sandbox (Landlock+seccomp)
- **Warum:** CTs Sandbox ist simpler — OpenParallax Kernel-Isolation könnte CT härten
- **Aktion:** OpenParallax evaluieren, ggf. als optionalen Sandbox-Backend integrieren
- **Quelle:** arXiv:2604.12986 (OpenParallax), github.com/openparallax

### 5. 3D-Risikotaxonomie nach AgentDoG-Vorbild
- **Was:** AgentDoG hat 3D-Sicherheitstaxonomie (Tasks, Tools, Scenarios)
- **Warum:** CTs IC bewertet nur 1-dimensional (risk_level: low/medium/high/critical)
- **Aktion:** IC mit 3D-Taxonomie erweitern (Bug-Typ × Datei-Typ × Operation)
- **Quelle:** arXiv:2601.18491 (AgentDoG)

### 6. ePCA-Formalismus studieren
- **Was:** ePCA hat FORMAL BEWEISBARE Sicherheit statt semantischer Checks
- **Warum:** CTs IC ist semantisch (Regex-Matching) — formale Methoden wären stärker
- **Aktion:** Paper lesen, bewerten ob formal methods für CT praktikabel sind
- **Quelle:** ePCA Paper (Mai 2026)

---

## 🟢 PRIORITÄT 3 — LANGFRISTIGE FORSCHUNG

### 7. Rekursive Selbstverbesserung nach HyperAgents-Vorbild
- **Was:** HyperAgents (Meta) verbessert den eigenen Verbesserungsmechanismus
- **Warum:** CTs BLM lernt aus Bugs, aber der LERNMECHANISMUS selbst ist statisch
- **Aktion:** BLM V3: Meta-Learning — der Consolidator lernt bessere Consolidation-Strategien
- **Quelle:** verdent.ai/guides/meta-hyperagents-ai-coding

### 8. KAN (Kolmogorov-Arnold Networks) als MetaBrain-Substrat
- **Was:** KAN nutzt Kolmogorov-Repräsentationstheorem für lernbare Aktivierungsfunktionen
- **Warum:** Könnte MetaBrains Konsens-Findung effizienter und interpretierbarer machen
- **Aktion:** Evaluieren ob KAN als Ersatz für Bayesian+Kálmán taugt (unwahrscheinlich, aber prüfen)
- **Quelle:** arXiv:2404.19756 (KAN, MIT/Caltech)

### 9. Containment-Gap-Studie in CT-Tests einbauen
- **Was:** CSA-Studie testet 6 Containment-Prinzipien, CT sollte ALLE erfüllen
- **Warum:** CT adressiert die Prinzipien architektonisch, aber nicht formal getestet
- **Aktion:** 6-Prinzipien-Test-Suite für CT schreiben, als Dauer-Regression
- **Quelle:** CSA Research Note (Juni 2026)

---

## 📋 DIREKT UMSETZBAR (Quick Wins)

- [x] Forschungsmappe angelegt: `GEHIRN_BIBLIOTHEK/research/2026-06-23-brain-landscape/`
- [ ] Agent-Cybernetics-Paper als PDF in research/ ablegen
- [ ] OpenParallax-Repo klonen und IC/EL vergleichen
- [ ] CIv8r-Website durchlesen, Kolmogorov/Prigogine-Ideen extrahieren
- [ ] Metacognitive-Architectures Paper (SOFAI, MAP) in Qdrant vektorisieren

---

## 📁 DATEIEN

| Datei | Pfad |
|-------|------|
| Master-Synthese | `research/2026-06-23-brain-landscape/00_MASTER_SYNTHESE.md` |
| Kybernetische Gehirne (19 Systeme) | `research/2026-06-23-brain-landscape/1_kybernetische_gehirne.md` |
| Sicherheits-Architekturen (13 Systeme) | `research/2026-06-23-brain-landscape/2_sicherheits_architekturen.md` |
| Metakognitive Architekturen | `research/2026-06-23-brain-landscape/3_metacognitive_multi_brain.md` |
| Dieser TODO | `research/2026-06-23-brain-landscape/TODO.md` |
