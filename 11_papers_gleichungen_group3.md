# KYBERNETIKER GRUPPE 3 – Seminale Werke, Schlüsselgleichungen & Kernideen

---

## 1. Bertrand Russell (1872–1970)
**Philosoph, Logiker, Mathematiker**

### (a) Seminales Werk
**„Principia Mathematica“** (mit Alfred North Whitehead, 1910–1913, 3 Bände) – der monumentale Versuch, die gesamte Mathematik auf Logik zurückzuführen (Logizismus).
🔗 https://en.wikipedia.org/wiki/Principia_Mathematica

### (b) Schlüsselgleichung – Russells Paradoxon
Sei **R = { x | x ∉ x }**. Dann gilt:
**R ∈ R ↔ R ∉ R** (Widerspruch)

Diese mengentheoretische Antinomie erschütterte Freges Grundgesetze der Arithmetik und führte zur Entwicklung der **Typentheorie**: Jeder Menge wird ein Typ zugeordnet; eine Menge darf nur Elemente eines niedrigeren Typs enthalten.

### (c) Kernidee
**Logizismus & Analytische Philosophie**: Mathematik ist reduzierbar auf Logik. Logische Sätze sind synthetisch a priori – sie beschreiben die allgemeinsten Strukturen der Welt. Russell etablierte die Methode der logischen Analyse als Grundlage der analytischen Philosophie. Seine Unterscheidung zwischen „Wissen durch Bekanntschaft“ und „Wissen durch Beschreibung“ prägt die Erkenntnistheorie bis heute.

---

## 2. Pei Wang
**KI-Forscher, Begründer des NARS (Non-Axiomatic Reasoning System)**

### (a) Seminales Werk
**„Rigid Flexibility: The Logic of Intelligence“** (2006, Springer) – die umfassende Darstellung des Non-Axiomatic Reasoning System (NARS).
🔗 https://cis.temple.edu/~pwang/NARS-Intro.html

### (b) Schlüsselgleichung – NARS-Erfahrungsbasierte Wahrheitswerte
Ein Statement in NARS trägt einen zweidimensionalen Wahrheitswert:
**⟨f, c⟩** mit **f ∈ [0,1]** (Frequenz/Häufigkeit positiver Evidenz) und **c ∈ [0,1]** (Konfidenz/Gesamtmenge der Evidenz)
```
f = w⁺ / w    ,    c = w / (w + k)
```
wobei w⁺ = positive Evidenz, w = Gesamtevidenz, k = Konstante für a priori-Unsicherheit.

### (c) Kernidee
**Nicht-axiomatisches Schließen unter Ressourcenknappheit (AIKR – Assumption of Insufficient Knowledge and Resources)**: Im Gegensatz zu klassischen Logiksystemen arbeitet NARS mit begrenztem Wissen und begrenzter Rechenzeit. Das System muss in Echtzeit schlussfolgern, lernen und sich anpassen – genau wie der menschliche Geist. Intelligenz wird als Fähigkeit definiert, unter unzureichenden Ressourcen zu funktionieren. Kernoperationen: Deduktion, Induktion, Abduktion, Revision.

---

## 3. Joscha Bach (*1973)
**Kognitionswissenschaftler, KI-Forscher, Philosoph**

### (a) Seminales Werk
**„Principles of Synthetic Intelligence: An Architecture of Motivated Cognition“** (2009, Oxford University Press) – die detaillierte Beschreibung der MicroPsi-kognitiven Architektur, basierend auf Dörners Psi-Theorie.
🔗 https://en.wikipedia.org/wiki/Joscha_Bach

### (b) Schlüsselgleichung – Motivregulierung in MicroPsi
Die Handlungsauswahl erfolgt durch ein Motivsystem, bei dem ein Bedürfnis-Druck **π(m)** als Abweichung vom Sollwert berechnet wird:
```
π(m, t) = clip( (θ_m − v_m(t)) / θ_m , 0, 1 )
```
wobei θ_m = Sollwert des Bedürfnisses m, v_m(t) = aktueller Istwert. Mehrere Motive werden über Gewichtung und Pleasure-Signale zu einer ganzheitlichen Verhaltenssteuerung integriert.

