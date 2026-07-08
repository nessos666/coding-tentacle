# GEHIRN BIBLIOTHEK — 6 Gehirn-Arten: Mathematik & Forschung
> Coding Tentacle | 18.06.2026

---

## Übersicht: 6 Gehirn-Arten

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                       │
│  GEHIRN A       GEHIRN B        GEHIRN C       GEHIRN D              │
│  Bayesian       Shannon         Graph          RL                    │
│  Konfidenz      Entropie        Struktur       Belohnung             │
│  "Wie sicher?"  "Wie neu?"      "Was hängt     "Was lohnt            │
│                                  zusammen?"     sich?"               │
│                                                                       │
│  GEHIRN E       GEHIRN F                                             │
│  Kybernetisch   ACT-R / Spreading Activation                         │
│  Alle 4         Kognitives Modell                                    │
│  vereint        "Was feuert mit?"                                    │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Gehirn A — Bayesian (Konfidenz-basiert)

### Mathematik

```
NARS-LOGIK (Non-Axiomatic Reasoning System, Pei Wang):

Wahrheitswert = ⟨f, c⟩
  f = frequency = positive_evidence / total_evidence
  c = confidence = total_evidence / (total_evidence + k)
  k = 1 (systemweite Konstante)

BEISPIEL:
  Pattern "guard_clause" wurde 4× angewendet, 3× erfolgreich
  f = 3/4 = 0.75
  c = 4/(4+1) = 0.80
  → "75% Erfolgsrate, aber nur 80% sicher weil nur 4 Datenpunkte"

ABNÄHME (Forgetting):
  c_decay = c * e^(-λ * t_unused)
  λ = 0.01/Tag
  → Nach 30 Tagen ohne Nutzung: c = 0.80 * e^(-0.3) = 0.59

SCHWELLEN:
  c > 0.5 → Pattern vorschlagen
  c > 0.8 → Pattern als "verified" markieren
  c < 0.2 → Pattern als "deprecated" markieren
  c < 0.05 → Löschen (nach ~300 Tagen ohne Nutzung)
```

### Implementierung

```python
class BayesianBrain:
    def __init__(self, k=1.0, decay_lambda=0.01):
        self.patterns = {}  # {name: (f, c, last_used)}
        self.k = k
        self.decay_lambda = decay_lambda
    
    def update(self, pattern_name, success):
        """Bayesian Update nach jedem Fix-Versuch"""
        f, c, _ = self.patterns.get(pattern_name, (0.5, 0.1, now()))
        
        # Update mit Pseudo-Count
        n = c * self.k / (1 - c)  # Virtuelle Anzahl vorheriger Versuche
        n += 1
        
        if success:
            f_new = (f * (n-1) + 1.0) / n
        else:
            f_new = (f * (n-1) + 0.0) / n
        
        c_new = n / (n + self.k)
        self.patterns[pattern_name] = (f_new, c_new, now())
    
    def confidence(self, pattern_name):
        f, c, last = self.patterns.get(pattern_name, (0.5, 0.0, now()))
        days_unused = (now() - last).days
        c_decayed = c * np.exp(-self.decay_lambda * days_unused)
        return c_decayed
    
    def should_apply(self, pattern_name):
        return self.confidence(pattern_name) > 0.5
```

### Forschung

- **BayesAgent** (AAAI 2026): Erstes System, das LLM-Agenten mit probabilistischen graphischen Modellen (PGMs) verbindet. Kalibrierte Konfidenz in unsicheren Umgebungen. https://arxiv.org/abs/2406.05516
- **NARS** (Pei Wang, Temple University): Seit 2006. Nicht-axiomatische Logik mit ⟨f,c⟩ Wahrheitswerten. https://cis.temple.edu/~wangp/
- **ACT-R** (CMU): Deklaratives Gedächtnis mit Aktivierungsgleichung. Siehe Gehirn F.

### Stärken
- Mathematisch sauber: jede Entscheidung hat eine Begründung
- Kalibriert: Konfidenz spiegelt tatsächliche Datenmenge wider
- Vergisst natürlich durch Decay

### Schwächen
- Kein Konzept von "Bug-Typen" — nur flache Pattern-Liste
- Keine strukturellen Zusammenhänge zwischen Patterns
- Langsam bei komplett neuen Bug-Typen (braucht ≥3 Episoden)

