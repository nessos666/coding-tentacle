"""
GEHIRN AH — Neural Turing Machine Brain (Graves 2014, DeepMind)
Controller-Netzwerk + externer Speicher mit differenzierbaren Lese-/Schreibköpfen.
Addressierung via Content + Location. Shift-basierte Interaktion.
Vorgänger des DNC. Fokus: differenzierbare Adressierung.

Mathematik:
  w_content = softmax(β·cosine(k, M[i]))      (content addressing)
  w_location = shift(interpolate(w_prev, w_content, g))  (location)

Autor: Hermes + David | Coding Tentacle 2026
"""
import numpy as np, math
from collections import defaultdict

class NeuralTuringMachineBrain:
    """Gehirn AH — NTM: Differenzierbarer Speicherzugriff."""
    def __init__(self, memory_size=32, word_size=16, controller_dim=32):
        self.N=memory_size; self.M_dim=word_size; self.ctrl_dim=controller_dim
        self.M=np.zeros((memory_size, word_size))  # Memory Matrix
        self.w_read=np.zeros(memory_size); self.w_read[0]=1  # Read weights
        self.w_write=np.zeros(memory_size); self.w_write[0]=1  # Write weights
        
        self.W_in=np.random.randn(controller_dim, 384)*0.1
        self.W_out=np.random.randn(64, controller_dim)*0.1
        self.patterns=defaultdict(lambda: {'success':0,'total':0,'read_vector':np.zeros(word_size)})
        self.total_bugs=0
    
    def _content_addressing(self, key, beta=2.0):
        """Cosine-Ähnlichkeit + Softmax"""
        k=np.array(key)[:self.M_dim] if len(key)>self.M_dim else np.pad(key,(0,max(0,self.M_dim-len(key))))
        sims=np.array([np.dot(k,self.M[i])/(np.linalg.norm(k)*np.linalg.norm(self.M[i])+1e-8) for i in range(self.N)])
        w=np.exp(beta*sims); return w/np.sum(w)
    
    def _read(self, key):
        """Content-basierter Lesezugriff"""
        w_content=self._content_addressing(key)
        # Interpolation mit vorherigen Read-Weights
        g=0.5  # Interpolationsfaktor
        self.w_read=g*w_content+(1-g)*self.w_read
        return self.M.T @ self.w_read  # (word_size,)
    
    def _write(self, key, data):
        """Content-basierter Schreibzugriff mit Erase+Add"""
        w_content=self._content_addressing(key)
        g=0.5
        self.w_write=g*w_content+(1-g)*self.w_write
        
        d=np.array(data)[:self.M_dim] if len(data)>self.M_dim else np.pad(data,(0,max(0,self.M_dim-len(data))))
        # Erase + Add
        erase=np.outer(self.w_write, np.ones(self.M_dim))
        add=np.outer(self.w_write, d)
        self.M=self.M*(1-0.1*erase)+0.1*add
    
    def think(self,sig,emb):
        self.total_bugs+=1
        bt=sig.split(':')[0] if ':' in sig else sig
        e=np.array(emb)
        
        # Controller: Nutze ersten ctrl_dim-Werte des Embeddings direkt
        trimmed=e[:self.ctrl_dim] if len(e)>=self.ctrl_dim else np.pad(e,(0,self.ctrl_dim-len(e)))
        state=np.tanh(trimmed)
        readout=self._read(e)
        
        # Kombinierte Repräsentation
        combined=np.concatenate([state[:16], readout[:16]])
        
        if self.patterns[bt]['total']>=2:
            kp=self.patterns[bt]
            rate=kp['success']/kp['total']
            stored_sim=np.dot(readout,kp['read_vector'])/(np.linalg.norm(readout)*np.linalg.norm(kp['read_vector'])+1e-8)
            conf=min(1.0, rate*max(0,stored_sim))
            return {'action':'APPLY_PATTERN' if conf>0.3 else 'EXPLORE',
                    'pattern':f'ntm_{bt}','confidence':conf,
                    'read_sim':float(stored_sim),
                    'reasoning':f'NTM: {bt} read_sim={stored_sim:.2f} conf={conf:.2f}'}
        return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                'reasoning':f'NTM: {bt} nicht im Speicher.'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        self.patterns[bt]['total']+=1
        if success: self.patterns[bt]['success']+=1
        if emb and success:
            e=np.array(emb)
            self._write(e, np.ones(self.M_dim))
            self.patterns[bt]['read_vector']=self._read(e)
    
    def stats(self):
        used=np.sum(np.any(np.abs(self.M)>0.01, axis=1))
        return {'brain_type':'Neural Turing Machine','total_bugs':self.total_bugs,
                'memory_used':f'{used}/{self.N}','patterns':len(self.patterns)}
    def __repr__(self): return f"NTMBrain(mem={np.sum(np.any(np.abs(self.M)>0.01,axis=1))}/{self.N})"

if __name__=="__main__":
    print("GEHIRN AH — Neural Turing Machine"); b=NeuralTuringMachineBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(20):
        bt=['NullPointer','OffByOne','TypeError'][i%3]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<16,emb)
        if i%5==0: print(f"  Bug{i+1}: {dec['action']:15s}")
    print(b.stats()); print("✅ Gehirn AH läuft.")
