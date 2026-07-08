"""
GEHIRN L — Genetischer Algorithmus Brain (Holland 1975) v3
FIX: Nischen-Erhaltung gegen Monokultur. Bug-Typ+Pattern getrennt.
Autor: Hermes + David | Coding Tentacle Gehirn Bibliothek
"""
import random, math, numpy as np
from collections import defaultdict

class GeneticBrain:
    def __init__(self, pop_size=30, mutation_rate=0.15, elite_size=5):
        self.pop_size=pop_size; self.mutation_rate=mutation_rate; self.elite_size=elite_size
        self.population=[]; self.total_bugs=0; self.generation=0
    
    def think(self,sig,emb):
        self.total_bugs+=1
        bt=sig.split(':')[0] if ':' in sig else sig
        candidates=[p for p in self.population if p[0].lower()==bt.lower()]
        if not candidates:
            candidates=[p for p in self.population if bt.lower() in p[0].lower() or p[0].lower() in bt.lower()]
        if not candidates:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                    'reasoning':f'Kein evolviertes Pattern für {bt}. Pop:{len(self.population)}'}
        best=max(candidates,key=lambda x:x[2])
        conf=min(1.0,best[2]/10)
        return {'action':'APPLY_PATTERN' if conf>0.2 else 'EXPLORE','pattern':best[1],
                'confidence':conf,'fitness':best[2],'generation':best[3],
                'reasoning':f"Evolviert: {best[0]}→{best[1]} Fit={best[2]:.1f}"}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        for i,(pbt,ppat,pfit,pgen) in enumerate(self.population):
            if pbt==bt and ppat==pat:
                new_fit=pfit+(2.0 if success else -0.3)
                self.population[i]=(bt,pat,max(0.1,new_fit),pgen)
                break
        else:
            self.population.append((bt,pat,1.0 if success else 0.3,self.generation))
        if self.total_bugs%15==0 and len(self.population)>=5:
            self._evolve()
    
    def _evolve(self):
        self.generation+=1
        pop=sorted(self.population,key=lambda x:-x[2])
        elite=pop[:self.elite_size]
        new_pop=list(elite)
        # Nischen-Erhaltung: mindestens 1 pro Bug-Typ aus der Gesamtpopulation
        seen_types=set(p[0] for p in elite)
        for p in pop:
            if p[0] not in seen_types and len(new_pop)<self.pop_size:
                new_pop.append(p); seen_types.add(p[0])
        # Crossover + Mutation
        while len(new_pop)<self.pop_size:
            a=random.choice(pop[:max(3,len(pop)//2)])
            b=random.choice(pop[:max(3,len(pop)//2)])
            child_bt=b[0] if random.random()<0.5 else a[0]
            child_pat=b[1] if random.random()<0.5 else a[1]
            child_fit=(a[2]+b[2])/2
            if random.random()<self.mutation_rate:
                child_fit+=random.uniform(-1.5,1.5)
                if random.random()<0.15:
                    all_types=list(set(p[0] for p in self.population))
                    if all_types: child_bt=random.choice(all_types)
            new_pop.append((child_bt,child_pat,max(0.1,child_fit),self.generation))
        self.population=new_pop[:self.pop_size]
    
    def stats(self):
        n=len(self.population)
        best=max(self.population,key=lambda x:x[2]) if self.population else ('?','?',0,0)
        bt_counts={}
        for p in self.population:
            bt_counts[p[0]]=bt_counts.get(p[0],0)+1
        return {'brain_type':'Genetic Algorithm v3','total_bugs':self.total_bugs,
                'population':n,'generation':self.generation,
                'best':f'{best[0]}→{best[1]} fit={best[2]:.1f}',
                'diversity':bt_counts}
    def __repr__(self): return f"GeneticBrain(pop={len(self.population)},gen={self.generation})"

if __name__=="__main__":
    print("GEHIRN L v3 — Genetischer Algorithmus")
    b=GeneticBrain()
    bugs=[("NullPointer:pay.py:1","guard_clause",True),("NullPointer:auth.py:2","guard_clause",True),
          ("OffByOne:page.py:1","boundary_check",True),("NullPointer:order.py:3","guard_clause",True),
          ("TypeError:parse.py:1","type_convert",True),("NullPointer:user.py:4","guard_clause",True),
          ("MemoryLeak:cache.py:1","weakref",True),("NullPointer:email.py:5","try_except",False)]
    for i,(sig,pat,ok) in enumerate(bugs):
        dec=b.think(sig,[0]*384)
        print(f"  Bug{i+1}: {dec['action']:15s} fit={dec.get('fitness',0):.1f}")
        b.learn(sig,pat,ok)
    print(b.stats()); print("✅ Gehirn L v3 läuft.")