---

## Gehirn B — Shannon (Entropie-gesteuert)

### Mathematik

```
SHANNON-ENTROPIE:
  H(X) = -Σ p(x) · log₂ p(x)
  
  p(x) = Ähnlichkeit zu nächstem bekannten Bug
       = cosine_sim(bug_embedding, nearest_neighbor_embedding)
  
  SURPRISAL (Überraschungswert):
  I(x) = -log₂ p(x)
  
  I(x) > 3 bits → "Sehr überraschend! Das ist neu. LERNEN!"
  I(x) < 1 bit  → "Kaum überraschend. Bekanntes Muster. ANWENDEN!"

KL-DIVERGENZ (wie anders ist dieser Bug?):
  D_KL(P_new || P_old) = Σ P_new(x) · log(P_new(x) / P_old(x))

JENSEN-SHANNON-DISTANZ (symmetrisch):
  JSD(P, Q) = ½ D_KL(P||M) + ½ D_KL(Q||M)  wobei M = ½(P+Q)
```

### Implementierung

```python
class ShannonBrain:
    def __init__(self, explore_threshold=2.5):
        self.episodes = []  # Liste aller Embeddings
        self.explore_threshold = explore_threshold
    
    def surprisal(self, bug_embedding):
        """-log p(bug) — wie überraschend ist das?"""
        if not self.episodes:
            return float('inf')
        
        similarities = cosine_similarity(bug_embedding, self.episodes)
        p = max(similarities)  # Wahrscheinlichkeit = Ähnlichkeit zum nächsten
        
        return -np.log2(max(p, 0.001))
    
    def decide(self, bug_embedding):
        s = self.surprisal(bug_embedding)
        
        if s > self.explore_threshold:
            return "EXPLORE", s  # Neues Muster entdeckt
        else:
            return "EXPLOIT", s  # Bekanntes Muster
    
    def entropy_of_memory(self):
        """Wie 'geordnet' ist das Gedächtnis?"""
        if len(self.episodes) < 2:
            return 0.0
        
        # Paarweise Ähnlichkeiten
        sims = cosine_similarity(self.episodes, self.episodes)
        
        # Entropie der Ähnlichkeitsverteilung
        probs = np.histogram(sims.flatten(), bins=20, density=True)[0]
        probs = probs[probs > 0]
        
        return -np.sum(probs * np.log2(probs))
```

### Forschung

- **Predictive Coding** (Friston, 2005): Das Gehirn als Entropie-Minimierungsmaschine
- **Free Energy Principle**: Agenten handeln, um Überraschung zu minimieren
- **Novelty Detection via Information Theory**: Surprisal als Lernsignal (arXiv:2205.10345)

### Stärken
- Erkennt SOFORT neue Bug-Typen
- Braucht keine vordefinierten Pattern-Kategorien
- Entropie = objektives Maß für "wie gut kenne ich meine Bugs?"

### Schwächen
- Weiß nicht, WELCHES Pattern es anwenden soll — nur DASS es bekannt ist
- Kein Konfidenz-Maß für einzelne Patterns
- Tendiert zum "Überexplorieren" bei Rauschen

---

## Gehirn C — Graph (Struktur-basiert)

### Mathematik

```
GRAPH-METRIKEN:

Betweenness Centrality:
  C_B(v) = Σ σ_st(v) / σ_st
  → Welche Patterns sind "Brücken" zwischen Bug-Typen?

PageRank:
  PR(v) = (1-d)/N + d · Σ PR(u)/L(u)
  → Welches Pattern wird am häufigsten von anderen referenziert?

Community Detection (Louvain):
  Modularity Q = 1/(2m) · Σ [A_ij - k_i k_j/(2m)] · δ(c_i, c_j)
  → Welche Patterns bilden natürliche Gruppen?

Graph Convolution:
  H^(l+1) = σ(D̃^(-½) · Ã · D̃^(-½) · H^(l) · W^(l))
  → Embedding eines Knotens = Gemittelt über seine Nachbarn

TGN (Temporal Graph Network):
  Für jede Kante (u,v) zum Zeitpunkt t:
  - Message: msg = f(h_u, h_v, edge_features, t)
  - Update: h_u_new = GRU(h_u_old, aggregate(msgs))
  → Knoten-Embedding evolviert MIT dem Graphen
```

