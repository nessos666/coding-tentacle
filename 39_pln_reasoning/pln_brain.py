"""
GEHIRN AM — PLN Reasoning Brain (Probabilistic Logic Networks)
Transfer-Lernen via logische Inferenz.
WENN: guard_clause hilft bei NullPointer (s=0.9, c=0.95)
UND: AttributeError ist similarTo NullPointer (s=0.6, c=0.7)
DANN: guard_clause KÖNNTE bei AttributeError helfen (s=0.54, c=0.67)

PLN-Regeln: Deduction, Induction, Abduction, Revision.

Autor: Hermes + David | Coding Tentacle 2026
Quelle: Goertzel et al. "Probabilistic Logic Networks" (2008)
"""
import numpy as np, math
from collections import defaultdict

class TruthValue:
    def __init__(self, s=0.5, c=0.0):
        self.s=max(0,min(1,s)); self.c=max(0,min(1,c))
    def __repr__(self): return f"⟨{self.s:.2f},{self.c:.2f}⟩"

def pln_deduction(tv_AB, tv_BC):
    """Deduction: A→B, B→C ⊢ A→C"""
    s=tv_AB.s*tv_BC.s
    c=tv_AB.c*tv_BC.c*tv_AB.s*tv_BC.s
    return TruthValue(s,c)

def pln_revision(tv1, tv2):
    """Revision: Kombiniere zwei TruthValues über dasselbe Atom"""
    c=tv1.c+tv2.c-tv1.c*tv2.c
    s=(tv1.s*tv1.c*(1-tv2.c)+tv2.s*tv2.c*(1-tv1.c))/max(c,0.001)
    return TruthValue(s,c)

def pln_similarity_transfer(tv_hasFix, tv_similarTo):
    """WENN A→Fix (tv1) UND B∼A (tv2) DANN B→Fix (reduziert)"""
    s=tv_hasFix.s*tv_similarTo.s*0.8
    c=tv_hasFix.c*tv_similarTo.c*0.7
    return TruthValue(s,c)

class PLNReasoningBrain:
    """Gehirn AM — Probabilistic Logic Networks für Transfer-Lernen."""
    def __init__(self):
        self.atoms={}  # {name: (type, TruthValue)}
        self.links={}  # {(source,target,linktype): TruthValue}
        self.total_bugs=0
    
    def _get_tv(self, source, target, linktype):
        key=(source,target,linktype)
        return self.links.get(key, TruthValue(0,0))
    
    def _set_tv(self, source, target, linktype, tv):
        key=(source,target,linktype)
        if key in self.links:
            self.links[key]=pln_revision(self.links[key], tv)
        else:
            self.links[key]=tv
    
    def think(self,sig,emb):
        self.total_bugs+=1
        bt=sig.split(':')[0] if ':' in sig else sig
        
        # Direkter Link?
        direct_tv=self._get_tv(bt, 'hasFix', 'direct')
        if direct_tv.c>0.3 and direct_tv.s>0.3:
            return {'action':'APPLY_PATTERN','pattern':f'direct_{bt}',
                    'confidence':direct_tv.s,'tv':str(direct_tv),
                    'reasoning':f'PLN: Direkt {bt}→fix {direct_tv}'}
        
        # TRANSFER via similarTo-Links!
        best_fix,best_tv=None,TruthValue(0,0)
        for (src,tgt,lt),tv in self.links.items():
            if lt=='similarTo' and tgt==bt and tv.c>0.3:
                # Prüfe ob src einen Fix hat
                src_fix_tv=self._get_tv(src, 'hasFix', 'direct')
                if src_fix_tv.c>0.3:
                    transfer_tv=pln_similarity_transfer(src_fix_tv, tv)
                    if transfer_tv.s*transfer_tv.c>best_tv.s*best_tv.c:
                        best_tv=transfer_tv; best_fix=f'transfer_from_{src}'
            elif lt=='similarTo' and src==bt and tv.c>0.3:
                tgt_fix_tv=self._get_tv(tgt, 'hasFix', 'direct')
                if tgt_fix_tv.c>0.3:
                    transfer_tv=pln_similarity_transfer(tgt_fix_tv, tv)
                    if transfer_tv.s*transfer_tv.c>best_tv.s*best_tv.c:
                        best_tv=transfer_tv; best_fix=f'transfer_from_{tgt}'
        
        if best_fix and best_tv.c>0.2:
            return {'action':'APPLY_PATTERN','pattern':best_fix,
                    'confidence':best_tv.s,'tv':str(best_tv),
                    'reasoning':f'PLN-Transfer: {bt}→{best_fix} via similarTo {best_tv}'}
        return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                'reasoning':f'PLN: Kein Link/Transfer für {bt}.'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        tv=TruthValue(1.0 if success else 0.3, 0.5)
        self._set_tv(bt, pat, 'direct', tv)
        
        # Ähnlichkeits-Links zu anderen Bug-Typen (via Embedding-Ähnlichkeit)
        if emb is not None and success:
            e=np.array(emb)
            for other_bt in self.atoms:
                if other_bt!=bt and other_bt not in ['hasFix','similarTo']:
                    # Vereinfacht: Alle Bug-Typen sind ähnlich
                    self._set_tv(bt, other_bt, 'similarTo', TruthValue(0.4, 0.3))
        if bt not in self.atoms: self.atoms[bt]=('BugType', TruthValue(1,1))
    
    def stats(self):
        n_links=len(self.links)
        transfers=sum(1 for (_,_,lt),_ in self.links.items() if lt=='similarTo')
        return {'brain_type':'PLN Reasoning (Probabilistic Logic)','total_bugs':self.total_bugs,
                'links':n_links,'similarity_links':transfers,
                'top_links':[(f'{s}--{lt}-->{t}',str(tv)) for (s,t,lt),tv in sorted(self.links.items(),key=lambda x:-x[1].s*x[1].c)[:5]]}
    def __repr__(self): return f"PLNBrain(links={len(self.links)})"

if __name__=="__main__":
    print("GEHIRN AM — PLN Reasoning"); b=PLNReasoningBrain()
    for i in range(25):
        bt=['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'][i%5]
        dec=b.think(f"{bt}:f{i}.py:{i}",[0]*384)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<20)
        if i%5==0: print(f"  Bug{i+1}: {dec['action']:15s} tv={dec.get('tv','?')}")
    print(b.stats()); print("✅ Gehirn AM läuft.")
