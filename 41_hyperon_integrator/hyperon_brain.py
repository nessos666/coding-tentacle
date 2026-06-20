"""
GEHIRN AO — Hyperon Integrator
Shared AtomSpace + alle 5 Sub-Gehirne (AJ-AN).
Koordiniert: Memory → Abstraktion → Regeln → Reasoning → Aktion.
AtomSpace als gemeinsame Wissensbasis (Hypergraph).

Pipeline:
  Bug → AJ (Modern Hopfield: "Kenn ich das?")
      → AK (Deep PC: "Auf welcher Ebene?")
      → AL (Chunking: "Neue Regel lernen?")
      → AM (PLN: "Transfer auf ähnliche Bugs?")
      → AN (MeTTa: "Kognitive Regel ausführen.")
      → Output: Fix + Konfidenz + Gelerntes

Autor: Hermes + David | Coding Tentacle 2026
"""
import sys, numpy as np
from collections import defaultdict

sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/36_modern_hopfield')
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/37_deep_predictive')
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/38_chunking')
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/39_pln_reasoning')
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/40_metta_cognitive')
from hopfield_brain import ModernHopfieldBrain
from deep_pc_brain import DeepPredictiveCodingBrain
from chunking_brain import ChunkingBrain
from pln_brain import PLNReasoningBrain
from metta_brain import MeTTaCognitiveBrain

class HyperonIntegratorBrain:
    """Gehirn AO — Integrator: Koordiniert AJ-AN via Shared AtomSpace."""
    def __init__(self):
        # Sub-Gehirne
        self.hopfield=ModernHopfieldBrain(beta=8.0)        # AJ
        self.deep_pc=DeepPredictiveCodingBrain()             # AK
        self.chunking=ChunkingBrain()                        # AL
        self.pln=PLNReasoningBrain()                         # AM
        self.metta=MeTTaCognitiveBrain()                     # AN
        
        # Shared AtomSpace (Hypergraph)
        self.atomspace={}  # {atom_id: {type, properties, links}}
        self.total_bugs=0
        self.stage_results={}
    
    def think(self,sig,emb):
        self.total_bugs+=1; bt=sig.split(':')[0] if ':' in sig else sig
        
        # Stage 1: Modern Hopfield — Gedächtnisabruf
        r1=self.hopfield.think(sig,emb)
        self.stage_results['hopfield']=r1
        
        # Stage 2: Deep PC — Abstraktionsebene bestimmen
        r2=self.deep_pc.think(sig,emb)
        self.stage_results['deep_pc']=r2
        
        # Stage 3: Chunking — Existierende Regeln prüfen
        r3=self.chunking.think(sig,emb)
        self.stage_results['chunking']=r3
        
        # Stage 4: PLN — Transfer-Reasoning
        r4=self.pln.think(sig,emb)
        self.stage_results['pln']=r4
        
        # Stage 5: MeTTa — Kognitive Regel ausführen
        r5=self.metta.think(sig,emb)
        self.stage_results['metta']=r5
        
        # INTEGRATION: Gewichtete Abstimmung aller Stages
        responses=[r for r in [r1,r2,r3,r4,r5] if r['action']=='APPLY_PATTERN']
        
        if responses:
            # Wähle Response mit höchster Konfidenz
            best=max(responses, key=lambda r: r.get('confidence',0))
            voters=[f"{r.get('reasoning','')[:30]}" for r in responses]
            return {'action':'APPLY_PATTERN','pattern':best['pattern'],
                    'confidence':best['confidence'],
                    'voters':len(responses),'total_stages':5,
                    'reasoning':f'Hyperon: {len(responses)}/5 Stages → {best["pattern"]}'}
        
        # Kein Konsens → Single-Stage Fallback
        for r in [r3, r1, r5]:  # Chunking > Hopfield > MeTTa
            if r.get('confidence',0)>0.2:
                return r
        
        return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                'voters':0,'total_stages':5,
                'reasoning':'Hyperon: Alle Stages = EXPLORE. Lernmodus.'}
    
    def learn(self,sig,pat,success,emb=None):
        # Alle Sub-Gehirne lernen parallel
        if emb:
            self.hopfield.learn(sig,pat,success,emb)
            self.deep_pc.learn(sig,pat,success,emb)
        self.chunking.learn(sig,pat,success,emb)
        self.pln.learn(sig,pat,success,emb)
        self.metta.learn(sig,pat,success,emb)
        
        # Shared AtomSpace updaten
        bt=sig.split(':')[0] if ':' in sig else sig
        if bt not in self.atomspace:
            self.atomspace[bt]={'type':'BugType','fixes':{},'success':0,'total':0}
        self.atomspace[bt]['total']+=1
        if success: self.atomspace[bt]['success']+=1
        self.atomspace[bt]['fixes'][pat]=self.atomspace[bt]['fixes'].get(pat,0)+1
    
    def stats(self):
        return {'brain_type':'Hyperon Integrator (AJ-AN)','total_bugs':self.total_bugs,
                'sub_brains':5,'atomspace_atoms':len(self.atomspace),
                'stage_performance':{k:f"{v.get('action','?')}" for k,v in self.stage_results.items()},
                'patterns':sum(len(a['fixes']) for a in self.atomspace.values())}
    def __repr__(self): return f"HyperonIntegrator(atoms={len(self.atomspace)})"

if __name__=="__main__":
    print("GEHIRN AO — Hyperon Integrator (5 Sub-Gehirne)")
    b=HyperonIntegratorBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(30):
        bt=['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'][i%5]
        emb=m.encode(f"{bt} error in code requires fix").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<25,emb)
        if i%6==0: print(f"  Bug{i+1}: {dec['action']:15s} voters={dec.get('voters',0)}/5")
    print(b.stats()); print("✅ Gehirn AO läuft.")