### Implementierung

```python
class GraphBrain:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.embeddings = {}  # node_id → 384dim embedding
    
    def add_episode(self, bug_id, features, pattern, success):
        self.graph.add_node(bug_id,
            pattern=pattern,
            success=success,
            features=features)
        self.embeddings[bug_id] = encode(features)
        
        # Verbinde mit ähnlichen Bugs
        for existing in self.graph.nodes:
            if existing == bug_id:
                continue
            sim = cosine(self.embeddings[bug_id], self.embeddings[existing])
            if sim > 0.7:
                self.graph.add_edge(existing, bug_id, weight=sim)
                self.graph.add_edge(bug_id, existing, weight=sim)
    
    def find_related(self, bug_features, hops=2):
        """Graph-Traversal: 2-Hop-Nachbarschaft"""
        query_emb = encode(bug_features)
        
        # Finde nächsten Knoten
        nearest = max(self.graph.nodes,
            key=lambda n: cosine(query_emb, self.embeddings.get(n, [0]*384)))
        
        # BFS über 2 Hops
        neighbors = nx.single_source_shortest_path_length(
            self.graph, nearest, cutoff=hops)
        
        return list(neighbors.keys())
    
    def bridge_patterns(self):
        """Welche Patterns verbinden verschiedene Bug-Typen?"""
        bc = nx.betweenness_centrality(self.graph, weight='weight')
        return sorted(bc.items(), key=lambda x: x[1], reverse=True)[:10]
```

### Forschung

- **Graph-based Agent Memory: Taxonomy, Techniques, and Applications** (arXiv:2602.05665, Feb 2026): Umfassende Taxonomie von Graph-basierten Agent-Memory-Systemen
- **Zep / Graphiti** (20k⭐): Temporal Knowledge Graph mit 94.8% DMR. https://github.com/getzep/graphiti
- **TGN** (Twitter/X Research, 2020): Temporal Graph Networks für evolvierende Graphen
- **MAGMA** (2026): Multi-Graph-basierte Agentic Memory Architecture

### Stärken
- Findet VERBORGENE Zusammenhänge (A→B→C via Graph-Traversal)
- Strukturierte Beziehungen (Bug--[has_pattern]-->(Pattern))
- Community Detection = automatische Bug-Typ-Klassifikation

### Schwächen
- Aufwändiger Aufbau (Graph-Datenbank nötig)
- Kein natives Konfidenz-Maß
- Teuer bei vielen Episoden (>10K Knoten)

---

## Gehirn D — Reinforcement Learning (Belohnungs-basiert)

### Mathematik

```
Q-LEARNING:
  Q(s, a) ← Q(s, a) + α [r + γ · max_a' Q(s', a') - Q(s, a)]
  
  s = State (Bug-Typ, Pattern-Anzahl, Memory-Auslastung)
  a = Action (STORE, APPLY, IGNORE, CONSOLIDATE, FORGET)
  r = Reward (+1 Fix hielt, -1 Fix scheiterte, +0.5 neues Pattern, -0.1 speichern)

GRPO (Group Relative Policy Optimization, DeepSeek R1):
  Für eine Gruppe G von Aktionen:
  advantage_i = (r_i - mean(G_rewards)) / std(G_rewards)
  loss = -E[ min(ratio · advantage, clip(ratio, 1-ε, 1+ε) · advantage) ]

POLICY GRADIENT:
  ∇J(θ) = E[ ∇log π_θ(a|s) · Q^π(s,a) ]
  → "Bewege die Policy in Richtung der Aktionen mit höherem Q-Wert"
```

### Implementierung

