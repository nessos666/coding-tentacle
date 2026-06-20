"""
GEHIRN AJ — Modern Hopfield Network (Krotov/Hopfield 2016, Ramsauer 2021)
SOFTMAX-BASIERTE Speicherung. Exponentielle Kapazität.
Mathematisch äquivalent zur Transformer-Attention!
Update: x_new = X · softmax(β · X^T · x)
X = Matrix aller Pattern-Embeddings. β = Temperatur.

Autor: Hermes + David | Coding Tentacle 2026
Quelle: Ramsauer et al. "Hopfield Networks is All You Need" (ICLR 2021)
"""
import numpy as np, math
from collections import defaultdict

class ModernHopfieldBrain:
    """Gehirn AJ — Modern Hopfield: Softmax-Attention als Gedächtnisabruf."""
    def __init__(self, beta=8.0, max_patterns=500):
        self.beta=beta; self.max_patterns=max_patterns
        self.X=[]  # Liste aller Pattern-Vektoren (je 128dim)
        self.pattern_names=[]  # Namen der Patterns
        self.success_labels=[]  # 1=erfolgreich, 0=gescheitert
        self.pattern_dim=128
        self.total_bugs=0
    
    def _encode(self, emb):
        e=np.array(emb)
        if len(e)>self.pattern_dim:
            return e[:self.pattern_dim]
        return np.pad(e,(0,max(0,self.pattern_dim-len(e))))
    
    def _retrieve(self, query):
        """Modern Hopfield Retrieval: softmax(β·X^T·q)·X^T"""
        if not self.X: return None, 0.0
        
        X_mat=np.array(self.X)  # (M, D)
        q=self._encode(query)
        
        # Attention-Scores: β · X @ q
        scores=self.beta * (X_mat @ q)
        scores-=np.max(scores)  # Numerische Stabilität
        attn_weights=np.exp(scores)/np.sum(np.exp(scores))  # Softmax
        
        # Gewichteter Abruf: Σ attn_i · pattern_i
        retrieved=attn_weights @ X_mat  # (D,)
        
        # Erfolgsgewichtete Konfidenz
        success_weighted=np.sum(attn_weights * np.array(self.success_labels))
        
        # Ähnlichster Pattern-Name
        best_idx=np.argmax(attn_weights)
        return self.pattern_names[best_idx], float(success_weighted)
    
    def think(self,sig,emb):
        self.total_bugs+=1
        bt=sig.split(':')[0] if ':' in sig else sig
        
        if len(self.X)<2:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                    'reasoning':'Modern Hopfield: Noch zu wenige Patterns (<2).'}
        
        name, conf=self._retrieve(emb)
        
        if conf>0.3:
            return {'action':'APPLY_PATTERN','pattern':name,'confidence':conf,
                    'patterns_stored':len(self.X),
                    'reasoning':f'Modern Hopfield: {name} via Softmax-Attention (conf={conf:.2f})'}
        return {'action':'EXPLORE','pattern':None,'confidence':conf,
                'patterns_stored':len(self.X),
                'reasoning':f'Modern Hopfield: Kein starker Match (max conf={conf:.2f})'}
    
    def learn(self,sig,pat,success,emb=None):
        if emb is None: return
        e=self._encode(emb)
        self.X.append(e)
        self.pattern_names.append(pat)
        self.success_labels.append(1.0 if success else 0.0)
        if len(self.X)>self.max_patterns:
            self.X=self.X[-self.max_patterns:]
            self.pattern_names=self.pattern_names[-self.max_patterns:]
            self.success_labels=self.success_labels[-self.max_patterns:]
    
    def stats(self):
        stored=len(self.X)
        succ=np.mean(self.success_labels) if self.success_labels else 0
        return {'brain_type':'Modern Hopfield (Softmax-Attention)','total_bugs':self.total_bugs,
                'patterns_stored':stored,'capacity_type':'EXPONENTIAL',
                'success_rate':f'{succ:.0%}','beta':self.beta}
    def __repr__(self): return f"ModernHopfield(patterns={len(self.X)})"

if __name__=="__main__":
    print("GEHIRN AJ — Modern Hopfield (Softmax-Attention)")
    b=ModernHopfieldBrain(beta=8.0)
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(25):
        bt=['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'][i%5]
        emb=m.encode(f"{bt} error in code requires fix").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<20,emb)
        if i%5==0: print(f"  Bug{i+1}: {dec['action']:15s} conf={dec.get('confidence',0):.2f}")
    print(b.stats()); print("✅ Gehirn AJ läuft.")
