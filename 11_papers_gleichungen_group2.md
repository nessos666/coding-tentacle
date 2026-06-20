# KYBERNETIKER GRUPPE 2 – Seminalarbeiten, Schlüsselgleichungen & Kernideen

> **Forschungsarbeit in Englisch – Dokumentation in Deutsch**
> Erstellt für die GEHIRN-Bibliothek

---

## 1. Benoît Mandelbrot (1924–2010)

**(a) Seminalarbeit:**
- **"How Long Is the Coast of Britain? Statistical Self-Similarity and Fractional Dimension"**
  - *Science*, Vol. 156, No. 3775, S. 636–638, 1967
  - DOI: [10.1126/science.156.3775.636](https://doi.org/10.1126/science.156.3775.636)
  - URL: https://www.science.org/doi/10.1126/science.156.3775.636

**(b) Schlüsselgleichung – Fraktale Dimension:**
```
D = log(N) / log(1/r)
```
wobei *N* die Anzahl selbstähnlicher Teile und *r* der Skalierungsfaktor ist.

Sowie die **Mandelbrot-Menge**:
```
z_{n+1} = z_n² + c
```
mit komplexen Zahlen *z* und *c*.

**(c) Kernidee:**
Die **fraktale Geometrie** beschreibt die *gebrochene Dimension* natürlicher Strukturen. Mandelbrot zeigte, dass Küstenlinien, Berge, Wolken und Finanzmärkte selbstähnliche Muster aufweisen, die mit der klassischen euklidischen Geometrie nicht erfassbar sind. Fraktale sind *Skaleninvarianz* – das Ganze ähnelt seinen Teilen auf jeder Vergrößerungsstufe. Chaos und Ordnung koexistieren in einer mathematisch präzisen Form.

---

## 2. Ilya Prigogine (1917–2003)

**(a) Seminalarbeit:**
- **"Thermodynamics of Irreversible Processes"**
  - Buch (1. Auflage 1955, basierend auf Arbeiten ab 1945); Nobelpreis 1977
  - Schlüsselpaper mit R. Lefever: **"Theory of Dissipative Structures"** (1968)
  - URL (Nobel Lecture 1977): https://www.nobelprize.org/uploads/2018/06/prigogine-lecture.pdf
  - Buch mit G. Nicolis: **"Self-Organization in Nonequilibrium Systems"**, Wiley, 1977, ISBN 0-471-02401-5

**(b) Schlüsselgleichung – Entropiebilanz:**
```
dS = d_eS + d_iS
```
```
d_iS/dt ≥ 0   (Zweiter Hauptsatz für offene Systeme)
```
wobei *d_eS* der Entropieaustausch mit der Umgebung und *d_iS* die innere Entropieproduktion ist. Im Nichtgleichgewicht kann gelten:
```
d_eS/dt < 0  und  |d_eS/dt| > d_iS/dt  ⇒  dS/dt < 0
```

**(c) Kernidee:**
**Dissipative Strukturen** entstehen fern vom thermodynamischen Gleichgewicht. Entgegen der klassischen Thermodynamik, die Zerfall und Unordnung vorhersagt, können offene Systeme, die Energie und Materie mit ihrer Umgebung austauschen, spontan Ordnung und komplexe Strukturen bilden. *Ordnung durch Fluktuation* – das System „verbraucht" Entropie durch Export an die Umgebung und schafft so lokale Ordnung. Dies revolutionierte das Verständnis von Leben als dissipativem Prozess.

---

## 3. Hermann Haken (1927–2024)

**(a) Seminalarbeit:**
- **"Synergetics – An Introduction"**
  - Buch (Springer, 1977, 3. Auflage 1983); basiert auf Laser-Theorie der 1960er Jahre
  - Frühes Schlüsselpaper: H. Haken, *"A nonlinear theory of laser noise and coherence"*, Zeitschrift für Physik, 1964
  - URL (Wikipedia): https://en.wikipedia.org/wiki/Synergetics_(Haken)

**(b) Schlüsselgleichung – Versklavungsprinzip (Slaving Principle):**
```
ξ̇_s = f(ξ_s, ξ_f, t)     (langsame Ordnungsparameter)
ξ̇_f = g(ξ_s, ξ_f, t)     (schnelle Variablen)
```
Im Grenzfall adiabatischer Elimination:
```
ξ_f(t) ≈ h(ξ_s(t))       (schnelle Variablen werden von Ordnungsparametern „versklavt")
```

**(c) Kernidee:**
Die **Synergetik** ist die Lehre vom Zusammenwirken. In komplexen Systemen nahe Instabilitätspunkten entstehen makroskopische Muster und Strukturen durch das kooperative Verhalten vieler Teilsysteme. Wenige **Ordnungsparameter** (langsame Moden) bestimmen das Verhalten des gesamten Systems, während die schnellen Freiheitsgrade diesen folgen (*Versklavungsprinzip*). Synergetik überbrückt Physik, Chemie, Biologie und Sozialwissenschaften als universelle Theorie der Selbstorganisation.

---

## 4. Edward N. Lorenz (1917–2008)

**(a) Seminalarbeit:**
- **"Deterministic Nonperiodic Flow"**
  - *Journal of the Atmospheric Sciences*, Vol. 20, S. 130–141, 1963
  - DOI: [10.1175/1520-0469(1963)020<0130:DNF>2.0.CO;2](https://doi.org/10.1175/1520-0469(1963)020<0130:DNF>2.0.CO;2)
  - URL: https://journals.ametsoc.org/view/journals/atsc/20/2/1520-0469_1963_020_0130_dnf_2_0_co_2.xml

**(b) Schlüsselgleichung – Lorenz-Attraktor:**
```
dx/dt = σ(y − x)
dy/dt = x(ρ − z) − y
dz/dt = xy − βz
```
mit den klassischen Parametern: σ = 10, ρ = 28, β = 8/3.

**(c) Kernidee:**
**Deterministisches Chaos** bedeutet, dass einfache deterministische Gleichungen unvorhersagbares, nichtperiodisches Verhalten erzeugen können. Sensitive Abhängigkeit von den Anfangsbedingungen – der **Schmetterlingseffekt** – zeigt, dass minimale Unterschiede im Ausgangszustand zu dramatisch verschiedenen Entwicklungen führen. Die Grenzen der Vorhersagbarkeit sind *systemimmanent*, nicht durch mangelnde Daten bedingt. Der Lorenz-Attraktor wurde zur Ikone der Chaostheorie.

---

## 5. John Henry Holland (1929–2015)

**(a) Seminalarbeit:**
- **"Adaptation in Natural and Artificial Systems"**
  - University of Michigan Press, 1975 (Neuauflage MIT Press, 1992)
  - ISBN: 0-262-58111-6
  - URL: https://mitpress.mit.edu/9780262581110/adaptation-in-natural-and-artificial-systems/

**(b) Schlüsselgleichung – Schema-Theorem:**
```
m(H, t+1) ≥ m(H, t) · (f(H) / f̄) · [1 − p_c · (δ(H)/(L−1))] · (1 − p_m)^{o(H)}
```
wobei *m(H,t)* die Anzahl der Individuen mit Schema *H* in Generation *t*, *f(H)* die Fitness des Schemas, *f̄* die durchschnittliche Fitness, *p_c* die Crossover-Wahrscheinlichkeit, *δ(H)* die definierende Länge des Schemas, *p_m* die Mutationswahrscheinlichkeit und *o(H)* die Ordnung des Schemas ist.

**(c) Kernidee:**
**Genetische Algorithmen** sind eine Methode der evolutionären Optimierung, inspiriert von Darwins natürlicher Selektion. Holland zeigte, dass Adaption als Suche in komplexen Räumen durch genetische Operatoren (Selektion, Crossover, Mutation) formalisiert werden kann. Das Schema-Theorem beweist, dass überdurchschnittlich „fitte" Schemata exponentiell in der Population wachsen. Lernen und Evolution sind strukturell ähnliche adaptive Prozesse – die Grundlage komplexer adaptiver Systeme.

---

## 6. Stuart Kauffman (geb. 1939)

**(a) Seminalarbeit:**
- **"The Origins of Order: Self-Organization and Selection in Evolution"**
  - Oxford University Press, 1993, ISBN 0-19-507951-5
  - Vorarbeiten: S. Kauffman, *"Metabolic stability and epigenesis in randomly constructed genetic nets"*, Journal of Theoretical Biology, Vol. 22, S. 437–467, 1969
  - URL (NK-Modell): https://en.wikipedia.org/wiki/NK_model

**(b) Schlüsselgleichung – NK-Fitnesslandschaft:**
```
W = (1/N) · ∑_{i=1}^{N} w_i(g_i; g_{i1}, ..., g_{iK})
```
wobei *W* die Gesamtfitness, *N* die Anzahl der Gene, *K* die Anzahl epistatischer Interaktionen pro Gen und *w_i* der Fitnessbeitrag des Gens *i* in Abhängigkeit von seinen *K* Partnern ist.

**(c) Kernidee:**
**Selbstorganisation und Selektion** sind komplementäre Kräfte der Evolution. Kauffman zeigte, dass komplexe Netzwerke (z.B. Genregulationsnetzwerke) intrinsische Ordnungseigenschaften besitzen, die nicht allein durch Selektion erklärbar sind: *Ordnung umsonst* (order for free). Das NK-Modell beschreibt „tunably rugged" Fitnesslandschaften. **Autokatalytische Mengen** zeigen, wie Leben aus kollektiver katalytischer Schließung entstehen kann. Der **adjacent possible** beschreibt die kreative Expansion des Möglichen in biologischen und technologischen Systemen.

---

## 7. Andrey N. Kolmogorov (1903–1987)

**(a) Seminalarbeit:**
- **"Three Approaches to the Quantitative Definition of Information"**
  - *Problemy Peredachi Informatsii*, Vol. 1, No. 1, S. 3–11, 1965
  - (Englische Übersetzung: *Problems of Information Transmission*, Vol. 1, S. 1–7)
  - DOI: [10.1080/00207166808803030](https://doi.org/10.1080/00207166808803030)

**(b) Schlüsselgleichung – Kolmogorov-Komplexität:**
```
K_U(x) = min { |p| : U(p) = x }
```
wobei *K_U(x)* die algorithmische Komplexität des Strings *x* bezüglich einer universellen Turingmaschine *U* ist, und *|p|* die Länge des kürzesten Programms *p*, das *x* erzeugt.

**(c) Kernidee:**
Die **algorithmische Informationstheorie** definiert die Komplexität eines Objekts als die Länge des kürzesten Computerprogramms, das dieses Objekt erzeugen kann. Anders als Shannons statistische Information misst Kolmogorovs Ansatz die *inhärente* Komplexität – nicht nur die Unwahrscheinlichkeit. Ein zufälliger String hat maximale Kolmogorov-Komplexität (er ist algorithmisch inkompressibel). Dies begründet eine tiefe Verbindung zwischen Berechenbarkeit, Zufall und Information.

---

## 8. René Thom (1923–2002)

**(a) Seminalarbeit:**
- **"Stabilité Structurelle et Morphogénèse"**
  - (Englisch: *Structural Stability and Morphogenesis*)
  - W.A. Benjamin, 1972 (französisches Original); englische Übersetzung von D.H. Fowler, 1975
  - ISBN: 0-8053-9267-3
  - URL: https://en.wikipedia.org/wiki/Catastrophe_theory

**(b) Schlüsselgleichung – Spitzenkatastrophe (Cusp Catastrophe):**
```
V(x; a, b) = x⁴/4 + a·x²/2 + b·x
```
wobei *V* die Potentialfunktion, *x* die Zustandsvariable und *a, b* die Kontrollparameter sind. Die Gleichgewichtsfläche ist gegeben durch:
```
∂V/∂x = x³ + a·x + b = 0
```

**(c) Kernidee:**
Die **Katastrophentheorie** klassifiziert Diskontinuitäten (plötzliche qualitative Sprünge), die aus kontinuierlichen, glatten Parameteränderungen entstehen. Thom's Satz von den **sieben elementaren Katastrophen** (Falte, Spitze, Schwalbenschwanz, Schmetterling, hyperbolischer, elliptischer und parabolischer Nabel) liefert eine universelle Geometrie der Morphogenese: Wie entstehen Formen, Brüche und Diskontinuitäten in Natur und Gesellschaft? Die Theorie verbindet Topologie, Differentialgeometrie und Biologie.

---

## 9. Valentino Braitenberg (1926–2011)

**(a) Seminalarbeit:**
- **"Vehicles: Experiments in Synthetic Psychology"**
  - MIT Press, 1984, ISBN 0-262-52112-1
  - URL (PDF): https://library.agnescameron.info/artificial+intelligence/Vehicles,+Experiments+in+Synthetic+Psychology,+Valentino+Braitenberg+(1984).pdf
  - URL (Wikipedia): https://en.wikipedia.org/wiki/Braitenberg_vehicle

**(b) Schlüsselgleichung – Fahrzeug-Sensormotorik:**
```
v_L = f(s_L, s_R)    Linke Radgeschwindigkeit
v_R = g(s_L, s_R)    Rechte Radgeschwindigkeit
```
wobei *s_L, s_R* die Sensorsignale (z.B. Lichtintensität) sind. Für Fahrzeug 2 (Aggression/Taxis):
```
v_L = α·s_L,   v_R = α·s_R        (direkte Kopplung)
```
Für Fahrzeug 3 (Liebe/Vermeidung):
```
v_L = α·s_R,   v_R = α·s_L        (gekreuzte Kopplung)
```

**(c) Kernidee:**
**Synthetische Psychologie** durch aufsteigende Komplexität. Braitenbergs Gedankenexperiment zeigt, wie aus einfachsten sensomotorischen Kopplungen emergente, psychologisch interpretierbare Verhaltensweisen entstehen. Fahrzeuge mit nur zwei Sensoren und zwei Motoren zeigen Verhalten, das als *Angst, Aggression, Liebe, Neugier* interpretiert werden kann – ohne jede explizite Programmierung. Das Gesetz der notwendigen Vielfalt und die Kontinuumshypothese: Komplexität des Verhaltens entsteht aus der Architektur der Verschaltung, nicht aus der Komplexität der Komponenten.

---

## 10. James Lovelock (1919–2022)

**(a) Seminalarbeit:**
- **"Atmospheric Homeostasis by and for the Biosphere: The Gaia Hypothesis"**
  - J.E. Lovelock & L. Margulis, *Tellus*, Vol. 26, S. 2–10, 1974
  - DOI: [10.3402/tellusa.v26i1-2.9731](https://doi.org/10.3402/tellusa.v26i1-2.9731)
  - URL: https://www.jameslovelock.org/atmospheric-homeostasis-by-and-for-the-biosphere-the-gaia-hypothesis/
  - Daisyworld-Modell (mit A.J. Watson): *Tellus B*, Vol. 35, S. 284–289, 1983

**(b) Schlüsselgleichung – Daisyworld-Dynamik:**
```
dA_w/dt = A_w · (x · β(T_w) − γ)       (Weiße Gänseblümchen)
dA_b/dt = A_b · (x · β(T_b) − γ)       (Schwarze Gänseblümchen)
x = 1 − A_w − A_b                       (Unbedeckte Fläche)
```
wobei *β(T)* die temperaturabhängige Wachstumsrate und *γ* die Sterberate ist. Die planetare Temperatur ergibt sich aus der Energiebilanz:
```
σ·T⁴ = S·(1 − α)    mit planetarer Albedo α
```

**(c) Kernidee:**
Die **Gaia-Hypothese** betrachtet die Erde als selbstregulierendes System, in dem die Biosphäre aktiv die physikalisch-chemischen Bedingungen (Temperatur, Atmosphärenzusammensetzung) in einem für das Leben optimalen Bereich hält. *Homeostasis durch und für die Biosphäre* – Leben ist nicht passiver Bewohner, sondern aktiver Gestalter seiner Umwelt. Das Daisyworld-Modell demonstriert mathematisch, wie globale Temperaturregulation durch einfache biologische Rückkopplungen ohne Teleologie emergieren kann.

---

## 11. Buckminster Fuller (1895–1983)

**(a) Seminalarbeit:**
- **"Synergetics: Explorations in the Geometry of Thinking"**
  - Macmillan, 1975 (Band 1); Band 2: *Synergetics 2*, Macmillan, 1979
  - ISBN: 0-02-065320-4
  - URL (Online): https://rwgrayprojects.com/synergetics/toc/toc.html
  - URL (BFI): https://www.bfi.org/about-fuller/big-ideas/synergetics/

**(b) Schlüsselgleichung – Vektor-Gleichgewicht & Synergetik:**
```
Frequenz (f) → Anzahl der Unterteilungen:
V = 10f² + 2     (Vertex-Anzahl für geodätische Kuppeln, Ikosaeder-basiert)
E = 30f²         (Kanten-Anzahl)
```
Grundprinzip der Synergetik:
```
2 + 2 = 5   (Systemverhalten ≠ Summe der Teile)
Tensegrity: Zug + Druck = strukturelle Integrität
```
**Ephemeralisierung:** Mehr Output mit weniger Input.

**(c) Kernidee:**
**Synergetik** ist die empirisch-mathematische Wissenschaft von Systemen in Transformation. Fuller zeigte, dass die Natur in *Dreiecken, Tetraedern und geodätischen Geometrien* operiert – nicht im kartesischen Koordinatensystem. Das **Vektor-Gleichgewicht** (Kuboktaeder) ist der energetisch stabilste Zustand mit 12 gleichen Vektoren im Gleichgewicht. **Tensegrity** (tensional integrity) beschreibt Strukturen, bei denen Zug- und Druckelemente ein selbststabilisierendes Ganzes bilden. *Es gibt keine Dinge, nur energetische Prozesse und Geometrien.*

---

## 12. Henri Atlan (geb. 1931)

**(a) Seminalarbeit:**
- **"L'Organisation biologique et la théorie de l'information"**
  - Hermann, Paris, 1972 (Neuauflage: Éditions du Seuil, 2006)
  - ISBN: 978-2020833257
  - Schlüsselkonzept aus: **"Entre le cristal et la fumée"**, Seuil, Paris, 1979
  - URL (Wikipedia): https://en.wikipedia.org/wiki/Henri_Atlan

**(b) Schlüsselgleichung – Komplexität durch Rauschen:**
Basierend auf Shannons Kanaltheorem, reinterpretiert für hierarchische Systeme:
```
C = H_max − H_obs
```
wobei *C* die Komplexität des Systems, *H_max* die maximale Entropie (Gleichverteilung) und *H_obs* die beobachtete Entropie (redundanzbereinigt) ist.
Für Selbstorganisation gilt:
```
dC/dt > 0   wenn Rauschen/Niveau optimal
```
Informationsgewinn durch Rauschen:
```
I(X;Y) = H(X) − H(X|Y)
```

**(c) Kernidee:**
Das **Prinzip der Komplexität durch Rauschen** (*complexité par le bruit*) erweitert von Foersters *order from noise*. Atlan zeigt, dass Zufallsfluktuationen („Rauschen") in hierarchisch organisierten Systemen nicht bloß destruktiv, sondern *generativ* wirken: Sie ermöglichen dem System, neue Zustände zu explorieren und so seine Komplexität zu erhöhen. Leben existiert *zwischen Kristall und Rauch* – zwischen starrer Ordnung und Chaos. Selbstorganisation entsteht formal durch Anwendung des Shannon'schen Kanaltheorems auf mehrstufige biologische Systeme.

---

## 13. Karl Friston (geb. 1959)

**(a) Seminalarbeit:**
- **"The Free-Energy Principle: A Unified Brain Theory?"**
  - *Nature Reviews Neuroscience*, Vol. 11, S. 127–138, 2010
  - DOI: [10.1038/nrn2787](https://doi.org/10.1038/nrn2787)
  - URL: https://www.nature.com/articles/nrn2787
  - Grundlagenpapier: **"A Free Energy Principle for Biological Systems"**, *Entropy*, Vol. 14, S. 2100–2121, 2012, DOI: [10.3390/e14112100](https://doi.org/10.3390/e14112100)

**(b) Schlüsselgleichung – Variations-Freie-Energie:**
```
F = D_KL[q(ϑ) || p(ϑ)] − ln p(s|m)
```
oder äquivalent:
```
F = ⟨ln q(ϑ) − ln p(ϑ, s|m)⟩_q
```
wobei *q(ϑ)* die erkennende (approximative) Posteriorverteilung über versteckte Zustände *ϑ*, *p(ϑ, s|m)* das generative Modell und *s* die sensorischen Beobachtungen sind. **Aktive Inferenz**:
```
a* = arg min_a F(s, a)
```

**(c) Kernidee:**
Das **Freie-Energie-Prinzip** (FEP) postuliert, dass alle biologischen Systeme – vom Einzeller bis zum Gehirn – danach streben, ihre *Variations-Freie-Energie* zu minimieren. Dies ist gleichbedeutend mit der Minimierung von Überraschung (prediction error) bzw. der Maximierung von Evidenz für das eigene generative Modell. Das Gehirn als **Bayesianische Inferenzmaschine** sagt ständig sensorische Inputs voraus und passt entweder seine internen Modelle an (Perzeption) oder handelt, um die Umwelt zu verändern (Aktive Inferenz). Das FEP vereint Wahrnehmung, Handlung, Lernen und Aufmerksamkeit unter einem einzigen mathematischen Imperativ.

---

## 14. Judea Pearl (geb. 1936)

**(a) Seminalarbeit:**
- **"Causal Diagrams for Empirical Research"**
  - *Biometrika*, Vol. 82, No. 4, S. 669–710, 1995
  - DOI: [10.1093/biomet/82.4.669](https://doi.org/10.1093/biomet/82.4.669)
  - URL: https://academic.oup.com/biomet/article-abstract/82/4/669/251647
- Buch: **"Causality: Models, Reasoning, and Inference"**, Cambridge University Press, 2000 (2. Auflage 2009), ISBN 978-0521895606
- Buch: **"Probabilistic Reasoning in Intelligent Systems"**, Morgan Kaufmann, 1988

**(b) Schlüsselgleichung – Do-Kalkül (Intervention):**
```
P(Y | do(X=x)) = ∑_z P(Y | X=x, Z=z) · P(Z=z)
```
Die **Back-Door-Formel** zur Identifikation kausaler Effekte:
```
P(Y | do(X)) = ∑_z P(Y | X, Z=z) · P(Z=z)
```
wobei *Z* eine Menge von Kovariaten ist, die die Back-Door-Kriterien erfüllt.
Strukturgleichungsmodell (SCM):
```
Y = f_Y(X, U_Y)     X = f_X(U_X)
```

**(c) Kernidee:**
Die **Kausale Revolution**: Korrelation ist nicht Kausalität – und Pearl formalisierte den Unterschied mathematisch präzise. Durch **Strukturelle Kausalmodelle** (SCMs), gerichtete azyklische Graphen (DAGs) und den **Do-Kalkül** wird kausales Schließen aus Beobachtungsdaten erstmals rigoros möglich. Die Frage „Was passiert, wenn ich eingreife?" (*do(X)*) wird von der Frage „Was sehe ich?" (*see(X)*) getrennt. Bayessche Netze modellieren probabilistische Abhängigkeiten; der Do-Operator ermöglicht kontrafaktisches Denken. Das ist die mathematische Grundlage für Politik-Evaluation, medizinische Studien und KI-Systeme, die Ursache-Wirkungs-Zusammenhänge verstehen.

---

## Übersichtstabelle

| # | Kybernetiker | Kernkonzept | Disziplin |
|---|-------------|-------------|-----------|
| 1 | **Mandelbrot** | Fraktale Geometrie & Selbstähnlichkeit | Mathematik |
| 2 | **Prigogine** | Dissipative Strukturen & Nichtgleichgewicht | Thermodynamik |
| 3 | **Haken** | Synergetik & Versklavungsprinzip | Physik/Systemtheorie |
| 4 | **Lorenz** | Deterministisches Chaos & Schmetterlingseffekt | Meteorologie/Mathematik |
| 5 | **Holland** | Genetische Algorithmen & Schema-Theorem | Informatik/Komplexität |
| 6 | **Kauffman** | NK-Modell & Autokatalytische Mengen | Biologie/Komplexität |
| 7 | **Kolmogorov** | Algorithmische Komplexität | Mathematik |
| 8 | **Thom** | Katastrophentheorie & Morphogenese | Topologie/Mathematik |
| 9 | **Braitenberg** | Synthetische Psychologie & Fahrzeuge | Kybernetik/Neurowissenschaft |
| 10 | **Lovelock** | Gaia-Hypothese & Erdsystem-Homeostase | Geophysik/Biologie |
| 11 | **Fuller** | Synergetik & Tensegrity | Architektur/Design Science |
| 12 | **Atlan** | Komplexität durch Rauschen | Biophysik/Philosophie |
| 13 | **Friston** | Freie-Energie-Prinzip & Aktive Inferenz | Neurowissenschaft |
| 14 | **Pearl** | Kausale Inferenz & Do-Kalkül | Informatik/Statistik |

---

*Zusammengestellt für die GEHIRN-Bibliothek | Juni 2026*
*Quellen: Wikipedia, Originalpublikationen, Semantic Scholar, ResearchGate, Nobel Foundation, MIT Press, Nature, Springer, Oxford University Press*