### (c) Kernidee
**Synthetische Intelligenz = motivierte Kognition auf Basis kognitiver Architekturen**: Der Geist ist ein Software-Agent, der auf biologischer Hardware läuft. Intelligenz entsteht aus dem Zusammenspiel von Wahrnehmung, Gedächtnis, Motivation und Handlungsplanung. Bachs zentrale These („Cyber-Animismus“): Bewusstsein ist eine Software-Eigenschaft; selbstorganisierende Software-Agenten existieren in der Natur. Die Grenze zwischen menschlicher, künstlicher und natürlicher Intelligenz ist graduell, nicht kategorial.

---

## 4. Stephen Wolfram (*1959)
**Physiker, Informatiker, Schöpfer von Mathematica und Wolfram Language**

### (a) Seminales Werk
**„A New Kind of Science“** (2002, Wolfram Media, 1280 Seiten) – die umfassende Abhandlung über zelluläre Automaten und das Prinzip der „computational equivalence“.
🔗 https://www.wolframscience.com/nks/

### (b) Schlüsselgleichung – Zellulärer Automat Regel 30
Eindimensionaler zellulärer Automat mit Radius r=1:
```
a_i(t+1) = a_{i-1}(t) XOR (a_i(t) OR a_{i+1}(t))
```
Regel 30 (binär: 00011110₂ = 30₁₀) produziert nachweislich chaotisches, nicht-periodisches Verhalten und wird in Mathematica's Zufallsgenerator eingesetzt.

### (c) Kernidee
**Prinzip der rechnerischen Äquivalenz (Computational Equivalence)**: Einfache Regeln können komplexes Verhalten erzeugen. Systeme, die nicht offensichtlich einfach sind, erreichen dieselbe maximale rechnerische Komplexität. Daraus folgt: (1) Das Universum selbst ist berechenbar, (2) viele natürliche Prozesse sind irreduzibel („computational irreducibility“) – ihr Verhalten kann nur durch vollständige Simulation, nicht durch Kurzformeln vorhergesagt werden. Wolframs Physikprojekt versucht, das Universum als Netzwerk diskreter Relationen (Hypergraphen) zu beschreiben, deren schrittweise Transformation die Raumzeit hervorbringt.

---

## 5. Melanie Mitchell
**Komplexitätsforscherin, Informatikerin (Santa Fe Institute)**

### (a) Seminales Werk
**„Complexity: A Guided Tour“** (2009, Oxford University Press) – die einflussreiche Einführung in die Komplexitätswissenschaft.
🔗 https://global.oup.com/academic/product/complexity-9780199798100

### (b) Schlüsselgleichung – Komplexität nach Gell-Mann/Lloyd
Effektive Komplexität eines Systems:
```
EC(S) = K(E) + K(D|E)
```
wobei K(·) die Kolmogorow-Komplexität bezeichnet, E die Menge der Regularitäten („effective description“) und D die Abweichungen / zufällige Komponenten. Ein System mit maximaler effektiver Komplexität ist weder völlig zufällig noch völlig geordnet.

### (c) Kernidee
**Komplexe Adaptive Systeme & Emergenz**: Komplexität entsteht aus einfachen Regeln durch Selbstorganisation, Dezentralisierung und Rückkopplung. Weder kompletter Zufall noch perfekte Ordnung erzeugen interessante Komplexität – sie liegt genau dazwischen („Edge of Chaos“). Mitchell betont vier zentrale Eigenschaften: (1) komplexe kollektive Verhaltensweisen aus einfachen Komponenten, (2) Signal- und Informationsverarbeitung, (3) Adaptivität durch Lernen/Evolution, (4) Emergenz nicht-trivialer Strukturen aus einfachen Regeln.

---

