"""
GEHIRN G — Predictive Coding / Free Energy Brain (Friston)

Industrie-Standard. Basierend auf:
- Friston (2005-2024): Free Energy Principle
- Active Inference: Wahrnehmung + Handlung = Überraschung minimieren
- Predictive Coding: Gehirn als Vorhersagemaschine

Mathematik:
  Freie Energie:  F = D_KL[Q(s)||P(s)] - E_Q[ln P(o|s)]
  Überraschung:   -ln P(o|m) ≤ F
  Vorhersagefehler: ε = o - g(μ)  (sensorisch)
  Aktive Inferenz:  a* = argmin_a F(o, a, s)

Vorteil: Vereint Wahrnehmen + Handeln + Lernen in EINEM Prinzip.
         Der Agent MINIMIERT kontinuierlich seine Überraschung.

Autor: Hermes + David | Coding Tentacle Gehirn Bibliothek
"""

import time, math
import numpy as np
from collections import deque
from dataclasses import dataclass, field


@dataclass
class GenerativeModel:
    """Internes Modell: 'Wie die Welt funktioniert'"""
    states: np.ndarray          # μ — geschätzte Zustände
    precision: float = 1.0       # Π — Präzision (inverse Varianz)
    learning_rate: float = 0.1   # α — Lernrate für Modell-Update
    
    def predict(self) -> np.ndarray:
        """g(μ) — Vorhersage aus internen Zuständen"""
        return self.states  # Vereinfacht: Zustand = Vorhersage
    
    def update(self, prediction_error: np.ndarray):
        """μ ← μ + α·ε·Π — Zustand anpassen basierend auf Fehler"""
        self.states += self.learning_rate * prediction_error * self.precision


