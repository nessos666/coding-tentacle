"""
GEHIRN BN — Superposition/Quantum Brain
HÄLT MEHRERE FIX-HYPOTHESEN GLEICHZEITIG.
Quanten-inspiriert: Ein Bug-Zustand = Superposition von Fixes.
Kollaps bei Messung (Entscheidung).

Mathematik: |ψ⟩ = Σ α_i·|fix_i⟩  mit Σ|α_i|² = 1
           P(fix_i) = |α_i|²  (Born-Regel)
           Kollaps: Messung → ein Fix wird real

Autor: Hermes + David | Coding Tentacle 2026
"""
import numpy as np, math
from collections import defaultdict

class SuperpositionBrain:
    """Gehirn BN — Quanten-inspiriert: Hält mehrere Fixes in Superposition."""
    def __init__(self):
        self.superpositions={}  # {bug_type: {fix: amplitude}}
        self.collapsed=[]  # Kollabierte Zustände
        self.entanglements=defaultdict(lambda: defaultdict(float))  # Verschränkung
        self.patterns=defaultdict(lambda: {'success':0,'total':0})
        self.total_bugs=0
    
    def _normalize(self, amps):
        """Normiere Amplituden: Σ|α|² = 1"""
        norm=math.sqrt(sum(a*a for a in amps.values()))
        if norm>0: return {k: v/norm for k,v in amps.items()}
        return amps
    
    def _superpose(self, bt, pat, success):
        """Füge Fix zur Superposition hinzu oder verstärke Amplitude"""
        if bt not in self.superpositions:
            self.superpositions[bt]={}
        amps=self.superpositions[bt]
        # Erfolg → Amplitude erhöhen, Misserfolg → reduzieren
        if success:
            amps[pat]=amps.get(pat,0.1)+0.15
        else:
            amps[pat]=max(0.01, amps.get(pat,0.1)-0.1)
        self.superpositions[bt]=self._normalize(amps)
    
    def _entangle(self, bt1, bt2):
        """Verschränke ähnliche Bug-Typen"""
        amps1=self.superpositions.get(bt1,{})
        amps2=self.superpositions.get(bt2,{})
        for fix in set(list(amps1.keys())+list(amps2.keys())):
            a1=amps1.get(fix,0); a2=amps2.get(fix,0)
            self.entanglements[(bt1,bt2)][fix]=a1*a2
    
    def _measure(self, bt):
        """Kollaps: Wähle einen Fix nach Born-Regel"""
        amps=self.superpositions.get(bt,{})
        if not amps: return None, 0.0
        
        fixes=list(amps.keys())
        probs=np.array([amps[f]**2 for f in fixes])
        if probs.sum()==0: return None, 0.0
        probs/=probs.sum()
        
        # Stochastischer Kollaps
        idx=np.random.choice(len(fixes), p=probs)
        self.collapsed.append({'bug':bt,'chosen':fixes[idx],'probs':dict(zip(fixes,probs))})
        return fixes[idx], amps[fixes[idx]]**2
    
    def think(self,sig,emb):
        self.total_bugs+=1; bt=sig.split(':')[0] if ':' in sig else sig
        
        if bt not in self.superpositions or not self.superpositions[bt]:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                    'reasoning':f'Superposition: {bt} — Kein Zustand. |ψ⟩=0.'}
        
        # Kollaps: Messung
        fix,prob=self._measure(bt)
        
        if fix and prob>0.15:
            # Verschränkung mit ähnlichen Typen prüfen
            entangled_info=""
            for (b1,b2),amps in self.entanglements.items():
                if b1==bt or b2==bt:
                    other=b1 if b2==bt else b2
                    entangled_info=f" entangled_with={other}"
            
            amps=self.superpositions[bt]
            amp_str={f'{f[:10]}':f'{a:.2f}' for f,a in sorted(amps.items(),key=lambda x:-abs(x[1]))[:3]}
            
            return {'action':'APPLY_PATTERN','pattern':fix,
                    'confidence':prob,'superposition':amp_str,
                    'entangled':entangled_info,
                    'reasoning':f'Superposition: |ψ⟩ kollabiert → {fix} (P={prob:.0%}){entangled_info}'}
        
        return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                'reasoning':f'Superposition: {bt} — Kein Fix > 15%. Mehr Daten.'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        self.patterns[bt]['total']+=1
        if success: self.patterns[bt]['success']+=1
        self._superpose(bt, pat, success)
    
    def stats(self):
        n_states=len(self.superpositions)
        n_collapsed=len(self.collapsed)
        return {'brain_type':'Superposition/Quantum','total_bugs':self.total_bugs,
                'superposed_states':n_states,'collapsed':n_collapsed,
                'active_superpositions':{bt:{f[:10]:f'{a:.2f}' for f,a in amps.items()} for bt,amps in self.superpositions.items()}}
    def __repr__(self): return f"SuperpositionBrain(states={len(self.superpositions)})"

if __name__=="__main__":
    print("GEHIRN BN — Superposition/Quantum"); b=SuperpositionBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(20):
        bt=['NullPointer','OffByOne','TypeError'][i%3]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<16,emb)
        if i%5==0: print(f"  Bug{i+1}: {dec['action']:15s} |ψ⟩={dec.get('superposition','?')}")
    print(b.stats()); print("✅ Gehirn BN läuft.")
