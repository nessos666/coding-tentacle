"""
GEHIRN A — Bayesian Brain (NARS-Logik)

Eigenständig. Keine externen Abhängigkeiten außer numpy.
Später in Coding Tentacle einsteckbar via BrainInterface.

Mathematik:
  Wahrheit = ⟨frequency, confidence⟩
  frequency = positive_evidence / total_evidence
  confidence = total_evidence / (total_evidence + k)

Autor: Hermes + David
Projekt: Coding Tentacle — Gehirn Bibliothek
"""

import math
import time
import numpy as np
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Pattern:
    """Ein Bug-Muster mit Bayesian-Konfidenz"""
    name: str
    frequency: float = 0.5       # Wie oft erfolgreich? (0..1)
    confidence: float = 0.1       # Wie sicher? (0..1)
    total_uses: int = 0           # Absolute Anzahl Anwendungen
    successes: int = 0            # Absolute Anzahl Erfolge
    last_used: float = 0.0        # Unix-Timestamp
    created: float = field(default_factory=time.time)
    deprecated: bool = False
    
    @property
    def age_days(self) -> float:
        return (time.time() - self.created) / 86400
    
    @property
    def days_unused(self) -> float:
        if self.last_used == 0:
            return self.age_days
        return (time.time() - self.last_used) / 86400


class BayesianBrain:
    """
    Gehirn A — Trifft Entscheidungen mit kalibrierter Konfidenz.
    
    KEINE externen Abhängigkeiten außer numpy.
    Eigenständig lauffähig. Kein Coding Tentacle nötig.
    """
    
    def __init__(self, k: float = 1.0, decay_lambda: float = 0.01):
        """
        Args:
            k: System-Konstante. Höher = mehr Evidenz nötig für hohe Konfidenz.
            decay_lambda: Täglicher Konfidenz-Verlust (0 = nie vergessen)
        """
        self.k = k
        self.decay_lambda = decay_lambda
        self.patterns: dict[str, Pattern] = {}
        self.total_bugs_seen: int = 0
        self.total_learned: int = 0
    
    # ─── BRAIN INTERFACE (standardisiert) ───
    
    def think(self, bug_signature: str, bug_embedding: list[float]) -> dict:
        """
        Bug kommt rein → Gehirn sucht ähnliche Patterns → Entscheidung raus.
        
        Returns:
            {
                'action': 'APPLY_PATTERN' | 'EXPLORE' | 'NO_PATTERN',
                'pattern': str | None,
                'confidence': float (0..1),
                'reasoning': str (erklärbar!)
            }
        """
        self.total_bugs_seen += 1
        
        # 1. Ähnlichste Patterns finden (aktuell: exakter Name-Match)
        # Später: Embedding-Cosine-Similarity
        candidates = self._find_candidates(bug_signature)
        
        if not candidates:
            return {
                'action': 'EXPLORE',
                'pattern': None,
                'confidence': 0.0,
                'reasoning': 'Kein ähnliches Pattern bekannt. Neues Terrain.'
            }
        
        # 2. Bestes Pattern nach Konfidenz (mit Decay)
        best = max(candidates, key=lambda p: self._effective_confidence(p))
        conf = self._effective_confidence(best)
        
        if conf > 0.25:
            return {
                'action': 'APPLY_PATTERN',
                'pattern': best.name,
                'confidence': conf,
                'reasoning': (
                    f"Pattern '{best.name}': "
                    f"{best.successes}/{best.total_uses} erfolgreich, "
                    f"Konfidenz={conf:.2f}"
                )
            }
        elif conf > 0.2:
            return {
                'action': 'EXPLORE',
                'pattern': best.name,
                'confidence': conf,
                'reasoning': (
                    f"Pattern '{best.name}' zu unsicher (Konfidenz={conf:.2f}<0.5). "
                    f"Mehr Daten sammeln."
                )
            }
        else:
            return {
                'action': 'NO_PATTERN',
                'pattern': best.name,
                'confidence': conf,
                'reasoning': (
                    f"Pattern '{best.name}' fast widerlegt (Konfidenz={conf:.2f}). "
                    f"Anti-Pattern?"
                )
            }
    
    def learn(self, bug_signature: str, pattern_name: str, success: bool) -> None:
        """
        Fix wurde validiert → Gehirn lernt daraus.
        
        Args:
            bug_signature: Eindeutige Bug-ID
            pattern_name: Name des angewendeten Patterns
            success: Hat der Fix gehalten?
        """
        self.total_learned += 1
        
        # Pattern finden oder neu anlegen
        if pattern_name not in self.patterns:
            self.patterns[pattern_name] = Pattern(name=pattern_name)
        
        pattern = self.patterns[pattern_name]
        
        # Bayesian Update
        pattern.total_uses += 1
        if success:
            pattern.successes += 1
        
        pattern.frequency = pattern.successes / pattern.total_uses
        pattern.confidence = pattern.total_uses / (pattern.total_uses + self.k)
        pattern.last_used = time.time()
        
        # Anti-Pattern erkennen (3× hintereinander gescheitert = deprecated)
        if pattern.total_uses >= 3 and pattern.successes == 0:
            pattern.deprecated = True
    
    def stats(self) -> dict:
        """Gesundheitszustand des Gehirns"""
        active = [p for p in self.patterns.values() if not p.deprecated]
        deprecated = [p for p in self.patterns.values() if p.deprecated]
        
        return {
            'brain_type': 'Bayesian (NARS-Logik)',
            'total_bugs_seen': self.total_bugs_seen,
            'total_learned': self.total_learned,
            'patterns_active': len(active),
            'patterns_deprecated': len(deprecated),
            'patterns_total': len(self.patterns),
            'avg_confidence': (
                np.mean([self._effective_confidence(p) for p in active])
                if active else 0.0
            ),
            'oldest_pattern_days': (
                max(p.age_days for p in self.patterns.values())
                if self.patterns else 0
            ),
        }
    
    # ─── INTERNE METHODEN ───
    
    def _effective_confidence(self, pattern: Pattern) -> float:
        """Konfidenz MIT Decay. Gewichtet mit Frequenz."""
        if pattern.deprecated:
            return 0.05
        decay = math.exp(-self.decay_lambda * pattern.days_unused)
        # Konfidenz × Frequenz — spiegelt WIRKLICHE Erfolgsrate wider
        return pattern.confidence * pattern.frequency * decay
    
    def _find_candidates(self, bug_signature: str) -> list[Pattern]:
        """Ähnliche Patterns finden via Bug-Typ + Embedding-Nähe"""
        bug_type = bug_signature.split(':')[0].lower() if ':' in bug_signature else bug_signature.lower()
        
        candidates = []
        for pattern in self.patterns.values():
            pattern_name_lower = pattern.name.lower()
            
            # Match: Bug-Typ im Pattern-Namen ODER umgekehrt
            if bug_type in pattern_name_lower or any(w in pattern_name_lower for w in bug_type.split('_') if w):
                candidates.append(pattern)
            # Auch: Pattern-Name enthält Bug-Typ
            elif pattern_name_lower.replace('→',' ').replace('_',' ').split()[0] == bug_type:
                candidates.append(pattern)
        
        # Fallback: Wenn keine direkten Matches, nimm alle Patterns mit Konfidenz > 0.3
        if not candidates:
            for pattern in self.patterns.values():
                if not pattern.deprecated and pattern.confidence > 0.3:
                    candidates.append(pattern)
        
        return candidates
    
    def __repr__(self) -> str:
        s = self.stats()
        return (
            f"BayesianBrain(patterns={s['patterns_active']} active, "
            f"{s['patterns_deprecated']} deprecated, "
            f"avg_conf={s['avg_confidence']:.2f})"
        )


