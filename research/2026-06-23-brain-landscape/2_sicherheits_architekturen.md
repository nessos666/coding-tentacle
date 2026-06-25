# Sicherheitskritische KI-Agenten-Architekturen (2024–2026)

## Forschungsbericht: Vergleich mit CTs IC+EL+SecurityStore-Architektur

> **Legende:** IC = Inhibitory Control (inhibitorische Kontrolle / harter Sicherheits-Gate), EL = Execution Layer (isolierte Ausführungsschicht), SecurityStore = read-only Wissensspeicher mit Zugriffstrennung

---

## 1. OpenParallax (April 2026) ⭐⭐⭐ HÖCHSTE RELEVANZ

| Aspekt | Details |
|--------|---------|
| **Paper** | arXiv:2604.12986 – *"Parallax: Why AI Agents That Think Must Never Act"* |
| **Repository** | github.com/openparallax/openparallax (Apache 2.0, Go + Python) |
| **Kernprinzip** | **Architektonische Trennung von Denken und Handeln** – die Reasoning-Komponente darf NIEMALS direkt Aktionen ausführen |

### Sicherheitsmechanismen:

1. **4-Tier-Shield-Pipeline** (entspricht CTs IC):
   - **Tier 1:** Policy-Regeln (deterministisch, regelbasiert)
   - **Tier 2:** ONNX-ML-Klassifikator (schnelle Inferenz)
   - **Tier 3:** LLM-Evaluator (semantische Bewertung)
   - **Tier 4:** Human-in-the-Loop-Approval (VETO-Recht)
   - Jeder Tool-Call durchläuft diese 4 Stufen BEVOR Ausführung

2. **Kernel-Sandboxing** (entspricht CTs EL):
   - Agent-Prozess auf OS-Ebene isoliert (Landlock + seccomp auf Linux)
   - Canary-Verification-Protokoll beim Startup
   - Kein direkter Dateisystem- oder Netzwerkzugriff möglich

3. **Tamper-Evident Audit Log** (teilweise CTs SecurityStore):
   - SHA-256-Hash-Chain über jede Aktion, jedes Verdict, jede Session
   - Append-only, manipulationssicher

### Vergleich mit CTs IC+EL+SecurityStore:

| CT-Komponente | OpenParallax-Äquivalent | Bewertung |
|---------------|------------------------|-----------|
| **IC** | 4-Tier-Shield (inkl. HITL-Veto) | ✅ **Überlegen** – mehrstufig, mit ML+LLM+Human-Eskalation |
| **EL** | Kernel-Sandbox (Landlock+seccomp) | ✅ **Vergleichbar bis stärker** – OS-Level-Isolation |
| **SecurityStore** | Hash-Chain-Audit-Log | ⚠️ **Teilweise** – Audit-Trail ja, aber kein dedizierter read-only Wissensspeicher |

**Fazit:** OpenParallax ist die architektonisch nächste Verwandte zu CTs Ansatz. Die fundamentale Trennung von Reasoning und Execution ist identisch zum IC-Konzept. Der 4-Tier-Shield ist eine ausgereiftere Version des IC-Gates. Ein dedizierter SecurityStore fehlt, wird aber durch manipulationssichere Logs teilweise kompensiert.

---

## 2. Provably Secure Agent Guardrail / ePCA (Mai 2026) ⭐⭐⭐

| Aspekt | Details |
|--------|---------|
| **Paper** | arXiv:2605.29251 – *"Provably Secure Agent Guardrail"* |
| **Framework** | ePCA = Executable Proof-Constrained Action |
| **Autoren** | Benlong Wu et al. (USTC) |

### Sicherheitsmechanismen:

1. **Formale Verifikation statt semantischer Guardrails:**
   - **Pessimismus** gegenüber der neuralen Reasoning-Ebene (LLM wird als vollständig kompromittiert betrachtet)
   - **Optimismus** gegenüber der isolierten Verifikationsebene
   - Aktionen müssen **formale logische Beweise** bestehen, nicht nur semantische Checks

