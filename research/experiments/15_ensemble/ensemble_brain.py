"""
GEHIRN O — Ensemble/Meta Brain
Weighted Voting über ALLE anderen Gehirne.
Jedes Gehirn stimmt ab → Gewicht nach historischer Erfolgsrate.
Mathematik: action = argmax_a Σ w_i · vote_i(a)

Autor: Hermes + David | Coding Tentacle Gehirn Bibliothek
"""
import numpy as np
from collections import defaultdict

class EnsembleBrain:
    """Gehirn O — Meta-Gehirn. Kombiniert alle Sub-Gehirne via gewichteter Abstimmung."""
    def __init__(self, sub_brains=None):
        self.sub_brains=sub_brains or []
        self.weights={}  # {brain_name: success_rate}
        self.vote_counts=defaultdict(lambda: defaultdict(int))  # {brain: {action: count}}
        self.total_bugs=0
    
    def add_brain(self, name, brain):
        self.sub_brains.append((name,brain))
        self.weights[name]=0.5  # Startgewicht
    
    def think(self,sig,emb):
        self.total_bugs+=1
        votes=defaultdict(float)
        reasonings=[]
        for name,brain in self.sub_brains:
            try:
                dec=brain.think(sig,emb)
                action=dec.get('action','EXPLORE')
                pat=dec.get('pattern','')
                w=self.weights.get(name,0.5)
                if action=='APPLY_PATTERN' and pat:
                    votes[pat]+=w
                elif action=='EXPLORE':
                    votes['EXPLORE']+=w*0.3
                reasonings.append(f"{name}:{action}")
            except:
                reasonings.append(f"{name}:error")
        if not votes:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,'reasoning':'Keine Sub-Gehirne.'}
        best=max(votes,key=votes.get)
        total_w=sum(self.weights.values())+0.001
        conf=votes[best]/total_w
        return {'action':'APPLY_PATTERN' if best!='EXPLORE' else 'EXPLORE',
                'pattern':best if best!='EXPLORE' else None,'confidence':conf,
                'votes':dict(votes),'ensemble_size':len(self.sub_brains),
                'reasoning':f"Ensemble: {best} ({conf:.0%}) | "+", ".join(reasonings[:3])}
    
    def learn(self,sig,pat,success,emb=None):
        # Gewichte updaten: Belohne Gehirne, die richtig lagen
        for name,brain in self.sub_brains:
            try:
                dec=brain.think(sig,emb)
                if dec.get('pattern')==pat:
                    delta=0.05 if success else -0.03
                    self.weights[name]=max(0.05,min(1.0,self.weights.get(name,0.5)+delta))
                brain.learn(sig,pat,success,emb)
            except:
                try: brain.learn(sig,pat,success)
                except: pass
    
    def stats(self):
        n=len(self.sub_brains)
        best=max(self.weights.items(),key=lambda x:x[1]) if self.weights else ('none',0)
        return {'brain_type':'Ensemble/Meta','total_bugs':self.total_bugs,
                'sub_brains':n,'weights':{k:f'{v:.2f}' for k,v in sorted(self.weights.items(),key=lambda x:-x[1])[:5]},
                'best_brain':best[0]}
    def __repr__(self): return f"EnsembleBrain({len(self.sub_brains)} sub-brains)"

if __name__=="__main__":
    print("GEHIRN O — Ensemble/Meta")
    import sys; sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/01_bayesian')
    sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/02_shannon_entropie')
    sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/11_hebbian')
    from bayesian_brain import BayesianBrain
    from shannon_brain import ShannonBrain
    from hebbian_brain import HebbianBrain
    
    b=EnsembleBrain()
    b.add_brain('Bayesian',BayesianBrain())
    b.add_brain('Shannon',ShannonBrain())
    b.add_brain('Hebbian',HebbianBrain())
    
    bugs=[("NullPointer:pay.py:1","guard_clause",True),("NullPointer:auth.py:2","guard_clause",True),
          ("OffByOne:page.py:1","boundary_check",True),("NullPointer:order.py:3","guard_clause",True),
          ("TypeError:parse.py:1","type_convert",True)]
    for i,(sig,pat,ok) in enumerate(bugs):
        dec=b.think(sig,[0]*384)
        print(f"  Bug{i+1}: {dec['action']:15s} {dec['reasoning'][:60]}")
        b.learn(sig,pat,ok)
    print(b.stats()); print("✅ Gehirn O läuft.")
