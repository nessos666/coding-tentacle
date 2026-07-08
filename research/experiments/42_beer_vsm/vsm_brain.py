"""
GEHIRN AP — Stafford Beer Viable System Model Brain
7-SCHICHTIGE ARCHITEKTUR nach Beer's VSM (1972, 1981)

SCHICHT 1 (S1): OPERATIONS — Bug-Fixing (primäre Aktivität)
SCHICHT 2 (S2): COORDINATION — Konfliktlösung zwischen parallelen Fixes
SCHICHT 3 (S3): CONTROL — Interne Optimierung, Ressourcen-Audit
SCHICHT 4 (S3*): AUDIT — Sporadische Tiefenprüfung aller Operationen
SCHICHT 5 (S4): INTELLIGENCE — Zukunft/Umwelt-Scan, neue Bug-Typen
SCHICHT 6 (S5): POLICY — Ultimative Entscheidungsinstanz, Identität
SCHICHT 7: ALGEDONIC LOOP — Schmerz/Lust-Signal für Gesamtsystem

Mathematik: Ashby's Varietät: V(S5) ≥ V(S4) ≥ V(S3) ≥ V(S1)
             Jede Schicht ABSORBIERT Varietät der darunterliegenden.

Autor: Hermes + David | Coding Tentacle 2026
Quelle: Beer "Brain of the Firm" (1972), "Heart of Enterprise" (1979)
"""
import numpy as np, math, random
from collections import defaultdict, deque

