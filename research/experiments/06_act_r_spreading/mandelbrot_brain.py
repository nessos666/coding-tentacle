"""
GEHIRN J — Mandelbrot Self-Similarity Brain
Mathematik: Fraktale Dimension, Hurst-Exponent, Power-Law, Selbstähnlichkeit auf Skalen
Autor: Hermes + David | Coding Tentacle Gehirn Bibliothek
"""

import time, math
import numpy as np
from collections import defaultdict

def hurst_exponent(series): 
    if len(series)<4: return 0.5
    s=np.array(series); n=len(s); y=np.cumsum(s-np.mean(s))
    r=np.max(y)-np.min(y); sd=np.std(s)
    if sd==0: return 0.5
    rs=r/sd; return math.log(rs)/math.log(n) if rs>0 else 0.5

def power_law_exponent(values):
    if len(values)<3: return 2.0
    x=np.sort([v for v in values if v>0])
    if len(x)<3: return 2.0
    n=len(x); ranks=np.arange(1,n+1)
    log_x=np.log(x); log_rank=np.log(ranks/(n+1))
    slope=-np.polyfit(log_x,log_rank,1)[0]
    return max(0.5,min(5.0,slope))

class MandelbrotBrain:
    """Gehirn J — Fraktale Selbstähnlichkeit auf allen Skalen."""
    def __init__(self, threshold=0.3):
        self.threshold=threshold
        self.scales={'line':{},'function':{},'class':{},'system':{}}
        self.bug_history=[]; self.total_bugs=0; self.scale_matches=0
    
    def think(self, bug_signature, bug_embedding):
        self.total_bugs+=1
        scale=self._extract_scale(bug_signature)
        bug_type=bug_signature.split(':')[0] if ':' in bug_signature else bug_signature
        candidates=[]
        for s_name,s_data in self.scales.items():
            for pname,(rate,cnt) in s_data.items():
                # Match: Bug-Typ im Pattern-Namen ODER Pattern-Name im Bug-Typ
                pn_lower=pname.lower(); bt_lower=bug_type.lower()
                # Breiterer Match: Bug-Typ TEIL des Pattern-Namens
                matched = (bt_lower in pn_lower or 
                          pn_lower in bt_lower or
                          any(part in pn_lower for part in bt_lower.split('_') if len(part)>2))
                if matched and rate>self.threshold and cnt>=1:
                    candidates.append((pname,rate,s_name,cnt))
        if not candidates:
            return {'action':'EXPLORE','pattern':None,'scale':scale,'confidence':0.0,
                    'reasoning':f'Kein selbstähnliches Pattern auf Skala {scale}.'}
        same=[c for c in candidates if c[2]==scale]
        chosen=max(same if same else candidates,key=lambda x:x[1])
        self.scale_matches+=1
        return {'action':'APPLY_PATTERN','pattern':chosen[0],'confidence':chosen[1],
                'scale':scale,'matched_scale':chosen[2],'cross_scale':scale!=chosen[2],
                'reasoning':f"Selbstähnlichkeit: '{chosen[0]}' Skala '{chosen[2]}' → '{scale}' (Rate={chosen[1]:.0%})"}
    
    def learn(self,bug_signature,pattern,success,embedding=None):
        scale=self._extract_scale(bug_signature)
        bug_type=bug_signature.split(':')[0] if ':' in bug_signature else bug_signature
        # Pattern mit Bug-Typ speichern: "NullPointer_guard_clause"
        full_pattern = f"{bug_type}_{pattern}"
        if full_pattern not in self.scales[scale]:
            self.scales[scale][full_pattern]=[0.5,1]
        rate,cnt=self.scales[scale][full_pattern]; cnt+=1
        rate=(rate*(cnt-1)+(1.0 if success else 0.0))/cnt
        self.scales[scale][full_pattern]=[rate,cnt]
        self.bug_history.append((bug_signature,pattern,success))
    
    def stats(self):
        tp=sum(len(s) for s in self.scales.values())
        ss=[1 if s else 0 for _,_,s in self.bug_history[-50:]]
        H=hurst_exponent(ss) if ss else 0.5
        bc=defaultdict(int)
        for sig,_,_ in self.bug_history: bc[sig.split(':')[0]]+=1
        alpha=power_law_exponent(list(bc.values())) if bc else 2.0
        trending="Trend" if H>0.55 else ("Mean-Reverting" if H<0.45 else "Random")
        tails="Schwere Tails" if alpha<2.5 else "Normal"
        return {'brain_type':'Mandelbrot Self-Similarity','total_bugs':self.total_bugs,
                'scale_matches':self.scale_matches,'total_patterns':tp,
                'hurst':f'{H:.2f} ({trending})','power_law':f'{alpha:.2f} ({tails})',
                'scales':{s:len(self.scales[s]) for s in self.scales}}
    
    def _extract_scale(self,sig):
        parts=sig.split(':')
        if len(parts)<2: return 'system'
        fp=parts[1]
        return 'function'
    
    def __repr__(self): s=self.stats(); return f"MandelbrotBrain(patterns={s['total_patterns']})"

if __name__=="__main__":
    print("="*60); print("GEHIRN J — Mandelbrot Self-Similarity — DEMO"); print("="*60)
    brain=MandelbrotBrain()
    bugs=[("NullPointer:pay.py:1","guard_clause",True),("NullPointer:auth.py:2","guard_clause",True),
          ("OffByOne:page.py:1","boundary_check",True),("NullPointer:order.py:3","guard_clause",True),
          ("TypeError:parse.py:1","type_convert",True),("NullPointer:user.py:4","guard_clause",True),
          ("MemoryLeak:cache.py:1","weakref",True),("NullPointer:email.py:5","try_except",False),
          ("OffByOne:list.py:2","boundary_check",True),("NullPointer:report.py:6","guard_clause",True)]
    for i,(sig,pattern,success) in enumerate(bugs):
        dec=brain.think(sig,[0.0]*384)
        print(f"Bug {i+1}: {sig[:40]} | {dec['action']:15s} | {dec['reasoning'][:55]}")
        brain.learn(sig,pattern,success)
    print(f"\n{'='*60}")
    for k,v in brain.stats().items(): print(f"  {k}: {v}")
    print(f"\n✅ Gehirn J läuft.")
