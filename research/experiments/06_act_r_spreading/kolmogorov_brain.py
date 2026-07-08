"""
GEHIRN I — Kolmogorov Compression Brain

Industrie-Standard. Basierend auf:
- Kolmogorov (1965): K(x) = Länge des kürzesten Programms, das x erzeugt
- Algorithmische Informationstheorie (Chaitin, Solomonoff)
- Intelligenz = Kompression (Krakauer, Santa Fe Institute)

Mathematik:
  K(x) = min{|p| : U(p) = x}      (Kolmogorov-Komplexität)
  NCD(x,y) = (C(xy)-min(C(x),C(y))) / max(C(x),C(y))  (Normalized Compression Distance)
  Intelligence = Compression Ratio (Krakauer)

Vorteil: Findet STRUKTUR durch Komprimierbarkeit.
         Einfache Patterns = stark komprimierbar = hohe Konfidenz.
         Komplexe Patterns = schlecht komprimierbar = unsicher.

Autor: Hermes + David | Coding Tentacle Gehirn Bibliothek
"""

import time, math, zlib
import numpy as np
from collections import defaultdict


def kolmogorov_approx(data: str) -> int:
    """Approximiere K(x) via gzip-Kompression"""
    return len(zlib.compress(data.encode(), level=9))


def ncd_distance(a: str, b: str) -> float:
    """Normalized Compression Distance zwischen a und b"""
    ca, cb = kolmogorov_approx(a), kolmogorov_approx(b)
    cab = kolmogorov_approx(a + b)
    return (cab - min(ca, cb)) / max(ca, cb) if max(ca, cb) > 0 else 1.0


class KolmogorovBrain:
    """
    Gehirn I — Misst Komplexität als Komprimierbarkeit.
    
    Kern-Idee: Ein Bug-Pattern ist GUT, wenn es den Bug TEXT stark komprimiert.
    "guard clause check payment" = 28 Zeichen → 20 komprimiert = Ratio 0.71
    
    Je besser ein Pattern den Bug erklärt, desto kürzer die Beschreibung.
    Intelligenz = Kompression.
    """
    
    def __init__(self, compression_threshold: float = 0.3):
        self.threshold = compression_threshold
        self.patterns: dict = {}        # {pattern_name: pattern_description}
        self.bug_descriptions: dict = {} # {bug_signature: description}
        self.compression_scores: dict = {} # {(bug, pattern): (ncd, success_count, total)}
        self.total_bugs: int = 0
    
    # ─── BRAIN INTERFACE ───
    
    def think(self, bug_signature: str, bug_embedding: list[float]) -> dict:
        self.total_bugs += 1
        
        if not self.patterns:
            return {
                'action': 'EXPLORE', 'pattern': None, 'confidence': 0.0,
                'reasoning': 'Keine Patterns zum Komprimieren. Leeres Modell.'
            }
        
        # 1. NCD zwischen Bug und jedem Pattern berechnen
        # Verwendet bug_signature als Approximation des Bug-Textes
        best_pattern, best_ncd, best_score = None, 1.0, 0
        
        for pat_name, pat_desc in self.patterns.items():
            d = ncd_distance(bug_signature, pat_desc)
            compressibility = 1.0 - d  # 1.0 = perfekt, 0.0 = gar nicht
            
            if compressibility > best_score:
                best_score = compressibility
                best_ncd = d
                best_pattern = pat_name
        
        if best_score > self.threshold:
            return {
                'action': 'APPLY_PATTERN',
                'pattern': best_pattern,
                'confidence': best_score,
                'ncd': best_ncd,
                'reasoning': (f'Pattern {best_pattern} komprimiert Bug auf '
                            f'{best_ncd:.2f} NCD. Komprimierbarkeit={best_score:.2f}')
            }
        
        return {
            'action': 'EXPLORE', 'pattern': None, 'confidence': 0.0,
            'ncd': best_ncd,
            'reasoning': f'Beste Komprimierbarkeit={best_score:.2f} < {self.threshold}. Neues Pattern nötig.'
        }
    
    def learn(self, bug_signature: str, pattern: str, success: bool,
              embedding: list[float] = None) -> None:
        
        # 1. Bug-Text speichern (für NCD-Berechnung)
        if bug_signature not in self.bug_descriptions:
            self.bug_descriptions[bug_signature] = bug_signature
        
        # 2. Pattern-Beschreibung aufbauen (akkumuliert Bug-Signaturen)
        if pattern not in self.patterns:
            self.patterns[pattern] = bug_signature
        else:
            self.patterns[pattern] += ' ' + bug_signature.split(':')[0]
            # Begrenzen auf ~500 Zeichen
            if len(self.patterns[pattern]) > 500:
                self.patterns[pattern] = self.patterns[pattern][-500:]
        
        # 3. Kompressions-Score tracken
        key = (bug_signature, pattern)
        if key not in self.compression_scores:
            ndist = ncd_distance(bug_signature, self.patterns[pattern])
            self.compression_scores[key] = [ndist, 0, 0]
        
        ncd_val, succ, total = self.compression_scores[key]
        total += 1
        if success:
            succ += 1
        self.compression_scores[key] = [ncd_val, succ, total]
    
    def stats(self) -> dict:
        avg_success = np.mean([s/t for _, s, t in self.compression_scores.values() if t > 0]) \
            if self.compression_scores else 0.0
        
        # Beste Patterns (höchste Komprimierbarkeit + Erfolg)
        pattern_scores = defaultdict(list)
        for (_, pat), (ncd_val, succ, total) in self.compression_scores.items():
            if total > 0:
                pattern_scores[pat].append((1.0 - ncd_val) * (succ/total))
        
        best = sorted(pattern_scores.items(), 
                     key=lambda x: np.mean(x[1]), reverse=True)[:3]
        
        return {
            'brain_type': 'Kolmogorov Compression (K(x))',
            'total_bugs': self.total_bugs,
            'patterns': len(self.patterns),
            'compression_entries': len(self.compression_scores),
            'avg_success_rate': f'{avg_success:.2f}',
            'best_patterns': [f'{p}: score={np.mean(s):.2f}' for p, s in best],
        }
    
    def __repr__(self) -> str:
        s = self.stats()
        return f"KolmogorovBrain(patterns={s['patterns']}, entries={s['compression_entries']})"