class VSMBrain:
    """Gehirn AP — 7-Schicht Viable System Model nach Stafford Beer."""
    def __init__(self):
        # S1: Operations — direkte Bug-Fix-Historie
        self.s1_operations=defaultdict(lambda: {'fixes':{}, 'success':0, 'total':0})
        # S2: Coordination — Anti-Oszillation zwischen konkurrierenden Fixes
        self.s2_coordination=defaultdict(lambda: {'active_fixes':set(), 'conflicts':0})
        # S3: Control — Ressourcen-Audit, interne Metriken
        self.s3_control={'total_ops':0, 'audit_log':deque(maxlen=100), 'efficiency':1.0}
        # S3*: Audit — sporadische Tiefenprüfung
        self.s3_star_audit={'last_audit':0, 'audit_interval':50, 'findings':[]}
        # S4: Intelligence — Umwelt-Scan, neue Bug-Klassen erkennen
        self.s4_intelligence={'novel_types':set(), 'environmental_shifts':[], 'predictions':{}}
        # S5: Policy — ultimative Identität, "Wer sind wir?"
        self.s5_policy={'identity':'bug_fixer','boundaries':set(), 'ethos':'minimize_surprise'}
        # S7: Algedonic Loop — Schmerz/Lust-Signal
        self.algedonic={'pain':0.0, 'pleasure':0.0, 'threshold':0.7}
        self.total_bugs=0
    
    # ═══════════ 7 SCHICHTEN ═══════════
    
    def _s1_operate(self, bt):
        """S1: Direkte Operation — welcher Fix für diesen Bug?"""
        if bt in self.s1_operations:
            ops=self.s1_operations[bt]
            if ops['total']>0:
                best_fix=max(ops['fixes'], key=ops['fixes'].get)
                rate=ops['fixes'][best_fix]/ops['total']
                return best_fix, rate
        return None, 0.0
    
    def _s2_coordinate(self, bt, fix, rate):
        """S2: Koordination — verhindert Oszillation zwischen Fixes"""
        coord=self.s2_coordination[bt]
        # Wenn mehrere Fixes aktiv → Konflikt
        if len(coord['active_fixes'])>1:
            coord['conflicts']+=1
            # Dämpfe Rate bei Konflikten
            rate*=0.7
        coord['active_fixes'].add(fix)
        return rate
    
    def _s3_control(self, rate):
        """S3: Interne Kontrolle — Ressourcen-Audit"""
        self.s3_control['total_ops']+=1
        # Effizienz: gleitender Durchschnitt der Raten
        n=self.s3_control['total_ops']
        self.s3_control['efficiency']=self.s3_control['efficiency']*(n-1)/n+rate/n
        self.s3_control['audit_log'].append(rate)
        # Bei Effizienz < 0.4 → Alarm
        if self.s3_control['efficiency']<0.4:
            self.algedonic['pain']+=0.1
        return rate
    
    def _s3_star_audit(self):
        """S3*: Sporadische Tiefenprüfung"""
        if self.total_bugs-self.s3_star_audit['last_audit']>=self.s3_star_audit['audit_interval']:
            self.s3_star_audit['last_audit']=self.total_bugs
            # Prüfe: Sind alle S1-Operationen gesund?
            for bt, ops in self.s1_operations.items():
                if ops['total']>=5 and ops['success']/ops['total']<0.3:
                    self.s3_star_audit['findings'].append(f"Weak:{bt}")
    
    def _s4_intelligence(self, bt, emb):
        """S4: Umwelt-Scan — erkennt neue Bug-Klassen"""
        if bt not in self.s1_operations or self.s1_operations[bt]['total']<2:
            self.s4_intelligence['novel_types'].add(bt)
            self.s4_intelligence['environmental_shifts'].append(bt)
        # Prädiktion: Welche Bug-Typen werden häufiger?
        if len(self.s4_intelligence['environmental_shifts'])>10:
            from collections import Counter
            trends=Counter(self.s4_intelligence['environmental_shifts'][-20:])
            self.s4_intelligence['predictions']=dict(trends.most_common(3))
    
    def _s5_policy(self, bt, fix, rate):
        """S5: Policy — 'Wer sind wir?' Ultimative Entscheidung"""
        # Identitäts-Check: Passt dieser Fix zu unserer Identität?
        if rate<0.15:
            # Zu unsicher → Policy verweigert
            return 0.0
        # Ethos: 'minimize_surprise' → hohe Rate = wenig Überraschung = gut
        if self.s5_policy['ethos']=='minimize_surprise':
            rate=min(1.0, rate*1.1)  # Belohne Sicherheit
        return rate
    
    def _s7_algedonic(self, success):
        """S7: Algedonic Loop — Schmerz/Lust"""
        if success:
            self.algedonic['pleasure']=min(1.0, self.algedonic['pleasure']+0.05)
            self.algedonic['pain']=max(0.0, self.algedonic['pain']-0.03)
        else:
            self.algedonic['pain']=min(1.0, self.algedonic['pain']+0.1)
            self.algedonic['pleasure']=max(0.0, self.algedonic['pleasure']-0.05)
    
    # ═══════════ BRAIN INTERFACE ═══════════
    
    def think(self,sig,emb):
        self.total_bugs+=1
        bt=sig.split(':')[0] if ':' in sig else sig
        
        # S1: Operations
        fix, rate=self._s1_operate(bt)
        if not fix:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                    'vsm_layer':'S1','reasoning':f'VSM S1: Kein Fix für {bt}.'}
        
        # S2: Coordination
        rate=self._s2_coordinate(bt, fix, rate)
        # S3: Control
        rate=self._s3_control(rate)
        # S4: Intelligence
        self._s4_intelligence(bt, emb)
        # S3*: Audit
        self._s3_star_audit()
        # S5: Policy
        rate=self._s5_policy(bt, fix, rate)
        
        if rate>0.2:
            return {'action':'APPLY_PATTERN','pattern':fix,'confidence':rate,
                    'vsm_layer':'S5 (Policy-approved)',
                    'algedonic':f'P:{self.algedonic["pleasure"]:.2f}/P:{self.algedonic["pain"]:.2f}',
                    'reasoning':f'VSM: S1→S5 Pipeline: {fix} (rate={rate:.2f})'}
        return {'action':'EXPLORE','pattern':None,'confidence':rate,
                'vsm_layer':'S5','reasoning':f'VSM: Policy verweigert {fix} (rate={rate:.2f})'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        ops=self.s1_operations[bt]
        ops['fixes'][pat]=ops['fixes'].get(pat,0)+1
        ops['total']+=1
        if success: ops['success']+=1
        self._s7_algedonic(success)
    
    def stats(self):
        return {'brain_type':'VSM 7-Layer (Stafford Beer)',
                'total_bugs':self.total_bugs,'vsm_layers':7,
                's1_operations':len(self.s1_operations),
                's2_conflicts':sum(c['conflicts'] for c in self.s2_coordination.values()),
                's3_efficiency':f'{self.s3_control["efficiency"]:.1%}',
                's4_novel_types':len(self.s4_intelligence['novel_types']),
                's7_algedonic':f'Pleasure={self.algedonic["pleasure"]:.2f} Pain={self.algedonic["pain"]:.2f}'}
    def __repr__(self): return f"VSMBrain(layers=7, ops={len(self.s1_operations)})"

if __name__=="__main__":
    print("GEHIRN AP — VSM 7-Layer (Beer)");
    b=VSMBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(30):
        bt=['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'][i%5]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<25,emb)
        if i%6==0: print(f"  Bug{i+1}: {dec['action']:15s} layer={dec.get('vsm_layer','?')} {dec.get('algedonic','')}")
    print(b.stats()); print("✅ Gehirn AP läuft.")