class PredictiveCodingBrain:
    """
    Gehirn G — Minimiert Freie Energie = Minimiert Überraschung.
    
    Kern-Mechanismen:
    - Generative Model: Internes Weltmodell erzeugt Vorhersagen
    - Prediction Error: Abweichung zwischen Vorhersage und Beobachtung
    - Free Energy: Oberes Limit für Überraschung → wird minimiert
    - Active Inference: Handlungen werden gewählt, um Überraschung zu reduzieren
    """
    
    def __init__(self, state_dim: int = 384, learning_rate: float = 0.1, 
                 precision: float = 1.0, history_size: int = 20):
        self.model = GenerativeModel(
            states=np.zeros(state_dim),
            precision=precision,
            learning_rate=learning_rate
        )
        self.history = deque(maxlen=history_size)
        self.total_bugs: int = 0
        self.total_surprise: float = 0.0
        self.patterns: dict = {}  # {pattern_name: (success_count, total_count)}
    
    # ─── BRAIN INTERFACE ───
    
    def think(self, bug_signature: str, bug_embedding: list[float]) -> dict:
        self.total_bugs += 1
        obs = np.array(bug_embedding)
        
        # 1. Vorhersage aus internem Modell
        prediction = self.model.predict()
        
        # 2. Vorhersagefehler berechnen
        if len(prediction) != len(obs):
            prediction = np.zeros_like(obs)
        error = obs - prediction
        
        # 3. Freie Energie (Überraschung) berechnen
        free_energy = self._free_energy(obs, prediction)
        self.total_surprise += free_energy
        
        # 4. Entscheidung basierend auf Freier Energie
        if free_energy > 50.0 or len(self.history) < 3:
            action = 'EXPLORE'
            pattern = None
            reasoning = f'Hohe Überraschung (F={free_energy:.1f}). Neues Terrain.'
        else:
            # Niedrige Überraschung → bekanntes Pattern anwenden
            action = 'APPLY_PATTERN'
            nearest = self._find_nearest_pattern(obs)
            pattern = nearest if nearest else 'default'
            reasoning = (f'Niedrige Überraschung (F={free_energy:.1f}). '
                        f'Internes Modell erklärt Bug gut. Pattern: {pattern}')
        
        return {
            'action': action,
            'pattern': pattern,
            'confidence': max(0.0, 1.0 - free_energy/100.0),
            'free_energy': free_energy,
            'prediction_error_norm': float(np.linalg.norm(error)),
            'reasoning': reasoning
        }
    
    def learn(self, bug_signature: str, pattern: str, success: bool,
              embedding: list[float] = None) -> None:
        obs = np.array(embedding) if embedding else np.zeros(384)
        
        # 1. Vorhersagefehler = Lernsignal
        prediction = self.model.predict()
        if len(prediction) == len(obs):
            error = obs - prediction
            self.model.update(error)  # μ ← μ + α·ε·Π
        
        # 2. Erfolgs-Tracking für Patterns
        if pattern not in self.patterns:
            self.patterns[pattern] = [0, 0]
        self.patterns[pattern][1] += 1
        if success:
            self.patterns[pattern][0] += 1
        
        # 3. History für Kontext
        self.history.append(obs)
    
    def stats(self) -> dict:
        avg_F = self.total_surprise / max(1, self.total_bugs)
        n_patterns = len(self.patterns)
        successful = sum(1 for s, t in self.patterns.values() if t > 0 and s/t > 0.5)
        
        return {
            'brain_type': 'Predictive Coding / Free Energy (Friston)',
            'total_bugs': self.total_bugs,
            'avg_free_energy': f'{avg_F:.1f}',
            'model_norm': f'{np.linalg.norm(self.model.states):.1f}',
            'history_size': len(self.history),
            'patterns': n_patterns,
            'successful_patterns': successful,
            'precision': self.model.precision,
        }
    
    # ─── INTERN ───
    
    def _free_energy(self, observation: np.ndarray, prediction: np.ndarray) -> float:
        """F ≈ ||o - g(μ)||²·Π — Vereinfachte Freie Energie"""
        if len(observation) != len(prediction):
            return 100.0
        error = observation - prediction
        return float(np.dot(error, error) * self.model.precision * 0.01)
    
    def _find_nearest_pattern(self, obs: np.ndarray) -> str:
        """Nächste Pattern über Embedding-Ähnlichkeit im History"""
        if not self.history:
            return None
        similarities = [np.dot(obs, h)/(np.linalg.norm(obs)*np.linalg.norm(h)) 
                       for h in self.history]
        best_idx = np.argmax(similarities)
        return f'history_pattern_{best_idx}'
    
    def _cosine(self, a: np.ndarray, b: np.ndarray) -> float:
        if len(a) != len(b) or len(a) == 0:
            return 0.0
        dot = np.dot(a, b)
        norm = np.linalg.norm(a) * np.linalg.norm(b)
        return dot / norm if norm > 0 else 0.0
    
    def __repr__(self) -> str:
        s = self.stats()
        return f"PredCodingBrain(F={s['avg_free_energy']}, patterns={s['patterns']})"


# ─── DEMO ───
if __name__ == "__main__":
    print("=" * 60)
    print("GEHIRN G — Predictive Coding / Free Energy — DEMO")
    print("=" * 60)
    
    brain = PredictiveCodingBrain(state_dim=384, learning_rate=0.1)
    np.random.seed(42)
    
    bugs = [
        ("NullPointer:pay.py:1", "guard_clause", True),
        ("NullPointer:auth.py:2", "guard_clause", True),
        ("OffByOne:page.py:1", "boundary_check", True),
        ("NullPointer:order.py:3", "guard_clause", True),
        ("TypeError:parse.py:1", "type_convert", True),
        ("NullPointer:user.py:4", "guard_clause", True),
        ("MemoryLeak:cache.py:1", "weakref", True),
        ("NullPointer:email.py:5", "try_except", False),
        ("OffByOne:list.py:2", "boundary_check", True),
        ("NullPointer:report.py:6", "guard_clause", True),
    ]
    
    for i, (sig, pattern, success) in enumerate(bugs):
        emb = (np.random.randn(384) * 0.5 + (1.0 if 'NullPointer' in sig else -1.0))
        emb = emb / np.linalg.norm(emb)
        
        dec = brain.think(sig, emb.tolist())
        F = dec.get('free_energy', 0)
        print(f"Bug {i+1}: {sig[:35]} | F={F:.1f} | {dec['action']:15s} | {dec['reasoning'][:55]}")
        brain.learn(sig, pattern, success, emb.tolist())
    
    print(f"\n{'='*60}")
    for k, v in brain.stats().items():
        print(f"  {k}: {v}")
    print(f"\n✅ Gehirn G läuft.")
