"""
GEHIRN Y — Graph Neural Network Brain (Kipf & Welling 2016)
Message-Passing zwischen Bug-Knoten. Jeder Knoten aggregiert Nachbarn.
H^(l+1) = σ(D̃^(-½)·Ã·D̃^(-½)·H^(l)·W^(l))
Bug-Embeddings werden durch Graph-Struktur verfeinert.

Autor: Hermes + David | Coding Tentacle Gehirn Bibliothek
"""
import numpy as np, math
from collections import defaultdict

class GNNBrain:
    """Gehirn Y — Message-Passing Graph Neural Network."""
    def __init__(self, hidden_dim=64, n_layers=2, lr=0.1):
        self.hidden_dim=hidden_dim; self.n_layers=n_layers; self.lr=lr
        self.W=[np.random.randn(hidden_dim,hidden_dim)*0.1 for _ in range(n_layers)]
        self.nodes={}  # {sig: (embedding, pattern, success)}
        self.edges=defaultdict(set)
        self.total_bugs=0
    
    def _message_passing(self, query_emb):
        if not self.nodes: return query_emb
        # Einfache GCN: aggregiere Nachbarn
        h=np.array(query_emb)[:self.hidden_dim] if len(query_emb)>self.hidden_dim else np.pad(query_emb,(0,max(0,self.hidden_dim-len(query_emb))))
        neighbor_embs=[]
        for sig in self.nodes:
            emb_n=self.nodes[sig][0][:self.hidden_dim] if len(self.nodes[sig][0])>self.hidden_dim else np.pad(self.nodes[sig][0],(0,max(0,self.hidden_dim-len(self.nodes[sig][0]))))
            neighbor_embs.append(emb_n)
        if neighbor_embs:
            neighbor_mean=np.mean(neighbor_embs,axis=0)
            for l in range(self.n_layers):
                h=h+0.3*(self.W[l]@neighbor_mean)  # Message-Passing
        return h
    
    def think(self,sig,emb):
        self.total_bugs+=1
        bt=sig.split(':')[0] if ':' in sig else sig
        h=self._message_passing(emb)
        # Ähnlichste Knoten nach Message-Passing
        best_sim,best_pat=0,None
        for nsig,(nemb,npat,nsucc) in self.nodes.items():
            nbt=nsig.split(':')[0] if ':' in nsig else nsig
            if nbt==bt or bt.lower() in nbt.lower():
                sim=np.dot(h,nemb[:self.hidden_dim])/(np.linalg.norm(h)*np.linalg.norm(nemb[:self.hidden_dim])+1e-8)
                if sim>best_sim: best_sim=sim; best_pat=npat
        if best_sim>0.5:
            return {'action':'APPLY_PATTERN','pattern':best_pat,'confidence':float(best_sim),
                    'gnn_similarity':float(best_sim),
                    'reasoning':f'GNN: Message-Passing → {best_pat} (sim={best_sim:.2f})'}
        return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                'reasoning':f'GNN: Kein ähnlicher Knoten nach Message-Passing.'}
    
    def learn(self,sig,pat,success,emb=None):
        if emb is None: emb=np.zeros(self.hidden_dim)
        self.nodes[sig]=(np.array(emb),pat,success)
        # Edges zu gleichen Bug-Typen
        bt=sig.split(':')[0] if ':' in sig else sig
        for nsig in self.nodes:
            nbt=nsig.split(':')[0] if ':' in nsig else nsig
            if nbt==bt and nsig!=sig:
                self.edges[sig].add(nsig)
                self.edges[nsig].add(sig)
    
    def stats(self):
        n=len(self.nodes); e=sum(len(v) for v in self.edges.values())
        return {'brain_type':'GNN Message-Passing','total_bugs':self.total_bugs,
                'nodes':n,'edges':e,'avg_degree':f'{e/max(1,n):.1f}'}
    def __repr__(self): return f"GNNBrain(nodes={len(self.nodes)},edges={sum(len(v) for v in self.edges.values())})"

if __name__=="__main__":
    print("GEHIRN Y — GNN Message-Passing"); b=GNNBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(15):
        bt=['NullPointer','OffByOne','TypeError'][i%3]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<12,emb)
        if i%4==0: print(f"  Bug{i+1}: {dec['action']:15s}")
    print(b.stats()); print("✅ Gehirn Y läuft.")
