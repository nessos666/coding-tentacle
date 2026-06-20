"""
GEHIRN BE — Wolfram Cellular Automata Brain
RULE-BASIERTE KOMPLEXITÄT. Einfachste Regeln → emergentes Verhalten.
Bug-Fixing als zellulärer Automat: Jeder Bug = Zelle. Regeln = Fix-Patterns.

Mathematik: s_i(t+1) = f(s_{i-1}(t), s_i(t), s_{i+1}(t))
           Rule 30: a_i' = a_{i-1} XOR (a_i OR a_{i+1})
           Rule 110 = Turing-vollständig!

Autor: Hermes + David | Coding Tentacle 2026
Quelle: Wolfram "A New Kind of Science" (2002)
"""
import numpy as np, math
from collections import defaultdict

class CellularAutomataBrain:
    """Gehirn BE — Zellulärer Automat: Einfache Regeln, emergentes Verhalten."""
    def __init__(self, grid_size=20, rule_set=None):
        self.N=grid_size
        # 8 Regeln (Rule 0-255 Style): 3-bit Input → 1-bit Output
        self.rules=rule_set or {  # Default: Rule 110 (Turing-vollständig!)
            (1,1,1):0, (1,1,0):1, (1,0,1):1, (1,0,0):0,
            (0,1,1):1, (0,1,0):1, (0,0,1):1, (0,0,0):0
        }
        self.grid=np.zeros((grid_size, grid_size))  # Zellgitter
        self.generation=0
        self.patterns=defaultdict(lambda: {'success':0,'total':0})
        self.total_bugs=0
    
    def _step_automaton(self, emb):
        """Ein Schritt des zellulären Automaten"""
        e=np.array(emb)[:self.N] if len(emb)>=self.N else np.pad(emb,(0,self.N-len(emb)))
        # Initialisiere erste Reihe mit Embedding
        self.grid[0]=(e>0).astype(float) if np.max(np.abs(e))>0 else np.random.randint(0,2,self.N)
        new_row=np.zeros(self.N)
        for i in range(self.N):
            left=self.grid[self.generation%self.N, (i-1)%self.N]
            center=self.grid[self.generation%self.N, i]
            right=self.grid[self.generation%self.N, (i+1)%self.N]
            new_row[i]=self.rules.get((int(left),int(center),int(right)),0)
        self.generation+=1
        self.grid[self.generation%self.N]=new_row
    
    def think(self,sig,emb):
        self.total_bugs+=1; bt=sig.split(':')[0] if ':' in sig else sig
        self._step_automaton(emb)
        
        if self.patterns[bt]['total']<2:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                    'generation':self.generation,
                    'reasoning':f'Wolfram CA: Gen#{self.generation} — {bt} emergiert...'}
        
        # Komplexität: Anzahl lebender Zellen / Gesamt
        alive=np.sum(self.grid>0)
        complexity=alive/(self.N*self.N)
        rate=self.patterns[bt]['success']/max(1,self.patterns[bt]['total'])
        conf=min(1.0, rate*complexity)
        
        return {'action':'APPLY_PATTERN' if conf>0.2 else 'EXPLORE',
                'pattern':f'rule_{bt}','confidence':conf,
                'complexity':f'{complexity:.2f}','generation':self.generation,
                'alive_cells':int(alive),
                'reasoning':f'Wolfram: Gen#{self.generation} {bt} alive={alive} complexity={complexity:.2f}'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        self.patterns[bt]['total']+=1
        if success: self.patterns[bt]['success']+=1
    
    def stats(self):
        alive=np.sum(self.grid>0)
        return {'brain_type':'Cellular Automata (Wolfram)','total_bugs':self.total_bugs,
                'generation':self.generation,'grid':f'{self.N}×{self.N}',
                'alive':f'{alive}/{self.N*self.N}',
                'rule_set':'Rule-110-like (Turing-complete)'}
    def __repr__(self): return f"CABrain(gen={self.generation})"

if __name__=="__main__":
    print("GEHIRN BE — Wolfram Cellular Automata"); b=CellularAutomataBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(25):
        bt=['NullPointer','OffByOne','TypeError'][i%3]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<20,emb)
        if i%5==0: print(f"  Gen{i+1}: {dec['action']:15s} alive={dec.get('alive_cells','?')} complexity={dec.get('complexity','?')}")
    print(b.stats()); print("✅ Gehirn BE läuft.")
