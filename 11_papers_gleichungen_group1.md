# Kybernetiker Gruppe 1 — Seminale Arbeiten, Schlüsselgleichungen & Kernideen

> **Forschungsdokumentation** — Recherchiert auf Englisch, verfasst auf Deutsch.
> Enthält für jede/n der 14 Kybernetiker/in: (a) seminales Paper mit URL, (b) mathematische Schlüsselgleichung mit Erläuterung, (c) Kernidee in einem Satz.

---

## 1. Norbert Wiener (1894–1964)

### (a) Seminales Werk
**„Cybernetics: Or Control and Communication in the Animal and the Machine“** (1948)
🔗 [https://archive.org/details/cyberneticsorcon0000wien](https://archive.org/details/cyberneticsorcon0000wien)

### (b) Schlüsselgleichung
**Wiener-Filter (optimale Signalvorhersage):**

$$H(\omega) = \frac{S_{xs}(\omega)}{S_{ss}(\omega)}$$

**Erläuterung:** Der Wiener-Filter ist die optimale lineare Übertragungsfunktion zur Trennung eines Nutzsignals von einem Rauschsignal. $H(\omega)$ ist die Filter-Übertragungsfunktion im Frequenzbereich, $S_{xs}(\omega)$ die Kreuzleistungsdichte zwischen Eingangssignal $x$ und gewünschtem Signal $s$, und $S_{ss}(\omega)$ die Autoleistungsdichte des gewünschten Signals. Dies ist die mathematische Grundlage für die Vorhersage und Regelung durch negative Rückkopplung — das Kernprinzip der Kybernetik.

### (c) Kernidee
**Lebewesen und Maschinen teilen die fundamentalen Prinzipien der Rückkopplung und Kommunikation: Kontrolle geschieht durch Informationsaustausch und negative Rückkopplung, nicht durch lineare Kausalität.**

---

## 2. Claude Shannon (1916–2001)

### (a) Seminales Werk
**„A Mathematical Theory of Communication“** (1948), Bell System Technical Journal, Vol. 27, S. 379–423, 623–656.
🔗 [https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf)

### (b) Schlüsselgleichung
**Shannon-Entropie (Informationsentropie):**

$$H = -\sum_{i=1}^{n} p_i \log_2 p_i$$

**Erläuterung:** $H$ ist die Entropie einer diskreten Zufallsvariable mit $n$ möglichen Werten, wobei $p_i$ die Wahrscheinlichkeit des $i$-ten Wertes ist. Die Entropie misst den durchschnittlichen Informationsgehalt (in Bits) bzw. die Unsicherheit einer Nachrichtenquelle. Sie bildet das Fundament der gesamten Informationstheorie und definiert die absolute Grenze verlustfreier Datenkompression sowie die Kanalkapazität $C = \max_{p(x)} I(X;Y)$.

### (c) Kernidee
**Jede Form von Kommunikation — ob Sprache, Bilder oder Daten — kann mathematisch als Übertragung von Information über einen verrauschten Kanal modelliert werden, wobei die Entropie das fundamentale Maß für Unsicherheit und Informationsgehalt darstellt.**

---

## 3. W. Ross Ashby (1903–1972)

### (a) Seminales Werk
**„An Introduction to Cybernetics“** (1956), London: Chapman & Hall.
🔗 [https://archive.org/details/introductiontocy00ashb](https://archive.org/details/introductiontocy00ashb)

### (b) Schlüsselgleichung
**Ashbys Gesetz der erforderlichen Varietät (Law of Requisite Variety):**

$$V_R \geq V_D \quad \text{bzw.} \quad V(E) \leq V(R)$$

**Erläuterung:** $V_R$ ist die Varietät (Anzahl möglicher Zustände) des Reglers, $V_D$ die Varietät der Störung (bzw. $V(E)$ die Varietät der Umwelt). Damit ein System stabil kontrolliert werden kann, muss der Regler mindestens ebenso viele unterscheidbare Zustände aufweisen können wie die zu regelnde Störung. Anders formuliert: **Nur Varietät kann Varietät absorbieren/zerstören.** Dies ist das fundamentale Prinzip der Steuerungskomplexität.

### (c) Kernidee
**Ein Kontrollsystem muss mindestens so viele Zustände (Varietät) besitzen wie das zu kontrollierende System — effektive Kontrolle erfordert ein der Umweltkomplexität entsprechendes internes Repertoire an Reaktionsmöglichkeiten.**

---

## 4. Warren McCulloch (1898–1969) & Walter Pitts (1923–1969)

### (a) Seminales Werk
**„A Logical Calculus of the Ideas Immanent in Nervous Activity“** (1943), Bulletin of Mathematical Biophysics, Vol. 5, S. 115–133.
🔗 [https://link.springer.com/article/10.1007/BF02478259](https://link.springer.com/article/10.1007/BF02478259)
📄 Auch verfügbar auf Wikipedia: [https://en.wikipedia.org/wiki/A_Logical_Calculus_of_the_Ideas_Immanent_in_Nervous_Activity](https://en.wikipedia.org/wiki/A_Logical_Calculus_of_the_Ideas_Immanent_in_Nervous_Activity)

### (b) Schlüsselgleichung
**McCulloch-Pitts-Neuronenmodell (Schwellenwert-Logikeinheit):**

$$y = f\left(\sum_{i=1}^{n} w_i x_i - \theta\right), \quad f(z) = \begin{cases} 1 & \text{falls } z \geq 0 \\ 0 & \text{falls } z < 0 \end{cases}$$

**Erläuterung:** $x_i \in \{0,1\}$ sind binäre Eingangssignale (erregend oder hemmend), $w_i \in \{-1, +1\}$ die synaptischen Gewichte, $\theta$ die Aktivierungsschwelle und $y \in \{0,1\}$ das Ausgangssignal. Die Funktion $f$ ist die Sprungfunktion (Heaviside-Funktion). Mit dieser Formulierung zeigten McCulloch und Pitts, dass jedes logische Gatter (AND, OR, NOT) und damit jede berechenbare Boolesche Funktion durch ein Netzwerk solcher Neuronen realisiert werden kann — der erste mathematische Beweis, dass das Gehirn als Turing-vollständiger Computer betrachtet werden kann.

### (c) Kernidee
**Neuronale Aktivität im Gehirn lässt sich vollständig mit Boolescher Logik beschreiben — jedes Gedankenkonstrukt („Idee") entspricht einer logischen Proposition, und das Gehirn ist ein universeller logischer Automat.**

---

## 5. Heinz von Foerster (1911–2002)

### (a) Seminales Werk
**„Objects: Tokens for (Eigen-)Behaviors“** (1976), erschienen in: *Hommage à Jean Piaget: Epistemology and Psychology of Functions*, Dordrecht: Reidel.
🔗 [https://monoskop.org/images/b/bf/Von_Foerster_Heinz_2003_Objects_Tokens_for_Eigen-Behaviors.pdf](https://monoskop.org/images/b/bf/Von_Foerster_Heinz_2003_Objects_Tokens_for_Eigen-Behaviors.pdf)

### (b) Schlüsselgleichung
**Eigenform-Gleichung (Rekursive Objektkonstitution):**

$$\text{Obj} = \text{COORD}(\text{Obj}, \text{Obj})$$

**Erläuterung:** $\text{COORD}$ ist ein koordinierender Operator, der sensorische und motorische Aktivität rekursiv verknüpft. $\text{Obj}$ erscheint als Fixpunkt (Eigenwert) dieser Rekursion. Mathematisch entspricht dies der Eigenwertgleichung $Ax = \lambda x$: Ein Objekt ist kein extern Gegebenes, sondern ein stabiler Eigenwert rekursiver kognitiv-motorischer Operationen. Diese Gleichung ist das Kernstück der Kybernetik zweiter Ordnung: Der Beobachter ist Teil des beobachteten Systems.

### (c) Kernidee
**Wirklichkeit wird nicht passiv von außen empfangen, sondern durch rekursive, selbstreferenzielle kognitive Prozesse aktiv konstruiert — Objekte sind stabile Muster (Eigenformen) in diesem rekursiven Netzwerk (Kybernetik zweiter Ordnung).**

---

## 6. Gregory Bateson (1904–1980)

### (a) Seminale Werke
**„Steps to an Ecology of Mind“** (1972), New York: Ballantine Books.
🔗 [https://ejcj.orfaleacenter.ucsb.edu/wp-content/uploads/2017/06/1972.-Gregory-Bateson-Steps-to-an-Ecology-of-Mind.pdf](https://ejcj.orfaleacenter.ucsb.edu/wp-content/uploads/2017/06/1972.-Gregory-Bateson-Steps-to-an-Ecology-of-Mind.pdf)

**„Toward a Theory of Schizophrenia“** (1956), mit Jackson, Haley & Weakland, *Behavioral Science*, 1(4), S. 251–264.
🔗 [https://onlinelibrary.wiley.com/doi/abs/10.1002/bs.3830010402](https://onlinelibrary.wiley.com/doi/abs/10.1002/bs.3830010402)

### (b) Schlüsselgleichung
**Batesons Informationsdefinition (logische, nicht probabilistische Formulierung):**

$$\text{Information} = \text{„ein Unterschied, der einen Unterschied macht“} \quad \text{(a difference that makes a difference)}$$

**Erläuterung:** Anders als Shannons probabilistische Entropie definiert Bateson Information als die Wahrnehmung einer Differenz, die im System eine Reaktion auslöst. Formal lässt sich dies als zweistufiger Prozess schreiben: $\Delta_1 = x_1 - x_0$ (sensorischer Unterschied), und $\Delta_2 = f(\Delta_1)$ (Unterschied, der im Empfängersystem wirksam wird). Bateson verknüpft dies mit Russells Typentheorie: Das Double-Bind-Konzept beschreibt eine Situation, in der widersprüchliche Botschaften auf unterschiedlichen logischen Ebenen kommuniziert werden — der Empfänger kann nicht gewinnen, egal was er tut.

### (c) Kernidee
**Geist ist kein inneres Phänomen, sondern ein Systemmerkmal, das aus Kommunikations- und Rückkopplungskreisläufen zwischen Organismus und Umwelt entsteht — Denken findet in zirkulären Prozessen statt, nicht in linearen Kausalketten.**

---

## 7. Margaret Mead (1901–1978)

### (a) Seminales Werk
**„Cybernetics of Cybernetics“** (1968), in: *Purposive Systems: Proceedings of the First Annual Symposium of the American Society for Cybernetics*, New York: Spartan Books.
🔗 [https://monoskop.org/File:Margaret_Mead_1968_Cybernetics_of_Cybernetics.pdf](https://monoskop.org/File:Margaret_Mead_1968_Cybernetics_of_Cybernetics.pdf)
📄 Auch: [https://quote.ucsd.edu/performingcybernetics/files/2017/03/mead-cybernetics.pdf](https://quote.ucsd.edu/performingcybernetics/files/2017/03/mead-cybernetics.pdf)

### (b) Schlüsselgleichung
**Kybernetik der Kybernetik (konzeptuelle Rekursion):**

$$\text{Kyb}^2 = \text{Kyb}(\text{Kyb}) \quad \text{— Die Kybernetik auf sich selbst angewendet}$$

**Erläuterung:** Mead prägte den Begriff *„Cybernetics of Cybernetics"* als rekursive Wendung: Die kybernetischen Prinzipien der Selbstregulation, Rückkopplung und Zirkularität werden auf die Disziplin selbst und auf die Gesellschaft angewendet. Dies ist weniger eine algebraische als eine konzeptuelle Rekursionsgleichung: Das Denken über Systeme wird selbst als System betrachtet. Sie forderte transdisziplinäre und transkulturelle Kommunikationsstrukturen, um die Kybernetik verantwortungsvoll gesellschaftlich einzubetten.

### (c) Kernidee
**Die Kybernetik muss auf sich selbst und auf die Gesellschaft angewendet werden — wir müssen die Rolle des Beobachters, die ethischen Implikationen und die transkulturelle Verantwortung kybernetischen Denkens reflektieren.**

---

## 8. John von Neumann (1903–1957)

### (a) Seminales Werk
**„Theory of Self-Reproducing Automata“** (posthum 1966, herausgegeben von Arthur W. Burks), Urbana: University of Illinois Press.
🔗 [https://archive.org/details/theoryofselfrepr00vonn_0](https://archive.org/details/theoryofselfrepr00vonn_0)
📄 Burks' Aufsatz dazu: [https://fab.cba.mit.edu/classes/865.18/replication/Burks.pdf](https://fab.cba.mit.edu/classes/865.18/replication/Burks.pdf)
📄 Wikipedia: [https://en.m.wikipedia.org/wiki/Von_Neumann_universal_constructor](https://en.m.wikipedia.org/wiki/Von_Neumann_universal_constructor)

### (b) Schlüsselgleichung
**Zellulärer Automat des universellen Konstruktors:**

$$\delta: \Sigma^5 \rightarrow \Sigma, \quad |\Sigma| = 29$$

**Erläuterung:** $\delta$ ist die Übergangsfunktion eines zweidimensionalen zellulären Automaten mit 29 Zuständen ($\Sigma$) und von-Neumann-Nachbarschaft (5 Zellen: Zentrum + 4 orthogonal angrenzende). Der Automat implementiert einen *universellen Konstruktor* — eine Konfiguration von ca. 200.000 Zellen, die in der Lage ist: (1) beliebige durch ein genetisches Band spezifizierte Konfigurationen zu konstruieren, (2) als universeller Computer zu fungieren, und (3) sich selbst samt des genetischen Bandes zu kopieren. Dies ist der erste formale Beweis, dass maschinelle Selbstreproduktion logisch möglich ist.

### (c) Kernidee
**Selbstreproduktion ist kein mysteriöses biologisches Phänomen, sondern ein logisch-mechanischer Prozess, der formal beschrieben und in Maschinen implementiert werden kann — vorausgesetzt, das System enthält eine vollständige Beschreibung seiner selbst.**

---

## 9. Humberto Maturana (1928–2021)

### (a) Seminale Werke
**„Autopoiesis: The Organization of Living Systems, Its Characterization and a Model“** (1974), mit F. Varela & R. Uribe, *BioSystems*, 5, S. 187–196.
🔗 [https://monoskop.org/images/d/dd/Varela_Maturana_Uribe_1974_Autopoiesis.pdf](https://monoskop.org/images/d/dd/Varela_Maturana_Uribe_1974_Autopoiesis.pdf)

**„Autopoiesis and Cognition: The Realization of the Living“** (1980), mit F. Varela, Dordrecht: Reidel.
🔗 [https://link.springer.com/book/10.1007/978-94-009-8947-4](https://link.springer.com/book/10.1007/978-94-009-8947-4)

### (b) Schlüsselgleichung
**Autopoietische Organisation (zirkuläre Produktion):**

$$\mathcal{A}(\mathcal{S}) = \mathcal{S}, \quad \text{wobei } \mathcal{S} = \{\text{Komponenten, die } \mathcal{S} \text{ produzieren}\}$$

**Erläuterung:** $\mathcal{S}$ ist ein lebendes System, definiert als Netzwerk von Produktionsprozessen, dessen Komponenten durch ihre Interaktionen rekursiv dasselbe Netzwerk erzeugen, das sie produziert. Die Organisation $\mathcal{A}$ ist invariant (strukturdeterminiert), während die Struktur sich ändern kann. Mathematisch bedeutet dies: Ein autopoietisches System ist ein Fixpunkt seiner eigenen Produktionsfunktion — es erhält sich selbst durch permanente Selbstherstellung. Dies unterscheidet Lebewesen fundamental von Maschinen (allopoietischen Systemen), die etwas anderes als sich selbst produzieren.

### (c) Kernidee
**Lebende Systeme sind autopoietisch — sie produzieren rekursiv genau die Komponenten, aus denen sie bestehen, und erhalten dadurch autonom ihre Identität in einer sich verändernden Umwelt.**

---

## 10. Francisco Varela (1946–2001)

### (a) Seminales Werk
**„Autopoiesis: The Organization of Living Systems, Its Characterization and a Model“** (1974), mit H. Maturana & R. Uribe, *BioSystems*, 5, S. 187–196.
🔗 [https://monoskop.org/images/d/dd/Varela_Maturana_Uribe_1974_Autopoiesis.pdf](https://monoskop.org/images/d/dd/Varela_Maturana_Uribe_1974_Autopoiesis.pdf)

**„Autonomy and Autopoiesis“** (1981), in: *Self-Organizing Systems*, S. 37–48.
🔗 [https://mechanism.ucsd.edu/bill/teaching/w22/phil147/Varela+-+1981+-+Autonomy+and+Autopoiesis.pdf](https://mechanism.ucsd.edu/bill/teaching/w22/phil147/Varela+-+1981+-+Autonomy+and+Autopoiesis.pdf)

### (b) Schlüsselgleichung
**Minimales Autopoiese-Modell (Sechskomponenten-System):**

$$\mathcal{K} = \{X, Y, Z, M, N, L\}, \quad \text{mit katalytischen Regeln:} \quad \begin{cases} X + M \rightarrow 2M \\ Y + L \rightarrow 2L \\ M + N \rightarrow Z \\ \ldots \end{cases}$$

**Erläuterung:** Varela, Maturana und Uribe entwarfen ein computergestütztes Modell eines minimalen autopoietischen Systems mit sechs Komponententypen. Die Produktionsregeln sind katalytisch (eine Komponente ermöglicht die Produktion anderer), und das gesamte Netzwerk bildet eine operational geschlossene Membran. Das Modell demonstriert, dass Autopoiese — die Selbstherstellung eines abgegrenzten Systems — formal spezifizierbar und simulierbar ist. Mathematisch entspricht dies einem zirkulär geschlossenen Reaktionsnetzwerk: $\prod_i P_i(\mathcal{S}) \subseteq \mathcal{S}$ (alle Produkte bleiben im System).

### (c) Kernidee
**Autopoiese — die Selbstherstellung und Selbsterhaltung eines abgegrenzten Systems — ist die definierende Eigenschaft des Lebens, die sich formal modellieren und computergestützt simulieren lässt.**

---

## 11. Stafford Beer (1926–2002)

### (a) Seminales Werk
**„Brain of the Firm“** (1972, 2. erweiterte Auflage 1981), Chichester: John Wiley & Sons.
🔗 [https://archive.org/download/brain-of-the-firm-reclaimed-v-1/Brain+of+the+Firm+-+Stafford+Beer.pdf](https://archive.org/download/brain-of-the-firm-reclaimed-v-1/Brain+of+the+Firm+-+Stafford+Beer.pdf)

### (b) Schlüsselgleichung
**Varietätsbilanz des Viable System Model (VSM):**

$$V_{\text{Management}}(S1) \geq \frac{V_{\text{Umwelt}}}{\sum_i V_{\text{Attenuatoren}} \cdot \prod_j V_{\text{Amplifikatoren}}}$$

**Erläuterung:** Das Viable System Model (VSM) ist Beers formales Modell für lebensfähige Organisationen. Es basiert auf Ashbys Varietätsgesetz und beschreibt fünf rekursiv verschachtelte Systemfunktionen (System 1–5), die Varietät managen. Die Gleichung drückt aus, dass das Management einer Organisation nur dann effektiv kontrollieren kann, wenn die Umweltvarietät durch Attenuatoren (Varietätsfilter) reduziert und die Managementvarietät durch Amplifikatoren (Varietätsverstärker) erhöht wird, bis ein Gleichgewicht erreicht ist. Das Modell wurde praktisch im Projekt Cybersyn in Chile (Allende-Regierung) implementiert.

### (c) Kernidee
**Organisationen sind lebensfähige Systeme, die durch rekursive Varietätsmanagement-Strukturen — Attenuatoren und Amplifikatoren — Stabilität und Anpassungsfähigkeit in einer überkomplexen Umwelt erreichen.**

---

## 12. Niklas Luhmann (1927–1998)

### (a) Seminales Werk
**„Soziale Systeme: Grundriß einer allgemeinen Theorie“** (1984), Frankfurt: Suhrkamp.
🔗 Deutsch: [https://reflexus.org/wp-content/uploads/Luhmann-1984-Social_Systems.pdf](https://reflexus.org/wp-content/uploads/Luhmann-1984-Social_Systems.pdf) (englische Übersetzung)

### (b) Schlüsselgleichung
**Kommunikation als dreistelliger Selektionsprozess:**

$$\text{Kommunikation} = \text{Sel}\bigl(\text{Information}, \;\text{Mitteilung}, \;\text{Verstehen}\bigr)$$

**Erläuterung:** $\text{Sel}$ bezeichnet eine dreifache Selektion: (1) *Information* — was wird aus der Welt ausgewählt und für mitteilenswert befunden? (2) *Mitteilung* — wie (in welcher Form) wird es kommuniziert? (3) *Verstehen* — wie wird die Differenz von Information und Mitteilung durch ein anderes System verstanden? Erst wenn alle drei Selektionen vollzogen sind, entsteht Kommunikation als emergente Einheit. Luhmann überträgt das Autopoiese-Konzept auf soziale Systeme: Soziale Systeme reproduzieren sich durch Kommunikation aus Kommunikation ($\text{Kom}_{t+1} = \mathcal{F}(\text{Kom}_t)$), nicht durch Handlungen oder psychische Zustände.

### (c) Kernidee
**Gesellschaft besteht nicht aus Menschen, sondern aus Kommunikationen — soziale Systeme sind autopoietische, sich selbst durch Kommunikation reproduzierende Einheiten, die operativ geschlossen und informationsoffen sind.**

---

## 13. Gordon Pask (1928–1996)

### (a) Seminale Werke
**„Conversation Theory: Applications in Education and Epistemology“** (1976), Amsterdam: Elsevier.
🔗 [https://www.pangaro.com/pask/Pask_Conversation_Theory_(indexed).pdf](https://www.pangaro.com/pask/Pask_Conversation_Theory_(indexed).pdf)

**„Developments in Conversation Theory — Part 1“** (1980), *International Journal of Man-Machine Studies*, 13, S. 357–411.

### (b) Schlüsselgleichung
**Lp-Protologik: Entailment-Mesh als Wissensstruktur**

$$\text{Entail}(A, B) \in \{ \text{produces}, \text{derives}, \text{analogizes}, \text{induces} \}$$

**Erläuterung:** Pasks *Conversation Theory* modelliert Lernen und Verstehen als Konversation zwischen zwei kognitiven Akteuren (Mensch-Mensch oder Mensch-Maschine). Der *Entailment-Mesh* (auch *Entailment-Netz*) ist ein gerichteter Graph, dessen Kanten verschiedene Entailment-Typen repräsentieren. Formaler: Ein Mesh $\mathcal{M} = (V, E)$ mit Knoten $V$ (Topics/Konzepte) und Kantentypen $E \subseteq V \times V \times \{\text{p, d, a, i}\}$. Lernen wird als Übereinstimmung der Meshes beider Teilnehmer ($\mathcal{M}_A \approx \mathcal{M}_B$) modelliert. Protologik Lp ist der zugrundeliegende formale Kalkül.

### (c) Kernidee
**Lernen und Verstehen sind konversationelle Akte — Wissen wird nicht übertragen, sondern durch rekursive Interaktion und Abgleich von Entailment-Strukturen zwischen Konversationsteilnehmern gemeinsam konstruiert.**

---

## 14. Ranulph Glanville (1946–2014)

### (a) Seminales Werk
**„The Question of Cybernetics“** (1987), *Cybernetics and Systems*, 18(2), S. 99–112.
🔗 [https://www.tandfonline.com/doi/abs/10.1080/01969728708902131](https://www.tandfonline.com/doi/abs/10.1080/01969728708902131)

Weitere Publikationen: [https://ranulphglanville.org.za/publications/](https://ranulphglanville.org.za/publications/)

### (b) Schlüsselgleichung
**Design als Konversation (rekursive Selbstinteraktion):**

$$\text{Design} = \text{Konversation}(\text{Designer}, \text{Design}) \quad \Leftrightarrow \quad D_{t+1} = \mathcal{K}(D_t, D_t)$$

**Erläuterung:** Glanville konzipiert Design als rekursive Konversation, in der der Designer mit dem Design (einer externen Repräsentation) „spricht". Der Designer agiert, beobachtet die Reaktion des Designs und handelt erneut — ein zirkulärer Prozess, formalisiert als $\mathcal{K}$, bei dem die Ausgabe einer Iteration zur Eingabe der nächsten wird. Dies ist eine kybernetische Reformulierung: Design erzeugt neues Wissen (der Designer lernt *über* und *durch* das Design), und dieser Prozess ist grundsätzlich unabschließbar. Glanville verbindet damit die Kybernetik zweiter Ordnung mit Designtheorie.

### (c) Kernidee
**Design ist eine Konversation mit sich selbst — ein rekursiver, kybernetischer Prozess, bei dem der Designer durch Handlung und deren Beobachtung neues Wissen erzeugt, ohne dass ein externer Referenzpunkt existiert (Kybernetik zweiter Ordnung in der Praxis).**

---

## Übersichtstabelle

| Nr. | Kybernetiker/in | Schlüsselkonzept | Schlüsselgleichung |
|-----|-----------------|------------------|-------------------|
| 1 | **Norbert Wiener** | Feedback-Regelung | $H(\omega) = S_{xs}(\omega)/S_{ss}(\omega)$ |
| 2 | **Claude Shannon** | Informationstheorie | $H = -\sum p_i \log_2 p_i$ |
| 3 | **W. Ross Ashby** | Requisite Variety | $V_R \geq V_D$ |
| 4 | **McCulloch & Pitts** | Neuronales Schwellenlogik-Modell | $y = f(\sum w_i x_i - \theta)$ |
| 5 | **Heinz von Foerster** | Eigenformen / Kybernetik 2. Ordnung | $\text{Obj} = \text{COORD}(\text{Obj}, \text{Obj})$ |
| 6 | **Gregory Bateson** | Double Bind / Ökologie des Geistes | $\text{Info} = \text{„a difference that makes a difference"}$ |
| 7 | **Margaret Mead** | Kybernetik der Kybernetik | $\text{Kyb}^2 = \text{Kyb}(\text{Kyb})$ |
| 8 | **John von Neumann** | Selbstreproduzierende Automaten | $\delta: \Sigma^5 \to \Sigma, \; \vert\Sigma\vert = 29$ |
| 9 | **Humberto Maturana** | Autopoiese | $\mathcal{A}(\mathcal{S}) = \mathcal{S}$ |
| 10 | **Francisco Varela** | Autopoiese-Modell | $\mathcal{K} = \{X,Y,Z,M,N,L\}$, katalytische Regeln |
| 11 | **Stafford Beer** | Viable System Model | $V_{\text{Mgmt}} \geq V_{\text{Umwelt}} / \text{(Attenuatoren} \cdot \text{Amplifikatoren)}$ |
| 12 | **Niklas Luhmann** | Soziale Autopoiese | $\text{Kommunikation} = \text{Sel}(\text{Info}, \text{Mitteilung}, \text{Verstehen})$ |
| 13 | **Gordon Pask** | Conversation Theory | $\text{Entail}(A,B) \in \{\text{p, d, a, i}\}$ |
| 14 | **Ranulph Glanville** | Design als Konversation | $D_{t+1} = \mathcal{K}(D_t, D_t)$ |

---

*Erstellt: Juni 2026 · Recherche: Englisch · Abfassung: Deutsch · System: GEHIRN_BIBLIOTHEK*
