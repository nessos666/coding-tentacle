"""
GEHIRN C — Graph Brain (Struktur-basiert)

Eigenständig. Nur numpy + networkx. Gleiche Schnittstelle.
Später in Coding Tentacle einsteckbar via BrainInterface.

Mathematik:
  Bug-Episoden = Knoten
  Ähnlichkeit > 0.7 → Kante
  Graph-Traversal: 2-Hop-Nachbarschaft finden
  PageRank: wichtigste Patterns

Autor: Hermes + David
"""

import time
import numpy as np
import networkx as nx
from dataclasses import dataclass, field


@dataclass
class BugNode:
    signature: str
    pattern: str
    success: bool
    timestamp: float = field(default_factory=time.time)


class GraphBrain:
    """
    Gehirn C — Findet verborgene Zusammenhänge via Graph-Traversal.
    Kein Konfidenz-Score. Aber: "Bug A ähnelt B, B ähnelt C → A und C sind verwandt".
    """
    
    def __init__(self, similarity_threshold: float = 0.7):
        self.threshold = similarity_threshold
        self.graph = nx.DiGraph()
        self._embeddings: dict[str, np.ndarray] = {}
        self.total_bugs_seen: int = 0
        self.total_learned: int = 0
        self.total_graph_hits: int = 0  # Graph-Traversal half
    
    # ─── BRAIN INTERFACE ───
    
    def think(self, bug_signature: str, bug_embedding: list[float]) -> dict:
        self.total_bugs_seen += 1
        emb = np.array(bug_embedding)
        
        if len(self.graph) == 0:
            return {
                'action': 'EXPLORE',
                'pattern': None,
                'graph_nodes': 0,
                'reasoning': 'Graph ist leer. Kein Wissen.'
            }
        
        # 1. Finde nächsten Knoten via Cosine
        nearest, nearest_sim = self._nearest_neighbor(emb)
        
        if nearest_sim < self.threshold:
            return {
                'action': 'EXPLORE',
                'pattern': None,
                'nearest_sim': nearest_sim,
                'graph_nodes': len(self.graph),
                'reasoning': f"Nächster Bug (sim={nearest_sim:.2f}) zu weit entfernt."
            }
        
        # 2. 2-Hop-Nachbarschaft = verwandte Bugs
        try:
            neighbors_1hop = set(self.graph.successors(nearest))
            neighbors_2hop = set()
            for n in neighbors_1hop:
                neighbors_2hop.update(self.graph.successors(n))
            all_related = {nearest} | neighbors_1hop | neighbors_2hop
        except (nx.NetworkXError, KeyError):
            all_related = {nearest}
        
        # 3. Erfolgreiche Patterns in der Nachbarschaft finden
        successful = []
        for node_id in all_related:
            if node_id in self.graph.nodes:
                node = self.graph.nodes[node_id]
                if node.get('success', False):
                    successful.append((node_id, node.get('pattern', ''), 
                                      self.graph.nodes[node_id].get('weight', 1.0)))
        
        if successful:
            self.total_graph_hits += 1
            best = max(successful, key=lambda x: x[2])
            return {
                'action': 'APPLY_PATTERN',
                'pattern': best[1],
                'confidence': nearest_sim,
                'graph_nodes': len(self.graph),
                'related_bugs': len(all_related),
                'reasoning': (
                    f"Graph-Traversal: {len(all_related)} verwandte Bugs gefunden. "
                    f"Pattern '{best[1]}' via {best[0]} (sim={nearest_sim:.2f})"
                )
            }
        
        return {
            'action': 'EXPLORE',
            'pattern': None,
            'graph_nodes': len(self.graph),
            'related_bugs': len(all_related),
            'reasoning': f"{len(all_related)} verwandte Bugs, aber keiner erfolgreich."
        }
    
    def learn(self, bug_signature: str, pattern: str, success: bool, 
              embedding: list[float] = None) -> None:
        self.total_learned += 1
        
        # Knoten hinzufügen
        self.graph.add_node(bug_signature, pattern=pattern, success=success)
        
        # Embedding speichern
        if embedding is not None:
            emb = np.array(embedding)
            self._embeddings[bug_signature] = emb
            
            # Kanten zu ähnlichen Bugs
            for existing, existing_emb in self._embeddings.items():
                if existing == bug_signature:
                    continue
                sim = self._cosine(emb, existing_emb)
                if sim > self.threshold:
                    self.graph.add_edge(existing, bug_signature, weight=sim)
                    self.graph.add_edge(bug_signature, existing, weight=sim)
    
    def stats(self) -> dict:
        n = len(self.graph)
        
        # PageRank: wichtigste Knoten
        pr = {}
        if n > 0:
            try:
                pr = nx.pagerank(self.graph, weight='weight')
            except:
                pass
        
        # Betweenness: Brücken-Patterns
        bc = {}
        if n > 1:
            try:
                bc = nx.betweenness_centrality(self.graph, weight='weight')
            except:
                pass
        
        top_pr = sorted(pr.items(), key=lambda x: x[1], reverse=True)[:3]
        top_bc = sorted(bc.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            'brain_type': 'Graph (Struktur-basiert)',
            'total_bugs_seen': self.total_bugs_seen,
            'total_learned': self.total_learned,
            'graph_nodes': n,
            'graph_edges': self.graph.number_of_edges(),
            'density': f"{nx.density(self.graph) if n > 1 else 0:.3f}",
            'graph_hits': self.total_graph_hits,
            'top_pagerank': [f"{k} ({v:.3f})" for k, v in top_pr],
            'top_bridges': [f"{k} ({v:.3f})" for k, v in top_bc],
        }
    
    # ─── INTERN ───
    
    def _nearest_neighbor(self, emb: np.ndarray) -> tuple:
        best_id, best_sim = None, 0.0
        for node_id, node_emb in self._embeddings.items():
            sim = self._cosine(emb, node_emb)
            if sim > best_sim:
                best_sim = sim
                best_id = node_id
        return best_id, best_sim
    
    def _cosine(self, a: np.ndarray, b: np.ndarray) -> float:
        if len(a) == 0 or len(b) == 0 or len(a) != len(b):
            return 0.0
        dot = np.dot(a, b)
        norm = np.linalg.norm(a) * np.linalg.norm(b)
        return dot / norm if norm > 0 else 0.0
    
    def __repr__(self) -> str:
        s = self.stats()
        return f"GraphBrain(nodes={s['graph_nodes']}, edges={s['graph_edges']})"


