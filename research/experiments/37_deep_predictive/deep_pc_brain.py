"""
GEHIRN AK — Deep Predictive Coding (6-Schichten, echte Weight-Updates)
Hierarchische Abstraktion: L0(Token)→L1(Pattern)→L2(Konzept)→L3(Meta)→L4(Strategic)→L5(Philosophical)
Jede Schicht sagt die darunter vorher. Weight-Updates via Prediction Error.

Autor: Hermes + David | Coding Tentacle 2026
Quelle: Friston (2005), PrediRep (2025)
"""
import numpy as np, math
from collections import defaultdict

class DeepPredictiveCodingBrain:
    """Gehirn AK — 6-Schicht Predictive Coding Hierarchie."""
    def __init__(self, dims=[384, 256, 128, 64, 32, 16], lr=0.05):
        self.dims=dims; self.lr=lr; self.L=len(dims)
        # Top-down Gewichte (von Schicht l → l+1 für Vorhersage)
        self.W=[np.random.randn(dims[l], dims[l+1])*0.05 for l in range(self.L-1)]
        self.states={}; self.patterns=defaultdict(lambda: {'success':0,'total':0})
        self.total_bugs=0
    
    def _predict(self, upper, l):
        # upper: (dim_l+1,), W[l]: (dim_l, dim_l+1) → pred: (dim_l,)
        return np.tanh(self.W[l] @ upper)
    
    def _infer(self, emb, bt, n_iter=8):
        if bt not in self.states:
            self.states[bt]=[np.zeros(d) for d in self.dims]
        s=self.states[bt]
        e=np.array(emb)
        s[0]=e[:self.dims[0]] if len(e)>=self.dims[0] else np.pad(e,(0,self.dims[0]-len(e)))
        
        for _ in range(n_iter):
            for l in range(self.L-1):
                pred=self._predict(s[l+1], l)
                err=s[l]-pred
                s[l]+=self.lr*err
            for l in range(self.L-2,-1,-1):
                pred=self._predict(s[l+1], l)
                err=s[l]-pred
                # W[l]: (dim_l, dim_l+1). Update: outer(error_l, state_{l+1})
                dw=self.lr*0.01*np.outer(err, s[l+1])
                if dw.shape==self.W[l].shape:
                    self.W[l]+=dw
        self.states[bt]=s
        return s
    
    def think(self,sig,emb):
        self.total_bugs+=1; bt=sig.split(':')[0] if ':' in sig else sig
        if self.patterns[bt]['total']<2:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                    'reasoning':f'Deep PC: {bt} braucht ≥2 Beispiele.'}
        s=self._infer(emb, bt)
        top_err=np.linalg.norm(s[-1])
        rate=self.patterns[bt]['success']/max(1,self.patterns[bt]['total'])
        conf=min(1.0,rate/(1+top_err))
        layer_info={l:f'{np.linalg.norm(s[l]):.1f}' for l in range(self.L)}
        return {'action':'APPLY_PATTERN' if conf>0.3 else 'EXPLORE',
                'pattern':f'pc_{bt}','confidence':conf,'top_error':float(top_err),
                'layers':layer_info,
                'reasoning':f'Deep PC: {bt} L0→L5 err={top_err:.2f} conf={conf:.2f}'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        self.patterns[bt]['total']+=1
        if success: self.patterns[bt]['success']+=1
        if emb: self._infer(emb, bt, n_iter=10)
    
    def stats(self):
        return {'brain_type':'Deep Predictive Coding (6-Layer)','total_bugs':self.total_bugs,
                'layers':self.L,'layer_dims':self.dims,'patterns':len(self.patterns)}
    def __repr__(self): return f"DeepPCHierarchy(layers={self.L})"

if __name__=="__main__":
    print("GEHIRN AK — Deep Predictive Coding (6-Layer)")
    b=DeepPredictiveCodingBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(25):
        bt=['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'][i%5]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<20,emb)
        if i%5==0: print(f"  Bug{i+1}: {dec['action']:15s} err={dec.get('top_error',0):.2f}")
    print(b.stats()); print("✅ Gehirn AK läuft.")
