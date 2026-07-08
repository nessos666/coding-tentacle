"""
GEHIRN AL — Chunking / Rule Learning Brain (SOAR-Stil)
Automatische Regel-Generierung aus Erfahrung.
SOAR-Chunking: WENN Bug_X + Fix_Y → Ergebnis_Z (wiederholt),
DANN: Erzeuge Regel IF Bug_X THEN Fix_Y (ohne Zwischenschritte).

Autor: Hermes + David | Coding Tentacle 2026
Quelle: SOAR Cognitive Architecture (Laird, CMU)
"""
import numpy as np
from collections import defaultdict

class ChunkingBrain:
    """Gehirn AL — Automatische Regel-Generierung via SOAR-Chunking."""
    def __init__(self, chunk_threshold=3):
        self.threshold=chunk_threshold  # Wie viele Wiederholungen für Chunk
        self.traces=defaultdict(list)  # {bug_type: [(pattern, success)]}  — episodische Spuren
        self.rules=[]  # [(condition, action, utility, confidence)]
        self.patterns=defaultdict(lambda: {'success':0,'total':0})
        self.total_bugs=0
    
    def think(self,sig,emb):
        self.total_bugs+=1
        bt=sig.split(':')[0] if ':' in sig else sig
        # Suche passende Regel
        candidates=[r for r in self.rules if r[0]==bt]
        if candidates:
            best=max(candidates, key=lambda r: r[2]*r[3])
            return {'action':'APPLY_PATTERN','pattern':best[1],
                    'confidence':best[3],'utility':best[2],
                    'reasoning':f'Chunking: Regel {bt}→{best[1]} (U={best[2]:.1f})'}
        if self.patterns[bt]['total']>=1:
            rate=self.patterns[bt]['success']/max(1,self.patterns[bt]['total'])
            return {'action':'APPLY_PATTERN' if rate>0.5 else 'EXPLORE',
                    'pattern':f'direct_{bt}','confidence':rate,
                    'reasoning':f'Chunking: Direkter Match {bt} (rate={rate:.0%})'}
        return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                'reasoning':f'Chunking: Kein Wissen über {bt}.'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        self.patterns[bt]['total']+=1
        if success: self.patterns[bt]['success']+=1
        
        # Episodische Spur
        self.traces[bt].append((pat, success))
        if len(self.traces[bt])>50: self.traces[bt]=self.traces[bt][-50:]
        
        # CHUNKING: Wenn genug Wiederholungen → erzeuge Regel
        successes=[t for t in self.traces[bt] if t[1]]
        if len(successes)>=self.threshold:
            # Häufigstes Pattern
            from collections import Counter
            pat_counter=Counter(t[0] for t in successes)
            best_pat,best_count=pat_counter.most_common(1)[0]
            
            if best_count>=self.threshold:
                # Prüfe ob Regel schon existiert
                existing=[r for r in self.rules if r[0]==bt and r[1]==best_pat]
                if existing:
                    existing[0]=(bt,best_pat,existing[0][2]+5,min(1.0,best_count/len(self.traces[bt])))
                else:
                    # NEUE REGEL!
                    utility=best_count*10.0
                    confidence=min(1.0,best_count/len(self.traces[bt]))
                    self.rules.append((bt, best_pat, utility, confidence))
    
    def stats(self):
        return {'brain_type':'Chunking/Rule Learning (SOAR)','total_bugs':self.total_bugs,
                'rules':len(self.rules),'chunk_threshold':self.threshold,
                'top_rules':[(f'{c}→{a}',f'U={u:.0f}') for c,a,u,cf in sorted(self.rules,key=lambda r:-r[2])[:5]]}
    def __repr__(self): return f"ChunkingBrain(rules={len(self.rules)})"

if __name__=="__main__":
    print("GEHIRN AL — Chunking/Rule Learning"); b=ChunkingBrain()
    for i in range(25):
        bt=['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'][i%5]
        dec=b.think(f"{bt}:f{i}.py:{i}",[0]*384)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<20)
        if i%5==0: print(f"  Bug{i+1}: {dec['action']:15s} rules={len(b.rules)}")
    print(b.stats()); print("✅ Gehirn AL läuft.")