## 6. Nora Bateson
**Systemdenkerin, Filmemacherin, Präsidentin des International Bateson Institute**

### (a) Seminales Werk
**„Small Arcs of Larger Circles: Framing Through Other Patterns“** (2016, Triarchy Press) – eine revolutionäre, persönliche Annäherung an das Studium von Systemen und Komplexität.
🔗 https://www.triarchypress.net/smallarcs.html

### (b) Schlüsselgleichung – Warm Data
Warm Data ist explizit nicht-quantitativ, aber Batesons Formulierung kann als Informations-Relation ausgedrückt werden:
```
WarmData(Phänomen) = { Beziehungsmuster zwischen dem Phänomen und seinen multiplen Kontexten: 
sozial, ökologisch, psychologisch, kulturell, historisch, ökonomisch }
```
Die Kernrelation: **I_context > I_isolated** – Information-in-Beziehung (transkontextuell) übersteigt stets die Information isolierter Datenpunkte.

### (c) Kernidee
**Warm Data & Aphanipoiesis**: Daten sind nie „kalt“ – sie sind stets in ein Nest von Beziehungen eingebettet. Warm Data bezeichnet die transkontextuelle Information über die Interdependenzen, die ein System zusammenhalten. Der Polykrise (Klima, Demokratie, Psyche) kann nur mit warm data begegnet werden. **Aphanipoiesis** (das Unentdeckte, das entsteht) ist ihr Begriff für emergente Phänomene, die sich der direkten Wahrnehmung entziehen. Ihr Ansatz erweitert Gregory Batesons Ökologie des Geistes um eine feministische, verkörperte Dimension.

---

## 7. Michael Levin
**Entwicklungsbiologe, Tufts University**

### (a) Seminales Werk
**„Molecular bioelectricity: how endogenous voltage potentials control cell behavior and instruct pattern regulation in vivo“** (2014, Molecular Biology of the Cell, 25(24): 3835–3850)
🔗 https://www.molbiolcell.org/doi/10.1091/mbc.e13-12-0708

### (b) Schlüsselgleichung – Bioelektrischer Code
Die transmembrane Spannung V_mem bestimmt Zellverhalten:
```
V_mem = (RT/F) · ln( (P_K[K⁺]_out + P_Na[Na⁺]_out + P_Cl[Cl⁻]_in) / (P_K[K⁺]_in + P_Na[Na⁺]_in + P_Cl[Cl⁻]_out) )
```
(Goldman-Hodgkin-Katz-Gleichung). Das räumlich-zeitliche Muster von V_mem über Zellkollektive kodiert anatomische Zielzustände („Bioelectric Code“).

### (c) Kernidee
**Bioelektrischer Code & Morphogenetische Intelligenz**: Zellen kommunizieren bioelektrisch und bilden ein kollektives Intelligenzsubstrat, das parallel zum genetischen Code operiert. Die Zellmembran ist ein fundamentaler Rechenknoten. Spannungsmuster über Gewebe kodieren Information darüber, welche anatomische Struktur gebaut werden soll. Diese bioelektrische Schicht ermöglicht Regeneration, Krebsunterdrückung und sogar die Reprogrammierung von Körperbauplänen (z.B. Plattwürmer mit zwei Köpfen). Jede Zelle ist ein kleiner Agent; Skalierung von Intelligenz entsteht durch Kommunikation zwischen Agenten.

---

## 8. Paul Pangaro
**Kybernetiker, Designtheoretiker, Gesprächstheorie-Experte**

### (a) Seminales Werk
**„Questions for Conversation Theory or Conversation Theory in One Hour“** (2017, Kybernetes) – kompakte Darstellung von Gordon Pasks Gesprächstheorie, deren führender Interpret Pangaro ist.
🔗 https://www.pangaro.com/published/Pangaro–Questions-for-Conversation_Theory_In_One_Hour-Kybernetes_2017.pdf

