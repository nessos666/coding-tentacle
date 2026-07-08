"""
GEHIRN BL — Homeostatic Brain
HÄLT ALLE INTERNEN METRIKEN IM GLEICHGEWICHT.
Wie der Körper: Temperatur, pH, Blutdruck — immer im Sollbereich.

Mathematik: ẋ = -k·(x - x_target)  (negative feedback)
           Homeostatic error = |x - x_target|

Autor: Hermes + David | Coding Tentacle 2026
"""
import numpy as np, math
from collections import defaultdict

class HomeostaticBrain:
    """Gehirn BL — Hält interne Metriken im Gleichgewicht."""
    def __init__(self):
        self.metrics={
            'success_rate': {'value':0.5, 'target':0.75, 'weight':0.2, 'min':0.1, 'max':1.0},
            'pattern_diversity': {'value':1.0, 'target':3.0, 'weight':0.15, 'min':1.0, 'max':10.0},
            'exploration_ratio': {'value':1.0, 'target':0.3, 'weight':0.2, 'min':0.05, 'max':0.8},
            'memory_utilization': {'value':0.0, 'target':0.6, 'weight':0.15, 'min':0.1, 'max':0.9},
            'response_time': {'value':1.0, 'target':0.5, 'weight':0.15, 'min':0.1, 'max':1.0},
            'confidence_calibration': {'value':0.5, 'target':0.8, 'weight':0.15, 'min':0.3, 'max':1.0},
        }
        self.patterns=defaultdict(lambda: {'success':0,'total':0})
        self.total_bugs=0; self.explored=0
    
    def _update_metrics(self, bt, success):
        """Alle Metriken aus aktuellen Daten ableiten"""
        # Success rate
        succs=sum(p['success'] for p in self.patterns.values())
        totals=sum(p['total'] for p in self.patterns.values())
        self.metrics['success_rate']['value']=succs/max(1,totals)
        # Pattern diversity
        self.metrics['pattern_diversity']['value']=len(self.patterns)
        # Exploration ratio
        self.metrics['exploration_ratio']['value']=self.explored/max(1,self.total_bugs)
        # Memory utilization
        self.metrics['memory_utilization']['value']=min(0.9, len(self.patterns)/20)
        # Confidence calibration: |confidence - success_rate|
        if self.patterns[bt]['total']>0:
            rate=self.patterns[bt]['success']/max(1,self.patterns[bt]['total'])
            self.metrics['confidence_calibration']['value']=rate
    
    def _homeostatic_error(self):
        """Gesamter Homeostase-Fehler"""
        err=0.0
        for name,m in self.metrics.items():
            deviation=(m['value']-m['target'])/max(abs(m['target']),0.01)
            err+=m['weight']*deviation**2
        return math.sqrt(err)
    
    def _homeostatic_action(self, bt):
        """Welche Aktion bringt die Metriken näher ans Ziel?"""
        # Wenn success_rate zu niedrig → mehr exploration
        if self.metrics['success_rate']['value']<0.5:
            self.explored+=1; return 'EXPLORE'
        # Wenn pattern_diversity zu niedrig → EXPLORE für neuen Typ
        if self.metrics['pattern_diversity']['value']<2.0 and self.patterns[bt]['total']>=3:
            return 'EXPLORE'
        # Wenn confidence_calibration gut → APPLY
        if self.metrics['confidence_calibration']['value']>0.5:
            return 'APPLY_PATTERN'
        return 'EXPLORE'
    
    def think(self,sig,emb):
        self.total_bugs+=1; bt=sig.split(':')[0] if ':' in sig else sig
        self._update_metrics(bt, self.patterns[bt]['success']/max(1,self.patterns[bt]['total'])>0.5 if self.patterns[bt]['total']>0 else False)
        
        homeo_err=self._homeostatic_error()
        
        if self.patterns[bt]['total']<1:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                    'homeostatic_error':f'{homeo_err:.3f}',
                    'reasoning':f'Homeostasis: {bt} neu. Metriken ausgleichen... (err={homeo_err:.3f})'}
        
        action=self._homeostatic_action(bt)
        rate=self.patterns[bt]['success']/max(1,self.patterns[bt]['total'])
        conf=rate
        
        return {'action':action,'pattern':f'homeo_{bt}','confidence':conf,
                'homeostatic_error':f'{homeo_err:.3f}',
                'metrics':{n:f'{m["value"]:.2f}' for n,m in self.metrics.items()},
                'reasoning':f'Homeostasis: {bt} err={homeo_err:.3f} → {action} (metrics in balance)'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        self.patterns[bt]['total']+=1
        if success: self.patterns[bt]['success']+=1
    
    def stats(self):
        return {'brain_type':'Homeostatic','total_bugs':self.total_bugs,
                'homeostatic_error':f'{self._homeostatic_error():.3f}',
                'metrics':{n:f'{m["value"]:.2f} (target={m["target"]})' for n,m in self.metrics.items()}}
    def __repr__(self): return f"HomeostaticBrain(err={self._homeostatic_error():.3f})"

if __name__=="__main__":
    print("GEHIRN BL — Homeostatic"); b=HomeostaticBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(25):
        bt=['NullPointer','OffByOne','TypeError'][i%3]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<20,emb)
        if i%5==0: print(f"  Bug{i+1}: {dec['action']:15s} err={dec.get('homeostatic_error','?')}")
    print(b.stats()); print("✅ Gehirn BL läuft.")
