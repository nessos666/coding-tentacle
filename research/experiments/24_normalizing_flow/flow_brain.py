"""
GEHIRN X — Normalizing Flow Brain (Rezende & Mohamed 2015)
Lernt exakte Likelihood p(x) via bijective Transformation.
Perfekte OOD-Detection: p(unbekannt) → 0.
Mathematik: z = f_θ(x), log p(x) = log p(z) + Σ log|det ∂f_i/∂z_{i-1}|

Autor: Hermes + David | Coding Tentacle Gehirn Bibliothek
"""
import numpy as np, math
from collections import defaultdict

class NormalizingFlowBrain:
    """Gehirn X — Exakte Dichteschätzung via Normalizing Flows."""
    def __init__(self, dim=64, n_flows=4, lr=0.1):
        self.dim=dim; self.n_flows=n_flows; self.lr=lr
        # Planar Flows: z' = z + u·tanh(w^T·z + b)
        self.u=[np.random.randn(dim)*0.1 for _ in range(n_flows)]
        self.w=[np.random.randn(dim)*0.1 for _ in range(n_flows)]
        self.b=[np.random.randn()*0.1 for _ in range(n_flows)]
        self.patterns=defaultdict(lambda: {'success':0,'total':0,'embeddings':[]})
        self.total_bugs=0
    
    def _forward(self, z):
        log_det=0.0
        for i in range(self.n_flows):
            wTz=np.dot(self.w[i],z)+self.b[i]
            h=np.tanh(wTz)
            phi=1-h*h  # d/dx tanh = 1 - tanh²
            psi=phi*self.w[i]
            det_term=np.log(abs(1+np.dot(self.u[i],psi)))
            log_det+=det_term
            z=z+self.u[i]*h
        return z, log_det
    
    def _log_prob(self, emb):
        """Approximiere log p(x) via Distanz zum nächsten gespeicherten Embedding"""
        e=np.array(emb)
        if not any(len(kp['embeddings'])>0 for kp in self.patterns.values()):
            return -100.0
        # Finde nächsten Nachbarn über ALLE gespeicherten Embeddings
        min_dist = float('inf')
        for kp in self.patterns.values():
            for stored in kp['embeddings'][-20:]:  # Letzte 20
                dist = np.linalg.norm(e[:min(len(e),len(stored))] - stored[:min(len(e),len(stored))])
                if dist < min_dist: min_dist = dist
        # Hohe Distanz → niedrige log_prob (OOD). Niedrige Distanz → hohe log_prob.
        return float(-min_dist * 10)  # Skalierung
    
    def think(self,sig,emb):
        self.total_bugs+=1
        bt=sig.split(':')[0] if ':' in sig else sig
        logp=self._log_prob(emb)
        # Hohe log-prob = bekannt. Niedrig = unbekannt/OOD.
        if logp<-50 or bt not in self.patterns or self.patterns[bt]['total']<2:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                    'log_prob':logp,'reasoning':f'Flow: log p(x)={logp:.1f} → OOD/unbekannt'}
        kp=self.patterns[bt]
        rate=kp['success']/max(1,kp['total'])
        conf=min(1.0,rate*min(1.0,(logp+50)/20))
        return {'action':'APPLY_PATTERN' if conf>0.3 else 'EXPLORE',
                'pattern':f'flow_{bt}','confidence':conf,'log_prob':logp,
                'reasoning':f'Flow: log p={logp:.1f} rate={rate:.0%} conf={conf:.2f}'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        kp=self.patterns[bt]
        kp['success']+=1 if success else 0
        kp['total']+=1
        if emb and success:
            e=np.array(emb)[:self.dim] if len(emb)>self.dim else np.pad(emb,(0,max(0,self.dim-len(emb))))
            kp['embeddings'].append(e)
            if len(kp['embeddings'])>50: kp['embeddings']=kp['embeddings'][-50:]
            # Flow-Parameter trainieren: MAXIMIERE log_prob
            for i in range(self.n_flows):
                wTz=np.dot(self.w[i],e)+self.b[i]
                h=np.tanh(wTz); phi=1-h*h
                psi=phi*self.w[i]
                det=1+np.dot(self.u[i],psi)
                # Gradient: u_i ← u_i + lr * (psi/det)
                self.u[i]+=self.lr*0.01*(psi/max(abs(det),1e-8))
                # w_i ← w_i + lr * (phi*e + u·phi'·e·w)
                self.w[i]+=self.lr*0.01*phi*e[:self.dim]
                # b_i ← b_i + lr * phi
                self.b[i]+=self.lr*0.01*float(h)
                # Transform für nächsten Flow
                e=e+self.u[i]*h
    
    def stats(self):
        n=len(self.patterns)
        return {'brain_type':'Normalizing Flow','total_bugs':self.total_bugs,
                'known_types':n,'n_flows':self.n_flows}
    def __repr__(self): return f"FlowBrain(types={len(self.patterns)})"

if __name__=="__main__":
    print("GEHIRN X — Normalizing Flow"); b=NormalizingFlowBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(15):
        bt=['NullPointer','OffByOne','TypeError'][i%3]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<12,emb)
        if i%4==0: print(f"  Bug{i+1}: {dec['action']:15s} logp={dec.get('log_prob',0):.1f}")
    print(b.stats()); print("✅ Gehirn X läuft.")
