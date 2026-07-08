"""
GEHIRN B — Shannon Brain (Entropie-gesteuert)

Eigenständig. Nur numpy. Gleiche Schnittstelle wie Gehirn A.
Später in Coding Tentacle einsteckbar via BrainInterface.

Mathematik:
  Surprisal = -log₂ p(bug)
  p(bug) = cosine_similarity(bug_embedding, nearest_neighbor)
  
  Hohe Überraschung → EXPLORE (neuer Bug-Typ)
  Niedrige Überraschung → EXPLOIT (bekanntes Muster)

Autor: Hermes + David
"""

import math
import time
import numpy as np
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MemoryEntry:
    """Ein gespeicherter Bug im Shannon-Gedächtnis"""
    signature: str
    embedding: np.ndarray
    pattern: str
    success: bool
    timestamp: float = field(default_factory=time.time)
    access_count: int = 0


class ShannonBrain:
    """
    Gehirn B — Misst Überraschung. Keine festen Pattern-Kategorien.
    Lernt: "Dieser Bug-Typ ist neu" vs "Das kenne ich schon".
    """
    
    def __init__(self, explore_threshold: float = 3.0, min_confidence: float = 0.3):
        """
        Args:
            explore_threshold: Surprisal > das → EXPLORE (in Bits)
            min_confidence: Mindest-Cosine-Ähnlichkeit für "bekannt"
        """
        self.explore_threshold = explore_threshold
        self.min_confidence = min_confidence
        self.memories: list[MemoryEntry] = []
        self.total_bugs_seen: int = 0
        self.total_learned: int = 0
        self.total_explored: int = 0
        self.total_exploited: int = 0
    
    # ─── BRAIN INTERFACE ───
    
    def think(self, bug_signature: str, bug_embedding: list[float]) -> dict:
        self.total_bugs_seen += 1
        emb = np.array(bug_embedding)
        
        if not self.memories:
            self.total_explored += 1
            return {
                'action': 'EXPLORE',
                'pattern': None,
                'confidence': 0.0,
                'surprisal': float('inf'),
                'reasoning': 'Kein einziges Memory. Alles ist neu.'
            }
        
        # Cosine-Ähnlichkeit zu ALLEN gespeicherten Bugs
        similarities = []
        for m in self.memories:
            sim = self._cosine(emb, m.embedding)
            similarities.append((sim, m))
        
        best_sim, best_match = max(similarities, key=lambda x: x[0])
        
        # Surprisal = -log₂(Ähnlichkeit)
        p = max(best_sim, 0.001)
        surprisal = -math.log2(p)
        
        if surprisal > self.explore_threshold:
            self.total_explored += 1
            return {
                'action': 'EXPLORE',
                'pattern': None,
                'confidence': best_sim,
                'surprisal': surprisal,
                'nearest_match': best_match.signature,
                'reasoning': (
                    f"Überraschung={surprisal:.1f} bits > Schwelle={self.explore_threshold}. "
                    f"Nächster bekannter Bug: '{best_match.signature}' (sim={best_sim:.2f}). "
                    f"Das ist NEU."
                )
            }
        
        self.total_exploited += 1
        
        # Bekannt: Ähnlichste erfolgreiche Patterns finden
        successful = [(s, m) for s, m in similarities if m.success and s > self.min_confidence]
        
        if successful:
            best_s, best_m = max(successful, key=lambda x: x[0])
            best_m.access_count += 1
            return {
                'action': 'APPLY_PATTERN',
                'pattern': best_m.pattern,
                'confidence': best_s,
                'surprisal': surprisal,
                'nearest_match': best_m.signature,
                'reasoning': (
                    f"Überraschung={surprisal:.1f} bits. Bekanntes Muster. "
                    f"Pattern '{best_m.pattern}' (sim={best_s:.2f})"
                )
            }
        
        # Bekannt aber alle ähnlichen Bugs sind gescheitert
        return {
            'action': 'EXPLORE',
            'pattern': None,
            'confidence': best_sim,
            'surprisal': surprisal,
            'nearest_match': best_match.signature,
            'reasoning': (
                f"Ähnlich zu '{best_match.signature}' aber alle ähnlichen Bugs sind "
                f"gescheitert. Besser was Neues probieren."
            )
        }
    
    def learn(self, bug_signature: str, pattern: str, success: bool, embedding: list[float] = None) -> None:
        self.total_learned += 1
        
        for m in self.memories:
            if m.signature == bug_signature:
                m.pattern = pattern
                m.success = success
                m.access_count += 1
                if embedding is not None:
                    m.embedding = np.array(embedding)
                return
        
        emb = np.array(embedding) if embedding is not None else np.zeros(384)
        self.memories.append(MemoryEntry(
            signature=bug_signature,
            embedding=emb,
            pattern=pattern,
            success=success
        ))
    
    def stats(self) -> dict:
        n = len(self.memories)
        
        # Entropie des Gedächtnisses
        if n >= 2:
            embeddings = np.array([m.embedding for m in self.memories if len(m.embedding) == 384])
            if len(embeddings) >= 2:
                # Paarweise Ähnlichkeiten
                sims = []
                for i in range(len(embeddings)):
                    for j in range(i+1, len(embeddings)):
                        sims.append(self._cosine(embeddings[i], embeddings[j]))
                if sims:
                    hist, _ = np.histogram(sims, bins=10, density=True)
                    hist = hist[hist > 0]
                    entropy = -np.sum(hist * np.log2(hist))
                else:
                    entropy = 0.0
            else:
                entropy = 0.0
        else:
            entropy = 0.0
        
        success_rate = (
            sum(1 for m in self.memories if m.success) / n
            if n > 0 else 0.0
        )
        
        return {
            'brain_type': 'Shannon (Entropie-gesteuert)',
            'total_bugs_seen': self.total_bugs_seen,
            'total_learned': self.total_learned,
            'memories_stored': n,
            'explored': self.total_explored,
            'exploited': self.total_exploited,
            'success_rate': f"{success_rate:.1%}",
            'entropy_bits': f"{entropy:.2f}",
            'explore_ratio': (
                f"{self.total_explored/max(1,self.total_bugs_seen):.1%}"
                if self.total_bugs_seen > 0 else "0%"
            )
        }
    
    # ─── INTERN ───
    
    def _cosine(self, a: np.ndarray, b: np.ndarray) -> float:
        if len(a) == 0 or len(b) == 0 or len(a) != len(b):
            return 0.0
        dot = np.dot(a, b)
        norm = np.linalg.norm(a) * np.linalg.norm(b)
        return dot / norm if norm > 0 else 0.0
    
    def __repr__(self) -> str:
        s = self.stats()
        return (
            f"ShannonBrain(memories={s['memories_stored']}, "
            f"explore/exploit={s['explore_ratio']}, "
            f"entropy={s['entropy_bits']}bits)"
        )


