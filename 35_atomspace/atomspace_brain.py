"""
GEHIRN AI — AtomSpace / OpenCog Brain (Goertzel 2008-2024)
Hypergraph-Wissensrepräsentation. Atoms + Links + TruthValues.
Probabilistic Logic Networks (PLN) für Reasoning.
Nodes = Konzepte. Links = Relationen. TruthValue = ⟨strength, confidence⟩.

Struktur:
  (BugType "NullPointer") --[hasFix]--> (FixPattern "guard_clause")
  (FixPattern "guard_clause") --[successRate]--> (TruthValue 0.85 0.90)

Autor: Hermes + David | Coding Tentacle 2026
"""
import numpy as np, math
from collections import defaultdict

class TruthValue:
    def __init__(self, strength=0.5, confidence=0.0):
        self.s=strength; self.c=confidence  # ⟨s,c⟩ — PLN TruthValue
    
    def merge(self, other):
        """Gewichtetes Mittel (nicht PLN-Revision — besser für wiederholte Evidenz)"""
        c=min(1.0, self.c+0.2)  # Langsam wachsende Konfidenz
        s=self.s*0.7+other.s*0.3  # Gewichtetes Mittel
        return TruthValue(s,c)
    
    def discounted(self, factor=0.9):
        return TruthValue(self.s*factor, self.c*factor)

class Atom:
    def __init__(self, atom_type, name, tv=None):
        self.type=atom_type; self.name=name
        self.tv=tv or TruthValue()
        self.incoming=set()  # Eingehende Links
        self.outgoing=set()  # Ausgehende Links
    
    def __repr__(self): return f"Atom({self.type}:{self.name}, s={self.tv.s:.2f})"

class Link:
    def __init__(self, link_type, sources, target, tv=None):
        self.type=link_type; self.sources=sources; self.target=target
        self.tv=tv or TruthValue()
    
    def __repr__(self): return f"Link({self.type}: {[s.name for s in self.sources]} → {self.target.name})"

class AtomSpaceBrain:
    """Gehirn AI — Hypergraph-Wissensbasis mit probabilistischem Reasoning."""
    def __init__(self):
        self.atoms={}  # {name: Atom}
        self.links=[]
        self.total_bugs=0
        # Grundatome
        self._init()
    
    def _init(self):
        for bt in ['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition']:
            self.atoms[bt]=Atom('BugType', bt, TruthValue(1.0,1.0))
    
    def _get_or_create(self, atype, name):
        if name not in self.atoms:
            self.atoms[name]=Atom(atype, name)
        return self.atoms[name]
    
    def _add_link(self, ltype, source_names, target_name, tv):
        sources=[self._get_or_create('Concept', s) for s in source_names]
        target=self._get_or_create('Concept', target_name)
        link=Link(ltype, sources, target, tv)
        for s in sources: s.outgoing.add(link)
        target.incoming.add(link)
        self.links.append(link)
        return link
    
    def _query(self, atype, name):
        """PLN-Abfrage: Finde verknüpfte Atome mit höchstem TruthValue"""
        # Suche in links statt in atom.incoming (robuster)
        best, best_tv = None, None
        for link in self.links:
            if link.type == 'hasFix' and link.target.name == name:
                tv = link.tv
                if best_tv is None or (tv.s * tv.c > best_tv.s * best_tv.c):
                    best = link.sources[0].name if link.sources else None
                    best_tv = tv
        if best is None:
            return None, None
        return best, best_tv
    
    def think(self,sig,emb):
        self.total_bugs+=1
        bt=sig.split(':')[0] if ':' in sig else sig
        fix,tv=self._query('BugType', bt)
        
        if fix is not None and tv is not None:
            if hasattr(tv,'c') and hasattr(tv,'s') and tv.c>0.15 and tv.s>0.2:
                return {'action':'APPLY_PATTERN','pattern':fix,
                        'confidence':tv.s,'tv_confidence':tv.c,
                        'reasoning':f'AtomSpace: {bt}→{fix} ⟨s={tv.s:.2f},c={tv.c:.2f}⟩'}
        return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                'reasoning':f'AtomSpace: Kein Link für {bt}. Wissensgraph aufbauen...'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        fix_name=f"{bt}_fix_{pat}"
        
        # Existierenden Link finden
        existing=None
        for link in self.links:
            if link.type=='hasFix' and link.sources[0].name==fix_name and link.target.name==bt:
                existing=link; break
        
        new_tv=TruthValue(1.0 if success else 0.3, 0.5)
        
        if existing:
            existing.tv=existing.tv.merge(new_tv)
        else:
            fix_atom=self._get_or_create('FixPattern', fix_name)
            bug_atom=self._get_or_create('BugType', bt)
            self._add_link('hasFix', [fix_name], bt, new_tv)
            
            # Kreuz-Links: ähnliche Bug-Typen
            for other_bt in self.atoms:
                if other_bt!=bt and other_bt in ['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition']:
                    sim=0.3  # Default-Ähnlichkeit
                    if success:
                        self._add_link('similarTo', [bt], other_bt, TruthValue(sim, 0.3))
    
    def stats(self):
        n_atoms=len(self.atoms); n_links=len(self.links)
        top_links=sorted(self.links, key=lambda l: l.tv.s*l.tv.c, reverse=True)[:3]
        return {'brain_type':'AtomSpace/OpenCog','total_bugs':self.total_bugs,
                'atoms':n_atoms,'links':n_links,
                'top_links':[f'{l.type}: {l.sources[0].name}→{l.target.name} s={l.tv.s:.2f}' for l in top_links]}
    def __repr__(self): return f"AtomSpace(atoms={len(self.atoms)}, links={len(self.links)})"

if __name__=="__main__":
    print("GEHIRN AI — AtomSpace/OpenCog"); b=AtomSpaceBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(20):
        bt=['NullPointer','OffByOne','TypeError'][i%3]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<16,emb)
        if i%5==0: print(f"  Bug{i+1}: {dec['action']:15s} tv={dec.get('confidence',0):.2f}")
    print(b.stats()); print("✅ Gehirn AI läuft.")