# ─── DEMO ───
if __name__ == "__main__":
    print("=" * 60)
    print("GEHIRN I — Kolmogorov Compression — DEMO")
    print("=" * 60)
    
    brain = KolmogorovBrain(compression_threshold=0.15)
    
    bugs = [
        ("NullPointer:payment.py:123:None-check-missing", "guard_clause", True),
        ("NullPointer:auth.py:89:session-expired-null", "guard_clause", True),
        ("OffByOne:paginator.py:67:index-out-of-range", "boundary_check", True),
        ("NullPointer:order.py:45:empty-cart-null", "guard_clause", True),
        ("TypeError:parser.py:34:str-int-concat", "type_convert", True),
        ("NullPointer:user.py:200:profile-null", "guard_clause", True),
        ("MemoryLeak:cache.py:12:lru-unbounded", "weakref", True),
        ("NullPointer:email.py:56:template-null", "try_except", False),
        ("OffByOne:counter.py:90:loop-boundary", "boundary_check", True),
        ("NullPointer:report.py:156:no-data-null", "guard_clause", True),
    ]
    
    for i, (sig, pattern, success) in enumerate(bugs):
        dec = brain.think(sig, [0.0]*384)
        ncd = dec.get('ncd', 1.0)
        print(f"Bug {i+1}: {sig[:55]} | NCD={ncd:.2f} | {dec['action']:15s} | {dec['reasoning'][:55]}")
        brain.learn(sig, pattern, success)
    
    print(f"\n{'='*60}")
    for k, v in brain.stats().items():
        print(f"  {k}: {v}")
    print(f"\n✅ Gehirn I läuft.")
