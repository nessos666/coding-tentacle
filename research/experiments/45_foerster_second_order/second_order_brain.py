"""
GEHIRN AS — Heinz von Foerster Second-Order Cybernetics Brain
7-SCHICHTIG. Der BEOBACHTER ist Teil des Systems.

SCHICHT 1: BEOBACHTUNG 1. ORDNUNG — Bug-Fix-Ergebnisse beobachten
SCHICHT 2: BEOBACHTUNG 2. ORDNUNG — Beobachten WIE wir beobachten
SCHICHT 3: EIGENWERTE — Stabile Zustände des Beobachtungssystems
SCHICHT 4: REKURSION — Beobachter beobachtet Beobachter (∞)
SCHICHT 5: TRIVIALE vs NICHT-TRIVIALE MASCHINEN — Ist der Bug deterministisch?
SCHICHT 6: ETHISCHER IMPERATIV — "Handle stets so, dass weitere Möglichkeiten entstehen"
SCHICHT 7: KONSTRUKTIVISMUS — Realität = Erfindung des Beobachters

Mathematik: Eigenform = Fixpunkt der rekursiven Beobachtung
           obs(obs(obs(...(bug)...))) → stabiler Eigenwert

Autor: Hermes + David | Coding Tentacle 2026
Quelle: von Foerster "Observing Systems" (1981)
"""
import numpy as np, math, random
from collections import defaultdict, deque