```python
class RLBrain:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.Q = {}  # {(bug_type, action): value}
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
    
    def choose_action(self, bug_type, memory_usage):
        state = (bug_type, memory_usage)
        actions = ['STORE', 'APPLY_PATTERN', 'IGNORE', 'CONSOLIDATE']
        
        if random.random() < self.epsilon:
            return random.choice(actions)
        
        qs = [self.Q.get((state, a), 0.0) for a in actions]
        return actions[np.argmax(qs)]
    
    def learn(self, bug_type, memory_usage, action, reward):
        state = (bug_type, memory_usage)
        old_q = self.Q.get((state, action), 0.0)
        
        # Nächster State (vereinfacht)
        next_memory = memory_usage + (1 if action == 'STORE' else 0)
        next_state = (bug_type, next_memory)
        
        max_next_q = max([self.Q.get((next_state, a), 0.0) 
                         for a in ['STORE', 'APPLY_PATTERN', 'IGNORE']])
        
        # Q-Learning Update
        self.Q[(state, action)] = old_q + self.alpha * (
            reward + self.gamma * max_next_q - old_q)
```

### Forschung

- **Agentic Memory: Learning Unified Long-Term and Short-Term Memory** (arXiv:2601.01885, Jan 2026): 3-Stufen-RL + GRPO für Memory-Management
- **A-Mem** (ByteDance, NeurIPS 2025): RL-trainiertes Memory — Agent entscheidet SELBST, was gespeichert wird
- **DeepSeek R1** (2025): GRPO als effiziente RL-Methode ohne Value-Network

### Stärken
- Findet optimale Strategien, die kein Mensch programmieren würde
- Adaptiert sich an Bug-Typ-Verteilung
- Braucht keine festen Schwellen (lernt sie selbst)

### Schwächen
- Kalter Start: braucht viele Episoden zum Trainieren
- Nicht erklärbar (Black Box)
- Kann falsche Strategien lernen, wenn Reward-Signal rauscht

---

## Gehirn E — Kybernetisch (Alle vereint)

### Mathematik (Kombination aus A+B+C+D)

```
1. BAYES-KONFIDENZ (A):
   confidence = total_evidence / (total_evidence + k)
   Für Pattern-Bewertung

2. SHANNON-ENTROPIE (B):
   surprisal = -log₂ p(bug)
   Für Explore/Exploit-Entscheidung

3. GRAPH-TRAVERSAL (C):
   related = BFS(pattern_node, cutoff=2)
   Für strukturelle Zusammenhänge

4. RL-POLICY (D):
   Q(state, action) mit GRPO-Update
   Für Memory-Aktionen (speichern/löschen/konsolidieren)

5. KONSOLIDIERUNGS-REGELKREIS:
   Wenn episodes_since_touch > threshold:
       Konsolidierung starten
       threshold = adaptiv (lernt optimalen Rhythmus)

6. HOMÖOSTASE:
   memory_usage = len(episodes) / max_episodes
   Ziel: 60-80%
   Wenn >80%: threshold senken → öfter konsolidieren
   Wenn <60%: threshold erhöhen → seltener konsolidieren

7. META-REFLEXION (alle 100 Episoden):
   fix_rate = erfolgreiche_fixes / total_fixes
   Wenn verbessert: Parameter beibehalten
   Wenn verschlechtert: Parameter anpassen (alle α, γ, ε)
```

### Implementierung (Kern-Loop)

```python
class KybernetischBrain:
    def __init__(self):
        self.bayesian = BayesianBrain()
        self.shannon = ShannonBrain()
        self.graph = GraphBrain()
        self.rl = RLBrain()
        self.episodes_since_consolidation = 0
        self.consolidation_threshold = 50  # Adaptiv!
        self.meta_interval = 100
    
    def process(self, bug):
        # 1. Entropie → Explore oder Exploit?
        surprise = self.shannon.surprisal(bug.embedding)
        
        if surprise > 2.5:
            # NEUER Bug-Typ → RL entscheidet, ob speichern
            action = self.rl.choose_action(bug.type, self.usage_pct())
            if action == 'STORE':
                self.graph.add_episode(bug)
                self.shannon.add_episode(bug.embedding)
            return action
        
        # 2. Bekannter Bug-Typ → Graph + Bayesian
        related = self.graph.find_related(bug.features)
        candidates = []
        for r in related:
            pattern = self.graph.nodes[r].get('pattern')
            if self.bayesian.should_apply(pattern):
                candidates.append((pattern, self.bayesian.confidence(pattern)))
        
        # 3. Bestes Pattern anwenden
        if candidates:
            best = max(candidates, key=lambda x: x[1])
            return ('APPLY', best[0], best[1])
        
        return ('NO_PATTERN', None, 0.0)
    
    def learn_from_result(self, pattern, success):
        # 4. Bayesian Update
        self.bayesian.update(pattern, success)
        
        # 5. RL Update
        reward = 1.0 if success else -0.5
        self.rl.learn(bug_type, self.usage_pct(), last_action, reward)
        
        # 6. Konsolidierungs-Check
        self.episodes_since_consolidation += 1
        if self.episodes_since_consolidation >= self.consolidation_threshold:
            self._consolidate()
            self.episodes_since_consolidation = 0
            
            # 7. Homöostase: Schwelle anpassen
            if self.usage_pct() > 0.8:
                self.consolidation_threshold = max(25, self.consolidation_threshold - 5)
            elif self.usage_pct() < 0.6:
                self.consolidation_threshold = min(100, self.consolidation_threshold + 5)
        
        # 8. Meta-Reflexion
        if self.total_episodes % self.meta_interval == 0:
            self._meta_reflect()
```