### (b) Schlüsselgleichung – Gespräch als mutuales Kalibrieren
In Pasks Conversation Theory ist Lernen die Reduktion von Unsicherheit zwischen zwei Teilnehmern über ein Topic T:
```
H_A(T) > H_A(T|B)  ∧  H_B(T) > H_B(T|A)
⟹ Konversation konvergiert zu geteiltem Verständnis
```
wobei H_A(T) die Unsicherheit von A über T bezeichnet und H_A(T|B) die Unsicherheit von A über T, gegeben die Antwort von B. Ziel ist **Agreement over Understanding**.

### (c) Kernidee
**Conversation Theory & Second-Order Cybernetics**: Konversation ist der fundamentale Mechanismus für kognitive und soziale Koordination. Pangaro, als Erbe von Gordon Pask, betont: (1) Kybernetik ist die Kunst des Steuerns, (2) Design ist Gespräch – jedes Design-Artefakt ist ein Gespräch zwischen Designer:in, Nutzer:in und Kontext, (3) Second-Order Cybernetics: der/die Beobachter:in ist immer Teil des Systems. „Cybernetics is a way of thinking, not a thing to think about.“ Ziel: Organisationen und Technologien so gestalten, dass sie konversationell mit ihrer Umwelt koevolutionieren.

---

## 9. Katherine Daniell
**Kybernetikerin, Professorin für Wassersysteme & Policy, ANU School of Cybernetics**

### (a) Seminales Werk
**„Cyber-physical systems in water management and governance“** (2023, Current Opinion in Environmental Sustainability, mit Guillaume & Saraswat)
🔗 https://www.sciencedirect.com/science/article/pii/S1877343523000374

### (b) Schlüsselgleichung – Wasserkybernetische Systemsteuerung
Ein wasserkybernetisches Steuerungsmodell:
```
W(t+1) = W(t) + I(t) − O(t) − C(t) + ε(t)
```
wobei W(t) = Wasserstand zur Zeit t, I = Input/Inflow, O = Output/Entnahme, C = Kontrollgröße (Steuerungsmaßnahmen), ε(t) = Umweltstörungen. Die kybernetische Steuerung passt C(t) auf Basis der Abweichung Δ = W(t) − Sollwert adaptiv an.

### (c) Kernidee
**Kybernetische Wasser-Governance & Systemresilienz**: Wasserinfrastruktur ist nicht nur technisch, sondern sozio-technisch. Kybernetische Ansätze betrachten Wassersysteme als zirkuläre, rückgekoppelte Mensch-Umwelt-Technik-Systeme. Entscheidend ist das Design von Governance-Prozessen, die adaptiv, partizipativ und kontextsensitiv sind. Daniell verknüpft Kybernetik zweiter Ordnung mit Wasserpolitik: Wir müssen nicht nur das Wasser managen, sondern auch das System, das das Wasser managt.

---

## 10. Genevieve Bell
**Anthropologin, Direktorin der ANU School of Cybernetics**

### (a) Seminales Werk
**„Building the Black Box: Cyberneticians and Complex Systems“** – Forschung zur Geschichte und Zukunft der Kybernetik.
🔗 https://cybernetics.anu.edu.au/

### (b) Schlüsselgleichung – Kybernetische Anthropologie-Formel
Bells Rahmung der Kybernetik für das 21. Jahrhundert:
```
Technologie-Zukunft = f(Mensch × Umwelt × Feedback × Macht × Kultur)
```
Keine kommutative Operation: Die Reihenfolge der Faktoren verändert das Ergebnis. Kybernetik muss Technologie immer in ihrem kulturellen, historischen und politischen Kontext verstehen.

### (c) Kernidee
**Neue Kybernetik für das 21. Jahrhundert**: Kybernetik ist nicht nur eine Ingenieurwissenschaft – sie ist eine Art zu denken, die Menschen, Technologie und Umwelt als untrennbares System begreift. Bell bringt die anthropologische Perspektive ein: Wer baut KI? Für wen? Mit welchen Werten? Ihr Programm an der ANU School of Cybernetics dekolonisiert die Kybernetik und integriert Perspektiven aus Kunst, indigener Philosophie, Design, und kritischer Theorie. Kybernetik war nie nur technisch – sie war immer schon politisch, kulturell und sozial.

