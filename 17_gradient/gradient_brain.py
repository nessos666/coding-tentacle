"""
GEHIRN Q — Gradient Descent / Optimierung Brain
Kontinuierliche Optimierung: Fix-Parameter via Gradientenabstieg.
Nicht "welches Pattern?" sondern "welche Parameter für diesen Fix?"
Mathematik: θ ← θ - η·∇L(θ).  Adam: m=β1·m+(1-β1)·g, v=β2·v+(1-β2)·g²

Autor: Hermes + David | Coding Tentacle Gehirn Bibliothek
"""
import numpy as np, math
from collections import defaultdict

class GradientBrain:
    """Gehirn Q — Optimiert Fix-Parameter via Gradientenabstieg."""
    def __init__(self, lr=0.1, beta1=0.9, beta2=0.999):
        self.lr=lr; self.beta1=beta1; self.beta2=beta2
        self.params=defaultdict(lambda: np.zeros(10))  # 10 Parameter pro Bug-Typ
        self.m=defaultdict(lambda: np.zeros(10))
        self.v=defaultdict(lambda: np.zeros(10))
        self.t=defaultdict(int)
        self.loss_history=defaultdict(list)
        self.total_bugs=0
    
    def think(self,sig,emb):
        self.total_bugs+=1
        bt=sig.split(':')[0] if ':' in sig else sig
        p=self.params[bt]
        # Konfidenz = 1/(1+loss) — je kleiner der Loss, desto höher Konfidenz
        avg_loss=np.mean(self.loss_history[bt][-10:]) if self.loss_history[bt] else 1.0
        conf=1/(1+avg_loss)
        return {'action':'APPLY_PATTERN' if conf>0.3 else 'EXPLORE',
                'pattern':f'gradient_fix_{bt}','confidence':conf,
                'loss':avg_loss,'param_norm':float(np.linalg.norm(p)),
                'reasoning':f"Gradient: θ({bt}) Loss={avg_loss:.3f} Conf={conf:.2f}"}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        # Loss: 0 wenn Erfolg, 1 wenn Misserfolg
        loss=0.0 if success else 1.0
        self.loss_history[bt].append(loss)
        # Gradient: Richtung zum Optimum (0=perfekt)
        grad=loss*0.1*np.random.randn(10)  # Stochastischer Gradient
        self.t[bt]+=1
        # Adam-Update
        self.m[bt]=self.beta1*self.m[bt]+(1-self.beta1)*grad
        self.v[bt]=self.beta2*self.v[bt]+(1-self.beta2)*(grad**2)
        m_hat=self.m[bt]/(1-self.beta1**self.t[bt])
        v_hat=self.v[bt]/(1-self.beta2**self.t[bt])
        self.params[bt]-=self.lr*m_hat/(np.sqrt(v_hat)+1e-8)
    
    def stats(self):
        n=len(self.params)
        losses={bt:np.mean(self.loss_history[bt][-10:]) for bt in self.params if self.loss_history[bt]}
        best=min(losses.items(),key=lambda x:x[1]) if losses else ('?',1)
        return {'brain_type':'Gradient Descent (Adam)','total_bugs':self.total_bugs,
                'optimized_types':n,'best_loss':f'{best[0]}:{best[1]:.3f}',
                'total_steps':sum(self.t.values())}
    def __repr__(self): return f"GradientBrain(types={len(self.params)})"

if __name__=="__main__":
    print("GEHIRN Q — Gradient Descent"); b=GradientBrain()
    for i in range(20):
        bt=['NullPointer','OffByOne','TypeError'][i%3]
        dec=b.think(f"{bt}:file{i}.py:{i}",[0]*384)
        b.learn(f"{bt}:file{i}.py:{i}",'fix',i<15 or i%3==1)
        if i%5==0: print(f"  Step{i}: {dec['reasoning'][:55]}")
    print(b.stats()); print("✅ Gehirn Q läuft.")