---

## Gehirn F — ACT-R / Spreading Activation (Kognitives Modell)

### Mathematik

```
ACT-R AKTIVIERUNGSGLEICHUNG:
  A_i = B_i + S_i + Σ_j W_j · S_ji + ε
  
  A_i = Aktivierung von Chunk i
  B_i = Base-Level-Aktivierung (= ln(Nutzungen) - d · ln(Zeit seit letzter Nutzung))
  S_i = Spreading Activation von aktuellem Kontext
  W_j = Gewicht von Quelle j
  S_ji = Assoziationsstärke zwischen j und i
  ε = Rauschen (logistisch verteilt)

BASE-LEVEL LEARNING:
  B = ln(Σ t_j^(-d))
  t_j = Zeit seit j-ter Nutzung
  d = Decay-Parameter (typisch 0.5)
  → Je öfter genutzt, desto höher B. Je länger her, desto niedriger.

RETRIEVAL-WAHRSCHEINLICHKEIT:
  P(retrieve) = 1 / (1 + e^(-(A_i - τ)/s))
  τ = Retrieval-Schwelle
  s = Rauschen (typisch 0.4)

SPREADING ACTIVATION:
  Wenn Bug X aktiv ist:
  → Alle mit X assoziierten Patterns bekommen S_i Boost
  → Je stärker die Assoziation (W_j · S_ji), desto mehr Boost
  → "Bug X feuert → Pattern Y wird warm → Pattern Y ist schneller abrufbar"
```

### Implementierung

```python
class ACTRBrain:
    def __init__(self, decay=0.5, threshold=0.0, noise=0.4):
        self.chunks = {}  # {name: [timestamps_of_use]}
        self.associations = {}  # {(source, target): strength}
        self.decay = decay
        self.threshold = threshold
        self.noise = noise
    
    def base_level_activation(self, chunk_name, current_time):
        timestamps = self.chunks.get(chunk_name, [])
        if not timestamps:
            return -float('inf')
        
        # B = ln(Σ t_j^(-d))
        ages = [current_time - t for t in timestamps]
        return np.log(sum(a ** (-self.decay) for a in ages))
    
    def spreading_activation(self, chunk_name, active_context):
        """Wie stark wird dieser Chunk vom aktiven Kontext aktiviert?"""
        s = 0.0
        for source in active_context:
            w = self.associations.get((source, chunk_name), 0.0)
            s += w  # Vereinfacht: W_j = 1.0, S_ji = association_strength
        return s
    
    def activation(self, chunk_name, current_time, active_context):
        B = self.base_level_activation(chunk_name, current_time)
        S = self.spreading_activation(chunk_name, active_context)
        eps = np.random.logistic(0, self.noise)
        return B + S + eps
    
    def retrieve(self, active_context, current_time, candidates):
        """Welcher Chunk wird abgerufen?"""
        activations = {}
        for c in candidates:
            A = self.activation(c, current_time, active_context)
            if A > self.threshold:
                activations[c] = A
        
        if not activations:
            return None
        
        # Softmax über Aktivierungen
        exp_A = {c: np.exp(A) for c, A in activations.items()}
        total = sum(exp_A.values())
        probs = {c: e/total for c, e in exp_A.items()}
        
        return max(probs, key=probs.get)
    
    def strengthen(self, source, target, increment=0.1):
        key = (source, target)
        self.associations[key] = self.associations.get(key, 0.0) + increment
```

