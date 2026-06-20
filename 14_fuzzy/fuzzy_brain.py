"""
GEHIRN N — Fuzzy Logic Brain (Zadeh 1965)
Bug-Typen sind NICHT binär. Ein Bug kann 0.7 NullPointer + 0.3 IndexError sein.
Mathematik: μ_A(x) ∈ [0,1] — Zugehörigkeitsgrad. Fuzzy-Regeln.
Autor: Hermes + David | Coding Tentacle Gehirn Bibliothek
"""
import math, numpy as np
from collections import defaultdict

def fuzzy_and(a,b): return min(a,b)
def fuzzy_or(a,b): return max(a,b)
def fuzzy_not(a): return 1.0-a

class FuzzyBrain:
    """Gehirn N — Unscharfe Logik. Kein Bug ist 100% ein Typ."""
    def __init__(self):
        self.rules=[]  # [(condition_pattern, action_pattern, weight)]
        self.memberships=defaultdict(dict)  # {bug_type: {keyword: degree}}
        self.total_bugs=0
    
    def _membership(self, bug_sig, category):
        """μ_category(bug) — wie sehr gehört dieser Bug zur Kategorie?"""
        sig_lower=bug_sig.lower()
        if category.lower() in sig_lower: return 0.9
        # Fuzzy-Matching über Keywords
        keywords={'nullpointer':['null','none','npe'],
                  'indexerror':['index','range','offby','boundary'],
                  'typeerror':['type','convert','cast','str','int'],
                  'memoryleak':['memory','leak','cache','buffer'],
                  'racecondition':['race','thread','concurrent','lock']}
        if category.lower() in keywords:
            scores=[0.5 if kw in sig_lower else 0.0 for kw in keywords[category.lower()]]
            return max(scores) if scores else 0.1
        return 0.1
    
    def think(self,sig,emb):
        self.total_bugs+=1
        # Fuzzy-Inferenz: Für jede Regel → Feuerungsgrad = min(Mitgliedschaften)
        fire_strengths=[]
        for cond_pat, action_pat, weight in self.rules:
            fire=fuzzy_and(self._membership(sig,cond_pat),weight)
            if fire>0.2:
                fire_strengths.append((action_pat,fire))
        if not fire_strengths:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                    'reasoning':'Keine Fuzzy-Regel feuert > 0.2.'}
        best=max(fire_strengths,key=lambda x:x[1])
        return {'action':'APPLY_PATTERN' if best[1]>0.3 else 'EXPLORE','pattern':best[0],
                'confidence':best[1],'fuzzy_fire':best[1],
                'reasoning':f"Fuzzy: {best[0]} feuert mit μ={best[1]:.2f}"}
    
    def learn(self,sig,pat,success,emb=None):
        # Regel lernen: IF Bug-Typ THEN Pattern
        bt=sig.split(':')[0] if ':' in sig else sig
        w=0.8 if success else 0.3
        # Regel finden/updaten
        for i,(cp,ap,w2) in enumerate(self.rules):
            if cp==bt and ap==pat:
                self.rules[i]=(cp,ap,fuzzy_or(w2,w))
                break
        else:
            self.rules.append((bt,pat,w))
    
    def stats(self):
        n=len(self.rules)
        top=sorted(self.rules,key=lambda x:-x[2])[:3]
        return {'brain_type':'Fuzzy Logic (Zadeh)','total_bugs':self.total_bugs,
                'rules':n,'top_rules':[f'IF {c} THEN {a} (μ={w:.2f})' for c,a,w in top]}
    def __repr__(self): return f"FuzzyBrain(rules={len(self.rules)})"

if __name__=="__main__":
    print("GEHIRN N — Fuzzy Logic"); b=FuzzyBrain()
    bugs=[("NullPointer:payment.py:null-check","guard_clause",True),
          ("IndexError:paginator.py:range-out","boundary_check",True),
          ("NullPointer:auth.py:session-null","guard_clause",True),
          ("TypeError:parser.py:int-str-concat","type_convert",True),
          ("MemoryLeak:cache.py:lru-buffer","weakref",True)]
    for i,(sig,pat,ok) in enumerate(bugs):
        dec=b.think(sig,[0]*384)
        print(f"  Bug{i+1}: {dec['action']:15s} μ={dec.get('fuzzy_fire',0):.2f} | {dec['reasoning'][:50]}")
        b.learn(sig,pat,ok)
    print(b.stats()); print("✅ Gehirn N läuft.")