# ─── DEMO ───
if __name__ == "__main__":
    print("=" * 60)
    print("GEHIRN B — Shannon Brain — DEMO")
    print("=" * 60)
    
    brain = ShannonBrain(explore_threshold=3.0)
    
    # Dummy-Embeddings (384dim Zufallsvektoren, später von SentenceTransformers)
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
        # Simuliere ähnliche Embeddings für gleiche Bug-Typen
        if 'NullPointer' in bug_sig:
            emb = np.random.randn(384) * 0.1 + 1.0
        elif 'OffByOne' in bug_sig:
            emb = np.random.randn(384) * 0.1 - 1.0
        elif 'TypeError' in bug_sig:
            emb = np.random.randn(384) * 0.1 + 2.0
        else:
            emb = np.random.randn(384) * 0.1 - 2.0
        
        emb = emb / np.linalg.norm(emb)
        
        decision = brain.think(bug_sig, emb.tolist())
        print(f"\n🐛 Bug #{i+1}: {bug_sig}")
        print(f"   Surprisal: {decision.get('surprisal', 0):.1f} bits")
        print(f"   🧠 {decision['reasoning']}")
        
        brain.learn(bug_sig, pattern, success)
    
    print(f"\n{'='*60}")
    print("📊 GEHIRN-STATUS:")
    for k, v in brain.stats().items():
        print(f"   {k}: {v}")
    
    # Zeige Explore/Exploit-Verlauf
    print(f"\n📈 EXPLORE vs EXPLOIT:")
    print(f"   Explore: {brain.total_explored} ({brain.total_explored/max(1,brain.total_bugs_seen):.0%})")
    print(f"   Exploit: {brain.total_exploited} ({brain.total_exploited/max(1,brain.total_bugs_seen):.0%})")
    
    print(f"\n✅ Gehirn B läuft eigenständig.")
