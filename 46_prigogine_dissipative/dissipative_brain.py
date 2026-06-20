"""
GEHIRN AT — Ilya Prigogine Dissipative Structures Brain
7-SCHICHTIG. Ordnung entsteht durch Energiefluss im Nicht-Gleichgewicht.

SCHICHT 1: ENTROPIE-PRODUKTION — dS = d_eS + d_iS (extern + intern)
SCHICHT 2: FLIESSGLEICHGEWICHT — Stationärer Zustand fern vom Gleichgewicht
SCHICHT 3: BIFURKATION — Plötzlicher Phasenübergang zu neuer Ordnung
SCHICHT 4: DISSIPATIVE STRUKTUR — Geordneter Zustand durch Energie-Dissipation
SCHICHT 5: IRREVERSIBILITÄT — Zeitpfeil: ΔS > 0 (immer)
SCHICHT 6: ORDNUNG DURCH FLUKTUATIONEN — Kleine Störungen → große Ordnung
SCHICHT 7: SELBSTORGANISIERTE KRITIKALITÄT — System am Rande des Chaos

Mathematik: dS/dt = d_eS/dt + d_iS/dt  mit d_iS ≥ 0 (2. Hauptsatz)
           Bifurkationsparameter λ: bei λ > λ_crit → neue Struktur

Autor: Hermes + David | Coding Tentacle 2026
Quelle: Prigogine "Order out of Chaos" (1984), Nobelpreis 1977
"""
import numpy as np, math, random
from collections import defaultdict, deque

