"""
GEHIRN D — RL Brain (Belohnungs-basiert)

Eigenständig. Nur numpy. Gleiche Schnittstelle.
Q-Learning: Jede Memory-Aktion hat erwartete Belohnung.

Mathematik:
  Q(s,a) ← Q(s,a) + α [r + γ·max Q(s',a') - Q(s,a)]
  State = Bug-Typ
  Actions = STORE, APPLY, IGNORE, FORGET

Autor: Hermes + David
"""

import time
import random
import numpy as np
from collections import defaultdict


class RLBrain:
    """
    Gehirn D — Entscheidet per Q-Learning, was es mit Bugs tun soll.
    
    Aktionen:
      STORE: Bug speichern
      APPLY_PATTERN: Bekanntes Pattern anwenden
      IGNORE: Nichts tun
      CONSOLIDATE: Alte Einträge komprimieren (selten)
    
    Reward:
      +1.0: Fix hat gehalten
      -0.5: Fix hat nicht gehalten
      +0.2: Pattern war hilfreich
      -0.1: Speichern kostet
      +0.5: Neues Pattern entdeckt
    """
    
    ACTIONS = ['STORE', 'APPLY_PATTERN', 'IGNORE', 'CONSOLIDATE']
    
    def __init__(self, alpha: float = 0.1, gamma: float = 0.9, epsilon: float = 0.15):
        self.alpha = alpha      # Lernrate
        self.gamma = gamma       # Discount-Faktor
        self.epsilon = epsilon   # Exploration-Rate
        self.Q: dict = defaultdict(float)  # {(bug_type, action): value}
        self.total_bugs_seen: int = 0
        self.total_learned: int = 0
        self.last_action: str = 'IGNORE'
        self.last_bug_type: str = ''
        self.reward_history: list = []
    
    # ─── BRAIN INTERFACE ───
    
    def think(self, bug_signature: str, bug_embedding: list[float]) -> dict:
        self.total_bugs_seen += 1
        bug_type = self._extract_type(bug_signature)
        self.last_bug_type = bug_type
        
        # ε-greedy: Explore oder Exploit?
        if random.random() < self.epsilon:
            action = random.choice(self.ACTIONS)
        else:
            qs = [self.Q[(bug_type, a)] for a in self.ACTIONS]
            action = self.ACTIONS[np.argmax(qs)]
        
        self.last_action = action
        
        q_values = {a: f"{self.Q[(bug_type, a)]:.2f}" for a in self.ACTIONS}
        
        if action == 'APPLY_PATTERN':
            return {
                'action': 'APPLY_PATTERN',
                'pattern': f"best_for_{bug_type}",
                'q_values': q_values,
                'reasoning': f"RL waehlt APPLY_PATTERN fuer {bug_type} (Q={self.Q[(bug_type, 'APPLY_PATTERN')]:.2f})"
            }
        elif action == 'STORE':
            return {
                'action': 'EXPLORE',
                'pattern': None,
                'q_values': q_values,
                'reasoning': f"RL waehlt STORE: Bug {bug_type} speichern (Q={self.Q[(bug_type, 'STORE')]:.2f})"
            }
        elif action == 'CONSOLIDATE':
            return {
                'action': 'EXPLORE',
                'pattern': None,
                'q_values': q_values,
                'reasoning': f"RL waehlt CONSOLIDATE (Q={self.Q[(bug_type, 'CONSOLIDATE')]:.2f})"
            }
        else:
            return {
                'action': 'NO_PATTERN',
                'pattern': None,
                'q_values': q_values,
                'reasoning': f"RL waehlt IGNORE (Q={self.Q[(bug_type, 'IGNORE')]:.2f})"
            }
    
    def learn(self, bug_signature: str, pattern: str, success: bool, 
              embedding: list[float] = None, action: str = None) -> None:
        self.total_learned += 1
        
        bug_type = self._extract_type(bug_signature)
        # Allow explicit action override for training
        actual_action = action if action else self.last_action
        
        # Reward berechnen
        if actual_action == 'APPLY_PATTERN':
            reward = 2.0 if success else -0.5  # HÖHERER Reward für Pattern-Nutzung
        elif actual_action == 'STORE':
            reward = 0.3 if success else -0.1  # Speichern ist ok, aber weniger wert
        elif actual_action == 'CONSOLIDATE':
            reward = 0.5
        else:  # IGNORE
            reward = -0.5 if success else 0.0  # Bereuen wenn Bug erfolgreich war
        
        self.reward_history.append(reward)
        
        # Q-Learning Update
        old_q = self.Q[(bug_type, actual_action)]
        next_qs = [self.Q[(bug_type, a)] for a in self.ACTIONS]
        max_next_q = max(next_qs) if next_qs else 0.0
        
        self.Q[(bug_type, actual_action)] = old_q + self.alpha * (
            reward + self.gamma * max_next_q - old_q)
    
    def stats(self) -> dict:
        total_r = len(self.reward_history)
        avg_r = np.mean(self.reward_history[-100:]) if self.reward_history else 0.0
        
        # Meistgewaehlte Aktionen
        action_counts = defaultdict(int)
        action_vals = defaultdict(list)
        for (bt, a), v in self.Q.items():
            action_counts[a] += 1
            action_vals[a].append(v)
        
        return {
            'brain_type': 'RL (Q-Learning)',
            'total_bugs_seen': self.total_bugs_seen,
            'total_learned': self.total_learned,
            'q_table_size': len(self.Q),
            'epsilon': f"{self.epsilon:.2f}",
            'avg_reward_last100': f"{avg_r:.2f}",
            'best_action': (
                max(action_counts, key=action_counts.get) if action_counts else 'N/A'
            ),
            'avg_q_per_action': {
                a: f"{np.mean(vals):.2f}" for a, vals in action_vals.items()
            }
        }
    
    def _extract_type(self, signature: str) -> str:
        return signature.split(':')[0] if ':' in signature else signature
    
    def __repr__(self) -> str:
        s = self.stats()
        return f"RLBrain(q_size={s['q_table_size']}, avg_r={s['avg_reward_last100']})"


