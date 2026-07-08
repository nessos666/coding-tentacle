"""
GEHIRN AC — Swarm Intelligence / Particle Swarm Brain (Kennedy & Eberhart 1995)
Viele einfache Partikel erkunden parallel den Lösungsraum.
Schwarm-Intelligenz: Information fließt via globalem Bestwert.
Mathematik: v_i ← ω·v_i + c1·r1·(pbest_i - x_i) + c2·r2·(gbest - x_i)

Autor: Hermes + David | Coding Tentacle 2026
"""
import numpy as np, math, random
from collections import defaultdict

class Particle:
    def __init__(self, dim=32):
        self.pos=np.random.randn(dim)*0.5
        self.vel=np.random.randn(dim)*0.1
        self.best_pos=self.pos.copy()
        self.best_score=-999
    
    def update(self, omega, c1, c2, gbest_pos):
        r1,r2=random.random(),random.random()
        self.vel=omega*self.vel+c1*r1*(self.best_pos-self.pos)+c2*r2*(gbest_pos-self.pos)
        self.pos+=self.vel

class SwarmBrain:
    """Gehirn AC — Schwarm-Intelligenz: 20 Partikel explorieren parallel."""
    def __init__(self, n_particles=20, dim=32, omega=0.7, c1=1.5, c2=1.5):
        self.n=n_particles; self.dim=dim; self.omega=omega; self.c1=c1; self.c2=c2
        self.swarm=[Particle(dim) for _ in range(n_particles)]
        self.gbest_pos=np.zeros(dim); self.gbest_score=-999
        self.patterns=defaultdict(lambda: {'success':0,'total':0,'embedding':np.zeros(dim)})
        self.total_bugs=0
    
    def _evaluate(self, pos, emb):
        """Bewerte eine Position: Nähe zum Bug-Embedding"""
        e=np.array(emb)[:self.dim] if len(emb)>self.dim else np.pad(emb,(0,max(0,self.dim-len(emb))))
        return float(np.dot(pos, e)/(np.linalg.norm(pos)*np.linalg.norm(e)+1e-8))
    
    def think(self,sig,emb):
        self.total_bugs+=1
        bt=sig.split(':')[0] if ':' in sig else sig
        
        if bt in self.patterns and self.patterns[bt]['total']>=2:
            # Schwarm sucht beste Position (Fix)
            for particle in self.swarm:
                score=self._evaluate(particle.pos, emb)
                if score>particle.best_score:
                    particle.best_score=score; particle.best_pos=particle.pos.copy()
                if score>self.gbest_score:
                    self.gbest_score=score; self.gbest_pos=particle.pos.copy()
                particle.update(self.omega, self.c1, self.c2, self.gbest_pos)
            
            kp=self.patterns[bt]
            rate=kp['success']/kp['total']
            conf=min(1.0,rate*max(0,self.gbest_score))
            return {'action':'APPLY_PATTERN' if conf>0.3 else 'EXPLORE',
                    'pattern':f'swarm_{bt}','confidence':conf,
                    'swarm_best':self.gbest_score,
                    'reasoning':f'Swarm: {bt} gbest={self.gbest_score:.2f} conf={conf:.2f}'}
        return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                'reasoning':f'Swarm: {bt} unbekannt. Schwarm formiert...'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        self.patterns[bt]['total']+=1
        if success: self.patterns[bt]['success']+=1
        if emb:
            e=np.array(emb)[:self.dim] if len(emb)>self.dim else np.pad(emb,(0,max(0,self.dim-len(emb))))
            self.patterns[bt]['embedding']=self.patterns[bt]['embedding']*0.9+e*0.1
    
    def stats(self):
        return {'brain_type':'Swarm Intelligence','total_bugs':self.total_bugs,
                'particles':self.n,'global_best':f'{self.gbest_score:.3f}',
                'patterns':len(self.patterns)}
    def __repr__(self): return f"SwarmBrain(particles={self.n})"

if __name__=="__main__":
    print("GEHIRN AC — Swarm Intelligence"); b=SwarmBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(15):
        bt=['NullPointer','OffByOne','TypeError'][i%3]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<12,emb)
        if i%4==0: print(f"  Bug{i+1}: {dec['action']:15s} gbest={dec.get('swarm_best',0):.2f}")
    print(b.stats()); print("✅ Gehirn AC läuft.")
