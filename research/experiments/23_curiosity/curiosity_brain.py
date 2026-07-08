"""
GEHIRN W — Curiosity-Driven / Intrinsic Motivation Brain (Schmidhuber 1991)
Intrinsische Belohnung für NEUES: r_int = prediction_error.
Agent wird NEUGIERIG auf unerforschte Bug-Typen.
Mathematik: ICM — r_i = ||f(s') - f_pred(s,a)||²

Autor: Hermes + David | Coding Tentacle Gehirn Bibliothek
"""
import numpy as np, math
from collections import defaultdict

class CuriosityBrain:
    """Gehirn W — Wird belohnt für Exploration des Unbekannten."""
    def __init__(self, lr=0.1, curiosity_weight=0.5):
        self.lr=lr; self.curiosity_weight=curiosity_weight
        self.known_patterns=defaultdict(lambda: {'success':0,'total':0,'embedding':np.zeros(64)})
        self.explored=set()
        self.total_bugs=0; self.total_explored=0
    
    def _novelty(self, emb):
        e=np.array(emb)[:64] if len(emb)>64 else np.pad(emb,(0,max(0,64-len(emb))))
        if not self.known_patterns: return 10.0  # Alles ist neu!
        # Distanz zum nächsten bekannten Pattern
        min_dist=min(np.linalg.norm(e-v['embedding']) for v in self.known_patterns.values())
        return float(min_dist)
    
    def think(self,sig,emb):
        self.total_bugs+=1
        bt=sig.split(':')[0] if ':' in sig else sig
        novelty=self._novelty(emb)
        # Curiosity: Wenn Bug-Typ unbekannt → EXPLORE (belohnt Neugier)
        if novelty>2.0 or bt not in self.known_patterns or self.known_patterns[bt]['total']<2:
            self.total_explored+=1
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,'novelty':novelty,
                    'reasoning':f"Neugier! Neuheit={novelty:.1f}. Exploration intrinsisch belohnt."}
        # Bekannt: Pattern anwenden
        kp=self.known_patterns[bt]
        rate=kp['success']/max(1,kp['total'])
        conf=min(1.0,rate*kp['total']/(kp['total']+2))
        return {'action':'APPLY_PATTERN','pattern':f'curious_{bt}','confidence':conf,
                'novelty':novelty,
                'reasoning':f"Bekannt (Neuheit={novelty:.1f}). Rate={rate:.0%} conf={conf:.2f}"}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        kp=self.known_patterns[bt]
        kp['success']+=1 if success else 0
        kp['total']+=1
        if emb:
            e=np.array(emb)[:64] if len(emb)>64 else np.pad(emb,(0,max(0,64-len(emb))))
            kp['embedding']=kp['embedding']*0.9+e*0.1
    
    def stats(self):
        n=len(self.known_patterns)
        return {'brain_type':'Curiosity-Driven (ICM)','total_bugs':self.total_bugs,
                'explored':self.total_explored,'explored_ratio':f'{self.total_explored/max(1,self.total_bugs):.0%}',
                'known_types':n}
    def __repr__(self): return f"CuriosityBrain(types={len(self.known_patterns)})"

if __name__=="__main__":
    print("GEHIRN W — Curiosity"); b=CuriosityBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(15):
        bt=['NullPointer','OffByOne','TypeError'][i%3]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<12,emb)
        if i%4==0: print(f"  Bug{i+1}: {dec['action']:15s} novelty={dec.get('novelty',0):.1f}")
    print(b.stats()); print("✅ Gehirn W läuft.")