# ─── DEMO ───
if __name__ == "__main__":
    print("=" * 60)
    print("GEHIRN D — RL Brain — DEMO")
    print("=" * 60)
    print("(RL braucht ~50 Bugs zum Trainieren. Kurze Demo.)")
    
    random.seed(42)
    brain = RLBrain(alpha=0.1, gamma=0.9, epsilon=0.3)
    
    bugs = [
        ("NullPointer:payment.py:123", "guard_clause", True),
        ("NullPointer:auth.py:89", "guard_clause", True),
        ("NullPointer:order.py:45", "try_except", False),
        ("OffByOne:paginator.py:67", "boundary_check", True),
        ("NullPointer:user.py:200", "guard_clause", True),
        ("TypeError:parser.py:34", "isinstance_check", True),
        ("NullPointer:email.py:56", "try_except", False),
        ("OffByOne:counter.py:90", "boundary_check", True),
        ("NullPointer:report.py:156", "guard_clause", True),
        ("MemoryLeak:cache.py:12", "weakref", True),
        # 5 extra zum Trainieren
        ("NullPointer:config.py:78", "guard_clause", True),
        ("NullPointer:logger.py:34", "guard_clause", True),
        ("OffByOne:list.py:12", "boundary_check", True),
        ("NullPointer:db.py:200", "try_except", False),
        ("TypeError:serializer.py:56", "isinstance_check", True),
    ]
    
    for i, (bug_sig, pattern, success) in enumerate(bugs):
        decision = brain.think(bug_sig, [0.0]*384)
        if i < 3:
            print(f"\n🐛 Bug #{i+1}: {bug_sig} → {decision['action']}")
            print(f"   Q-Werte: {decision.get('q_values', {})}")
        brain.learn(bug_sig, pattern, success)
    
    print(f"\n... insgesamt {len(bugs)} Bugs trainiert")
    print(f"\n{'='*60}")
    print("📊 GEHIRN-STATUS:")
    for k, v in brain.stats().items():
        print(f"   {k}: {v}")
    
    # Zeige gelernte Q-Werte
    print(f"\n📋 GELERNTE Q-WERTE (Top 5):")
    sorted_q = sorted(brain.Q.items(), key=lambda x: x[1], reverse=True)[:5]
    for (bt, a), v in sorted_q:
        print(f"   ({bt}, {a}): {v:.3f}")
    
    print(f"\n✅ Gehirn D laeuft eigenstaendig.")
