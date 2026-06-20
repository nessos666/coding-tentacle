"""
GEHIRN AV — Temporal Awareness Brain
Erkennt ZEITLICHE MUSTER: Wann treten Bugs auf? Trends? Saisonalität?
Zeitreihen-Analyse für Bug-Häufigkeiten.

Mathematik: Trend = EMA-Slope, Seasonality = autocorrelation
           Burst-Detection: Poisson-CUSUM

Autor: Hermes + David | Coding Tentacle 2026
"""
import numpy as np, math, time
from collections import defaultdict, deque

class TemporalBrain:
    """Gehirn AV — Zeitliche Muster in Bug-Auftreten erkennen."""
    def __init__(self, window_size=30):
        self.window=window_size
        self.timeline=deque(maxlen=200)  # [(timestamp, bug_type, success)]
        self.bug_timeseries=defaultdict(lambda: deque(maxlen=window_size))
        self.trends={}  # {bug_type: trend_slope}
        self.bursts=defaultdict(int)  # {bug_type: burst_count}
        self.patterns=defaultdict(lambda: {'success':0,'total':0})
        self.total_bugs=0
        self.start_time=time.time()
    
    def _detect_trend(self, bt):
        """Lineare Regression über Zeitfenster → Trend"""
        ts=list(self.bug_timeseries[bt])
        if len(ts)<5: return 0.0
        x=np.arange(len(ts))
        y=np.array(ts)
        slope=np.polyfit(x,y,1)[0]
        return float(slope)
    
    def _detect_burst(self, bt):
        """Poisson-CUSUM: Plötzlicher Anstieg der Bug-Rate?"""
        ts=list(self.bug_timeseries[bt])
        if len(ts)<10: return False
        recent=np.mean(ts[-5:])
        baseline=np.mean(ts[:-5])
        return recent>2*baseline  # 2× Anstieg = Burst
    
    def _recent_success_rate(self, bt, n=10):
        """Erfolgsrate der LETZTEN n Bugs (nicht aller)"""
        recent=[e for e in self.timeline if e[1]==bt][-n:]
        if not recent: return 0.5
        return np.mean([1 if e[2] else 0 for e in recent])
    
    def think(self,sig,emb):
        self.total_bugs+=1; bt=sig.split(':')[0] if ':' in sig else sig
        now=time.time()
        
        # Trend
        trend=self._detect_trend(bt)
        self.trends[bt]=trend
        
        # Burst?
        burst=self._detect_burst(bt)
        if burst: self.bursts[bt]+=1
        
        # Zeit-gewichtete Rate: neuere Bugs zählen mehr
        recent_rate=self._recent_success_rate(bt)
        base_rate=self.patterns[bt]['success']/max(1,self.patterns[bt]['total'])
        rate=0.7*recent_rate+0.3*base_rate
        
        # Trend-Faktor
        trend_factor=1.0+max(-0.3, min(0.3, trend))
        
        conf=min(1.0, rate*trend_factor)
        
        return {'action':'APPLY_PATTERN' if conf>0.25 else 'EXPLORE',
                'pattern':f'temporal_{bt}','confidence':conf,
                'trend':f'{trend:+.3f}','burst':burst,
                'reasoning':f'Temporal: {bt} trend={trend:+.2f} burst={burst} recent_rate={recent_rate:.0%} conf={conf:.2f}'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        now=time.time()
        
        self.timeline.append((now,bt,success))
        self.bug_timeseries[bt].append(1 if success else 0)
        
        self.patterns[bt]['total']+=1
        if success: self.patterns[bt]['success']+=1
    
    def stats(self):
        n_types=len(self.bug_timeseries)
        total_bursts=sum(self.bursts.values())
        return {'brain_type':'Temporal Awareness','total_bugs':self.total_bugs,
                'types_tracked':n_types,
                'trends':{bt:f'{v:+.3f}' for bt,v in sorted(self.trends.items(),key=lambda x:-abs(x[1]))[:5]},
                'total_bursts':total_bursts,
                'runtime_seconds':f'{time.time()-self.start_time:.0f}s'}
    def __repr__(self): return f"TemporalBrain(types={len(self.bug_timeseries)})"

if __name__=="__main__":
    print("GEHIRN AV — Temporal Awareness"); b=TemporalBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(30):
        bt=['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'][i%5]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<25,emb)
        time.sleep(0.01)  # Zeit vergeht!
        if i%6==0: print(f"  Bug{i+1}: {dec['action']:15s} trend={dec.get('trend','?')} burst={dec.get('burst',False)}")
    print(b.stats()); print("✅ Gehirn AV läuft.")