2. **Fundamentale Asymmetrie:**
   - LLM = höchster Gegner (fully penetrated adversary)
   - Verifikationsebene = isoliert, deterministisch, beweisbasiert

### Vergleich mit CTs IC+EL+SecurityStore:

| CT-Komponente | ePCA-Äquivalent | Bewertung |
|---------------|-----------------|-----------|
| **IC** | Formale Beweis-Constraints | ✅ **Überlegen** – mathematisch beweisbare Sicherheit statt heuristischer Checks |
| **EL** | Isolierte Verifikationsebene | ✅ **Vergleichbar** |
| **SecurityStore** | Logische Constraint-Datenbank | ✅ **Implizit vorhanden** – Constraints bilden Wissensbasis |

**Fazit:** ePCA ist die mathematisch rigoroseste Variante des IC-Konzepts. Statt semantischer Prüfungen werden formale Beweise verlangt. Dies ist CTs IC+EL konzeptionell sehr ähnlich, aber mit beweisbaren Garantien. Schwäche: nur für logisch formalisierbare Domänen praktikabel.

---

## 3. Anthropic Constitutional AI & Sicherheitssysteme (2024–2026) ⭐⭐⭐

### 3a. Constitutional AI (CAI) – Kernarchitektur

| Aspekt | Details |
|--------|---------|
| **Prinzip** | Selbstkritik + Revision + RL aus AI-Feedback |
| **Konstitution** | Schriftliche Prinzipien für "helpful, harmless, honest" (HHH) |
| **Prozess** | Modell generiert → kritisiert anhand Konstitution → revidiert → fine-tuned mit AI-Feedback |

### 3b. Constitutional Classifiers (Februar 2025)

- Input- und Output-Klassifikatoren auf Basis der Konstitution
- Training mit synthetischen Jailbreak-Daten
- 3.000+ Stunden Bug-Bounty-Programm
- **Verteidigung gegen universelle Jailbreaks**

### 3c. ASL-3 (AI Safety Level 3) – Mai 2025

- **Responsible Scaling Policy (RSP):** Härteste Sicherheitsstufe für Frontier-Modelle
- Deployment-Standards mit mehrstufigen Sicherheitsgarantien
- Sperrung von Nutzern bei Bedrohungserkennung
- Kontaktaufnahme mit Strafverfolgungsbehörden

### 3d. Petri – Open-Source Auditing (Oktober 2025)

- Automatisierte Alignment-Audits durch KI-Agenten
- **Auditor-Agent** → **Target-Model** → **Judge-Model**
- Multi-Turn, Tool-augmentierte Szenarien
- Open Source auf GitHub

### 3e. A3 – Automated Alignment Agent (2026)

- Agentisches Framework zur automatischen Sicherheitsfehler-Mitigation
- Reduziert Sycophancy, politische Verzerrung, verschachtelte Jailbreaks
- Minimale menschliche Intervention

### Vergleich mit CTs IC+EL+SecurityStore:

| CT-Komponente | Anthropic-Äquivalent | Bewertung |
|---------------|---------------------|-----------|
| **IC** | Constitutional Classifiers + ASL-3-Gates | ✅ **Stärker auf Model-Ebene** – Input/Output-Screening, aber kein architektonischer Veto-Mechanismus für Tool-Calls |
| **EL** | (nicht explizit Teil der CAI-Architektur) | ⚠️ **Fehlt** – Anthropic setzt auf Model-Safety, weniger auf Sandboxing |
| **SecurityStore** | Konstitution als Regelwerk, Petri-Audit-Logs | ✅ **Vergleichbar** – Die Konstitution ist ein read-only Regelwerk |

**Fazit:** Anthropic setzt primär auf **Model-inhärente Sicherheit** (HHH-Training, Konstitution, Classifier) statt auf architektonische Trennung. CTs IC+EL+SecurityStore ergänzt dies durch eine **strukturelle Sicherheitsebene**, die auch bei kompromittiertem Modell greift. Die Kombination beider Ansätze wäre ideal.

