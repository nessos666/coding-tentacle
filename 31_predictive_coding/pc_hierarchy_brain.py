"""
GEHIRN AE — Predictive Coding Hierarchy Brain (Rao & Ballard 1999, Friston)
Mehrschichtige Vorhersage-Hierarchie. Jede Schicht sagt die darunter vorher.
Prediction Errors fließen NACH OBEN. Predictions fließen NACH UNTEN.
Struktur: Embedding → L1 → L2 → L3 (zunehmende Abstraktion)

Mathematik:
  ε_l = x_l - pred_{l+1→l}              (prediction error)
  x_l ← x_l + α · ε_l                    (state update)
  W_{l+1→l} ← W + β · ε_l ⊗ x_{l+1}     (weight update)

Autor: Hermes + David | Coding Tentacle 2026
"""
import numpy as np, math
from collections import defaultdict

class PredictiveCodingHierarchyBrain:
    """Gehirn AE — Hierarchische Predictive Coding (3 Schichten)."""
    def __init__(self, dims=[384, 128, 64, 32], lr=0.05):
        self.dims=dims; self.lr=lr
        self.n_layers=len(dims)
        # Gewichte zwischen Schichten (top-down predictions)
        self.W=[np.random.randn(dims[l+1], dims[l])*0.05 for l in range(self.n_layers-1)]
        # Zustände pro Schicht (nach Bug-Typ)
        self.states={}  # {bug_type: [state_L0, state_L1, state_L2, state_L3]}
        self.patterns=defaultdict(lambda: {'success':0,'total':0})
        self.total_bugs=0
    
    def _predict(self, x_upper, l):
        """Sage Schicht l von Schicht l+1 vorher"""
        return np.tanh(self.W[l].T @ x_upper)  # (dim_l,)
    
    def _infer(self, emb, bt, n_iter=5):
        """Iterative Inferenz: Zustände laufen bis Konvergenz"""
        if bt not in self.states:
            self.states[bt]=[np.zeros(d) for d in self.dims]
        
        states=self.states[bt]
        states[0]=np.array(emb)[:self.dims[0]] if len(emb)>self.dims[0] else np.pad(emb,(0,max(0,self.dims[0]-len(emb))))
        
        for _ in range(n_iter):
            # Bottom-up: Prediction Errors berechnen
            for l in range(self.n_layers-1):
                pred=self._predict(states[l+1], l)
                error=states[l]-pred
                states[l]+=self.lr*error  # State Update
            # Top-down: Predictions aktualisieren
            for l in range(self.n_layers-2,-1,-1):
                pred=self._predict(states[l+1], l)
                error=states[l]-pred
                # Weight Update (flatten für outer product)
                self.W[l]+=self.lr*0.01*np.outer(error.flatten()[:self.dims[l]], 
                                                  states[l+1].flatten()[:self.dims[l+1]]).reshape(self.W[l].shape)
        
        self.states[bt]=states
        return states
    
    def think(self,sig,emb):
        self.total_bugs+=1
        bt=sig.split(':')[0] if ':' in sig else sig
        
        if self.patterns[bt]['total']<2:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                    'reasoning':f'PC-Hierarchie: {bt} zu wenige Beispiele.'}
        
        states=self._infer(emb, bt)
        # Prediction Error auf oberster Schicht = Überraschung
        top_error=np.linalg.norm(states[-1])
        rate=self.patterns[bt]['success']/max(1,self.patterns[bt]['total'])
        conf=min(1.0, rate/(1+top_error))
        
        return {'action':'APPLY_PATTERN' if conf>0.3 else 'EXPLORE',
                'pattern':f'pc_{bt}','confidence':conf,
                'top_error':float(top_error),
                'reasoning':f'PC-Hierarchie: {bt} top_err={top_error:.2f} conf={conf:.2f}'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        self.patterns[bt]['total']+=1
        if success: self.patterns[bt]['success']+=1
        if emb: self._infer(emb, bt, n_iter=8)
    
    def stats(self):
        return {'brain_type':'Predictive Coding Hierarchy (3-Layer)',
                'total_bugs':self.total_bugs,'layers':self.n_layers,
                'patterns':len(self.patterns)}
    def __repr__(self): return f"PCHierarchy(layers={self.n_layers}, patterns={len(self.patterns)})"

if __name__=="__main__":
    print("GEHIRN AE — Predictive Coding Hierarchy"); b=PredictiveCodingHierarchyBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(20):
        bt=['NullPointer','OffByOne','TypeError'][i%3]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<16,emb)
        if i%5==0: print(f"  Bug{i+1}: {dec['action']:15s} err={dec.get('top_error',0):.2f}")
    print(b.stats()); print("✅ Gehirn AE läuft.")