# ─── DEMO ───
if __name__ == "__main__":
    print("=" * 60)
    print("GEHIRN C — Graph Brain — DEMO")
    print("=" * 60)
    
    brain = GraphBrain(similarity_threshold=0.7)
    np.random.seed(42)
    
    bugs = [
        ("NullPointer:payment.py:123", "guard_clause", True),
        ("NullPointer:auth.py:89", "guard_clause", True),
        ("OffByOne:paginator.py:67", "boundary_check", True),
        ("NullPointer:order.py:45", "try_except", False),
        ("TypeError:parser.py:34", "isinstance_check", True),
        ("NullPointer:user.py:200", "guard_clause", True),
        ("MemoryLeak:cache.py:12", "weakref", True),
        ("NullPointer:email.py:56", "try_except", False),
        ("OffByOne:counter.py:90", "boundary_check", True),
        ("NullPointer:report.py:156", "guard_clause", True),
    ]
    
    for i, (bug_sig, pattern, success) in enumerate(bugs):
        if 'NullPointer' in bug_sig:
            emb = (np.random.randn(384) * 0.05 + 1.0)
        elif 'OffByOne' in bug_sig:
            emb = (np.random.randn(384) * 0.05 - 1.0)
        elif 'TypeError' in bug_sig:
            emb = (np.random.randn(384) * 0.05 + 2.0)
        else:
            emb = (np.random.randn(384) * 0.05 - 2.0)
        emb = emb / np.linalg.norm(emb)
        
        decision = brain.think(bug_sig, emb.tolist())
        print(f"\n🐛 Bug #{i+1}: {bug_sig}")
        print(f"   🧠 {decision['reasoning']}")
        print(f"   Graph: {decision.get('graph_nodes',0)} nodes, "
              f"{decision.get('related_bugs',0)} related")
        
        brain.learn(bug_sig, pattern, success, emb.tolist())
    
    print(f"\n{'='*60}")
    print("📊 GEHIRN-STATUS:")
    for k, v in brain.stats().items():
        print(f"   {k}: {v}")
    
    print(f"\n✅ Gehirn C läuft eigenständig.")