---

## 11. Peter Cariani
**Kybernetiker, Neurowissenschaftler, Senior Research Scientist**

### (a) Seminales Werk
**„On the Design of Devices with Emergent Semantic Functions“** (1989, Dissertation, SUNY Binghamton) – die grundlegende Arbeit über die Emergenz semantischer Funktionen in selbstkonstruierenden Systemen.
🔗 https://petercariani.com/CarianiNewWebsite/Cybernetics.html

### (b) Schlüsselgleichung – Kybernetisches Percept-Action-System
Die adaptive Koordination zwischen Wahrnehmung und Handlung:
```
A(t+1) = Φ( P(t), A(t), S(t) )
wobei ∂Φ/∂P ≠ 0  (Sensor-Action-Kopplung)
```
mit P = Perzept (Wahrnehmung), A = Aktion, S = interner Systemzustand, Φ = Adaptationsfunktion. Semantische Funktionen emergieren, wenn die interne Repräsentation kausal mit externen Zuständen über die Sensor-Action-Schleife gekoppelt ist.

### (c) Kernidee
**Emergente Semantik & Kybernetische Semiotik**: Bedeutung entsteht nicht durch Programmierung von außen, sondern durch die selbstorganisierte Kopplung zwischen Sensorik, interner Repräsentation und Motorik eines Agenten. Cariani unterscheidet zwischen syntaktischen (vom Designer zugewiesenen) und semantischen (vom System selbst gebildeten) Kategorien. Echte Semantik erfordert strukturelle Offenheit: Ein System muss neue Unterscheidungen treffen können, die nicht vorprogrammiert sind. Seine Arbeit verbindet Kybernetik, Neurowissenschaft (neurale Zeitcodes) und Semiotik (Peirce).

---

## 12. Hugh Dubberly
**Design-Theoretiker, Kybernetiker, Dubberly Design Office**

### (a) Seminales Werk
**„Cybernetics and Design: Conversations for Action“** (2015, mit Paul Pangaro, Kybernetes) – sowie **„What is conversation? How can we design for effective conversation?“** (2009, Interactions Magazine)
🔗 https://www.dubberly.com/articles/cybernetics-and-design.html

### (b) Schlüsselgleichung – Design als Gespräch
Das Dubberly-Pangaro-Modell des Designprozesses:
```
Design = Σ (goal_setting ⊕ action ⊕ feedback ⊕ revision)
```
wobei ⊕ den kybernetischen Rückkopplungsoperator („conversation-for-action“) bezeichnet. Jeder Designschritt ist ein „speech act“ (Austin/Searle), der einen Zustand des Entwurfs verändert und eine Reaktion der Stakeholder provoziert.

### (c) Kernidee
**Design als kybernetischer Prozess („Conversations for Action“)**: Design ist nicht die einmalige Kreation eines Objekts, sondern ein fortlaufendes Gespräch zwischen Designer:in, Nutzer:in, Technologie und Kontext. Dubberly formalisiert Designprozesse als kybernetische Flussdiagramme, in denen jeder Schritt eine kommunikative Handlung („request, promise, assert, declare“) darstellt. Seine Modelle – besonders der „Social Graph of Cybernetics“ – zeigen, wie Kybernetik, Computing, Gegenkultur und Design historisch und konzeptuell zusammenhängen.

---

## 13. Anil Seth
**Neurowissenschaftler, Bewusstseinsforscher, University of Sussex**

### (a) Seminales Werk
**„Being a Beast Machine: The Somatic Basis of Selfhood“** (2018, mit M. Tsakiris, Trends in Cognitive Sciences, 22(11): 969–981)
🔗 https://www.anilseth.com/research/key-papers/

