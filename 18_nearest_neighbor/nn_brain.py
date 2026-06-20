"""
GEHIRN R — Nearest Neighbor / Case-Based Reasoning Brain
Keine Abstraktion. Kein Modell. Nur: Finde die k ähnlichsten alten Bugs.
Reines instance-based learning. k-NN auf Embeddings.
Mathematik: y = mode(y_i für i in k-Nächste-Nachbarn(x))

Autor: Hermes + David | Coding Tentacle Gehirn Bibliothek
"""
import numpy as np
from collections import defaultdict, Counter

class NearestNeighborBrain:
    """Gehirn R — k-NN Case-Based Reasoning."""
    def __init__(self, k=5, threshold=0.5):
        self.k=k; self.threshold=threshold
        self.cases=[]  # [(embedding, bug_type, pattern, success)]
        self.total_bugs=0
    
    def _cosine(self,a,b):
        a,b=np.array(a),np.array(b)
        if len(a)==0 or len(b)==0: return 0.0
        norm=np.linalg.norm(a)*np.linalg.norm(b)
        return np.dot(a,b)/norm if norm>0 else 0.0
    
    def think(self,sig,emb):
        self.total_bugs+=1
        if not self.cases:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,'reasoning':'Keine Cases. Erstes Beispiel.'}
        # k nächste Nachbarn
        sims=[(self._cosine(emb,c[0]),c) for c in self.cases]
        sims.sort(key=lambda x:-x[0])
        top_k=sims[:self.k]
        avg_sim=np.mean([s for s,_ in top_k])
        # Mehrheitsvotum der erfolgreichen Patterns
        votes=Counter()
        for sim,(_,_,pat,succ) in top_k:
            if succ: votes[pat]+=sim
        if not votes:
            return {'action':'EXPLORE','pattern':None,'confidence':avg_sim,
                    'reasoning':f'{self.k}-NN: Kein erfolgreiches Pattern (sim={avg_sim:.2f})'}
        best=votes.most_common(1)[0]
        conf=best[1]/sum(votes.values()) if votes else 0
        return {'action':'APPLY_PATTERN' if avg_sim>self.threshold else 'EXPLORE',
                'pattern':best[0],'confidence':conf,'nn_similarity':avg_sim,
                'reasoning':f'{self.k}-NN: {best[0]} ({len(top_k)} Nachbarn, sim={avg_sim:.2f})'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        self.cases.append((np.array(emb) if emb else np.zeros(384),bt,pat,success))
        if len(self.cases)>500: self.cases=self.cases[-500:]
    
    def stats(self):
        n=len(self.cases)
        succ=sum(1 for _,_,_,s in self.cases if s)/max(1,n)
        return {'brain_type':'k-NN Case-Based Reasoning','total_bugs':self.total_bugs,
                'cases':n,'success_rate':f'{succ:.0%}'}
    def __repr__(self): return f"NNBrain(cases={len(self.cases)})"

if __name__=="__main__":
    print("GEHIRN R — k-NN Case-Based"); b=NearestNeighborBrain(k=5)
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(10):
        bt=['NullPointer','OffByOne','TypeError'][i%3]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:file{i}.py:{i}",emb)
        print(f"  Bug{i+1}: {dec['action']:15s} sim={dec.get('nn_similarity',0):.2f} | {dec['reasoning'][:50]}")
        b.learn(f"{bt}:file{i}.py:{i}",f"fix_{bt}",i<8,emb)
    print(b.stats()); print("✅ Gehirn R läuft.")
