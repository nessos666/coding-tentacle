"""
GEHIRN BP — Human-Collaboration Brain
ARBEITET MIT DEM ENTWICKLER ZUSAMMEN. Nicht autonom — partizipativ.
4 Modi: Assistive, Advisory, Co-Creative, Agentic.

Mathematik: Decision = α·human_judgment + (1-α)·brain_judgment
           α = trust_level (steigt mit Übereinstimmung)

Autor: Hermes + David | Coding Tentacle 2026
Quelle: 6 AI-Human Collaboration Models (Augment Code, 2026)
"""
import numpy as np, math
from collections import defaultdict

class HumanCollabBrain:
    """Gehirn BP — Mensch-Maschine-Kollaboration."""
    def __init__(self):
        self.mode='advisory'  # assistive/advisory/co_creative/agentic
        self.trust=0.5  # Vertrauen des Brain in den Menschen
        self.agreement_history=[]  # Wie oft stimmten Brain + Mensch überein?
        self.human_overrides=0
        self.brain_suggestions=0
        self.patterns=defaultdict(lambda: {'success':0,'total':0,'human_label':None})
        self.total_bugs=0
    
    def _update_trust(self, agreed):
        if agreed:
            self.trust=min(1.0, self.trust+0.05)
        else:
            self.trust=max(0.2, self.trust-0.1)
        self.agreement_history.append(agreed)
    
    def _collaboration_weight(self):
        """Wie stark gewichten wir Brain vs Human?"""
        if self.mode=='assistive':
            return 0.2  # Meistens Mensch
        elif self.mode=='advisory':
            return 0.5*self.trust  # Ausgewogen
        elif self.mode=='co_creative':
            return 0.7  # Mehr Brain
        elif self.mode=='agentic':
            return 0.9  # Meistens Brain
        return 0.5
    
    def think(self,sig,emb):
        self.total_bugs+=1; bt=sig.split(':')[0] if ':' in sig else sig
        
        if self.patterns[bt]['total']<1:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                    'mode':self.mode,
                    'reasoning':f'Collab: {bt} neu. Frage Entwickler...'}
        
        p=self.patterns[bt]
        rate=p['success']/max(1,p['total'])
        human_label=p.get('human_label')
        
        # Brain-Vorschlag
        brain_conf=rate
        # Human-Label (wenn vorhanden)
        human_conf=1.0 if human_label and p['total']>0 and p['success']/p['total']>0.5 else 0.5
        
        # Kollaborations-Gewichtung
        alpha=self._collaboration_weight()
        conf=alpha*brain_conf+(1-alpha)*human_conf
        
        self.brain_suggestions+=1
        
        return {'action':'APPLY_PATTERN' if conf>0.3 else 'EXPLORE',
                'pattern':f'collab_{bt}','confidence':conf,
                'mode':self.mode,'trust':f'{self.trust:.2f}','alpha':f'{alpha:.2f}',
                'agreement_rate':f'{np.mean(self.agreement_history[-20:]):.0%}' if self.agreement_history else 'N/A',
                'reasoning':f'Collab({self.mode}): br={brain_conf:.0%} hu={human_conf:.0%} α={alpha:.2f} → {conf:.2f}'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        self.patterns[bt]['total']+=1
        if success: self.patterns[bt]['success']+=1
    
    def human_feedback(self, bt, label, agreed):
        """Entwickler gibt Feedback"""
        self.patterns[bt]['human_label']=label
        self._update_trust(agreed)
        if not agreed: self.human_overrides+=1
    
    def stats(self):
        return {'brain_type':'Human-Collaboration','total_bugs':self.total_bugs,
                'mode':self.mode,'trust':f'{self.trust:.2f}',
                'agreement':f'{np.mean(self.agreement_history[-20:]):.0%}' if self.agreement_history else 'N/A',
                'human_overrides':self.human_overrides}
    def __repr__(self): return f"HumanCollabBrain(mode={self.mode}, trust={self.trust:.2f})"

if __name__=="__main__":
    print("GEHIRN BP — Human-Collaboration"); b=HumanCollabBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(20):
        bt=['NullPointer','OffByOne','TypeError'][i%3]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<16,emb)
        # Simulierter Entwickler ist meist einverstanden
        b.human_feedback(bt, f"fix_{bt}", i<18)
        if i%5==0: print(f"  Bug{i+1}: {dec['action']:15s} trust={dec.get('trust','?')} α={dec.get('alpha','?')}")
    print(b.stats()); print("✅ Gehirn BP läuft.")