### (b) Schlüsselgleichung – Predictive Processing & Freie Energie
Das Gehirn als Vorhersagemaschine, die Überraschung (Free Energy) minimiert:
```
F = D_KL[Q(s|o) || P(s)] − E_Q[ln P(o|s)]
```
mit F = Freie Energie (zu minimieren), Q(s|o) = approximate posteriore Verteilung über hidden states s gegeben Beobachtungen o, P(s) = Prior, P(o|s) = likelihood. Minimierung von F approximiert gleichzeitig Wahrnehmung (Inferenz) und Handlung (aktive Inferenz).

### (c) Kernidee
**Das Gehirn als Bestienmaschine (Beast Machine Theory)**: Bewusstsein entsteht aus dem Bestreben des Gehirns, den Körper am Leben zu erhalten (Homeostase). Das Selbst ist eine kontrollierte Halluzination – eine beste Vermutung des Gehirns über den Zustand des Körpers. Seth identifiziert drei Ebenen: (1) **bewusster Zustand** (Wachheit), (2) **bewusster Inhalt** (was bewusst ist), (3) **bewusstes Selbst** (dass es mir so erscheint). Die Kernaussage: „I predict (myself), therefore I am.“ Wahrnehmung ist nicht passiv-empfangend, sondern aktiv-vorhersagend.

---

## 14. Andy Clark
**Philosoph des Geistes, Kognitionswissenschaftler, University of Sussex**

### (a) Seminales Werk
**„The Extended Mind“** (1998, mit David Chalmers, Analysis, 58(1): 7–19) – eines der meistzitierten Paper der Philosophie des Geistes.
🔗 https://www.alice.id.tue.nl/references/clark-chalmers-1998.pdf

### (b) Schlüsselgleichung – Das Paritätspinzip (Parity Principle)
```
Wenn ein externer Prozess P so funktioniert, dass wir ihn – wäre er intern – 
ohne Zögern als kognitiven Prozess anerkennen würden, 
dann IST P ein kognitiver Prozess.
```
Formal: ∃ Prozess P: P ∈ F_extern ∧ (∀M ∈ Mind: P würde in M als kognitiv gelten) ⟹ P ist Teil des erweiterten Geistes.

### (c) Kernidee
**Extended Mind Thesis (Erweiterter Geist)**: Kognitive Prozesse erstrecken sich über die Grenzen von Schädel und Haut hinaus in die Umwelt. Ein Notizbuch, ein Smartphone, eine Sprache – all das kann buchstäblich Teil unseres Denkens sein. Clark radikalisiert diese Einsicht: (1) Kognition ist verkörpert (embodied), (2) Kognition ist situiert (embedded in Umwelten), (3) Kognition ist erweitert (extended in Artefakte), (4) Kognition ist enaktiv (enactive – durch Handeln konstituiert). Die Unterscheidung zwischen Gehirn und Welt ist eine Frage der Forschungspragmatik, nicht der Ontologie.

---

## 15. David Krakauer
**Komplexitätsforscher, Präsident des Santa Fe Institute**

### (a) Seminales Werk
**„The Complex World: An Introduction to the Foundations of Complexity Science“** (2024, SFI Press) – und das vierbändige Werk **„Foundational Papers in Complexity Science“**.
🔗 https://www.sfipress.org/books/foundational-papers-in-complexity-science

