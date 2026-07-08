"""
GEHIRN AR — Gregory Bateson Deuterolearning Brain
7-SCHICHTIGES LERNEN ZU LERNEN. Meta-Patterns über Lernprozessen.

SCHICHT 1: LERNING I — Einfaches Lernen (Pattern→Fix)
SCHICHT 2: LERNING II — Deuterolearning (Lernen WIE man lernt)
SCHICHT 3: LERNING III — Korrektur von Learning II (System-Change)
SCHICHT 4: SCHISMOGENESE — Symmetrische/Komplementäre Eskalation erkennen
SCHICHT 5: DOUBLE BIND — Paradoxe Kommunikation auflösen
SCHICHT 6: THE PATTERN THAT CONNECTS — Alles ist verbunden
SCHICHT 7: ECOLOGY OF MIND — Geist = System, nicht Gehirn

Mathematik: L_rate(t) = L_rate(0) · exp(β · meta_success)
           Meta-Learning = Δ(learning_rate) = f(history_of_learning)

Autor: Hermes + David | Coding Tentacle 2026
Quelle: Bateson "Steps to an Ecology of Mind" (1972)
"""
import numpy as np, math, random
from collections import defaultdict, deque

class BatesonBrain:
    """Gehirn AR — Deuterolearning nach Gregory Bateson."""
    def __init__(self):
        # S1: Learning I — Basis-Lernen
        self.learning_I=defaultdict(lambda: {'rate':0.5, 'history':deque(maxlen=30)})
        # S2: Learning II — Meta-Lernen: WIE lerne ich?
        self.learning_II={'meta_rate':0.1, 'context_history':[], 'context_classes':{}}
        # S3: Learning III — System-Change: Korrektur von S2
        self.learning_III={'system_changes':0, 'corrections':[], 'threshold':10}
        # S4: Schismogenese — Eskalation erkennen
        self.schismogenesis={'symmetric':0, 'complementary':0, 'warnings':[]}
        # S5: Double Bind — Paradoxien
        self.double_bind={'traps':[], 'resolutions':0, 'active_trap':None}
        # S6: Pattern that connects — Verbindungen zwischen Bug-Typen
        self.connections=defaultdict(lambda: defaultdict(float))
        # S7: Ecology of Mind — System-Denken
        self.ecology={'mind_extends_to':set(), 'system_health':1.0}
        # Direkter Pattern-Speicher
        self.patterns=defaultdict(lambda: {'success':0,'total':0,'context':'unknown'})
        self.total_bugs=0
        self.learning_log=deque(maxlen=100)
    
    def _learn_context(self, bt):
        """S2: Welcher Lern-Kontext liegt vor?"""
        if bt not in self.learning_II['context_classes']:
            self.learning_II['context_classes'][bt]={'type':'new','confidence':0.5}
        ctx=self.learning_II['context_classes'][bt]
        ctx['confidence']=min(1.0, ctx['confidence']+0.1)
        return ctx
    
    def _detect_schismogenesis(self, bt, success):
        """S4: Eskalation erkennen"""
        if not success:
            self.schismogenesis['complementary']+=1
            if self.schismogenesis['complementary']>5:
                self.schismogenesis['warnings'].append(f"Complementary escalation: {bt}")
                self.schismogenesis['complementary']=0
    
    def _detect_double_bind(self, bt, pat):
        """S5: Paradoxe Situation?"""
        p=self.patterns[bt]
        if p['total']>=3 and p['success']/p['total']<0.3:
            # Pattern ist aktiv aber schädlich → Double Bind
            self.double_bind['traps'].append({'bug':bt,'pattern':pat,'repetitions':p['total']})
            if len(self.double_bind['traps'])>3:
                self.double_bind['resolutions']+=1
                self.double_bind['traps']=[]
    
    def _connect_patterns(self, bt, success):
        """S6: Pattern that connects"""
        for other_bt in self.patterns:
            if other_bt!=bt:
                self.connections[bt][other_bt]+=0.01
                self.ecology['mind_extends_to'].add(other_bt)
    
    def _system_check(self):
        """S7: Ecology of Mind — System-Gesundheit"""
        all_rates=[p['success']/max(1,p['total']) for p in self.patterns.values()]
        self.ecology['system_health']=np.mean(all_rates) if all_rates else 0.5
    
    def think(self,sig,emb):
        self.total_bugs+=1; bt=sig.split(':')[0] if ':' in sig else sig
        ctx=self._learn_context(bt)
        self._system_check()
        
        if bt in self.patterns and self.patterns[bt]['total']>=1:
            p=self.patterns[bt]
            base_rate=p['success']/max(1,p['total'])
            # Learning II: Meta-Rate beeinflusst Basis-Rate
            meta_boost=self.learning_II['meta_rate']*ctx['confidence']
            rate=min(1.0, base_rate+meta_boost)
            health=self.ecology['system_health']
            conf=rate*health
            
            # Learning III: System-Change nötig?
            if self.learning_III['system_changes']>=self.learning_III['threshold']:
                self.learning_II['meta_rate']*=1.5
                self.learning_III['system_changes']=0
                self.learning_III['corrections'].append(f"Meta-reset at bug {self.total_bugs}")
            
            return {'action':'APPLY_PATTERN' if conf>0.3 else 'EXPLORE',
                    'pattern':f'bateson_{bt}','confidence':conf,
                    'meta_rate':self.learning_II['meta_rate'],
                    'system_health':health,
                    'reasoning':f'Bateson: {bt} L1={base_rate:.0%} + L2={meta_boost:.0%} → {conf:.2f}'}
        return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                'reasoning':f'Bateson: Learning I beginnt für {bt}.'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        p=self.patterns[bt]; p['total']+=1
        if success: p['success']+=1
        
        # Learning I
        old_rate=self.learning_I[bt]['rate']
        new_rate=old_rate+(0.1 if success else -0.05)
        self.learning_I[bt]['rate']=max(0.1, min(1.0, new_rate))
        self.learning_I[bt]['history'].append(success)
        
        # Learning II: Meta-Learning
        hist=list(self.learning_I[bt]['history'])
        if len(hist)>=5:
            recent_success=np.mean([1 if h else 0 for h in hist[-5:]])
            self.learning_II['meta_rate']=self.learning_II['meta_rate']*0.9+recent_success*0.1
        
        self._detect_schismogenesis(bt, success)
        self._detect_double_bind(bt, pat)
        self._connect_patterns(bt, success)
        
        self.learning_log.append({'bug':bt,'success':success,'meta_rate':self.learning_II['meta_rate']})
    
    def stats(self):
        return {'brain_type':'Bateson Deuterolearning 7-Layer',
                'total_bugs':self.total_bugs,
                'L1_patterns':len(self.learning_I),
                'L2_meta_rate':f'{self.learning_II["meta_rate"]:.3f}',
                'L3_system_changes':self.learning_III['system_changes'],
                'S4_schismogenesis_warnings':len(self.schismogenesis['warnings']),
                'S5_double_binds_resolved':self.double_bind['resolutions'],
                'S7_system_health':f'{self.ecology["system_health"]:.2f}'}
    def __repr__(self): return f"BatesonBrain(L2_rate={self.learning_II['meta_rate']:.3f})"

if __name__=="__main__":
    print("GEHIRN AR — Bateson Deuterolearning"); b=BatesonBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(30):
        bt=['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'][i%5]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<25,emb)
        if i%6==0: print(f"  Bug{i+1}: {dec['action']:15s} L2={dec.get('meta_rate',0):.3f} health={dec.get('system_health',0):.2f}")
    print(b.stats()); print("✅ Gehirn AR läuft.")
