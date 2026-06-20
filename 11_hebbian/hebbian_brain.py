"""
GEHIRN K — Hebbian Learning Brain (Hebb 1949)
"Neurons that fire together, wire together."
Associative memory via co-occurrence weight strengthening.
Mathematik: Δw_ij = η · x_i · x_j   (Hebb'sche Regel)
Autor: Hermes + David | Coding Tentacle Gehirn Bibliothek
"""
import time, math, numpy as np
from collections import defaultdict

class HebbianBrain:
    """Gehirn K — Assoziatives Lernen durch Ko-Aktivierung."""
    def __init__(self, lr=0.1, decay=0.001, threshold=0.3):
        self.lr=lr; self.decay=decay; self.threshold=threshold
        self.weights=defaultdict(float)  # {(bug_type,pattern): strength}
        self.total_bugs=0
    
    def think(self, sig, emb):
        self.total_bugs+=1
        bt=sig.split(':')[0] if ':' in sig else sig
        candidates=[]
        for (bt2,pat),w in self.weights.items():
            if bt in bt2 or bt2 in bt:
                candidates.append((pat,w))
        if not candidates:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,'reasoning':f'Keine Hebb-Verbindung für {bt}'}
        best=max(candidates,key=lambda x:x[1])
        conf=min(1.0,best[1])
        return {'action':'APPLY_PATTERN' if conf>self.threshold else 'EXPLORE',
                'pattern':best[0],'confidence':conf,
                'reasoning':f"Hebb: '{best[0]}' Stärke={best[1]:.2f}"}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        key=(bt,pat)
        # Hebb: Δw = η·x_i·x_j - decay
        self.weights[key]+=self.lr*(1.0 if success else 0.2)
        # Decay alle Gewichte
        for k in list(self.weights.keys()):
            self.weights[k]-=self.decay
            if self.weights[k]<0.01: del self.weights[k]
    
    def stats(self):
        n=len(self.weights)
        top=sorted(self.weights.items(),key=lambda x:-x[1])[:3]
        return {'brain_type':'Hebbian Learning','total_bugs':self.total_bugs,
                'connections':n,'top':[f'{k[0]}→{k[1]}:{v:.2f}' for k,v in top]}
    def __repr__(self): return f"HebbianBrain(connections={len(self.weights)})"

if __name__=="__main__":
    print("GEHIRN K — Hebbian Learning"); b=HebbianBrain()
    bugs=[("NullPointer:pay.py:1","guard_clause",True),("NullPointer:auth.py:2","guard_clause",True),
          ("OffByOne:page.py:1","boundary_check",True),("NullPointer:order.py:3","guard_clause",True),
          ("TypeError:parse.py:1","type_convert",True),("NullPointer:user.py:4","guard_clause",True),
          ("MemoryLeak:cache.py:1","weakref",True),("NullPointer:email.py:5","try_except",False),
          ("OffByOne:list.py:2","boundary_check",True),("NullPointer:report.py:6","guard_clause",True)]
    for i,(sig,pat,ok) in enumerate(bugs):
        dec=b.think(sig,[0]*384)
        print(f"  Bug{i+1}: {dec['action']:15s} conf={dec['confidence']:.1f}")
        b.learn(sig,pat,ok)
    print(b.stats()); print("✅ Gehirn K läuft.")
