"""
GEHIRN M — Attention/Transformer Brain (Vaswani 2017)
Self-Attention: Q·K^T → Softmax → Weighted V
Memory als Key-Value-Store. Query = aktueller Bug.
Mathematik: Attention(Q,K,V) = softmax(QK^T/√d_k)·V

Autor: Hermes + David | Coding Tentacle Gehirn Bibliothek
"""
import math, numpy as np
from collections import defaultdict

class AttentionBrain:
    """Gehirn M — Attention über Memory-Einträge. Q=aktueller Bug, K/V=gespeicherte Bugs."""
    def __init__(self, d_k=64, temperature=1.0):
        self.d_k=d_k; self.temperature=temperature
        self.keys=[]     # [(signature, key_embedding)]
        self.values=[]   # [(pattern, success)]
        self.total_bugs=0
    
    def _attention(self, Q, keys):
        if not keys: return []
        K=np.array(keys)
        Q=np.array(Q)[:self.d_k] if len(Q)>self.d_k else np.pad(Q,(0,max(0,self.d_k-len(Q))))
        K=K[:,:self.d_k] if K.shape[1]>self.d_k else np.pad(K,((0,0),(0,max(0,self.d_k-K.shape[1]))))
        scores=Q @ K.T / math.sqrt(self.d_k)
        scores/=self.temperature
        scores-=np.max(scores)
        probs=np.exp(scores)/np.sum(np.exp(scores))
        return probs
    
    def think(self,sig,emb):
        self.total_bugs+=1
        Q=np.array(emb)
        if not self.keys:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,'reasoning':'Leerer Key-Value-Store.'}
        key_embs=[k[1] for k in self.keys]
        attn=self._attention(Q,key_embs)
        # Gewichtete Aggregation der Values
        pattern_scores=defaultdict(float)
        for i,(pat,success) in enumerate(self.values):
            pattern_scores[pat]+=attn[i]*(1.0 if success else -0.3)
        if not pattern_scores: return {'action':'EXPLORE','pattern':None,'confidence':0.0,'reasoning':'Keine Patterns.'}
        best=max(pattern_scores,key=pattern_scores.get)
        conf=min(1.0,max(0.0,pattern_scores[best]))
        return {'action':'APPLY_PATTERN' if conf>0.2 else 'EXPLORE','pattern':best,'confidence':conf,
                'attn_weights':f'{np.max(attn):.2f}','reasoning':f"Attention: {best} (score={conf:.2f})"}
    
    def learn(self,sig,pat,success,emb=None):
        if emb is None: emb=np.zeros(384)
        self.keys.append((sig,np.array(emb)))
        self.values.append((pat,success))
        if len(self.keys)>200:  # Limit
            self.keys=self.keys[-200:]; self.values=self.values[-200:]
    
    def stats(self):
        n=len(self.keys)
        succ=sum(1 for _,s in self.values if s)/max(1,n)
        return {'brain_type':'Attention/Transformer','total_bugs':self.total_bugs,
                'memory_size':n,'success_rate':f'{succ:.0%}'}
    def __repr__(self): return f"AttentionBrain(memory={len(self.keys)})"

if __name__=="__main__":
    print("GEHIRN M — Attention"); b=AttentionBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    bugs=[("NullPointer:pay.py:1","guard_clause",True),("NullPointer:auth.py:2","guard_clause",True),
          ("OffByOne:page.py:1","boundary_check",True),("NullPointer:order.py:3","guard_clause",True),
          ("TypeError:parse.py:1","type_convert",True),("NullPointer:user.py:4","guard_clause",True)]
    for i,(sig,pat,ok) in enumerate(bugs):
        emb=m.encode(f"bug {sig}").tolist()
        dec=b.think(sig,emb)
        print(f"  Bug{i+1}: {dec['action']:15s} conf={dec['confidence']:.1f}")
        b.learn(sig,pat,ok,emb)
    print(b.stats()); print("✅ Gehirn M läuft.")
