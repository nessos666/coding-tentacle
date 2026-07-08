"""
GEHIRN V — Memory Palace Brain (Method of Loci)
Räumliches Gedächtnis: Bug-Patterns in virtuellem 2D-Raum gespeichert.
Ähnliche Bugs = räumlich nah. Abruf via "geistiger Spaziergang".
Mathematik: Position = f(embedding) via 2D-Projektion. Retrieval = KNN im Raum.

Autor: Hermes + David | Coding Tentacle Gehirn Bibliothek
"""
import numpy as np, math
from collections import defaultdict

class MemoryPalaceBrain:
    """Gehirn V — Räumliches Gedächtnis. Patterns im 2D-Raum verankert."""
    def __init__(self, grid_size=20):
        self.grid_size=grid_size
        self.palace={}  # {(x,y): (bug_type, pattern, success_count, total)}
        self.embedding_cache={}
        self.total_bugs=0
        self._init_grid()
    
    def _init_grid(self):
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                self.palace[(x,y)]=None
    
    def _embed_to_pos(self, emb):
        e=np.array(emb)
        # PCA-ähnliche Reduktion auf 2D
        x=int((np.mean(e[:128])+1)*self.grid_size/2)%self.grid_size if len(e)>0 else 0
        y=int((np.mean(e[128:256])+1)*self.grid_size/2)%self.grid_size if len(e)>128 else 0
        return (x,y)
    
    def think(self,sig,emb):
        self.total_bugs+=1
        pos=self._embed_to_pos(emb)
        # Suche im Umkreis (räumliche Nähe = semantische Nähe)
        candidates=[]
        for dx in range(-2,3):
            for dy in range(-2,3):
                nx,ny=(pos[0]+dx)%self.grid_size,(pos[1]+dy)%self.grid_size
                cell=self.palace.get((nx,ny))
                if cell:
                    bt,pat,succ,tot=cell
                    if tot>0:
                        rate=succ/tot
                        dist=math.sqrt(dx*dx+dy*dy)
                        score=rate/(1+dist)
                        if score>0.3: candidates.append((pat,score,dist,bt))
        if not candidates:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,'position':pos,
                    'reasoning':f'Palast-Position {pos} leer. Nichts im Umkreis.'}
        best=max(candidates,key=lambda x:x[1])
        return {'action':'APPLY_PATTERN','pattern':best[0],'confidence':best[1],
                'position':pos,'distance':best[2],'source_type':best[3],
                'reasoning':f"Palast: {best[0]} bei Distanz {best[2]:.1f} (Score={best[1]:.2f})"}
    
    def learn(self,sig,pat,success,emb=None):
        if emb is None: return
        pos=self._embed_to_pos(emb)
        cell=self.palace.get(pos)
        if cell:
            bt,p,succ,tot=cell
            self.palace[pos]=(bt,pat,succ+(1 if success else 0),tot+1)
        else:
            bt=sig.split(':')[0] if ':' in sig else sig
            self.palace[pos]=(bt,pat,1 if success else 0,1)
    
    def stats(self):
        occupied=sum(1 for v in self.palace.values() if v is not None)
        return {'brain_type':'Memory Palace (Method of Loci)','total_bugs':self.total_bugs,
                'occupied_positions':f'{occupied}/{self.grid_size*self.grid_size}',
                'density':f'{occupied/(self.grid_size*self.grid_size):.1%}'}
    def __repr__(self): return f"MemoryPalace(occupied={sum(1 for v in self.palace.values() if v is not None)})"

if __name__=="__main__":
    print("GEHIRN V — Memory Palace"); b=MemoryPalaceBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(15):
        bt=['NullPointer','OffByOne','TypeError'][i%3]
        emb=m.encode(f"{bt} error bug").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<12,emb)
        if i%4==0: print(f"  Bug{i+1}: {dec['action']:15s} pos={dec.get('position','?')}")
    print(b.stats()); print("✅ Gehirn V läuft.")
