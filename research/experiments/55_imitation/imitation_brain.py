"""
GEHIRN BB — Imitation Learning Brain
LERNT DURCH BEOBACHTUNG ANDERER BRAINS.
Demonstrationsspeicher → Policy-Extraktion → Generalisierung.
Kein eigenes Trial-and-Error nötig.

Mathematik: π_imit = argmin Σ ||π(s) - π_demo(s)||²
           Behavioral Cloning + DAgger

Autor: Hermes + David | Coding Tentacle 2026
"""
import numpy as np, math
from collections import defaultdict, deque

class ImitationBrain:
    """Gehirn BB — Lernt durch Beobachtung von Experten-Brains."""
    def __init__(self, lr=0.1):
        self.lr=lr
        self.demonstrations=deque(maxlen=100)  # (bug_type, pattern, success) von Experten
        self.policy=defaultdict(lambda: np.zeros(64))  # Gelernte Policy
        self.expert_weights=defaultdict(lambda: 0.5)  # Vertrauen in Experten
        self.patterns=defaultdict(lambda: {'success':0,'total':0,'imitated':0})
        self.total_bugs=0
    
    def observe_expert(self, bt, pat, success, emb):
        """Beobachte einen Experten-Fix und lerne daraus"""
        self.demonstrations.append((bt, pat, success, emb if emb else np.zeros(64)))
        if success:
            # Behavioral Cloning: Gewichte → Experten-Entscheidung
            e=np.array(emb)[:64] if len(emb)>=64 else np.pad(emb,(0,64-len(emb)))
            self.policy[bt]=self.policy[bt]*0.9+e*0.1
            self.expert_weights[bt]=min(1.0, self.expert_weights[bt]+0.1)
    
    def think(self,sig,emb):
        self.total_bugs+=1; bt=sig.split(':')[0] if ':' in sig else sig
        e=np.array(emb)[:64] if len(emb)>=64 else np.pad(emb,(0,64-len(emb)))
        
        if self.patterns[bt]['total']<1:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                    'reasoning':f'Imitation: {bt} keine Demonstration gesehen.'}
        
        # Policy ausführen: Ähnlichkeit zu gelernten Expert-Entscheidungen
        policy_emb=self.policy[bt]
        if np.linalg.norm(policy_emb)>0:
            sim=np.dot(e,policy_emb)/(np.linalg.norm(e)*np.linalg.norm(policy_emb)+1e-8)
        else:
            sim=0.0
        
        rate=self.patterns[bt]['success']/max(1,self.patterns[bt]['total'])
        expert_conf=self.expert_weights[bt]
        conf=min(1.0, sim*rate*expert_conf)
        
        return {'action':'APPLY_PATTERN' if conf>0.25 else 'EXPLORE',
                'pattern':f'imit_{bt}','confidence':conf,
                'expert_trust':f'{expert_conf:.2f}','sim':f'{sim:.2f}',
                'demonstrations':len(self.demonstrations),
                'reasoning':f'Imitation: {bt} sim={sim:.2f} expert_trust={expert_conf:.2f} conf={conf:.2f}'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        self.patterns[bt]['total']+=1
        if success: self.patterns[bt]['success']+=1
        # Auch eigenes Lernen zählt als Demonstration für andere
        if success and emb:
            self.observe_expert(bt, pat, success, emb)
            self.patterns[bt]['imitated']+=1
    
    def stats(self):
        return {'brain_type':'Imitation Learning','total_bugs':self.total_bugs,
                'demonstrations':len(self.demonstrations),
                'experts_trusted':{bt:f'{v:.2f}' for bt,v in self.expert_weights.items()},
                'patterns_imitated':sum(p['imitated'] for p in self.patterns.values())}
    def __repr__(self): return f"ImitationBrain(demos={len(self.demonstrations)})"

if __name__=="__main__":
    print("GEHIRN BB — Imitation Learning"); b=ImitationBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(25):
        bt=['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'][i%5]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<20,emb)
        if i%5==0: print(f"  Bug{i+1}: {dec['action']:15s} trust={dec.get('expert_trust','?')}")
    print(b.stats()); print("✅ Gehirn BB läuft.")
