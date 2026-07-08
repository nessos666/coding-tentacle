"""
GEHIRN F — ACT-R / Spreading Activation Brain

Industrie-Standard. Basierend auf:
- ACT-R (Anderson, CMU, seit 1993): Adaptive Control of Thought-Rational
- Spreading Activation (Collins & Loftus, 1975)
- python_actr (Python-Portierung, 2025)

Mathematik:
  Base-Level Activation:  B_i = ln(Σ t_j^(-d))
  Spreading Activation:   S_i = Σ W_j * S_ji
  Gesamt-Aktivierung:     A_i = B_i + S_i + ε
  Retrieval-Wkeit:        P = 1 / (1 + e^(-(A - τ)/s))

Vorteil: Biologisch plausibel. Natürliches Vergessen. Assoziatives Gedächtnis.
         Ein Bug weckt verwandte Patterns auf (Spreading).

Autor: Hermes + David | Coding Tentacle Gehirn Bibliothek
"""

import time, math
import numpy as np
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MemoryChunk:
    """ACT-R Chunk: Ein Gedächtniselement mit Aktivierung"""
    name: str
    creation_time: float = field(default_factory=time.time)
    access_times: list = field(default_factory=list)
    associations: dict = field(default_factory=dict)  # {other_chunk: strength}
    
    def base_level(self, current_time: float, decay: float = 0.5) -> float:
        """B = ln(Σ t_j^(-d)) — je öfter/genutzt, desto höher"""
        if not self.access_times:
            return -10.0  # Nie genutzt = sehr niedrig
        ages = [max(0.001, current_time - t) for t in self.access_times]
        return math.log(sum(a ** (-decay) for a in ages))
    
    def access(self, current_time: float):
        self.access_times.append(current_time)


