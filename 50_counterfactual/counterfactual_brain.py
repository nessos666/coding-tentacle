"""
GEHIRN AW — Counterfactual Reasoning Brain
"Was WÄRE wenn ich X statt Y gemacht hätte?"
Geht über Kausalität hinaus: Stellt HYPOTHETISCHE Fragen.

Mathematik: CF(Y|X=x, X=x') = E[Y|do(X=x')] - E[Y|do(X=x)]
           = E[Y|X=x', Pa(X)] - E[Y|X=x, Pa(X)]  (via parents)

Autor: Hermes + David | Coding Tentacle 2026
"""
import numpy as np, math
from collections import defaultdict

class CounterfactualBrain:
    """Gehirn AW — Stellt 'Was wäre wenn' Fragen über Bug-Fixes."""
    def __init__(self):
        self.history=[]  # [(bug_type, pattern, success, embedding)]
        self.patterns=defaultdict(lambda: {'success':0,'total':0})
        self.counterfactuals=[]  # gespeicherte hypothetische Szenarien
        self.total_bugs=0
    
    def _find_similar_bugs(self, emb, bt, n=5):
        """Finde n ähnlichste Bugs (für Pa(X)-Matching)"""
        e=np.array(emb)
        similarities=[]
        for h in self.history:
            if h[0]==bt: continue  # gleicher Bug-Typ zählt nicht
            he=np.array(h[3])
            sim=np.dot(e,he)/(np.linalg.norm(e)*np.linalg.norm(he)+1e-8)
            similarities.append((sim, h))
        similarities.sort(key=lambda x:-x[0])
        return [h for _,h in similarities[:n]]
    
    def _counterfactual_estimate(self, bt, chosen_pat, alt_pat, emb):
        """Schätze Erfolgswk. für alternative Pattern"""
        # Finde ähnliche Bugs wo das alternative Pattern verwendet wurde
        similar=self._find_similar_bugs(emb, bt)
        alt_successes=[h for h in similar if h[1]==alt_pat and h[2]]
        alt_total=[h for h in similar if h[1]==alt_pat]
        if alt_total:
            return len(alt_successes)/len(alt_total)
        # Fallback: globale Rate des alternativen Patterns
        if alt_pat in self.patterns and self.patterns[alt_pat]['total']>0:
            return self.patterns[alt_pat]['success']/self.patterns[alt_pat]['total']
        return 0.0
    
    def think(self,sig,emb):
        self.total_bugs+=1; bt=sig.split(':')[0] if ':' in sig else sig
        
        if self.patterns[bt]['total']<1:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                    'reasoning':f'Counterfactual: Keine Daten für {bt}.'}
        
        # Bestes Pattern nach Erfolgsrate
        direct_rate=self.patterns[bt]['success']/max(1,self.patterns[bt]['total'])
        
        # Counterfactual: Was WÄRE mit dem zweitbesten Pattern?
        all_pats=[(p,self.patterns[p]['success']/max(1,self.patterns[p]['total']),self.patterns[p]['total']) 
                  for p in self.patterns]
        all_pats.sort(key=lambda x:-x[1])
        
        alternatives=[p for p in all_pats if p[0]!=bt and p[2]>=2]
        
        if alternatives:
            alt_pat,alt_rate,_=alternatives[0]
            cf_rate=self._counterfactual_estimate(bt, f'fix_{bt}', alt_pat, emb)
            
            # Speichere Counterfactual
            self.counterfactuals.append({
                'bug':bt,'chosen':f'fix_{bt}','alternative':alt_pat,
                'chosen_rate':direct_rate,'alt_rate':cf_rate,
                'benefit':direct_rate-cf_rate
            })
            
            conf=min(1.0, direct_rate)
            return {'action':'APPLY_PATTERN' if conf>0.2 else 'EXPLORE',
                    'pattern':f'cf_{bt}','confidence':conf,
                    'counterfactual':f'Alt:{alt_pat} would be {cf_rate:.0%}',
                    'benefit':direct_rate-cf_rate,
                    'reasoning':f'CF: {bt} direct={direct_rate:.0%} vs alt={alt_pat}={cf_rate:.0%} '
                               f'(benefit={direct_rate-cf_rate:+.0%})'}
        
        conf=min(1.0, direct_rate)
        return {'action':'APPLY_PATTERN' if conf>0.2 else 'EXPLORE',
                'pattern':f'cf_{bt}','confidence':conf,
                'reasoning':f'CF: {bt} direct={direct_rate:.0%} (keine Alternative)'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        self.history.append((bt, pat, success, emb if emb else np.zeros(64)))
        if len(self.history)>200: self.history=self.history[-200:]
        self.patterns[pat]['total']+=1
        if success: self.patterns[pat]['success']+=1
    
    def stats(self):
        return {'brain_type':'Counterfactual Reasoning','total_bugs':self.total_bugs,
                'cf_analyzed':len(self.counterfactuals),
                'best_benefit':(max(self.counterfactuals,key=lambda c:c['benefit'])['benefit'] if self.counterfactuals else 0)}
    def __repr__(self): return f"CounterfactualBrain(cfs={len(self.counterfactuals)})"

if __name__=="__main__":
    print("GEHIRN AW — Counterfactual Reasoning"); b=CounterfactualBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(25):
        bt=['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'][i%5]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<20,emb)
        if i%6==0: print(f"  Bug{i+1}: {dec['action']:15s} cf={dec.get('counterfactual','?')}")
    print(b.stats()); print("✅ Gehirn AW läuft.")
