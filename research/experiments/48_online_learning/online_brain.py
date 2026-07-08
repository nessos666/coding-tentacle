"""
GEHIRN AU — Online Learning Brain
LERNT AUS JEDEM EINZELNEN BUG — kein Batch nötig.
Inkrementelles Update nach JEDEM Bug. Kein separates Training/Test.
Mathematik: θ_{t+1} = θ_t + η·∇L(θ_t; bug_t) — SGD in Echtzeit.

Autor: Hermes + David | Coding Tentacle 2026
"""
import numpy as np, math
from collections import defaultdict

class OnlineLearningBrain:
    """Gehirn AU — Lernt inkrementell aus jedem einzelnen Bug."""
    def __init__(self, lr=0.1, decay=0.001):
        self.lr=lr; self.decay=decay
        self.weights=defaultdict(lambda: np.zeros(64))  # {bug_type: weight_vector}
        self.counts=defaultdict(int)
        self.success_ema=defaultdict(float)  # Exponential Moving Average
        self.total_bugs=0
    
    def _encode(self, emb):
        e=np.array(emb)[:64] if len(emb)>64 else np.pad(emb,(0,max(0,64-len(emb))))
        return e
    
    def think(self,sig,emb):
        self.total_bugs+=1; bt=sig.split(':')[0] if ':' in sig else sig
        e=self._encode(emb)
        
        if self.counts[bt]==0:
            # ERSTER Bug dieses Typs — direkt lernen, dann anwenden
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                    'online_step':0,'reasoning':f'Online: Erster {bt}. Lerne direkt.'}
        
        # Online-Vorhersage: dot(weights, embedding)
        w=self.weights[bt]
        sim=np.dot(w,e)/(np.linalg.norm(w)*np.linalg.norm(e)+1e-8)
        rate=self.success_ema[bt]
        conf=min(1.0, max(0,sim)*rate)
        
        return {'action':'APPLY_PATTERN' if conf>0.3 else 'EXPLORE',
                'pattern':f'online_{bt}','confidence':conf,
                'online_step':self.counts[bt],
                'reasoning':f'Online: {bt} step={self.counts[bt]} sim={sim:.2f} ema={rate:.2f}'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        self.counts[bt]+=1
        if emb:
            e=self._encode(emb)
            # SGD Update pro Bug: w += lr * (target - pred) * x
            target=1.0 if success else -0.5
            pred=np.dot(self.weights[bt],e)/(np.linalg.norm(e)+1e-8)
            error=target-pred
            self.weights[bt]+=self.lr*error*e
            # Decay
            self.weights[bt]*=(1-self.decay)
            # EMA der Erfolgsrate
            alpha=0.1
            self.success_ema[bt]=self.success_ema[bt]*(1-alpha)+(1 if success else 0)*alpha
    
    def stats(self):
        return {'brain_type':'Online Learning (SGD per Bug)','total_bugs':self.total_bugs,
                'types':len(self.counts),
                'avg_steps':f'{np.mean(list(self.counts.values())):.0f}' if self.counts else '0',
                'success_ema':{bt:f'{v:.2f}' for bt,v in self.success_ema.items()}}
    def __repr__(self): return f"OnlineBrain(types={len(self.counts)})"

if __name__=="__main__":
    print("GEHIRN AU — Online Learning"); b=OnlineLearningBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(20):
        bt=['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'][i%5]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<16,emb)
        if i%5==0: print(f"  Bug{i+1}: {dec['action']:15s} step={dec.get('online_step',0)} ema={b.success_ema.get(bt,0):.2f}")
    print(b.stats()); print("✅ Gehirn AU läuft.")