class ACTRBrain:
    """
    Gehirn F — Simuliert menschliches Gedächtnis mit Aktivierungsgleichungen.
    
    Kern-Mechanismen:
    - Base-Level Learning: Je öfter genutzt, desto leichter abrufbar
    - Spreading Activation: Ähnliche Chunks feuern mit
    - Decay: Ungenutztes Wissen verblasst
    - Noise: Stochastischer Abruf (nicht deterministisch)
    """
    
    def __init__(self, decay: float = 0.5, threshold: float = -2.0,
                 noise: float = 0.4, spreading_weight: float = 0.3):
        self.decay = decay
        self.threshold = threshold
        self.noise = noise
        self.spreading_weight = spreading_weight
        self.chunks: dict[str, MemoryChunk] = {}
        self.total_bugs: int = 0
        self.total_retrievals: int = 0
        self.total_failures: int = 0  # Retrieval unter Threshold
    
    # ─── BRAIN INTERFACE ───
    
    def think(self, bug_signature: str, bug_embedding: list[float]) -> dict:
        self.total_bugs += 1
        now = time.time()
        bug_type = self._extract_type(bug_signature)
        emb = np.array(bug_embedding)
        
        # 1. Aktiven Kontext bestimmen (Bug-Typ + ähnliche Chunks)
        active_context = self._find_active_context(bug_type, emb)
        
        # 2. Spreading Activation: aktive Chunks aktivieren assoziierte Chunks
        activations = {}
        for chunk_name, chunk in self.chunks.items():
            B = chunk.base_level(now, self.decay)
            S = self._spreading(chunk_name, active_context)
            eps = np.random.logistic(0, self.noise)
            A = B + S + eps
            activations[chunk_name] = A
        
        # 3. Chunks über Threshold abrufen
        candidates = {n: a for n, a in activations.items() if a > self.threshold}
        
        if not candidates:
            self.total_failures += 1
            max_act = max(activations.values()) if activations else -999
            return {
                'action': 'EXPLORE',
                'pattern': None,
                'retrievable': 0,
                'reasoning': f'Kein Chunk über Threshold ({self.threshold}). '
                             f'Max Aktivierung: {max_act:.1f}'
            }
        
        # 4. Stochastischer Abruf (Softmax über Aktivierungen)
        self.total_retrievals += 1
        names = list(candidates.keys())
        acts = np.array([candidates[n] for n in names])
        probs = np.exp(acts - np.max(acts))
        probs /= probs.sum()
        
        chosen_idx = np.random.choice(len(names), p=probs)
        chosen = names[chosen_idx]
        self.chunks[chosen].access(now)
        
        # 5. Pattern aus Chunk extrahieren
        pattern = self._chunk_to_pattern(chosen)
        
        return {
            'action': 'APPLY_PATTERN',
            'pattern': pattern,
            'confidence': min(1.0, candidates[chosen] / 10.0),
            'retrievable': len(candidates),
            'activation': candidates[chosen],
            'reasoning': f'Chunk {chosen} aktiviert (A={candidates[chosen]:.1f}) '
                         f'via {"Spreading" if self._spreading(chosen, active_context) > 0.5 else "Base-Level"}'
        }
    
    def learn(self, bug_signature: str, pattern: str, success: bool,
              embedding: list[float] = None) -> None:
        now = time.time()
        bug_type = self._extract_type(bug_signature)
        
        # Pattern als Chunk speichern (oder existierenden verstärken)
        chunk_name = f"{bug_type}_{pattern}"
        
        if chunk_name not in self.chunks:
            self.chunks[chunk_name] = MemoryChunk(name=chunk_name)
        
        chunk = self.chunks[chunk_name]
        chunk.access(now)
        
        # Erfolg/Misserfolg als Assoziationsstärke
        if success:
            # Stärkere Assoziation zum Bug-Typ
            if bug_type not in chunk.associations:
                chunk.associations[bug_type] = 0.0
            chunk.associations[bug_type] += 0.15
        
        # Assoziationen zu ähnlichen Chunks aufbauen (Spreading)
        if embedding is not None:
            emb = np.array(embedding)
            for other_name, other_chunk in self.chunks.items():
                if other_name == chunk_name:
                    continue
                # Vereinfacht: alle Chunks gleichen Typs assoziieren
                if bug_type in other_name:
                    chunk.associations[other_name] = min(2.0, 
                        chunk.associations.get(other_name, 0.0) + 0.05)
    
    def stats(self) -> dict:
        n = len(self.chunks)
        now = time.time()
        
        base_levels = [c.base_level(now, self.decay) for c in self.chunks.values()]
        n_assoc = sum(1 for c in self.chunks.values() if c.associations)
        
        return {
            'brain_type': 'ACT-R / Spreading Activation',
            'total_bugs': self.total_bugs,
            'chunks': n,
            'chunks_with_associations': n_assoc,
            'retrievals': self.total_retrievals,
            'failures': self.total_failures,
            'retrieval_rate': f'{self.total_retrievals/max(1,self.total_bugs):.0%}',
            'mean_base_level': f'{np.mean(base_levels):.1f}' if base_levels else 'N/A',
            'decay_rate': self.decay,
        }
    
    # ─── INTERN ───
    
    def _extract_type(self, sig: str) -> str:
        return sig.split(':')[0] if ':' in sig else sig
    
    def _find_active_context(self, bug_type: str, emb: np.ndarray) -> set:
        """Aktiver Kontext = Bug-Typ + ähnliche Chunks"""
        context = {bug_type}
        for name in self.chunks:
            if bug_type.lower() in name.lower():
                context.add(name)
        return context
    
    def _spreading(self, chunk_name: str, active_context: set) -> float:
        """S = Σ W_j * S_ji — Aktivierung von aktivem Kontext"""
        chunk = self.chunks.get(chunk_name)
        if not chunk:
            return 0.0
        total = 0.0
        for source in active_context:
            if source in chunk.associations:
                total += chunk.associations[source]
        return total * self.spreading_weight
    
    def _chunk_to_pattern(self, chunk_name: str) -> str:
        """'NullPointer_guard_clause' → 'guard_clause'"""
        parts = chunk_name.split('_', 1)
        return parts[1] if len(parts) > 1 else chunk_name
    
    def __repr__(self) -> str:
        return f"ACTRBrain(chunks={len(self.chunks)}, retrievals={self.total_retrievals})"


# ─── DEMO ───
if __name__ == "__main__":
    print("=" * 60)
    print("GEHIRN F — ACT-R / Spreading Activation — DEMO")
    print("=" * 60)
    
    brain = ACTRBrain(decay=0.5, threshold=-2.0, noise=0.3)
    np.random.seed(42)
    
    bugs = [
        ("NullPointer:pay.py:1", "guard_clause", True),
        ("NullPointer:auth.py:2", "guard_clause", True),
        ("NullPointer:order.py:3", "guard_clause", True),
        ("OffByOne:page.py:1", "boundary_check", True),
        ("NullPointer:user.py:4", "guard_clause", True),
        ("NullPointer:email.py:5", "try_except", False),
        ("OffByOne:list.py:2", "boundary_check", True),
        ("NullPointer:report.py:6", "guard_clause", True),
        ("TypeError:parse.py:1", "type_convert", True),
        ("NullPointer:config.py:7", "guard_clause", True),
    ]
    
    for i, (sig, pattern, success) in enumerate(bugs):
        emb = (np.random.randn(384) * 0.1 + (1.0 if 'NullPointer' in sig else -1.0))
        emb = emb / np.linalg.norm(emb)
        
        dec = brain.think(sig, emb.tolist())
        act = dec.get('activation', 0)
        print(f"Bug {i+1}: {sig[:35]} | {dec['action']:15s} | A={act:.1f} | {dec['reasoning'][:50]}")
        brain.learn(sig, pattern, success, emb.tolist())
    
    print(f"\n{'='*60}")
    for k, v in brain.stats().items():
        print(f"  {k}: {v}")
    print(f"\n✅ Gehirn F läuft.")