class DissipativeBrain:
    """Gehirn AT — Ordnung durch Nicht-Gleichgewicht (Prigogine)."""
    def __init__(self):
        # S1: Entropie-Produktion
        self.entropy={'total':0.0, 'internal':0.0, 'external':0.0}
        # S2: Fließgleichgewicht
        self.steady_state={'energy_flow':50.0, 'balance':0.5, 'history':deque(maxlen=60)}
        # S3: Bifurkation
        self.bifurcation={'parameter':0.0, 'critical_threshold':0.7, 'transitions':[]}
        # S4: Dissipative Struktur
        self.dissipative_structure={'ordered_patterns':{}, 'energy_cost':{}}
        # S5: Irreversibilität (Zeitpfeil)
        self.arrow_of_time={'history':deque(maxlen=200), 'irreversible_events':0}
        # S6: Ordnung durch Fluktuationen
        self.fluctuations={'perturbations':[], 'amplified':[], 'damped':[]}
        # S7: Selbstorganisierte Kritikalität
        self.soc={'avalanche_size':0, 'avalanche_ready':False, 'events':[]}
        self.patterns=defaultdict(lambda: {'success':0,'total':0,'energy':10.0})
        self.total_bugs=0
    
    def _entropy_production(self, success):
        """S1: dS = d_eS + d_iS"""
        self.entropy['internal']+=0.1  # Immer positiv (2. Hauptsatz)
        if success:
            self.entropy['external']-=0.15  # Ordnung durch Energie-Export
        else:
            self.entropy['external']+=0.05
        self.entropy['total']=self.entropy['internal']+self.entropy['external']
    
    def _steady_state_update(self):
        """S2: Fließgleichgewicht"""
        self.steady_state['history'].append(self.entropy['total'])
        if len(self.steady_state['history'])>10:
            self.steady_state['balance']=np.mean(list(self.steady_state['history'])[-10:])
        # Energiefluss: je mehr Bugs, desto mehr Energie nötig
        self.steady_state['energy_flow']=50.0+self.total_bugs*0.3
    
    def _bifurcation_check(self):
        """S3: Bifurkation — Phasenübergang?"""
        self.bifurcation['parameter']=self.entropy['total']/max(1,self.steady_state['energy_flow'])
        if self.bifurcation['parameter']>self.bifurcation['critical_threshold']:
            self.bifurcation['transitions'].append(self.total_bugs)
            self.bifurcation['parameter']*=0.5  # Reset nach Übergang
            # SOC: Avalanche!
            self.soc['avalanche_ready']=True
            self.soc['avalanche_size']=random.randint(3,8)
    
    def _amplify_fluctuation(self, bt, success):
        """S6: Ordnung durch Fluktuationen"""
        self.fluctuations['perturbations'].append((bt, success))
        if len(self.fluctuations['perturbations'])>5:
            recent=self.fluctuations['perturbations'][-5:]
            succ_rate=np.mean([1 for _,s in recent if s])
            if succ_rate>0.8:
                self.fluctuations['amplified'].append(bt)  # Fluktuation wird zur Ordnung!
            elif succ_rate<0.2:
                self.fluctuations['damped'].append(bt)
    
    def _soc_avalanche(self):
        """S7: Selbstorganisierte Kritikalität"""
        if self.soc['avalanche_ready']:
            self.soc['events'].append({'at_bug':self.total_bugs, 'size':self.soc['avalanche_size']})
            self.soc['avalanche_ready']=False
            self.soc['avalanche_size']=max(1, self.soc['avalanche_size']-1)
    
    def think(self,sig,emb):
        self.total_bugs+=1; bt=sig.split(':')[0] if ':' in sig else sig
        
        self._steady_state_update()
        self._bifurcation_check()
        self._soc_avalanche()
        
        if bt in self.patterns and self.patterns[bt]['total']>=1:
            p=self.patterns[bt]
            rate=p['success']/max(1,p['total'])
            energy=p['energy']
            
            # Energie-Faktor: mehr Energie = höhere Konfidenz
            energy_factor=min(1.5, max(0.5, energy/10.0))
            # SOC-Faktor: in Avalanche → niedrigere Schwelle
            soc_factor=0.8 if self.soc['avalanche_ready'] else 1.0
            
            conf=min(1.0, rate*energy_factor/soc_factor)
            bifurcation=self.bifurcation['parameter']
            
            return {'action':'APPLY_PATTERN' if conf>0.25 else 'EXPLORE',
                    'pattern':f'dissipative_{bt}','confidence':conf,
                    'entropy':f'{self.entropy["total"]:.2f}',
                    'bifurcation':f'{bifurcation:.3f}',
                    'avalanche':self.soc['avalanche_ready'],
                    'reasoning':f'Dissipativ: {bt} rate={rate:.0%} E={energy:.0f} '
                               f'dS={self.entropy["total"]:.1f} B={bifurcation:.2f} conf={conf:.2f}'}
        return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                'reasoning':f'Dissipativ: {bt} keine Struktur. Energie zuführen...'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        p=self.patterns[bt]; p['total']+=1
        
        # KRISTALLISATION: Patterns mit Energie > 20 werden resistent
        crystallized = p['energy'] > 15.0
        if crystallized:
            # Kristallisierte Patterns: Energieverlust stark gedämpft
            energy_loss_factor = 0.2
            energy_gain_factor = 0.5
        else:
            energy_loss_factor = 1.0
            energy_gain_factor = 1.0
        
        if success: 
            p['success']+=1
            p['energy']=min(30.0, p['energy']+2.0*energy_gain_factor)
        else:
            p['energy']=max(1.0, p['energy']-3.0*energy_loss_factor)
        
        self._entropy_production(success)
        self._amplify_fluctuation(bt, success)
        self.arrow_of_time['history'].append(success)
        self.arrow_of_time['irreversible_events']+=1
        for pat in self.patterns:
            self.patterns[pat]['energy']=max(1.0, self.patterns[pat]['energy']-0.05)
    
    def stats(self):
        return {'brain_type':'Dissipative Structures 7-Layer (Prigogine)',
                'total_bugs':self.total_bugs,
                'S1_entropy_total':f'{self.entropy["total"]:.2f}',
                'S2_energy_flow':f'{self.steady_state["energy_flow"]:.0f}',
                'S3_bifurcations':len(self.bifurcation['transitions']),
                'S6_amplified_fluctuations':len(self.fluctuations['amplified']),
                'S7_avalanche_events':len(self.soc['events']),
                'total_patterns':len(self.patterns)}
    def __repr__(self): return f"DissipativeBrain(dS={self.entropy['total']:.1f}, patterns={len(self.patterns)})"

if __name__=="__main__":
    print("GEHIRN AT — Dissipative Structures (Prigogine)"); b=DissipativeBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(35):
        bt=['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'][i%5]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<28,emb)
        if i%7==0: print(f"  Bug{i+1}: {dec['action']:15s} dS={dec.get('entropy','?')} B={dec.get('bifurcation','?')}")
    print(b.stats()); print("✅ Gehirn AT läuft.")
