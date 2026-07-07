# Metakognitive & Multi-Brain-Architekturen (2024–2026)
## Coding Tentacle Research | 23. Juni 2026

---

## 1. METAKOGNITIVE ARCHITEKTUREN

### SOFAI — Slow and Fast AI (Nature npj AI, Okt. 2025)
- **IBM Research / Oxford:** Kahneman-inspirierte Dual-Prozess-Architektur
- S1 (Fast Solver) + S2 (Slow Solver) + Metakognitiver Agent
- Metakognitives Modul: Echtzeit-MC, Reflektives MC, Lernendes MC
- **CT-Vergleich:** SOFAIs Metakognition entspricht konzeptionell SkepticBrain, aber kein Bayesian-Voting, kein Kálmán-Konsens, kein Multi-Brain
- **Quelle:** https://www.nature.com/articles/s44387-025-00027-5

### MARS — Metacognitive Agent Reflective Self-improvement (ICML 2025)
- Prompt-Optimierung durch Selbstreflexion
- Introspektion → Selbstbewertung → Strategie-Revision → Autonomes Lernen
- **CT-Vergleich:** Nur Prompt-Level, kein Architektur-Level. MetaBrain operiert auf Architekturebene.
- **Quelle:** Hou et al., 2026

### Metagent-P (ACL 2025 Findings)
- Neuro-symbolischer Planungsagent: Planning-Verification-Execution-Reflection
- **CT-Vergleich:** Ähnliche Reflexionsschleife wie SkepticBrain, aber nur für Planung

---

## 2. MULTI-BRAIN-KOORDINATION

### MAP — Modular Agentic Planner (Microsoft Research, Nature 2025)
- Hirn-inspirierte modulare Architektur mit PFC-Funktionen
- Konfliktüberwachung, Zustandsvorhersage, Aufgabenzerlegung, Orchestrierung
- **CT-Vergleich:** MAPs Modularität ähnelt CT, aber kein statistisches Vertrauensvoting
- **Quelle:** https://www.nature.com/articles/s41467-025-63804-5

### CoALA — Cognitive Architectures for Language Agents (TMLR 2024)
- Deskriptives Framework: Working Memory, Episodic Memory, Semantic Memory, Procedural Memory
- **CT-Vergleich:** CoALA klassifiziert, CT operiert. Kein Bayesian, kein Kálmán.

---

## 3. BAYESIAN TRUST-WEIGHTED VOTING

### Hallyburton & Pajic (IEEE 2024)
- Bayesian Methods for Trust in Collaborative Multi-Agent Autonomy
- Hierarchisches Bayesian-Updating für Vertrauensschätzung
- "Trust-Pseudomeasurements" (PSMs) aus Sensormessungen
- **CT-Vergleich:** DIREKTE Parallele zu MetaBrains Bayesian-Voting. CT überträgt dies von Sensorfusion auf kognitive Agenten.

---

## 4. KÁLMÁN-KONSENS-SYSTEME

### Distributed Kalman-Consensus Filter (DKCF, 2023–2026)
- DKCF mit adaptiver Unsicherheit (arXiv 2603.11328, 2026)
- Information-Weighted Kalman Consensus Filter (IWKCF)
- Adaptive Kalman Consensus Filters (a-KCF)
- **CT-Vergleich:** Konzeptionell IDENTISCH mit MetaBrains Kálmán-Konsens. Entscheidender Unterschied: DKCF = physische Sensor-Netzwerke, MetaBrain = kognitive Agenten-Entscheidungen. Dies ist die innovativste Komponente — Brücke von Signalverarbeitung zu kognitiver Orchestrierung.

---

## 5. KOGNITIVE ARCHITEKTUREN: ACT-R & SOAR

### LLM-ACTR (AAAI-MAKE 2025)
- ACT-R (produktionsbasiert) + LLM: Grounding + semantisches Wissen
- Reduzierte Halluzination vs reine LLM-Baselines

### CogRec — SOAR + LLM (OpenReview 2025)
- SOAR (regelbasiert) + LLM für Empfehlungssysteme
- Strukturierte Reasoning-Prozesse, LLM überwindet Wissensakquisitions-Engpass

### SBP-BRiMS 2025: LLM-Translation zwischen ACT-R und SOAR
- Automatisierte Übersetzung kognitiver Modelle
- Methodologische Grundlage für hybride Architektur-Integration

**CT-Vergleich:** ACT-R/SOAR liefern kognitive Plausibilität — CT liefert operative Zuverlässigkeit. Komplementär.

---

## 6. UNIQUE POSITIONING — CT vs ALLE

| System | Metakognition | Bayesian-Voting | Kálmán-Konsens | Multi-Brain | Safety-Integriert |
|--------|:---:|:---:|:---:|:---:|:---:|
| **MetaBrain V2** | ✅ SkepticBrain | ✅ | ✅ | ✅ | ✅ |
| MARS | ✅ Prompt-Level | ❌ | ❌ | ❌ | ❌ |
| SOFAI | ✅ Dual-Solver | ❌ | ❌ | ⚠️ | ❌ |
| MAP | ❌ | ❌ | ❌ | ✅ | ❌ |
| Hallyburton/Pajic | ❌ | ✅ | ❌ | ✅ | ⚠️ |
| DKCF-Literatur | ❌ | ❌ | ✅ | ✅ | ❌ |
| LLM-ACTR/CogRec | ❌ | ❌ | ❌ | ❌ | ✅ Grounding |
| CoALA | ❌ Deskriptiv | ❌ | ❌ | ❌ | ❌ |

**MetaBrain V2 ist das EINZIGE System das alle drei Säulen — Bayesian-Vertrauensgewichtung, Kálmán-Konsens-Filterung und metakognitive Kritik — in einer operativen Architektur vereint.**

---

## QUELLEN

- SOFAI: https://www.nature.com/articles/s44387-025-00027-5
- MAP: https://www.nature.com/articles/s41467-025-63804-5
- DKCF: arXiv 2603.11328 (2026)
- Hallyburton/Pajic: IEEE 2024
- MARS: ICML 2025
- CoALA: TMLR 2024 (Sumers et al.)
