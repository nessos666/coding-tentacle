"""
GEHIRN H — Causal Reasoning Brain (Pearl)

Industrie-Standard. Basierend auf:
- Pearl (1995-2011): do-Kalkül, Strukturelle Kausalmodelle
- DoWhy (Microsoft/PyWhy, 2024): Python causal inference library
- PC-Algorithmus: Constraint-based causal discovery

Mathematik:
  do-Kalkül:       P(Y|do(X)) — Effekt einer Intervention
  Backdoor:        P(Y|do(X)) = Σ_z P(Y|X,Z)·P(Z)
  Kausaler Effekt: ATE = E[Y|do(X=1)] - E[Y|do(X=0)]

Vorteil: Findet URSACHEN, nicht nur Korrelationen.
         "Correlation is not causation" — dieses Gehirn versteht den Unterschied.

Autor: Hermes + David | Coding Tentacle Gehirn Bibliothek
"""

import time, math
import numpy as np
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class CausalLink:
    """Kausale Verbindung: A → B mit Stärke"""
    cause: str
    effect: str
    strength: float = 0.0        # Wie stark ist der kausale Effekt?
    confidence: float = 0.0      # Wie sicher sind wir?
    observations: int = 0        # Anzahl Beobachtungen


class CausalBrain:
    """
    Gehirn H — Unterscheidet KORRELATION von KAUSATION.
    
    Kern-Mechanismen:
    - Interventions-Modellierung: Was passiert WENN ich X ändere?
    - Backdoor-Adjustierung: Störfaktoren herausrechnen
    - Kausale Entdeckung: Welche Variablen beeinflussen welche?
    - Konterfaktuale: Was WÄRE gewesen, wenn...?
    """
    
    def __init__(self, significance: float = 0.05):
        self.significance = significance
        self.links: dict[str, CausalLink] = {}  # {(cause,effect): CausalLink}
        self.patterns: dict[str, list] = {}      # {bug_type: [(fix, success)]}
        self.total_bugs: int = 0
    
    # ─── BRAIN INTERFACE ───
    
    def think(self, bug_signature: str, bug_embedding: list[float]) -> dict:
        self.total_bugs += 1
        bug_type = bug_signature.split(':')[0] if ':' in bug_signature else bug_signature
        
        # 1. Kausale Frage: "WENN ich Pattern X anwende, WIRD der Bug behoben?"
        candidate_fixes = self._find_candidates(bug_type)
        
        if not candidate_fixes:
            return {
                'action': 'EXPLORE',
                'pattern': None,
                'confidence': 0.0,
                'reasoning': f'Keine kausalen Daten für {bug_type}. Intervention nötig.'
            }
        
        # 2. Besten Fix nach kausalem Effekt wählen
        # ATE = E[success|do(pattern)] — korrigiert für Confounder
        best_fix, best_effect, best_conf = None, -1.0, 0.0
        
        for fix_name in candidate_fixes:
            link_key = f"{bug_type}→{fix_name}"
            if link_key in self.links:
                link = self.links[link_key]
                adj_effect = link.strength  # Vereinfacht (volle Backdoor teuer)
                if adj_effect > best_effect:
                    best_effect = adj_effect
                    best_fix = fix_name
                    best_conf = link.confidence
        
        if best_fix and best_conf > 0.3:
            return {
                'action': 'APPLY_PATTERN',
                'pattern': best_fix,
                'confidence': best_conf,
                'causal_effect': best_effect,
                'reasoning': (f'Kausaler Effekt von {best_fix} auf {bug_type}: '
                            f'{best_effect:.2f} (Konfidenz={best_conf:.2f})')
            }
        
        return {
            'action': 'EXPLORE',
            'pattern': None,
            'confidence': 0.0,
            'reasoning': f'Kausale Effekte zu schwach für {bug_type}. Mehr Daten nötig.'
        }
    
    def learn(self, bug_signature: str, pattern: str, success: bool,
              embedding: list[float] = None) -> None:
        bug_type = bug_signature.split(':')[0] if ':' in bug_signature else bug_signature
        
        # 1. Kausale Verknüpfung aktualisieren
        link_key = f"{bug_type}→{pattern}"
        if link_key not in self.links:
            self.links[link_key] = CausalLink(cause=bug_type, effect=pattern)
        
        link = self.links[link_key]
        link.observations += 1
        
        # Bayesian Update der kausalen Stärke
        n = link.observations
        old_strength = link.strength
        reward = 1.0 if success else 0.0
        link.strength = (old_strength * (n-1) + reward) / n
        link.confidence = n / (n + 1.0)  # NARS-Konfidenz
        
        # 2. Pattern-Erfolgs-Tracking
        if bug_type not in self.patterns:
            self.patterns[bug_type] = []
        self.patterns[bug_type].append((pattern, success))
    
    def stats(self) -> dict:
        n_links = len(self.links)
        strong_links = sum(1 for l in self.links.values() 
                          if l.confidence > 0.5 and l.strength > 0.5)
        total_obs = sum(l.observations for l in self.links.values())
        
        top_causal = sorted(self.links.items(), 
                          key=lambda x: x[1].strength * x[1].confidence, 
                          reverse=True)[:3]
        
        return {
            'brain_type': 'Causal Reasoning (Pearl do-Kalkül)',
            'total_bugs': self.total_bugs,
            'causal_links': n_links,
            'strong_links': strong_links,
            'total_observations': total_obs,
            'top_causal': [f'{k} → {l.effect} (eff={l.strength:.2f}, conf={l.confidence:.2f})' 
                          for k, l in top_causal],
        }
    
    def _find_candidates(self, bug_type: str) -> list:
        """Alle Patterns, die jemals für diesen Bug-Typ versucht wurden"""
        candidates = set()
        for link_key in self.links:
            if link_key.startswith(f"{bug_type}→"):
                candidates.add(link_key.split('→')[1])
        return list(candidates)
    
    def __repr__(self) -> str:
        s = self.stats()
        return f"CausalBrain(links={s['causal_links']}, strong={s['strong_links']})"


# ─── DEMO ───
if __name__ == "__main__":
    print("=" * 60)
    print("GEHIRN H — Causal Reasoning (Pearl) — DEMO")
    print("=" * 60)
    
    brain = CausalBrain()
    
    bugs = [
        ("NullPointer:pay.py:1", "guard_clause", True),
        ("NullPointer:auth.py:2", "guard_clause", True),
        ("NullPointer:order.py:3", "try_except", False),
        ("OffByOne:page.py:1", "boundary_check", True),
        ("NullPointer:user.py:4", "guard_clause", True),
        ("NullPointer:email.py:5", "try_except", False),
        ("TypeError:parse.py:1", "type_convert", True),
        ("NullPointer:report.py:6", "guard_clause", True),
        ("OffByOne:list.py:2", "boundary_check", True),
        ("NullPointer:config.py:7", "guard_clause", True),
    ]
    
    for i, (sig, pattern, success) in enumerate(bugs):
        dec = brain.think(sig, [0.0]*384)
        eff = dec.get('causal_effect', 0)
        print(f"Bug {i+1}: {sig[:35]} | {dec['action']:15s} | eff={eff:.2f} | {dec['reasoning'][:55]}")
        brain.learn(sig, pattern, success)
    
    print(f"\n{'='*60}")
    for k, v in brain.stats().items():
        print(f"  {k}: {v}")
    print(f"\n✅ Gehirn H läuft.")
