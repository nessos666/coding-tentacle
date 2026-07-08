"""
GEHIRN BO — Emotion/Affect Brain
MODELLIERT EMOTIONEN: Frustration, Zufriedenheit, Neugier, Langeweile.
Emotionen beeinflussen Entscheidungen: Frustriert → mehr Exploration.
Affective Computing (2025): "Emotion is necessary for AGI."

Mathematik: Frustration(t) = Σ(1-success_i)·decay^(t-i)
           Zufriedenheit = 1 - Frustration
           Emotionaler Zustand = f(Frust, Zufrieden, Neugier, Langeweile)

Autor: Hermes + David | Coding Tentacle 2026
Quelle: Artificial Emotion Survey (arXiv 2508.10286, 2025)
"""
import numpy as np, math
from collections import deque

class EmotionBrain:
    """Gehirn BO — Emotionen beeinflussen Bug-Fixing-Strategie."""
    def __init__(self, decay=0.9):
        self.decay=decay
        self.emotions={'frustration':0.0,'satisfaction':0.5,'curiosity':0.3,'boredom':0.0,'confidence':0.5,'anxiety':0.1}
        self.history=deque(maxlen=30)
        self.patterns={}
        self.total_bugs=0
    
    def _update_emotions(self, bt, success):
        self.history.append(success)
        recent=list(self.history)
        
        # Frustration: gleitende Summe der Misserfolge
        fails=sum(1 for s in recent if not s)
        weight=sum(self.decay**(len(recent)-i-1) for i in range(len(recent)))
        self.emotions['frustration']=min(1.0, fails*weight/max(1,len(recent)))
        # Satisfaction
        self.emotions['satisfaction']=1.0-self.emotions['frustration']
        # Curiosity: Neuheits-gesteuert
        self.emotions['curiosity']=max(0.1, self.emotions['curiosity']*0.95+(0.5 if not success else 0.1))
        # Boredom: zu viele gleiche Bugs in Folge
        if len(recent)>=5 and all(recent[-5:]):
            self.emotions['boredom']=min(1.0, self.emotions['boredom']+0.1)
        else:
            self.emotions['boredom']=max(0.0, self.emotions['boredom']-0.15)  # Schnellerer Abbau
        # Confidence
        if success: self.emotions['confidence']=min(1.0, self.emotions['confidence']+0.1)
        else: self.emotions['confidence']=max(0.1, self.emotions['confidence']-0.15)
    
    def _emotional_decision(self, bt, base_rate):
        """Emotionen modifizieren die Entscheidung"""
        e=self.emotions
        # ZUERST: Wenn hohe Konfidenz + Erfolgsrate → direkt anwenden
        if e['confidence']>0.6 and base_rate>0.5:
            return 'APPLY_PATTERN', base_rate*1.1
        if e['frustration']>0.7:
            return 'EXPLORE', base_rate*0.5
        if e['boredom']>0.8:
            return 'EXPLORE', base_rate*0.4
        if e['anxiety']>0.6:
            return 'EXPLORE', base_rate*0.3
        return 'APPLY_PATTERN' if base_rate>0.25 else 'EXPLORE', base_rate
    
    def think(self,sig,emb):
        self.total_bugs+=1; bt=sig.split(':')[0] if ':' in sig else sig
        
        if bt not in self.patterns:
            self.patterns[bt]={'success':0,'total':0}
        
        p=self.patterns[bt]
        rate=p['success']/max(1,p['total']) if p['total']>0 else 0.3
        action,conf=self._emotional_decision(bt, rate)
        
        return {'action':action,'pattern':f'emotion_{bt}','confidence':conf,
                'emotions':{k:f'{v:.2f}' for k,v in self.emotions.items()},
                'dominant_emotion':max(self.emotions,key=self.emotions.get),
                'reasoning':f'Emotion: {bt} {"😤" if self.emotions["frustration"]>0.5 else "😊"} '
                           f'Frust={self.emotions["frustration"]:.2f} Conf={self.emotions["confidence"]:.2f}'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        if bt not in self.patterns: self.patterns[bt]={'success':0,'total':0}
        self.patterns[bt]['total']+=1
        if success: self.patterns[bt]['success']+=1
        self._update_emotions(bt, success)
    
    def stats(self):
        return {'brain_type':'Emotion/Affect','total_bugs':self.total_bugs,
                'dominant_emotion':max(self.emotions,key=self.emotions.get),
                'emotional_state':{k:f'{v:.2f}' for k,v in self.emotions.items()}}
    def __repr__(self): return f"EmotionBrain({max(self.emotions,key=self.emotions.get)}={self.emotions[max(self.emotions,key=self.emotions.get)]:.2f})"

if __name__=="__main__":
    print("GEHIRN BO — Emotion/Affect"); b=EmotionBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(25):
        bt=['NullPointer','OffByOne','TypeError'][i%3]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<20 or i%3==0,emb)
        if i%5==0: print(f"  Bug{i+1}: {dec['action']:15s} {dec['reasoning'][:60]}")
    print(b.stats()); print("✅ Gehirn BO läuft.")