### Forschung

- **ACT-R** (CMU, seit 1993): Das führende kognitive Architektur-Modell. https://act-r.psy.cmu.edu/
- **Spreading Activation** (Collins & Loftus, 1975): Kognitionspsychologisches Modell der Gedächtnisaktivierung
- **Hybrid Personalization with ACT-R** (arXiv:2505.05083, 2025): ACT-R für LLM-Agenten adaptiert

### Stärken
- Biologisch plausibel (simuliert menschliches Gedächtnis)
- Natürliches Vergessen (Base-Level Decay)
- Spreading Activation = "ein Bug weckt verwandte Patterns auf"
- Keine harten Schwellen — probabilistischer Abruf

### Schwächen
- Komplex zu implementieren (viele Parameter)
- Braucht Zeitstempel für JEDE Nutzung
- Spreading Activation kann falsche Patterns "aufwecken"

---

## Vergleichsmatrix: Alle 6 Gehirn-Arten

| Dimension | A Bayesian | B Shannon | C Graph | D RL | E Kybernetisch | F ACT-R |
|-----------|-----------|-----------|---------|------|----------------|---------|
| **Konfidenz** | ✅✅✅ | ❌ | ❌ | ❌ | ✅✅ | ✅ (Aktivierung) |
| **Neuheitserkennung** | ❌ | ✅✅✅ | ✅ | ❌ | ✅✅ | ✅ |
| **Struktur** | ❌ | ❌ | ✅✅✅ | ❌ | ✅✅ | ✅✅ |
| **Selbstoptimierung** | ❌ | ❌ | ❌ | ✅✅✅ | ✅✅✅ | ❌ |
| **Vergessen** | ✅ (Decay) | ❌ | ❌ | ✅ (Policy) | ✅✅ | ✅✅✅ |
| **Erklärbarkeit** | ✅✅✅ | ✅✅ | ✅✅ | ❌ | ✅ | ✅✅ |
| **Kalter Start** | ✅✅ | ✅✅ | ✅ | ❌ | ✅ | ✅✅ |
| **Komplexität** | 2/10 | 3/10 | 5/10 | 7/10 | 9/10 | 6/10 |
| **MVP-Eignung** | ✅✅✅ | ✅✅ | ✅ | ❌ | ❌ | ✅ |

---

## Experiment-Plan

```
PHASE 1 (Woche 1-2): Gehirn A (Bayesian) + Gehirn B (Shannon)
  → Jedes als eigenständiges Python-Modul
  → Test: 50 BugsInPy-Bugs
  → Messen: Fix-Rate, Memory-Hit-Rate, falsche Vorschläge

PHASE 2 (Woche 3-4): Gehirn C (Graph) + Gehirn F (ACT-R)
  → Test gegen gleiche 50 Bugs
  → Vergleich mit A+B

PHASE 3 (Woche 5-6): Gehirn D (RL) bauen
  → Braucht mehr Bugs zum Trainieren (~200)
  → Vergleich mit A+B+C+F

PHASE 4 (Woche 7-8): Gehirn E (Kybernetisch) = A+B+C+D vereint
  → Test gegen alle Einzel-Gehirne
  → Entscheiden: E oder beste Kombination?

PHASE 5 (Woche 9-10): Gewinner mit Qdrant fusionieren
  → Gehirn = Entscheidungsschicht
  → Qdrant = Speicherschicht
```

---

## Quellen

1. BayesAgent (AAAI 2026): https://arxiv.org/abs/2406.05516
2. NARS: https://cis.temple.edu/~wangp/
3. Graph-based Agent Memory Taxonomy: https://arxiv.org/abs/2602.05665
4. Agentic Memory (RL+GRPO): https://arxiv.org/abs/2601.01885
5. ACT-R: https://act-r.psy.cmu.edu/
6. Spreading Activation: Collins & Loftus (1975), Psychological Review
7. Zep/Graphiti: https://github.com/getzep/graphiti
8. MAGMA: https://arxiv.org/abs/2601.03236