---

## 4. Ant Group – Adversarial AI Coding (AAC) Plugin (April 2026) ⭐⭐

| Aspekt | Details |
|--------|---------|
| **Repository** | github.com/antgroup/adversarial-ai-coding-plugin |
| **Konzept** | Self-Play-Sparring: "Elite-Hacker" vs. "Diligenter Entwickler" |
| **Typ** | IDE-Plugin (VS Code / JetBrains) |

### Sicherheitsmechanismen:

1. **Adversarial Engagement im selben Coding-Session:**
   - Ein LLM-Agent agiert als **Angreifer** (sucht Schwachstellen)
   - Ein LLM-Agent agiert als **Verteidiger** (behebt Schwachstellen)
   - **Iterative Iteration** bis zur Konvergenz

2. **Ergebnisse:**
   - Bis zu 48,2% des generierten Codes initial verwundbar
   - Top-Modelle: 37%–95,6% Verwundbarkeitsrate ohne AAC
   - AAC reduziert Verwundbarkeiten signifikant durch adversarialen Prozess

### Vergleich mit CTs IC+EL+SecurityStore:

| CT-Komponente | AAC-Äquivalent | Bewertung |
|---------------|----------------|-----------|
| **IC** | Adversarial Review („Skeptic Module") | ✅ **Stark** – integrierter gegnerischer Prüfer als IC-Instanz |
| **EL** | (nicht Teil des Plugins) | ❌ **Fehlt** – kein Sandboxing |
| **SecurityStore** | (nicht Teil des Plugins) | ❌ **Fehlt** |

**Fazit:** AAC implementiert das **Skeptic-Modul** des IC-Gates: ein adversarieller Review-Agent, der den generierten Code angreift. Dies ist eine konkrete Instanz von CTs IC-Idee, fokussiert auf Code Security. Ergänzt CT um den Aspekt des aktiven Angriffs statt nur passiver Prüfung.

---

## 5. NVIDIA NeMo Guardrails (2024–2026) ⭐⭐

| Aspekt | Details |
|--------|---------|
| **Repository** | github.com/NVIDIA-NeMo/Guardrails (Open Source) |
| **Typ** | Programmierbare Guardrail-Bibliothek für LLM-Anwendungen |

### Sicherheitsmechanismen:

1. **Fünf Rail-Typen:**
   - **Input Rails** – Filtern eingehender Prompts
   - **Output Rails** – Filtern ausgehender Antworten
   - **Dialog Rails** – Steuerung der Konversationsführung
   - **Retrieval Rails** – Absicherung von RAG-Datenquellen
   - **Action Rails** – Kontrolle von Tool-Ausführungen

2. **Programmierbar:** Colang-Sprache für Guardrail-Definition
3. **Multi-Layer:** Defense-in-Depth mit mehrstufigen Sicherheitsschichten

### Vergleich mit CTs IC+EL+SecurityStore:

| CT-Komponente | NeMo-Äquivalent | Bewertung |
|---------------|-----------------|-----------|
| **IC** | Action Rails + Input/Output Rails | ✅ **Gut** – programmierbare Sicherheitsgates auf Prompt- und Tool-Ebene |
| **EL** | (nicht Teil von NeMo) | ❌ **Fehlt** |
| **SecurityStore** | Retrieval Rails (teilweise) | ⚠️ **Ansatzweise** – schützt Wissensquellen, aber kein dedizierter Store |

**Fazit:** NeMo Guardrails ist eine **Prompt-Ebene-IC-Implementierung**. Es fehlen die architektonische Trennung (EL) und ein SecurityStore. Gut kombinierbar mit CTs Ansatz als zusätzliche Sicherheitsschicht.

---

## 6. NVIDIA NemoClaw + AgentIQ (GTC 2026) ⭐⭐

| Aspekt | Details |
|--------|---------|
| **Ankündigung** | GTC 2026 Keynote |
| **Typ** | Enterprise Agent Runtime mit Sicherheitsfokus |

### Sicherheitsmechanismen:

1. **NemoClaw:** OpenClaw Runtime + **Kernel-Level-Sandboxing**
2. **AgentIQ:** Open-Source Toolkit für Agent Composability
3. **Sicherheits-Wrapper** um zuvor verwundbare OpenClaw-Instanzen (24.478 ungesicherte Instanzen gefunden, kritische RCE)

### Vergleich mit CTs IC+EL+SecurityStore:

| CT-Komponente | NemoClaw-Äquivalent | Bewertung |
|---------------|--------------------|-----------|
| **IC** | (implizit, nicht primär) | ⚠️ **Schwach** – weniger Fokus auf Veto/Gates |
| **EL** | Kernel-Sandboxing der Runtime | ✅ **Stark** – Enterprise-Grade Sandboxing |
| **SecurityStore** | (nicht Teil des Systems) | ❌ **Fehlt** |

**Fazit:** NemoClaw ist primär eine **EL-Implementierung** (Sandbox auf Kernel-Ebene) als Reaktion auf RCE-Schwachstellen. Der IC- und SecurityStore-Aspekt fehlt. Interessant als Sandbox-Komponente für CTs Architektur.

---

## 7. Harness Engineering / PEV-Loops (2025–2026) ⭐⭐

| Aspekt | Details |
|--------|---------|
| **Konzept** | Plan-Execute-Verify (PEV) als strikte Phasen-Gates |
| **Quellen** | AugmentCode, "Code as Agent Harness" (arXiv:2605.18747), Medium-Artikel |

### Sicherheitsmechanismen:

1. **PEV-Loop mit Quality Gates:**
   - **Plan:** Agent erstellt Ausführungsplan
   - **Execute:** Ausführung in kontrollierter Umgebung
   - **Verify:** Automatische Verifikation vor nächstem Schritt
   - **Jede Phase** ist ein hartes Gate – keine Phase darf übersprungen werden

2. **Rules-Files, Constraints, Feedback-Loops:**
   - Deklarative Sicherheitsregeln
   - Automatische Verifikation und Rollback

### Vergleich mit CTs IC+EL+SecurityStore:

| CT-Komponente | PEV-Äquivalent | Bewertung |
|---------------|----------------|-----------|
| **IC** | Verify-Phase als hartes Gate | ✅ **Gut** – strukturierte Quality Gates |
| **EL** | Execute-Phase in isolierter Umgebung | ✅ **Vorhanden** |
| **SecurityStore** | Rules-Files (Constraints) | ⚠️ **Ansatzweise** |

**Fazit:** PEV implementiert IC und EL als **prozessuale Gates** – eine operationalisierte Version von CTs Konzept für Coding-Agenten.

---

## 8. Hopx / Bunnyshell – Coding Agent Sandboxes (2025–2026) ⭐

| Aspekt | Details |
|--------|---------|
| **Technologie** | Firecracker microVMs |
| **Startzeit** | <100ms |
| **Typ** | Ephemere, isolierte Ausführungsumgebungen |

### Sicherheitsmechanismen:

1. **Firecracker-basierte Isolation:** microVM-Level, nicht nur Container
2. **Ephemere Umgebungen:** automatische Zerstörung nach Nutzung
3. **Netzwerk-Policies:** granulare Kontrolle
4. **Ressourcen-Limits:** CPU, Memory, Disk

### Vergleich mit CTs IC+EL+SecurityStore:

| CT-Komponente | Hopx/Bunnyshell-Äquivalent | Bewertung |
|---------------|---------------------------|-----------|
| **IC** | (nicht Teil des Systems) | ❌ **Fehlt** |
| **EL** | Firecracker microVM | ✅✅ **Exzellent** – State-of-the-Art Sandboxing |
| **SecurityStore** | (nicht Teil des Systems) | ❌ **Fehlt** |

**Fazit:** Reine **EL-Implementierung** auf höchstem Niveau. Könnte als Sandbox-Backend für CTs Execution Layer dienen.

---

## 9. Galileo HITL-Oversight (2026) ⭐⭐

| Aspekt | Details |
|--------|---------|
| **Konzept** | Confidence-basierte Eskalation mit Human-in-the-Loop |
| **Quelle** | galileo.ai/blog/human-in-the-loop-agent-oversight |

### Sicherheitsmechanismen:

1. **Konfigurierbare Risikoschwellen:**
   - Agent handelt autonom unterhalb eines Confidence-Thresholds
   - Überschreitung → Eskalation an Menschen
   - VETO-Recht des Menschen für kritische Operationen

2. **Zentralisierte Policy-Architektur**
3. **Regulatorische Compliance-Frameworks**

### Vergleich mit CTs IC+EL+SecurityStore:

| CT-Komponente | Galileo-Äquivalent | Bewertung |
|---------------|-------------------|-----------|
| **IC** | Confidence-Threshold + HITL-Veto | ✅ **Sehr gut** – operationalisiertes VETO |
| **EL** | (nicht Teil des Systems) | ❌ **Fehlt** |
| **SecurityStore** | Policy-Datenbank | ⚠️ **Implizit** |

**Fazit:** Galileo implementiert das **Human-VETO** aus CTs IC sehr konkret mit definierten Schwellwerten – ein Pattern, das CT direkt übernehmen kann.

---

## 10. The Containment Gap (Juni 2026) ⭐ WICHTIGE WARNUNG

| Aspekt | Details |
|--------|---------|
| **Paper** | arXiv:2606.12797 |
| **Ergebnis** | Audit von LangChain, AutoGPT, OpenAI Agents SDK |

### Ergebnisse:

1. **Sechs Containment-Prinzipien** aus kompositionalem Agent-Modell abgeleitet
2. **0% native Compliance** in allen drei getesteten Frameworks
3. **Memory-Poisoning:** Ein einziger manipulierter Write erreicht 100% Korruption über 5 Modell-Backends
4. **Wrongful-Denial-Rate:** 88,9% nach Poisoning

### Vergleich mit CTs IC+EL+SecurityStore:

**Fazit:** Diese Studie **validiert CTs Architektur radikal**: Alle drei großen Agent-Frameworks haben KEINE architektonischen Sicherheitsgarantien. CTs IC+EL+SecurityStore-Kombination adressiert genau die sechs Containment-Prinzipien, die in der Studie als fehlend identifiziert wurden.

---

## 11. NIST AI RMF & ISO/IEC 42001 (Standards, 2024–2025) ⭐

| Aspekt | Details |
|--------|---------|
| **Framework** | NIST AI Risk Management Framework + Generative AI Profile (NIST.AI.600-1) |
| **ISO** | ISO/IEC 42001 (AI Management System), ISO/IEC 23894 |

### Anforderungen:
- Role-based Access Control
- Continuous Monitoring
- Adversarial Testing
- Lifecycle Logging & Traceability
- Human Oversight

### Vergleich mit CTs IC+EL+SecurityStore:

Diese Standards **untermauern CTs Ansatz normativ**: Alle drei Komponenten (IC, EL, SecurityStore) sind in den regulatorischen Anforderungen als Best Practices verankert.

---

## 12. Agentic AI Security: Threats, Defenses, Evaluation (Oktober 2025) ⭐

| Aspekt | Details |
|--------|---------|
| **Paper** | arXiv:2510.23883 – Umfassender Survey |
| **Thema** | Threats, Defenses, Benchmarks, Open Challenges |

### Relevante Defense-Strategien:

1. **Neural Sandboxing:** Output-Validierung gegen vordefinierte Label-Konzepte
2. **Execution Confinement:** Kontext-Isolation zur Reduzierung der Angriffsfläche
3. **Formal Safety Guarantees:** Ansätze zu beweisbarer Sicherheit

### Vergleich mit CTs IC+EL+SecurityStore:

Der Survey bestätigt CTs dreigliedrigen Ansatz als State-of-the-Art-Verteidigungsstrategie und identifiziert offene Herausforderungen bei der formalen Verifikation.

---

## 13. Layered Guardrail-Architekturen (2025–2026) ⭐

| Quellen | Diverse: Skywork, AgilityFeat, TrueFoundry, LiteLLM, Portkey, Kong |
|---------|-------------------------------------------------------------------|

### Gemeinsames Muster: **Defense-in-Depth**

1. **Model Safety Layer** – Prompt-Filtering, Toxicity Detection
2. **Tool Execution Layer** – Berechtigungsprüfung, Parameter-Validierung
3. **Policy Enforcement Layer** – Regelbasierte Veto-Mechanismen
4. **System Architecture Layer** – Prozessisolation, Audit-Logging

---

## Zusammenfassung: CTs IC+EL+SecurityStore im Vergleich

| System | IC-Veto | EL-Sandbox | SecurityStore | Offen | Reifegrad |
|--------|---------|-----------|---------------|-------|-----------|
| **OpenParallax** | ✅✅✅ 4-Tier | ✅✅✅ Kernel | ✅ Audit-Log | ✅ Open Source | Hoch |
| **ePCA** | ✅✅✅ Formal | ✅✅ isoliert | ✅ Constraints | ⚠️ Paper | Forschung |
| **Anthropic CAI** | ✅✅ Classifier | ❌ fehlt | ✅ Konstitution | ⚠️ Teilweise | Sehr Hoch |
| **AAC AntGroup** | ✅✅ Adversarial | ❌ fehlt | ❌ fehlt | ✅ Open Source | Mittel |
| **NeMo Guardrails** | ✅✅ 5 Rails | ❌ fehlt | ⚠️ Ansatz | ✅ Open Source | Hoch |
| **NemoClaw** | ⚠️ implizit | ✅✅✅ Kernel | ❌ fehlt | ✅ Open Source | Mittel |
| **PEV/Harness** | ✅✅ Verify-Gate | ✅ Execute | ⚠️ Rules | ⚠️ Konzept | Hoch |
| **Hopx** | ❌ fehlt | ✅✅✅ microVM | ❌ fehlt | ⚠️ Kommerziell | Hoch |
| **Galileo HITL** | ✅✅✅ Veto | ❌ fehlt | ⚠️ Policy | ❌ Kommerziell | Hoch |
| **Containment Gap** | ❌ 0% | ❌ 0% | ❌ 0% | – | Warnung |

### Kernaussagen:

1. **Kein existierendes System** implementiert alle drei CT-Komponenten (IC+EL+SecurityStore) vollständig
2. **OpenParallax** kommt CTs Vision am nächsten (IC+EL+Audit), hat aber keinen dedizierten SecurityStore
3. **IC (Inhibitory Control)** ist in vielen Systemen vorhanden, aber meist auf Prompt-Ebene – CTs architektonischer IC-Ansatz ist robuster
4. **EL (Execution Layer)** wird häufig vernachlässigt – die Containment-Gap-Studie zeigt katastrophale Konsequenzen
5. **SecurityStore** (read-only Wissensbasis) ist das am meisten fehlende Element – fast kein System hat dies explizit
6. **CTs Kombination ist einzigartig** und adressiert genau die Lücken, die in der Forschung 2025–2026 als kritisch identifiziert wurden

### Empfehlung für CT:

- **IC:** OpenParallax 4-Tier-Shield + Galileo Confidence-Thresholds + AAC Adversarial Review kombinieren
- **EL:** Hopx/Firecracker microVMs oder OpenParallax Kernel-Sandboxing als Execution-Backend
- **SecurityStore:** Als eigenständige Innovation entwickeln – keine existierende Implementierung deckt dies ab
- **Formale Verifikation:** ePCA-Ansatz für besonders kritische Operationen integrieren
- **Audit:** Petri für kontinuierliches adversariales Testing einsetzen
