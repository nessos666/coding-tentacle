"""
GEHIRN BD — Strategic Forgetting Brain
VERGISST AKTIV. Nicht nur Decay — strategisches Löschen.
Kriterien: Alter, Nutzlosigkeit, Redundanz, Schädlichkeit.

Strategien:
  1. Least-Recently-Used (LRU) — am längsten nicht genutzt → löschen
  2. Low-Utility — Erfolgsrate < Schwelle → löschen
  3. Redundancy — zu ähnlich zu anderem Pattern → mergen
  4. Age-based — zu alt ohne Bestätigung → löschen
  5. Capacity-bound — Speicher voll → schlechtestes löschen

Mathematik: Retention-Score = α·recency + β·utility + γ·uniqueness - δ·age

Autor: Hermes + David | Coding Tentacle 2026
"""
import numpy as np, math, time
from collections import defaultdict, OrderedDict

class StrategicForgettingBrain:
    """Gehirn BD — Aktives, strategisches Vergessen."""
    def __init__(self, max_memory=50, retention_alpha=0.4, retention_beta=0.4, retention_gamma=0.2, age_delta=0.01):
        self.max_memory=max_memory
        self.alpha=retention_alpha; self.beta=retention_beta; self.gamma=retention_gamma
        self.delta=age_delta
        
        self.memory=OrderedDict()  # {sig: (pattern, success, last_access, utility, embedding)}
        self.patterns=defaultdict(lambda: {'success':0,'total':0})
        self.forgotten=[]  # Was wurde gelöscht?
        self.total_bugs=0
    
    def _retention_score(self, sig, data):
        """Score: α·recency + β·utility + γ·uniqueness - δ·age"""
        pat, succ, last_acc, utility, emb=data
        # Recency: je kürzer her, desto höher
        recency=1.0/(1.0+(time.time()-last_acc)/3600.0)
        # Utility: Erfolgsrate
        p=self.patterns.get(sig.split(':')[0])
        utility_score=utility if p and p['total']>0 else 0.5
        # Uniqueness: wie einzigartig ist das Embedding?
        uniqueness=1.0  # Default
        if emb is not None:
            similarities=[]
            for other_sig,other_data in self.memory.items():
                if other_sig!=sig and other_data[4] is not None:
                    sim=np.dot(emb,other_data[4])/(np.linalg.norm(emb)*np.linalg.norm(other_data[4])+1e-8)
                    similarities.append(sim)
            if similarities:
                uniqueness=1.0-max(similarities)  # Einzigartig = keiner ist ähnlich
        # Age-Penalty
        age_penalty=self.delta*(time.time()-last_acc)/3600.0
        
        return self.alpha*recency+self.beta*utility_score+self.gamma*uniqueness-age_penalty
    
    def _prune(self):
        """Strategisches Vergessen: lösche schlechteste Einträge"""
        if len(self.memory)<=self.max_memory: return
        
        # Bewerte alle Einträge
        scores={sig:self._retention_score(sig, data) for sig,data in self.memory.items()}
        # Sortiere nach Score (niedrigste zuerst)
        sorted_items=sorted(scores.items(), key=lambda x:x[1])
        
        # Anzahl zu löschender Einträge
        to_remove=len(self.memory)-self.max_memory
        
        for sig,score in sorted_items[:to_remove]:
            self.forgotten.append({'sig':sig,'score':score,'time':time.time()})
            del self.memory[sig]
    
    def think(self,sig,emb):
        self.total_bugs+=1; bt=sig.split(':')[0] if ':' in sig else sig
        
        # Ähnlichste Erinnerung finden
        best_sig,best_sim=None,0
        e=np.array(emb)
        for msig,mdata in self.memory.items():
            if mdata[4] is not None:
                sim=np.dot(e,mdata[4])/(np.linalg.norm(e)*np.linalg.norm(mdata[4])+1e-8)
                if sim>best_sim: best_sim=sim; best_sig=msig
        
        if best_sig and best_sim>0.3:
            data=self.memory[best_sig]
            self.memory.move_to_end(best_sig)  # LRU: als kürzlich genutzt markieren
            data=(data[0],data[1],time.time(),data[3],data[4])  # Update last_access
            self.memory[best_sig]=data
            
            rate=self.patterns[bt]['success']/max(1,self.patterns[bt]['total'])
            conf=min(1.0, rate*best_sim)
            
            return {'action':'APPLY_PATTERN' if conf>0.25 else 'EXPLORE',
                    'pattern':data[0],'confidence':conf,
                    'memory_used':f'{len(self.memory)}/{self.max_memory}',
                    'forgotten':len(self.forgotten),
                    'reasoning':f'Forgetting: {data[0]} (sim={best_sim:.2f}) mem={len(self.memory)}/{self.max_memory}'}
        return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                'memory_used':f'{len(self.memory)}/{self.max_memory}',
                'reasoning':f'Forgetting: Keine Erinnerung. Lerne neu.'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        self.patterns[bt]['total']+=1
        if success: self.patterns[bt]['success']+=1
        
        if emb:
            e=np.array(emb)
            self.memory[sig]=(pat, success, time.time(), 1.0 if success else 0.3, e)
            self.memory.move_to_end(sig)
            self._prune()  # Strategisch vergessen
    
    def stats(self):
        return {'brain_type':'Strategic Forgetting','total_bugs':self.total_bugs,
                'memory':f'{len(self.memory)}/{self.max_memory}',
                'forgotten':len(self.forgotten),
                'retention_formula':f'α·recency + β·utility + γ·uniqueness - δ·age'}
    def __repr__(self): return f"ForgettingBrain(mem={len(self.memory)}/{self.max_memory}, lost={len(self.forgotten)})"

if __name__=="__main__":
    print("GEHIRN BD — Strategic Forgetting"); b=StrategicForgettingBrain(max_memory=15)
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(30):
        bt=['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'][i%5]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<25,emb)
        if i%6==0: print(f"  Bug{i+1}: {dec['action']:15s} mem={dec.get('memory_used','?')} lost={dec.get('forgotten',0)}")
    print(b.stats()); print("✅ Gehirn BD läuft.")
