"""
GEHIRN AG — SOAR Cognitive Architecture Brain (Laird/Newell/Simon, CMU ~1983-2024)
Vollständige kognitive Architektur:
  - Working Memory (aktuelle Bug-Situation)
  - Procedural Memory (Production Rules: IF pattern THEN fix)
  - Semantic Memory (Fakten über Bug-Typen)
  - Episodic Memory (vergangene Bug-Erfahrungen)
  - Decision Cycle: Input → Elaborate → Propose → Decide → Apply → Output

Autor: Hermes + David | Coding Tentacle 2026
"""
import numpy as np, math, random
from collections import defaultdict

class ProductionRule:
    def __init__(self, condition, action, utility=50.0):
        self.condition=condition  # Bug-Typ (String)
        self.action=action        # Fix-Pattern
        self.utility=utility       # Erwarteter Nutzen [0,100]
        self.fired=0               # Anzahl Aktivierungen
        self.successes=0

class SOARBrain:
    """Gehirn AG — Vollständige kognitive Architektur nach SOAR."""
    def __init__(self):
        # Working Memory (der aktuelle Zustand)
        self.wm={'current_bug':None,'current_embedding':None,'context':{}}
        # Procedural Memory (Produktionsregeln)
        self.production_rules=[]
        # Semantic Memory (Fakten)
        self.semantic={'bug_types':{},'pattern_stats':defaultdict(lambda: {'success':0,'total':0})}
        # Episodic Memory
        self.episodic=[]
        # Decision Cycle Counter
        self.decision_cycles=0
        self.total_bugs=0
    
    def _elaborate(self, sig, emb):
        """Phase 1: Working Memory mit Kontext füllen"""
        bt=sig.split(':')[0] if ':' in sig else sig
        self.wm['current_bug']=bt
        self.wm['current_embedding']=np.array(emb)
        self.wm['context']={'bug_type':bt,'has_rule':any(r.condition==bt for r in self.production_rules)}
    
    def _propose(self):
        """Phase 2: Passende Produktionsregeln vorschlagen"""
        bt=self.wm['current_bug']
        candidates=[r for r in self.production_rules if r.condition==bt]
        # Auch semantisch ähnliche Bug-Typen berücksichtigen
        if not candidates:
            for r in self.production_rules:
                if bt.lower() in r.condition.lower() or r.condition.lower() in bt.lower():
                    candidates.append(r)
        return candidates
    
    def _decide(self, candidates):
        """Phase 3: Beste Regel nach Utility auswählen"""
        if not candidates: return None
        # Softmax über Utility-Werte
        utils=np.array([r.utility for r in candidates])
        probs=np.exp(utils/10)/np.sum(np.exp(utils/10))
        chosen=np.random.choice(len(candidates), p=probs)
        return candidates[chosen]
    
    def _apply(self, rule):
        """Phase 4: Aktion ausführen"""
        if rule:
            rule.fired+=1
            success_rate=rule.successes/max(1,rule.fired)
            return rule.action, success_rate
        return None, 0.0
    
    def think(self,sig,emb):
        self.total_bugs+=1
        # SOAR Decision Cycle
        self._elaborate(sig, emb)
        candidates=self._propose()
        chosen=self._decide(candidates)
        action_name, rate=self._apply(chosen)
        
        if chosen and rate>0.3:
            return {'action':'APPLY_PATTERN','pattern':action_name,
                    'confidence':rate,'utility':chosen.utility,
                    'decision_cycles':self.decision_cycles,
                    'reasoning':f'SOAR: {chosen.condition}→{chosen.action} (U={chosen.utility:.0f})'}
        return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                'reasoning':f'SOAR: Keine Regel für {self.wm["current_bug"]}. Lerne neue Regel...'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        # Semantic Memory updaten
        self.semantic['pattern_stats'][pat]['total']+=1
        if success: self.semantic['pattern_stats'][pat]['success']+=1
        # Episodic Memory
        self.episodic.append({'bug':bt,'pattern':pat,'success':success,'time':self.total_bugs})
        if len(self.episodic)>100: self.episodic=self.episodic[-100:]
        
        # Production Rule lernen/updaten
        existing=[r for r in self.production_rules if r.condition==bt and r.action==pat]
        if existing:
            existing[0].successes+=1 if success else 0
            existing[0].utility+=10 if success else -5
            existing[0].utility=max(0,min(100,existing[0].utility))
        elif success:
            self.production_rules.append(ProductionRule(bt, pat))
        self.decision_cycles+=1
    
    def stats(self):
        return {'brain_type':'SOAR Cognitive Architecture','total_bugs':self.total_bugs,
                'production_rules':len(self.production_rules),
                'episodic_memories':len(self.episodic),
                'semantic_facts':len(self.semantic['pattern_stats'])}
    def __repr__(self): return f"SOARBrain(rules={len(self.production_rules)}, episodic={len(self.episodic)})"

if __name__=="__main__":
    print("GEHIRN AG — SOAR Cognitive Architecture"); b=SOARBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(20):
        bt=['NullPointer','OffByOne','TypeError'][i%3]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<16,emb)
        if i%5==0: print(f"  Cycle{i+1}: {dec['action']:15s} U={dec.get('utility',0):.0f}")
    print(b.stats()); print("✅ Gehirn AG läuft.")