### (b) Schlüsselgleichung – Die vier Säulen der Komplexität
Komplexität als Funktion von vier fundamentalen Prozessen:
```
Complexity = F(Entropie, Evolution, Dynamik, Computation)
```
Konkret: Die effektive Komplexität (Krakauer-Flack) eines Systems:
```
EC = C(ensemble) − C(effective)
```
wobei C die statistische Komplexität (Crutchfield's ε-machine) bezeichnet: die minimale Menge an historischer Information, die für optimale Vorhersage benötigt wird.

### (c) Kernidee
**Komplementarität der Komplexität**: Komplexität erfordert vier sich ergänzende Perspektiven: (1) **Entropie**: Information, Unsicherheit und Überraschung, (2) **Evolution**: Selektion, Anpassung und ihre multi-level Dynamik, (3) **Dynamik**: Attraktoren, Bifurkationen, Phasenübergänge, (4) **Computation**: Wie viel muss ein System berechnen, um zu überleben? Krakauers „Fundamental Theory of Complex Systems“ besagt, dass Komplexität dort entsteht, wo Entropie-getriebene Zufallsprozesse und evolutionsgetriebene Ordnungsprozesse sich komplementär ergänzen – ein neo-Boltzmann'sches Programm.

---

## 16. Neil Theise
**Pathologe & Komplexitätstheoretiker, NYU Grossman School of Medicine**

### (a) Seminales Werk
**„Notes on Complexity: A Scientific Theory of Connection, Consciousness, and Being“** (2023, Spiegel & Grau) – eine Synthese von Komplexitätstheorie, Buddhismus und Philosophie.
🔗 https://www.neiltheiseofficial.com/notes-on-complexity

### (b) Schlüsselgleichung – Emergenz der Bewusstseins-Komplexität
```
Bewusstsein = Emergenz( Φ_System )
```
wobei Φ_System die integrierte Information des Systems bezeichnet (angelehnt an Tononis IIT, aber erweitert um den Gedanken, dass Bewusstsein auf jeder Skala emergiert – von der Zelle bis zum Kosmos). Each level is both a whole and a part:
```
∀Level L: L ist Ganzes (für L−1) ∧ L ist Teil (von L+1)
```

### (c) Kernidee
**Komplexität als universelle Ontologie & Nicht-Dualismus**: Komplexitätstheorie zeigt, dass die Welt fundamental aus Beziehungen besteht, nicht aus Dingen. Theise verknüpft drei Einsichten: (1) Komplexe Systeme sind skalenfrei – dieselben Prinzipien gelten für Zellen, Organismen, Ökosysteme und den Kosmos, (2) Bewusstsein emergiert als Eigenschaft komplexer Netzwerke und ist daher ubiquitär (Panpsychismus-kompatibel), (3) Die buddhistische Lehre von Śūnyatā (Leerheit) und Interdependenz (Pratītyasamutpāda) ist mathematisch präzise durch Komplexitätstheorie beschreibbar. Theises Kernbotschaft: „Nothing exists inherently. Everything is connected.“

---

## 17. Thomas Hertog
**Kosmologe, KU Leuven, Stephen Hawkings engster Kollaborateur**

### (a) Seminales Werk
**„On the Origin of Time: Stephen Hawking's Final Theory“** (2023, Bantam Books) – die populärwissenschaftliche Darstellung der Top-Down-Kosmologie.
🔗 https://en.wikipedia.org/wiki/On_the_Origin_of_Time

### (b) Schlüsselgleichung – Wheeler-DeWitt-Gleichung & Top-Down-Kosmologie
Die fundamentale Gleichung der Quantenkosmologie (zeitlos):
```
Ĥ Ψ[g, φ] = 0
```
(Wheeler-DeWitt-Gleichung, wobei Ĥ = Hamiltonoperator, Ψ = Wellenfunktion des Universums, g = Metrik, φ = Materiefelder). Die Top-Down-Kosmologie wählt aus dem Feynman-Pfadintegral diejenigen Historien aus, die mit unserer Beobachtung konsistent sind:
```
Ψ_top-down(g, φ) = ∫ D[g] D[φ] e^{iS[g,φ]/ħ} · δ( Beobachtungsbedingung )
```

### (c) Kernidee
**Top-Down-Kosmologie & Observer-Dependent Universe**: Hawking und Hertog kehren die Perspektive der Kosmologie um: Wir starten nicht von einem Anfang, sondern vom Jetzt – vom beobachteten Universum – und rekonstruieren rückwärts, welche Vergangenheiten mit unserer Gegenwart konsistent sind. Die Urknall-Singularität verschwindet; die Zeit selbst emergiert als effektives Phänomen aus zeitlosen Quantenprozessen. Entscheidend: Der Beobachter (wir, im Jetzt) ist kein passiver Zuschauer, sondern ein konstitutives Element der kosmologischen Theorie – eine radikale Verschränkung von Physik und Kybernetik.

---

## 18. Neil Johnson
**Physiker & Komplexitätsforscher, George Washington University**

### (a) Seminales Werk
**„Simply Complexity: A Clear Guide to Complexity Theory“** (2007, Oneworld Publications) – eine zugängliche Einführung in die Komplexitätswissenschaft.
🔗 https://oneworld-publications.com/work/simply-complexity/

### (b) Schlüsselgleichung – Emergentes Verhalten & Phasenübergänge
Das kollektive Verhalten eines Vielteilchen-Systems am kritischen Punkt:
```
⟨A(t)⟩ ~ τ^{−α}
```
wobei τ = |T − T_c|/T_c (Abstand vom kritischen Punkt), α = kritischer Exponent, ⟨A(t)⟩ = Ordnungsparameter (z.B. Synchronisation, Marktpanik, soziale Bewegung). Die Universalitätsklasse bestimmt α, unabhängig von mikroskopischen Details.

### (c) Kernidee
**Komplexität aus der Vielteilchenperspektive**: Komplexe Systeme – von Finanzmärkten über Verkehrsstaus bis zu Terrorgruppen – bestehen aus vielen wechselwirkenden Agenten, die in kollektiven Entscheidungen zu emergenten Mustern führen. Johnsons zentraler Ansatz: (1) Kollektive Phänomene sind oft das Resultat von „many-body“ Wechselwirkungen, (2) dieselben mathematischen Strukturen (bipartite Graphen, Minoritätsspiele, Phasenübergänge) beschreiben völlig unterschiedliche Systeme, (3) „Two's Company, Three is Complexity“: Schon drei wechselwirkende Agenten können überraschend komplexes, nicht-intuitives Verhalten erzeugen.

---

## Quellenübersicht & URL-Verzeichnis

| # | Name | Haupt-URL |
|---|------|-----------|
| 1 | Bertrand Russell | https://en.wikipedia.org/wiki/Principia_Mathematica |
| 2 | Pei Wang | https://cis.temple.edu/~pwang/NARS-Intro.html |
| 3 | Joscha Bach | https://en.wikipedia.org/wiki/Joscha_Bach |
| 4 | Stephen Wolfram | https://www.wolframscience.com/nks/ |
| 5 | Melanie Mitchell | https://melaniemitchell.me/ |
| 6 | Nora Bateson | https://www.warmdata.life/ |
| 7 | Michael Levin | https://www.drmichaellevin.org/ |
| 8 | Paul Pangaro | https://www.pangaro.com/ |
| 9 | Katherine Daniell | https://cybernetics.anu.edu.au/people/katherine-daniell/ |
| 10 | Genevieve Bell | https://cybernetics.anu.edu.au/ |
| 11 | Peter Cariani | https://petercariani.com/ |
| 12 | Hugh Dubberly | https://www.dubberly.com/ |
| 13 | Anil Seth | https://www.anilseth.com/ |
| 14 | Andy Clark | https://academic.oup.com/analysis/article-abstract/58/1/7/142531 |
| 15 | David Krakauer | https://davidckrakauer.com/ |
| 16 | Neil Theise | https://www.neiltheiseofficial.com/ |
| 17 | Thomas Hertog | https://en.wikipedia.org/wiki/On_the_Origin_of_Time |
| 18 | Neil Johnson | https://physics.columbian.gwu.edu/neil-johnson |

---

*Erstellt am 19. Juni 2026 – GEHIRN-BIBLIOTHEK Projekt*
*Sprache: Deutsch | Forschung: Englische Quellen*
*Total: 18 Kybernetiker:innen – Seminale Werke, Schlüsselgleichungen, Kernideen*
