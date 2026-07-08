"""
GEHIRN AA — Differentiable Neural Computer Brain (Graves/DeepMind 2016)
Externe Memory-Matrix mit lesenden/schreibenden Attention-Köpfen.
Controller (NN) + Memory (N×W Matrix) + Read/Write Heads.
Mathematik: M_t = M_{t-1}·(1-w_t·e_t^T) + w_t·v_t^T (write)
            r_t = M_t^T · w_read_t (read)

Autor: Hermes + David | Coding Tentacle 2026
"""
import numpy as np, math
from collections import defaultdict

class DNCBrain:
    """Gehirn AA — DNC: Externer Speicher mit lesenden/schreibenden Köpfen."""
    def __init__(self, memory_size=64, word_size=32, n_read_heads=2, controller_dim=64):
        self.N=memory_size; self.W_dim=word_size; self.R=n_read_heads
        self.ctrl_dim=controller_dim
        
        # Memory
        self.M=np.zeros((memory_size, word_size))  # N×W memory matrix
        self.usage=np.zeros(memory_size)  # Memory usage vector
        
        # Controller weights (vereinfacht: linear)
        self.W_ctrl=np.random.randn(controller_dim, controller_dim)*0.1
        self.W_out=np.random.randn(controller_dim, 64)*0.1
        self.state=np.zeros(controller_dim)
        
        # Pattern-tracker
        self.patterns=defaultdict(lambda: {'success':0,'total':0})
        self.total_bugs=0
    
    def _content_addressing(self, key, beta=1.0):
        """Cosine-Ähnlichkeit zwischen key und allen Memory-Slots"""
        k=np.array(key)[:self.W_dim] if len(key)>self.W_dim else np.pad(key,(0,max(0,self.W_dim-len(key))))
        sims=np.array([np.dot(k,self.M[i])/(np.linalg.norm(k)*np.linalg.norm(self.M[i])+1e-8) for i in range(self.N)])
        w=np.exp(beta*sims)/np.sum(np.exp(beta*sims))
        return w
    
    def _write_memory(self, key, data):
        """Schreibe data in Memory an Position mit höchster Ähnlichkeit zu key"""
        k=np.array(key)[:self.W_dim] if len(key)>self.W_dim else np.pad(key,(0,max(0,self.W_dim-len(key))))
        d=np.array(data)[:self.W_dim] if len(data)>self.W_dim else np.pad(data,(0,max(0,self.W_dim-len(data))))
        w=self._content_addressing(k)
        # Write: M = M·(1-w·e^T) + w·v^T
        erase=np.outer(w,np.ones(self.W_dim))
        add=np.outer(w,d)
        self.M=self.M*(1-0.1*erase)+0.1*add
        self.usage+=w; self.usage=np.clip(self.usage,0,1)
    
    def _read_memory(self, key):
        """Lese aus Memory an Position mit höchster Ähnlichkeit"""
        k=np.array(key)[:self.W_dim] if len(key)>self.W_dim else np.pad(key,(0,max(0,self.W_dim-len(key))))
        w=self._content_addressing(k)
        return self.M.T @ w  # (word_size,)
    
    def think(self,sig,emb):
        self.total_bugs+=1
        bt=sig.split(':')[0] if ':' in sig else sig
        
        # Controller: state → output
        e=np.array(emb)[:self.ctrl_dim] if len(emb)>self.ctrl_dim else np.pad(emb,(0,max(0,self.ctrl_dim-len(emb))))
        self.state=np.tanh(self.W_ctrl @ self.state + e[:self.ctrl_dim]*0.1)
        
        # Read aus Memory
        readout=self._read_memory(emb)
        
        # Combine controller + memory readout
        combined=np.concatenate([self.state[:32], readout[:32]])
        sim=float(np.dot(combined, combined)/(np.linalg.norm(combined)**2+1e-8))
        
        if bt in self.patterns and self.patterns[bt]['total']>=2:
            kp=self.patterns[bt]
            rate=kp['success']/kp['total']
            conf=min(1.0,rate*sim)
            return {'action':'APPLY_PATTERN' if conf>0.3 else 'EXPLORE',
                    'pattern':f'dnc_{bt}','confidence':conf,
                    'memory_usage':f'{np.mean(self.usage):.1%}',
                    'reasoning':f'DNC: {bt} rate={rate:.0%} sim={sim:.2f} conf={conf:.2f}'}
        return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                'reasoning':f'DNC: {bt} nicht im Memory. Schreiben...'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        self.patterns[bt]['total']+=1
        if success: self.patterns[bt]['success']+=1
        if emb:
            # Write to memory: key=emb, data=success_vector
            d=np.ones(self.W_dim)*(1.0 if success else -0.5)
            self._write_memory(emb, d)
    
    def stats(self):
        n=len(self.patterns)
        used=np.sum(self.usage>0.1)
        return {'brain_type':'DNC (DeepMind 2016)','total_bugs':self.total_bugs,
                'memory_used':f'{used}/{self.N}','patterns':n}
    def __repr__(self): return f"DNCBrain(mem={np.sum(self.usage>0.1)}/{self.N})"

if __name__=="__main__":
    print("GEHIRN AA — Differentiable Neural Computer"); b=DNCBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(15):
        bt=['NullPointer','OffByOne','TypeError'][i%3]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<12,emb)
        if i%4==0: print(f"  Bug{i+1}: {dec['action']:15s} mem={dec.get('memory_usage','?')}")
    print(b.stats()); print("✅ Gehirn AA läuft.")
