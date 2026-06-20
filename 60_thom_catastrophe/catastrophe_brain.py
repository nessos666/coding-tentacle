"""
GEHIRN BG — René Thom Catastrophe Theory Brain
PLÖTZLICHE SPRÜNGE IN STETIGEN SYSTEMEN.
7 elementare Katastrophen: Fold, Cusp, Swallowtail, Butterfly,
Hyperbolic/Umbilic, Elliptic/Umbilic, Parabolic/Umbilic.

Mathematik: V(x; a,b) = x⁴ + a·x² + b·x  (Cusp-Katastrophe)
           Bifurkationsmenge: 4a³ + 27b² = 0

Autor: Hermes + David | Coding Tentacle 2026
Quelle: Thom "Structural Stability and Morphogenesis" (1972)
"""
import numpy as np, math
from collections import defaultdict

class CatastropheBrain:
    """Gehirn BG — Erkennt plötzliche Sprünge/Phasenübergänge (Thom)."""
    def __init__(self):
        # Cusp-Katastrophen-Parameter pro Bug-Typ
        self.a=defaultdict(lambda: 0.0)  # Normal-Faktor
        self.b=defaultdict(lambda: 0.0)  # Splitting-Faktor
        self.catastrophe_points=[]  # Wo sprangen Systeme?
        self.patterns=defaultdict(lambda: {'success':0,'total':0,'history':[]})
        self.total_bugs=0
    
    def _cusp_potential(self, a, b, x):
        """V(x) = x⁴/4 + a·x²/2 + b·x"""
        return x**4/4 + a*x**2/2 + b*x
    
    def _is_catastrophe(self, a, b):
        """Bifurkationsmenge: 4a³ + 27b² < 0 → Katastrophen-Region"""
        return 4*a**3 + 27*b**2 < 0
    
    def _update_parameters(self, bt, success):
        """Kontrollparameter a,b evolvieren"""
        # a = Normal-Faktor (Erfolgsrate)
        rate=self.patterns[bt]['success']/max(1,self.patterns[bt]['total'])
        self.a[bt]=self.a[bt]*0.9+(rate-0.5)*0.1  # Zentriert um 0.5
        # b = Splitting-Faktor (Variabilität)
        if len(self.patterns[bt]['history'])>=3:
            recent=self.patterns[bt]['history'][-3:]
            self.b[bt]=np.std([1 if r else 0 for r in recent])
        else:
            self.b[bt]=0.0
    
    def think(self,sig,emb):
        self.total_bugs+=1; bt=sig.split(':')[0] if ':' in sig else sig
        
        self._update_parameters(bt, self.patterns[bt]['success']/max(1,self.patterns[bt]['total'])>0.5 if self.patterns[bt]['total']>0 else False)
        
        a,b=self.a[bt],self.b[bt]
        in_catastrophe=self._is_catastrophe(a, b)
        
        if in_catastrophe:
            self.catastrophe_points.append(self.total_bugs)
        
        if self.patterns[bt]['total']<2:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                    'a':f'{a:.3f}','b':f'{b:.3f}',
                    'reasoning':f'Catastrophe: {bt} a={a:.2f} b={b:.2f} — zu wenig Daten.'}
        
        rate=self.patterns[bt]['success']/max(1,self.patterns[bt]['total'])
        # Im Katastrophen-Regime: plötzlicher Sprung → Überraschung
        if in_catastrophe:
            # Das System KÖNNTE plötzlich springen → vorsichtig
            conf=rate*0.5
            action='EXPLORE'
        else:
            conf=rate
            action='APPLY_PATTERN' if conf>0.25 else 'EXPLORE'
        
        return {'action':action,'pattern':f'catastrophe_{bt}','confidence':conf,
                'a':f'{a:.3f}','b':f'{b:.3f}','catastrophe_region':in_catastrophe,
                'catastrophes':len(self.catastrophe_points),
                'reasoning':f'Catastrophe: a={a:.2f} b={b:.2f} {"⚠️SPRUNG" if in_catastrophe else "stabil"} conf={conf:.2f}'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        self.patterns[bt]['total']+=1
        if success: self.patterns[bt]['success']+=1
        self.patterns[bt]['history'].append(success)
        if len(self.patterns[bt]['history'])>50: self.patterns[bt]['history']=self.patterns[bt]['history'][-50:]
    
    def stats(self):
        return {'brain_type':'Catastrophe Theory (Thom)','total_bugs':self.total_bugs,
                'catastrophes_detected':len(self.catastrophe_points),
                'parameters':{bt:f'a={self.a[bt]:.2f} b={self.b[bt]:.2f}' for bt in self.a}}
    def __repr__(self): return f"CatastropheBrain(jumps={len(self.catastrophe_points)})"

if __name__=="__main__":
    print("GEHIRN BG — Catastrophe Theory (Thom)"); b=CatastropheBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(25):
        bt=['NullPointer','OffByOne','TypeError'][i%3]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<20,emb)
        if i%5==0: print(f"  Bug{i+1}: {dec['action']:15s} a={dec.get('a','?')} b={dec.get('b','?')} jump={dec.get('catastrophe_region',False)}")
    print(b.stats()); print("✅ Gehirn BG läuft.")
