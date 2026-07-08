"""
GEHIRN AQ — Maturana/Varela Autopoiesis Brain
7-SCHICHTIGE SELBST-ERSCHAFFUNG. Das Gehirn erhält sich selbst.

SCHICHT 1: MEMBRANE — Grenze zwischen System und Umwelt
SCHICHT 2: METABOLISMUS — Interne Transformation von Komponenten
SCHICHT 3: STRUKTURELLE KOPPLUNG — Mit Umwelt gekoppelt, nicht determiniert
SCHICHT 4: SELBST-REPARATUR — Beschädigte Komponenten automatisch heilen
SCHICHT 5: SELBST-REPRODUKTION — Neue Komponenten aus bestehenden
SCHICHT 6: KOGNITION — "Leben = Kognition" (Maturana)
SCHICHT 7: KONSENSUELLE DOMÄNE — Sprache als Koordination von Handlungen

Mathematik: Autopoiese = f(Produktion, Transformation, Zerfall)
            dC/dt = P(C) - T(C) - D(C)  (in equilibrium: P = T + D)

Autor: Hermes + David | Coding Tentacle 2026
Quelle: Maturana & Varela "Autopoiesis and Cognition" (1980)
"""
import numpy as np, math, time, random
from collections import defaultdict

class AutopoiesisBrain:
    """Gehirn AQ — Selbsterschaffendes System nach Maturana/Varela."""
    def __init__(self):
        # S1: MEMBRANE — Was gehört zum System? Grenzen
        self.membrane={'known_types':set(), 'boundary_strength':1.0, 'leaks':0}
        # S2: METABOLISMUS — Interne Transformation
        self.metabolism={'components':{}, 'energy':100.0, 'turnover_rate':0.1}
        # S3: STRUKTURELLE KOPPLUNG — Recurrente Interaktionen mit Umwelt
        self.structural_coupling={'perturbations':[], 'adaptations':0}
        # S4: SELBST-REPARATUR — Beschädigte Teile heilen
        self.repair={'damaged_components':set(), 'repair_log':[], 'auto_heal_threshold':3}
        # S5: SELBST-REPRODUKTION — Neue Komponenten = Generalisierung
        self.reproduction={'offspring':[], 'viability_threshold':0.6}
        # S6: KOGNITION — "Living systems are cognitive systems"
        self.cognition={'effective_action':[], 'structural_history':[]}
        # S7: KONSENSUELLE DOMÄNE — Sprache
        self.consensual={'shared_distinctions':set(), 'languaging_events':0}
        # Pattern-Speicher
        self.patterns=defaultdict(lambda: {'success':0,'total':0,'health':1.0,'age':0})
        self.total_bugs=0
    
    def _membrane_check(self, bt):
        """S1: Gehört dieser Bug zu unserem System?"""
        if bt not in self.membrane['known_types']:
            self.membrane['known_types'].add(bt)
            self.membrane['boundary_strength']*=0.99
        return bt in self.membrane['known_types']
    
    def _metabolize(self, pat):
        """S2: Interne Transformation — Pattern-Energie umwandeln"""
        self.metabolism['energy']+=0.5  # Energie aus erfolgreichem Fix
        if pat in self.metabolism['components']:
            self.metabolism['components'][pat]*=1.01  # Wachstum
        else:
            self.metabolism['components'][pat]=1.0
        # Turnover: alte Komponenten abbauen
        for c in list(self.metabolism['components']):
            self.metabolism['components'][c]*=(1-self.metabolism['turnover_rate'])
            if self.metabolism['components'][c]<0.1:
                del self.metabolism['components'][c]
    
    def _auto_repair(self):
        """S4: Automatische Heilung beschädigter Patterns"""
        for pat in list(self.repair['damaged_components']):
            if pat in self.patterns and self.patterns[pat]['total']>=self.repair['auto_heal_threshold']:
                self.patterns[pat]['health']=min(1.0, self.patterns[pat]['health']+0.2)
                if self.patterns[pat]['health']>0.7:
                    self.repair['damaged_components'].discard(pat)
                    self.repair['repair_log'].append(f"Healed:{pat}")
    
    def _reproduce(self):
        """S5: Selbst-Reproduktion — erfolgreiche Patterns generalisieren"""
        viable=[p for p,data in self.patterns.items() 
                if data['total']>=3 and data['success']/data['total']>=self.reproduction['viability_threshold']]
        for p in viable:
            if p not in self.reproduction['offspring']:
                self.reproduction['offspring'].append(p)
    
    def _cognize(self, bt, success):
        """S6: Kognition — Effektive Handlungen speichern"""
        self.cognition['effective_action'].append({'bug':bt,'success':success,'time':self.total_bugs})
        if len(self.cognition['effective_action'])>50:
            self.cognition['effective_action']=self.cognition['effective_action'][-50:]
    
    def think(self,sig,emb):
        self.total_bugs+=1; bt=sig.split(':')[0] if ':' in sig else sig
        
        # S1: Membran — gehört der Bug zu uns?
        self._membrane_check(bt)
        # S3: Strukturelle Kopplung
        self.structural_coupling['perturbations'].append(bt)
        if len(self.structural_coupling['perturbations'])>100:
            self.structural_coupling['perturbations']=self.structural_coupling['perturbations'][-100:]
        # S4: Auto-Repair laufend
        self._auto_repair()
        
        if bt in self.patterns and self.patterns[bt]['total']>=1:
            p=self.patterns[bt]
            rate=p['success']/max(1,p['total'])
            health=p['health']
            conf=rate*health
            return {'action':'APPLY_PATTERN' if conf>0.3 else 'EXPLORE',
                    'pattern':f'autopoietic_{bt}','confidence':conf,
                    'health':health,'membrane':len(self.membrane['known_types']),
                    'reasoning':f'Autopoiesis: {bt} rate={rate:.0%} health={health:.2f} conf={conf:.2f}'}
        return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                'reasoning':f'Autopoiesis: {bt} nicht im System. Membran-Erweiterung...'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        p=self.patterns[bt]
        p['total']+=1
        
        # STRUKTURELLE KOPPLUNG: Je älter das Pattern, desto resistenter
        pattern_age = p['age']
        coupling_strength = min(0.8, pattern_age / 20.0)  # Max 0.8 nach 16 Wiederholungen
        
        if success: 
            p['success']+=1
            p['health']=min(1.0, p['health']+0.2)
        else:
            # Dämpfung durch strukturelle Kopplung
            p['health']=max(0.2, p['health']-0.2*(1.0-coupling_strength))
        p['age']+=1
        
        self._metabolize(pat)
        self._cognize(bt, success)
        self._reproduce()
        
        if p['health']<0.4:
            self.repair['damaged_components'].add(bt)
    
    def stats(self):
        return {'brain_type':'Autopoiesis 7-Layer (Maturana/Varela)',
                'total_bugs':self.total_bugs,
                'membrane_types':len(self.membrane['known_types']),
                'metabolism_components':len(self.metabolism['components']),
                'energy':f'{self.metabolism["energy"]:.0f}',
                'repairs':len(self.repair['repair_log']),
                'offspring':len(self.reproduction['offspring']),
                'cognition_events':len(self.cognition['effective_action'])}
    def __repr__(self): return f"AutopoiesisBrain(components={len(self.metabolism['components'])})"

if __name__=="__main__":
    print("GEHIRN AQ — Autopoiesis (Maturana/Varela)"); b=AutopoiesisBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(30):
        bt=['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'][i%5]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<25,emb)
        if i%6==0: print(f"  Bug{i+1}: {dec['action']:15s} health={dec.get('health',0):.2f}")
    print(b.stats()); print("✅ Gehirn AQ läuft.")