class SecondOrderBrain:
    """Gehirn AS — Second-Order Cybernetics: Der Beobachter im System."""
    def __init__(self):
        # S1: Beobachtung 1. Ordnung — was sehen wir?
        self.obs1={'direct':deque(maxlen=50), 'patterns_seen':set()}
        # S2: Beobachtung 2. Ordnung — WIE sehen wir?
        self.obs2={'filters':[], 'biases':defaultdict(float), 'blind_spots':set()}
        # S3: Eigenwerte — Stabile Beobachtungsmuster
        self.eigenvalues={'stable_patterns':{}, 'convergence_count':0}
        # S4: Rekursion — Selbstbezüglichkeit
        self.recursion={'depth':0, 'max_depth':7, 'self_reference_log':[]}
        # S5: Triviale vs Nicht-Triviale Maschinen
        self.machine_type=defaultdict(lambda: 'unknown')  # 'trivial' | 'non_trivial'
        # S6: Ethischer Imperativ
        self.ethical={'options_created':0, 'options_destroyed':0}
        # S7: Konstruktivismus — Realität = konstruiert
        self.constructivism={'constructed_reality':{}, 'perturbations':[]}
        self.patterns=defaultdict(lambda: {'success':0,'total':0,'observer_bias':0.0})
        self.total_bugs=0
    
    def _observe_first_order(self, bt, emb):
        """S1: Direkte Beobachtung"""
        self.obs1['direct'].append(bt)
        self.obs1['patterns_seen'].add(bt)
        return bt in self.patterns
    
    def _observe_second_order(self, bt, success):
        """S2: Beobachte den Beobachter"""
        # Welche Biases haben wir?
        if success:
            self.obs2['biases'][bt]+=0.05  # Positiver Bias für diesen Typ
        else:
            self.obs2['biases'][bt]-=0.03  # Negativer Bias
        # Blinde Flecken: Bug-Typen, die wir NIE sehen
        all_types={'NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition',
                   'StackOverflow','ImportError','KeyError','ValueError','AttributeError'}
        self.obs2['blind_spots']=all_types-self.obs1['patterns_seen']
    
    def _compute_eigenvalues(self):
        """S3: Stabile Beobachtungsmuster finden"""
        if len(self.obs1['direct'])<10: return
        from collections import Counter
        freq=Counter(self.obs1['direct'])
        total=len(self.obs1['direct'])
        for bt,count in freq.most_common(5):
            stability=count/total
            if stability>0.15:
                self.eigenvalues['stable_patterns'][bt]=stability
        self.eigenvalues['convergence_count']+=1
    
    def _recursive_observe(self, bt, depth=0):
        """S4: Rekursive Selbstbeobachtung"""
        if depth>=self.recursion['max_depth']:
            return self.patterns[bt]['success']/max(1,self.patterns[bt]['total'])
        self.recursion['depth']=depth
        rate=self._recursive_observe(bt, depth+1)  # Rekursion!
        self.recursion['self_reference_log'].append(f"depth{depth}:{bt}={rate:.2f}")
        return rate*0.95  # Dämpfung pro Rekursionsschicht
    
    def _classify_machine(self, bt):
        """S5: Triviale vs Nicht-triviale Maschine"""
        p=self.patterns[bt]
        if p['total']>=5:
            consistency=p['success']/p['total']
            if consistency>0.9 or consistency<0.1:
                self.machine_type[bt]='trivial'  # Determinierbar
            else:
                self.machine_type[bt]='non_trivial'  # Unvorhersagbar
    
    def _ethical_check(self, success):
        """S6: 'Handle stets so, dass weitere Möglichkeiten entstehen'"""
        if success:
            self.ethical['options_created']+=1
        else:
            self.ethical['options_destroyed']+=1
    
    def _construct_reality(self, bt):
        """S7: Realität ist konstruiert, nicht entdeckt"""
        self.constructivism['constructed_reality'][bt]=self.patterns[bt]['success']/max(1,self.patterns[bt]['total'])
        self.constructivism['perturbations'].append(bt)
    
    def think(self,sig,emb):
        self.total_bugs+=1; bt=sig.split(':')[0] if ':' in sig else sig
        
        known=self._observe_first_order(bt, emb)
        self._compute_eigenvalues()
        
        if known and self.patterns[bt]['total']>=1:
            # S4: Rekursive Beobachtung
            recursive_rate=self._recursive_observe(bt)
            
            p=self.patterns[bt]
            direct_rate=p['success']/max(1,p['total'])
            # S2: Observer-Bias einrechnen
            bias=self.obs2['biases'][bt]
            # S5: Maschinentyp
            self._classify_machine(bt)
            machine_factor=1.2 if self.machine_type[bt]=='trivial' else 0.8
            
            conf=min(1.0, (direct_rate+bias)*machine_factor*recursive_rate)
            eigenvalues=list(self.eigenvalues['stable_patterns'].keys())[:3]
            
            return {'action':'APPLY_PATTERN' if conf>0.25 else 'EXPLORE',
                    'pattern':f'observed_{bt}','confidence':conf,
                    'machine_type':self.machine_type[bt],
                    'eigenvalues':eigenvalues,
                    'reasoning':f'2nd-Order: {bt} direct={direct_rate:.0%} bias={bias:+.0%} '
                               f'machine={self.machine_type[bt]} conf={conf:.2f}'}
        return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                'reasoning':f'2nd-Order: {bt} unbeobachtet. Beobachte...'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        p=self.patterns[bt]; p['total']+=1
        
        # EIGENWERT-STABILITÄT: Stabile Patterns widerstehen Perturbationen
        stability = self.eigenvalues['stable_patterns'].get(bt, 0.0)
        
        if success: 
            p['success']+=1
        else:
            # Dämpfung proportional zur Eigenwert-Stabilität
            damping = min(0.9, stability * 2.0)  # Max 90% Dämpfung
            effective_penalty = 1.0 - damping  # Nur der ungedämpfte Anteil zählt
            p['total']-=effective_penalty  # Reduziere 'total' statt 'success' zu reduzieren
        
        self._observe_second_order(bt, success)
        self._ethical_check(success)
        self._construct_reality(bt)
    
    def stats(self):
        return {'brain_type':'Second-Order Cybernetics 7-Layer (von Foerster)',
                'total_bugs':self.total_bugs,
                'S1_observed':len(self.obs1['patterns_seen']),
                'S2_blind_spots':len(self.obs2['blind_spots']),
                'S3_eigenvalues':len(self.eigenvalues['stable_patterns']),
                'S5_non_trivial':sum(1 for v in self.machine_type.values() if v=='non_trivial'),
                'S6_options_created':self.ethical['options_created'],
                'S6_options_destroyed':self.ethical['options_destroyed']}
    def __repr__(self): return f"SecondOrderBrain(eigenvalues={len(self.eigenvalues['stable_patterns'])})"

if __name__=="__main__":
    print("GEHIRN AS — Second-Order Cybernetics (von Foerster)"); b=SecondOrderBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(30):
        bt=['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'][i%5]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<25,emb)
        if i%6==0: print(f"  Bug{i+1}: {dec['action']:15s} machine={dec.get('machine_type','?')} conf={dec.get('confidence',0):.2f}")
    print(b.stats()); print("✅ Gehirn AS läuft.")