# ─── DEMO (eigenständig lauffähig) ───
if __name__ == "__main__":
    print("=" * 60)
    print("GEHIRN A — Bayesian Brain — DEMO")
    print("=" * 60)
    
    brain = BayesianBrain(k=1.0, decay_lambda=0.01)
    
    # Simuliere 10 Bug-Fixes
    bugs = [
        ("NullPointer:payment.py:123", "NullPointer→guard_clause", True),
        ("NullPointer:auth.py:89", "NullPointer→guard_clause", True),
        ("NullPointer:order.py:45", "NullPointer→try_except", False),
        ("OffByOne:paginator.py:67", "OffByOne→boundary_check", True),
        ("NullPointer:user.py:200", "NullPointer→guard_clause", True),
        ("TypeError:parser.py:34", "TypeError→isinstance_check", True),
        ("NullPointer:email.py:12", "NullPointer→try_except", False),
        ("OffByOne:counter.py:90", "OffByOne→boundary_check", True),
        ("NullPointer:report.py:156", "NullPointer→guard_clause", True),
        ("NullPointer:config.py:78", "NullPointer→try_except", False),
    ]
    
    for i, (bug_sig, pattern, success) in enumerate(bugs):
        # 1. Denken
        decision = brain.think(bug_sig, [0.0]*384)  # Dummy-Embedding
        print(f"\n🐛 Bug #{i+1}: {bug_sig}")
        print(f"   🧠 Denkt: {decision['reasoning']}")
        
        # 2. Lernen
        brain.learn(bug_sig, pattern, success)
        print(f"   📚 Lernt: Pattern='{pattern}', Erfolg={success}")
    
    # 3. Gesundheitscheck
    print(f"\n{'='*60}")
    print("📊 GEHIRN-STATUS:")
    stats = brain.stats()
    for k, v in stats.items():
        print(f"   {k}: {v}")
    
    # 4. Pattern-Details
    print(f"\n📋 PATTERNS:")
    for name, p in brain.patterns.items():
        eff = brain._effective_confidence(p)
        status = "⚠️ DEPRECATED" if p.deprecated else "✅ ACTIVE"
        print(f"   {name}: f={p.frequency:.2f}, c={p.confidence:.2f}, "
              f"eff={eff:.2f}, uses={p.total_uses}, {status}")
    
    print(f"\n✅ Gehirn A läuft eigenständig. Kein Coding Tentacle nötig.")
