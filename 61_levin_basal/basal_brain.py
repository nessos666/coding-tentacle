"""
GEHIRN BH — Michael Levin Basal Cognition Brain
JEDE ZELLE DENKT. Kognition auf allen Ebenen.
Bioelektrizität als Rechenmodell: Spannungsmuster = Gedächtnis.

Mathematik: V_mem = RT/F · ln(P_K·[K]_out + P_Na·[Na]_out) / (P_K·[K]_in + P_Na·[Na]_in)
           Gap Junctions: I_ij = g_gap · (V_i - V_j)

Autor: Hermes + David | Coding Tentacle 2026
Quelle: Levin "Molecular Bioelectricity" (2014), "Cognition all the way down" (2025)
"""
import numpy as np, math
from collections import defaultdict

class BasalCognitionBrain:
    """Gehirn BH — Kognition auf Zellebene (Levin)."""
    def __init__(self, n_cells=30):
        self.n=n_cells
        # Zell-Potentiale (Bioelektrizität)
        self.V=np.random.randn(n_cells)*0.1
        # Gap-Junction-Leitfähigkeiten (Zell-Zell-Kommunikation)
        self.gap=np.random.rand(n_cells, n_cells)*0.1
        np.fill_diagonal(self.gap, 0)
        # Pattern-Memory in Zellverbänden
        self.cell_memory=defaultdict(lambda: np.zeros(n_cells))
        self.patterns=defaultdict(lambda: {'success':0,'total':0})
        self.total_bugs=0
    
    def _update_potentials(self, emb):
        """Bioelektrische Dynamik: V_i += Σ g_ij·(V_j - V_i) + external"""
        e=np.array(emb)[:self.n] if len(emb)>=self.n else np.pad(emb,(0,self.n-len(emb)))
        # Gap-Junction-Strom
        delta=np.zeros(self.n)
        for i in range(self.n):
            for j in range(self.n):
                delta[i]+=self.gap[i,j]*(self.V[j]-self.V[i])
        # Externer Reiz (Embedding)
        delta+=e*0.1
        # Update
        self.V+=delta*0.1
        self.V=np.clip(self.V, -2, 2)
    
    def _read_cell_memory(self, bt):
        """Lese Pattern aus Zellverband"""
        mem=self.cell_memory[bt]
        if np.linalg.norm(mem)>0:
            return float(np.dot(self.V, mem)/(np.linalg.norm(self.V)*np.linalg.norm(mem)+1e-8))
        return 0.0
    
    def _write_cell_memory(self, bt, success):
        """Schreibe Pattern in Zellverband (Hebb-artig)"""
        if success:
            self.cell_memory[bt]=self.cell_memory[bt]*0.8+self.V*0.2
        else:
            self.cell_memory[bt]=self.cell_memory[bt]*0.95  # Langsam vergessen
    
    def think(self,sig,emb):
        self.total_bugs+=1; bt=sig.split(':')[0] if ':' in sig else sig
        self._update_potentials(emb)
        
        mem_signal=self._read_cell_memory(bt)
        
        if self.patterns[bt]['total']<2:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                    'mean_potential':f'{np.mean(self.V):.2f}',
                    'reasoning':f'Basal: {bt} Zellverband formiert... V̄={np.mean(self.V):.2f}mV'}
        
        rate=self.patterns[bt]['success']/max(1,self.patterns[bt]['total'])
        conf=min(1.0, rate*max(0,mem_signal))
        
        return {'action':'APPLY_PATTERN' if conf>0.2 else 'EXPLORE',
                'pattern':f'basal_{bt}','confidence':conf,
                'mem_signal':f'{mem_signal:.2f}','mean_V':f'{np.mean(self.V):.2f}',
                'reasoning':f'Basal: {bt} V̄={np.mean(self.V):.2f}mV mem={mem_signal:.2f} conf={conf:.2f}'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        self.patterns[bt]['total']+=1
        if success: self.patterns[bt]['success']+=1
        self._write_cell_memory(bt, success)
        if emb: self._update_potentials(emb)
    
    def stats(self):
        return {'brain_type':'Basal Cognition (Levin)','total_bugs':self.total_bugs,
                'cells':self.n,'mean_potential':f'{np.mean(self.V):.3f}mV',
                'cell_memories':len(self.cell_memory)}
    def __repr__(self): return f"BasalCognitionBrain(cells={self.n})"

if __name__=="__main__":
    print("GEHIRN BH — Basal Cognition (Levin)"); b=BasalCognitionBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(25):
        bt=['NullPointer','OffByOne','TypeError'][i%3]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<20,emb)
        if i%5==0: print(f"  Bug{i+1}: {dec['action']:15s} V={dec.get('mean_V','?')}mV mem={dec.get('mem_signal','?')}")
    print(b.stats()); print("✅ Gehirn BH läuft.")
