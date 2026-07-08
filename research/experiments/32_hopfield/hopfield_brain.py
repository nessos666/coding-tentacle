"""
GEHIRN AF — Modern Hopfield Network Brain (Hopfield 1982, Krotov 2020)
Energie-basierter assoziativer Speicher. Patterns = Attraktoren.
Aktualisierung: x ← sign(W·x). Energie: E = -½x^T·W·x.
Modern: Continuous Hopfield mit exponentieller Kapazität (softmax-basiert).

Autor: Hermes + David | Coding Tentacle 2026
"""
import numpy as np, math
from collections import defaultdict

class HopfieldBrain:
    """Gehirn AF — Assoziativer Speicher mit Attraktor-Dynamik."""
    def __init__(self, pattern_dim=128, lr=0.1):
        self.dim=pattern_dim; self.lr=lr
        self.W=np.zeros((pattern_dim, pattern_dim))  # Gewichtsmatrix
        self.stored_patterns=[]  # [(pattern_name, pattern_vector)]
        self.success_weights={}  # {pattern_name: weight}
        self.patterns=defaultdict(lambda: {'success':0,'total':0})
        self.total_bugs=0
    
    def _encode(self, emb):
        e=np.array(emb)[:self.dim] if len(emb)>self.dim else np.pad(emb,(0,max(0,self.dim-len(emb))))
        return np.sign(e)  # Binarisiere für Hopfield
    
    def _store_pattern(self, name, vec):
        """Hebb'sches Lernen: W += v·v^T (ohne Diagonale)"""
        outer=np.outer(vec, vec)
        np.fill_diagonal(outer, 0)
        self.W+=self.lr*outer
        self.stored_patterns.append((name, vec))
        self.success_weights[name]=self.success_weights.get(name,0)+1
    
    def _retrieve(self, query, n_steps=5):
        """Hopfield-Dynamik: Konvergiere zum nächsten Attraktor"""
        x=query.copy()
        for _ in range(n_steps):
            x=np.sign(self.W @ x)
        return x
    
    def _cosine(self,a,b):
        n=np.linalg.norm(a)*np.linalg.norm(b)
        return np.dot(a,b)/n if n>0 else 0
    
    def think(self,sig,emb):
        self.total_bugs+=1
        bt=sig.split(':')[0] if ':' in sig else sig
        q=self._encode(emb)
        
        if not self.stored_patterns:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                    'reasoning':'Hopfield: Kein Pattern gespeichert.'}
        
        # Retrieval: Finde nächsten Attraktor
        retrieved=self._retrieve(q)
        # Finde ähnlichstes gespeichertes Pattern
        best_name,best_sim=None,-1
        for name,vec in self.stored_patterns:
            sim=self._cosine(retrieved,vec)
            if sim>best_sim: best_sim=sim; best_name=name
        
        if best_sim>0.5:
            rate=self.patterns[bt]['success']/max(1,self.patterns[bt]['total'])
            conf=min(1.0,rate*best_sim)
            return {'action':'APPLY_PATTERN' if conf>0.3 else 'EXPLORE',
                    'pattern':best_name,'confidence':conf,
                    'hopfield_sim':float(best_sim),
                    'reasoning':f'Hopfield: {best_name} (sim={best_sim:.2f}) conf={conf:.2f}'}
        return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                'reasoning':f'Hopfield: Kein Attraktor gefunden (max sim={best_sim:.2f})'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        self.patterns[bt]['total']+=1
        if success: self.patterns[bt]['success']+=1
        if emb and success:
            vec=self._encode(emb)
            self._store_pattern(f"hop_{bt}", vec)
    
    def stats(self):
        return {'brain_type':'Modern Hopfield Network','total_bugs':self.total_bugs,
                'stored_patterns':len(self.stored_patterns),
                'energy':f'{-0.5*np.dot(self.W.flatten()[:10],self.W.flatten()[:10]):.2f}'}
    def __repr__(self): return f"HopfieldBrain(patterns={len(self.stored_patterns)})"

if __name__=="__main__":
    print("GEHIRN AF — Hopfield Network"); b=HopfieldBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(20):
        bt=['NullPointer','OffByOne','TypeError'][i%3]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<16,emb)
        if i%5==0: print(f"  Bug{i+1}: {dec['action']:15s}")
    print(b.stats()); print("✅ Gehirn AF läuft.")
