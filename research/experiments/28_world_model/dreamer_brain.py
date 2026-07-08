"""
GEHIRN AB v2 — World Model / Dreamer Brain (Fixed)
FIX: Direkter Similarity-basierter Traum-Mechanismus.
Statt Transition-Modell → träume über nächste-Nachbarn in Embedding-Space.
"""
import numpy as np, math
from collections import defaultdict

class WorldModelBrain:
    """Gehirn AB v2 — Dreamer: Similarity-basierte Vorhersage."""
    def __init__(self, lr=0.1):
        self.lr=lr
        self.dreams=defaultdict(list)  # {bug_type: [(embedding, success)]}
        self.patterns=defaultdict(lambda: {'success':0,'total':0})
        self.total_bugs=0
    
    def _dream_best(self, emb, bt):
        """Träume den besten Fix: finde ähnlichste erfolgreiche Episode"""
        e=np.array(emb)
        if bt not in self.dreams or not self.dreams[bt]:
            return None, 0.0
        
        successes=[(d_emb,sim) for d_emb,succ in self.dreams[bt] 
                   if succ and (sim:=np.dot(e,d_emb)/(np.linalg.norm(e)*np.linalg.norm(d_emb)+1e-8))>0.3]
        if not successes: return None, 0.0
        best=max(successes,key=lambda x:x[1])
        return best[0], best[1]
    
    def think(self,sig,emb):
        self.total_bugs+=1
        bt=sig.split(':')[0] if ':' in sig else sig
        e=np.array(emb)
        
        if self.patterns[bt]['total']<2:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                    'reasoning':f'Dreamer: {bt} zu wenige Traum-Daten ({self.patterns[bt]["total"]}/2)'}
        
        _, dream_sim = self._dream_best(emb, bt)
        rate=self.patterns[bt]['success']/max(1,self.patterns[bt]['total'])
        conf=min(1.0,rate*dream_sim)
        
        return {'action':'APPLY_PATTERN' if conf>0.3 else 'EXPLORE',
                'pattern':f'dream_{bt}','confidence':conf,
                'dream_sim':dream_sim,
                'reasoning':f'Dreamer: {bt} geträumt sim={dream_sim:.2f} conf={conf:.2f}'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        self.patterns[bt]['total']+=1
        if success: self.patterns[bt]['success']+=1
        if emb is not None:
            e=np.array(emb)
            self.dreams[bt].append((e, success))
            if len(self.dreams[bt])>30: self.dreams[bt]=self.dreams[bt][-30:]
    
    def stats(self):
        return {'brain_type':'Dreamer v2','total_bugs':self.total_bugs,
                'dream_banks':{bt:len(v) for bt,v in self.dreams.items()},
                'patterns':len(self.patterns)}
    def __repr__(self): return f"Dreamer(types={len(self.dreams)})"

if __name__=="__main__":
    print("GEHIRN AB v2 — Dreamer"); b=WorldModelBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(15):
        bt=['NullPointer','OffByOne','TypeError'][i%3]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<12,emb)
        if i%4==0: print(f"  Bug{i+1}: {dec['action']:15s} sim={dec.get('dream_sim',0):.2f}")
    print(b.stats()); print("✅ Gehirn AB v2 läuft.")
