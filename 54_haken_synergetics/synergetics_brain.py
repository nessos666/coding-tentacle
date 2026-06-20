"""
GEHIRN BA — Haken Synergetics Brain
VERSKLAVUNGSPRINZIP: Wenige Ordnungsparameter steuern das ganze System.
Nahe Bifurkationspunkten bestimmen langsame Moden die schnellen Moden.

Mathematik: dq/dt = -∂V/∂q + F(t)  (Ordnungsparameter-Dynamik)
           Versklavung: s = f(q)  (schnelle Moden = Funktion der langsamen)

Autor: Hermes + David | Coding Tentacle 2026
Quelle: Haken "Synergetics" (1977), "Advanced Synergetics" (1983)
"""
import numpy as np, math
from collections import defaultdict, deque

class SynergeticsBrain:
    """Gehirn BA — Ordnungsparameter steuern das System (Haken)."""
    def __init__(self, n_order_params=3, n_fast_modes=10, lr=0.1):
        self.n_order=n_order_params; self.n_fast=n_fast_modes; self.lr=lr
        # Ordnungsparameter (langsame Moden) — STEUERN alles
        self.order_params=np.zeros(n_order_params)
        # Schnelle Moden — VERSKLAVT von Ordnungsparametern
        self.fast_modes=np.zeros(n_fast_modes)
        # Kopplungsmatrix: Ordnungsparameter → schnelle Moden
        self.coupling=np.random.randn(n_fast_modes, n_order_params)*0.1
        # Potential-Landschaft
        self.potential=defaultdict(float)
        self.patterns=defaultdict(lambda: {'success':0,'total':0,'order_signal':np.zeros(n_order_params)})
        self.total_bugs=0
        self.bifurcation_history=deque(maxlen=50)
    
    def _evolve_order_params(self, bt, emb, success):
        """Ordnungsparameter-Dynamik: dq/dt = -∂V/∂q"""
        e=np.array(emb)[:self.n_order] if len(emb)>=self.n_order else np.pad(emb,(0,self.n_order-len(emb)))
        # Potential: V(q) = ½(q-q_target)²
        q_target=e if success else -e*0.5
        dq=-1.0*(self.order_params-q_target)  # Gradient Descent im Potential
        self.order_params+=self.lr*dq
        # Bifurkations-Check: Plötzlicher Sprung?
        if np.linalg.norm(dq)>1.0:
            self.bifurcation_history.append(self.total_bugs)
    
    def _enslave_fast_modes(self):
        """Schnelle Moden = f(Ordnungsparameter) — VERSKLAVT"""
        self.fast_modes=np.tanh(self.coupling @ self.order_params)
    
    def _identify_order_pattern(self, bt):
        """Welcher Ordnungsparameter dominiert diesen Bug-Typ?"""
        p=self.patterns[bt]
        if p['total']>=3:
            # Der Ordnungsparameter mit höchstem Signal dominiert
            idx=np.argmax(np.abs(p['order_signal']))
            return idx, p['order_signal'][idx]
        return 0, 0.0
    
    def think(self,sig,emb):
        self.total_bugs+=1; bt=sig.split(':')[0] if ':' in sig else sig
        self._enslave_fast_modes()
        
        if self.patterns[bt]['total']<1:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                    'reasoning':f'Synergetics: {bt} kein Ordnungsparameter.'}
        
        idx, signal=self._identify_order_pattern(bt)
        rate=self.patterns[bt]['success']/max(1,self.patterns[bt]['total'])
        # Ordnungsparameter-Stärke = Konfidenz
        order_strength=abs(signal)
        conf=min(1.0, rate*order_strength)
        
        return {'action':'APPLY_PATTERN' if conf>0.2 else 'EXPLORE',
                'pattern':f'order_{bt}','confidence':conf,
                'order_param':idx,'order_strength':f'{order_strength:.2f}',
                'bifurcations':len(self.bifurcation_history),
                'reasoning':f'Synergetics: {bt} OrderParam#{idx} strength={order_strength:.2f} conf={conf:.2f}'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        self.patterns[bt]['total']+=1
        if success: self.patterns[bt]['success']+=1
        
        if emb:
            self._evolve_order_params(bt, emb, success)
            # Ordnungsparameter-Signal für diesen Bug-Typ speichern
            self.patterns[bt]['order_signal']=self.order_params.copy()
    
    def stats(self):
        return {'brain_type':'Synergetics (Haken)','total_bugs':self.total_bugs,
                'order_params':f'{self.order_params[:3]}','n_order':self.n_order,
                'fast_modes':f'{np.linalg.norm(self.fast_modes):.1f}',
                'bifurcations':len(self.bifurcation_history),
                'patterns':len(self.patterns)}
    def __repr__(self): return f"SynergeticsBrain(bifurcations={len(self.bifurcation_history)})"

if __name__=="__main__":
    print("GEHIRN BA — Synergetics (Haken)"); b=SynergeticsBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(30):
        bt=['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'][i%5]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<25,emb)
        if i%6==0: print(f"  Bug{i+1}: {dec['action']:15s} order=#{dec.get('order_param','?')} strength={dec.get('order_strength','?')}")
    print(b.stats()); print("✅ Gehirn BA läuft.")
