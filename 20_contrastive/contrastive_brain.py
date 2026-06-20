"""
GEHIRN T — Contrastive Learning Brain
Lernt: Was unterscheidet einen GUTEN Fix von einem SCHLECHTEN?
Positive Paare: (Bug, erfolgreicher Fix). Negative Paare: (Bug, gescheiterter Fix).
InfoNCE Loss: L = -log(exp(sim(q,k+)/τ) / Σ exp(sim(q,k_i)/τ))

Autor: Hermes + David | Coding Tentacle Gehirn Bibliothek
"""
import numpy as np, math
from collections import defaultdict

def cosine(a,b):
    a,b=np.array(a),np.array(b)
    n=np.linalg.norm(a)*np.linalg.norm(b)
    return np.dot(a,b)/n if n>0 else 0.0

class ContrastiveBrain:
    """Gehirn T — Kontrastives Lernen: Gute vs schlechte Fixes unterscheiden."""
    def __init__(self, temperature=0.1, lr=0.1):
        self.tau=temperature; self.lr=lr
        self.anchors=defaultdict(list)     # {bug_type: [(embedding, is_success)]}
        self.prototypes=defaultdict(lambda: np.zeros(384))  # {bug_type: prototype_embedding}
        self.total_bugs=0
    
    def think(self,sig,emb):
        self.total_bugs+=1
        bt=sig.split(':')[0] if ':' in sig else sig
        if bt not in self.prototypes or not self.anchors[bt]:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                    'reasoning':f'Kein Prototyp für {bt}. Kontrastives Lernen starten.'}
        # Ähnlichkeit zum Prototyp (gutem Fix)
        q=np.array(emb)
        proto=self.prototypes[bt]
        sim=cosine(q,proto)
        conf=max(0,sim)
        # Prüfe: Sind genug positive Beispiele?
        pos=sum(1 for _,s in self.anchors[bt] if s)
        neg=sum(1 for _,s in self.anchors[bt] if not s)
        return {'action':'APPLY_PATTERN' if conf>0.3 and pos>neg else 'EXPLORE',
                'pattern':f'contrastive_{bt}','confidence':conf,
                'similarity':sim,'pos_neg_ratio':f'{pos}/{neg}',
                'reasoning':f"Contrast: sim={sim:.2f} pos/neg={pos}/{neg} Prototyp-Norm={np.linalg.norm(proto):.1f}"}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        emb_arr=np.array(emb) if emb else np.zeros(384)
        self.anchors[bt].append((emb_arr,success))
        # Prototyp updaten: Mittel aller ERFOLGREICHEN Embeddings
        pos_embs=[e for e,s in self.anchors[bt] if s]
        if pos_embs:
            self.prototypes[bt]=np.mean(pos_embs,axis=0)
        # Kontrastiver Loss: Erfolgreiche näher an Prototyp, gescheiterte weiter weg
        if success:
            # Positiv: Prototyp → Embedding
            self.prototypes[bt]+=self.lr*(emb_arr-self.prototypes[bt])
        else:
            # Negativ: Prototyp WEG von Embedding
            self.prototypes[bt]-=self.lr*0.3*(emb_arr-self.prototypes[bt])
        if len(self.anchors[bt])>100:
            self.anchors[bt]=self.anchors[bt][-100:]
    
    def stats(self):
        n=len(self.anchors)
        ratios={bt:f"{sum(1 for _,s in v if s)}/{len(v)}" for bt,v in self.anchors.items()}
        return {'brain_type':'Contrastive Learning (InfoNCE)','total_bugs':self.total_bugs,
                'prototypes':n,'pos_neg_ratios':ratios}
    def __repr__(self): return f"ContrastiveBrain(prototypes={len(self.anchors)})"

if __name__=="__main__":
    print("GEHIRN T — Contrastive Learning"); b=ContrastiveBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(15):
        bt=['NullPointer','OffByOne','TypeError'][i%3]
        emb=m.encode(f"{bt} error in code").tolist()
        dec=b.think(f"{bt}:file{i}.py:{i}",emb)
        b.learn(f"{bt}:file{i}.py:{i}",f"fix_{bt}",i<12,emb)
        if i%4==0: print(f"  Bug{i+1}: {dec['action']:15s} sim={dec.get('similarity',0):.2f} | {dec['reasoning'][:55]}")
    print(b.stats()); print("✅ Gehirn T läuft.")
