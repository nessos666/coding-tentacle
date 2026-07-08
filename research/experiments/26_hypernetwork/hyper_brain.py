"""
GEHIRN Z v2 — Hypernetwork Brain (Fixed)
FIX: Meta-Learning mit richtiger Few-Shot-Adaption.
Statt generierter Gewichte → direkt Similarity im Embedding-Space.
"""
import numpy as np, math
from collections import defaultdict

class HypernetworkBrain:
    """Gehirn Z v2 — Few-Shot Meta-Learning via Prototype-Netzwerke."""
    def __init__(self, meta_lr=0.05, latent_dim=32):
        self.meta_lr=meta_lr; self.latent_dim=latent_dim
        self.prototypes={}  # {bug_type: prototype_embedding}
        self.task_memory=defaultdict(lambda: {'x':[], 'y':[]})
        self.total_bugs=0
    
    def think(self,sig,emb):
        self.total_bugs+=1
        bt=sig.split(':')[0] if ':' in sig else sig
        e=np.array(emb)
        
        if len(self.task_memory[bt]['x'])<3:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                    'reasoning':f'Few-Shot: {bt} braucht ≥3 Beispiele. ({len(self.task_memory[bt]["x"])}/3)'}
        
        # Prototyp aus positiven Beispielen
        pos=[self.task_memory[bt]['x'][i] for i,y in enumerate(self.task_memory[bt]['y']) if y>0.5]
        if not pos:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                    'reasoning':f'Few-Shot: {bt} keine positiven Beispiele.'}
        
        proto=np.mean(pos,axis=0)
        sim=np.dot(e,proto)/(np.linalg.norm(e)*np.linalg.norm(proto)+1e-8)
        conf=max(0,min(1.0,sim*len(pos)/max(1,len(self.task_memory[bt]['x']))))
        
        return {'action':'APPLY_PATTERN' if conf>0.3 else 'EXPLORE',
                'pattern':f'meta_{bt}','confidence':conf,
                'shots':len(pos),'similarity':float(sim),
                'reasoning':f'Meta: {bt} proto-sim={sim:.2f} ({len(pos)} shots) conf={conf:.2f}'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        if emb is None: return
        e=np.array(emb)
        self.task_memory[bt]['x'].append(e)
        self.task_memory[bt]['y'].append(1.0 if success else 0.0)
        if len(self.task_memory[bt]['x'])>50:
            self.task_memory[bt]['x']=self.task_memory[bt]['x'][-50:]
            self.task_memory[bt]['y']=self.task_memory[bt]['y'][-50:]
    
    def stats(self):
        return {'brain_type':'Hypernetwork v2 (Prototype Networks)',
                'total_bugs':self.total_bugs,
                'tasks':{bt:len(v['x']) for bt,v in self.task_memory.items()}}
    def __repr__(self): return f"Hypernetwork(tasks={len(self.task_memory)})"

if __name__=="__main__":
    print("GEHIRN Z v2 — Hypernetwork"); b=HypernetworkBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(20):
        bt=['NullPointer','OffByOne','TypeError'][i%3]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<16,emb)
        if i%5==0: print(f"  Bug{i+1}: {dec['action']:15s} shots={dec.get('shots',0)}")
    print(b.stats()); print("✅ Gehirn Z v2 läuft.")
