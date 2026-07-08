"""
GEHIRN P — Game Theory Brain (von Neumann/Nash)
Bug-Fixing als Zwei-Spieler-Nullsummenspiel: Agent vs Bug.
Minimax: Wähle Fix, der den SCHLIMMSTEN Fall minimiert.
Nash-Equilibrium: Kein Spieler kann sich allein verbessern.

Mathematik:
  Minimax:  a* = argmax_a min_b payoff(a,b)
  Nash:     (a*,b*): ∀a,b: U1(a*,b*) ≥ U1(a,b*) ∧ U2(a*,b*) ≥ U2(a*,b)

Autor: Hermes + David | Coding Tentacle Gehirn Bibliothek
"""
import numpy as np
from collections import defaultdict

class GameTheoryBrain:
    def __init__(self):
        self.payoffs=defaultdict(lambda: defaultdict(float))  # {(bug_type,fix): {outcome: payoff}}
        self.total_bugs=0
    
    def think(self,sig,emb):
        self.total_bugs+=1
        bt=sig.split(':')[0] if ':' in sig else sig
        # Alle Fixes für diesen Bug-Typ
        fixes=list(self.payoffs[bt].keys())
        if not fixes:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                    'reasoning':f'Keine Strategien für {bt}. Exploration.'}
        # Minimax: Wähle Fix mit höchstem SCHLECHTESTEM Outcome
        best_fix,max_min=None,-999
        for fix in fixes:
            outcomes=self.payoffs[bt][fix]
            if not outcomes: continue
            # Worst-case dieses Fixes
            worst=min(outcomes.values()) if outcomes else 0
            if worst>max_min:
                max_min=worst; best_fix=fix
        if best_fix:
            payoff=self.payoffs[bt][best_fix].get('success',0.5)
            return {'action':'APPLY_PATTERN','pattern':best_fix,
                    'confidence':payoff,'minimax_value':max_min,
                    'reasoning':f"Minimax: {best_fix} worst={max_min:.1f} (Nash-safe)"}
        return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                'reasoning':f'Alle Strategien dominiert für {bt}.'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        outcome='success' if success else 'failure'
        # Sicherstellen dass payoffs[bt][pat] ein dict ist
        if not isinstance(self.payoffs[bt].get(pat), dict):
            self.payoffs[bt][pat] = defaultdict(float)
        self.payoffs[bt][pat][outcome]=self.payoffs[bt][pat].get(outcome,0)+1
    
    def stats(self):
        n_fixes=sum(len(f) for f in self.payoffs.values())
        # Nash: Gibt es dominante Strategien?
        dominant=0
        for bt,fixes in self.payoffs.items():
            for fix,outcomes in fixes.items():
                s=outcomes.get('success',0); f=outcomes.get('failure',0)
                if s+f>2 and s/(s+f)>0.7: dominant+=1
        return {'brain_type':'Game Theory (Minimax/Nash)','total_bugs':self.total_bugs,
                'strategies':n_fixes,'dominant_strategies':dominant}
    def __repr__(self): return f"GameTheoryBrain(strategies={sum(len(f) for f in self.payoffs.values())})"

if __name__=="__main__":
    print("GEHIRN P — Game Theory (Minimax)"); b=GameTheoryBrain()
    for i in range(10):
        bt=['NullPointer','OffByOne','TypeError'][i%3]
        pat={'NullPointer':'guard_clause','OffByOne':'boundary_check','TypeError':'type_convert'}[bt]
        dec=b.think(f"{bt}:file{i}.py:{i}",[0]*384)
        print(f"  Bug{i+1}: {dec['action']:15s} | {dec['reasoning'][:50]}")
        b.learn(f"{bt}:file{i}.py:{i}",pat,i<7 or i%3!=0)
    print(b.stats()); print("✅ Gehirn P läuft.")
