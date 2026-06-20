"""
GEHIRN AX — Brain Mesh / Multi-Brain Communication
Gehirne kommunizieren miteinander via Message-Passing-Protokoll.
Jedes Brain kann andere Brains um Rat fragen.
Shared Knowledge Pool für Cross-Brain-Learning.

Protokoll:
  REQUEST(bug_type, embedding) → RESPONSE(pattern, confidence, reasoning)
  BROADCAST(learning_update) → alle Brains lernen mit

Autor: Hermes + David | Coding Tentacle 2026
"""
import numpy as np, math
from collections import defaultdict

class BrainMesh:
    """Gehirn AX — Ermöglicht Kommunikation zwischen beliebigen Sub-Brains."""
    def __init__(self, sub_brains=None):
        self.sub_brains=sub_brains or {}  # {name: brain_instance}
        self.message_log=[]  # Alle Nachrichten
        self.knowledge_pool=defaultdict(lambda: {'votes':defaultdict(int),'total':0})
        self.total_bugs=0
        self.trust_scores=defaultdict(lambda: 0.5)  # {brain_name: trust}
    
    def add_brain(self, name, brain):
        self.sub_brains[name]=brain
    
    def _query_all(self, sig, emb):
        """REQUEST an alle Brains — sammle Antworten"""
        responses={}
        for name,brain in self.sub_brains.items():
            try:
                resp=brain.think(sig, emb)
                responses[name]=resp
                self.message_log.append(('REQUEST',name,resp.get('action','?')))
            except:
                responses[name]={'action':'ERROR','confidence':0.0}
        return responses
    
    def _aggregate_responses(self, responses):
        """Gewichtete Aggregation aller Brain-Antworten"""
        votes=defaultdict(float)
        total_weight=0
        
        for name,resp in responses.items():
            if resp['action']=='APPLY_PATTERN' and 'pattern' in resp:
                trust=self.trust_scores[name]
                weight=resp.get('confidence',0.5)*trust
                votes[resp['pattern']]+=weight
                total_weight+=weight
        
        if not votes:
            return None, 0.0
        
        best=max(votes,key=votes.get)
        conf=votes[best]/max(total_weight,0.001)
        return best, conf
    
    def _broadcast_learn(self, sig, pat, success, emb):
        """BROADCAST: Alle Brains lernen aus DER EINEN Erfahrung"""
        for name,brain in self.sub_brains.items():
            try:
                brain.learn(sig, pat, success, emb)
                self.message_log.append(('BROADCAST',name,'learned'))
            except:
                try: brain.learn(sig, pat, success)
                except: pass
    
    def _update_trust(self, responses, success):
        """Trust-Scores basierend auf Korrektheit updaten"""
        for name,resp in responses.items():
            if resp['action']=='APPLY_PATTERN' and success:
                self.trust_scores[name]=min(1.0, self.trust_scores[name]+0.05)
            elif resp['action']=='APPLY_PATTERN' and not success:
                self.trust_scores[name]=max(0.1, self.trust_scores[name]-0.03)
    
    def think(self,sig,emb):
        self.total_bugs+=1; bt=sig.split(':')[0] if ':' in sig else sig
        
        if not self.sub_brains:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                    'reasoning':'Mesh: Keine Brains angeschlossen.'}
        
        # Alle Brains befragen
        responses=self._query_all(sig, emb)
        best_pat, conf=self._aggregate_responses(responses)
        
        if best_pat:
            voters=[n for n,r in responses.items() if r.get('pattern')==best_pat]
            return {'action':'APPLY_PATTERN' if conf>0.25 else 'EXPLORE',
                    'pattern':best_pat,'confidence':conf,
                    'voters':len(voters),'total_brains':len(self.sub_brains),
                    'top_trust':max(self.trust_scores.items(),key=lambda x:x[1])[0],
                    'reasoning':f'Mesh: {best_pat} ({len(voters)}/{len(self.sub_brains)} brains) conf={conf:.2f}'}
        return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                'reasoning':'Mesh: Kein Konsens.'}
    
    def learn(self,sig,pat,success,emb=None):
        # Erst selbst lernen (via Knowledge Pool)
        bt=sig.split(':')[0] if ':' in sig else sig
        self.knowledge_pool[bt]['votes'][pat]+=1
        self.knowledge_pool[bt]['total']+=1
        
        # Broadcast an alle Sub-Brains
        if emb:
            self._broadcast_learn(sig, pat, success, emb)
        
        # Trust updaten
        responses=self._query_all(sig, emb) if emb else {}
        self._update_trust(responses, success)
    
    def stats(self):
        n_brains=len(self.sub_brains)
        n_msgs=len(self.message_log)
        return {'brain_type':'Brain Mesh (Multi-Brain Communication)',
                'total_bugs':self.total_bugs,'connected_brains':n_brains,
                'messages':n_msgs,
                'trust_scores':{n:f'{v:.2f}' for n,v in sorted(self.trust_scores.items(),key=lambda x:-x[1])[:5]},
                'knowledge_pool_entries':len(self.knowledge_pool)}
    def __repr__(self): return f"BrainMesh(brains={len(self.sub_brains)})"

if __name__=="__main__":
    print("GEHIRN AX — Brain Mesh (Multi-Brain)")
    import sys
    sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/01_bayesian'); from bayesian_brain import BayesianBrain
    sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/11_hebbian'); from hebbian_brain import HebbianBrain
    sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/16_game_theory'); from game_theory_brain import GameTheoryBrain
    
    b=BrainMesh()
    b.add_brain('Bayesian',BayesianBrain()); b.add_brain('Hebbian',HebbianBrain()); b.add_brain('GameTheory',GameTheoryBrain())
    
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(20):
        bt=['NullPointer','OffByOne','TypeError'][i%3]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<16,emb)
        if i%5==0: print(f"  Bug{i+1}: {dec['action']:15s} voters={dec.get('voters',0)}/{dec.get('total_brains',0)}")
    print(b.stats()); print("✅ Gehirn AX läuft.")
