"""
GEHIRN AY — Curriculum Learning Brain
Lernt "einfache Bugs zuerst, schwere später".
Ordnung des Trainings nach Schwierigkeit.
Misst Bug-Schwierigkeit via: Fix-Erfolgsrate, Embedding-Komplexität, Neuheit.

Mathematik: Difficulty(bug) = α·(1-success_rate) + β·complexity + γ·novelty
           Curriculum: sortiere Bugs nach steigender Difficulty

Autor: Hermes + David | Coding Tentacle 2026
"""
import numpy as np, math, random
from collections import defaultdict, deque

class CurriculumBrain:
    """Gehirn AY — Ordnet eigenes Training: einfach → schwer."""
    def __init__(self, alpha=0.5, beta=0.3, gamma=0.2, stages=5):
        self.alpha=alpha; self.beta=beta; self.gamma=gamma
        self.stages=stages  # Curriculum-Stufen
        self.current_stage=0
        
        self.difficulty=defaultdict(float)  # {bug_type: difficulty_score}
        self.complexity=defaultdict(float)  # Embedding-Komplexität
        self.novelty=defaultdict(float)     # Wie neu/ungewohnt
        self.patterns=defaultdict(lambda: {'success':0,'total':0,'stage_learned':0})
        self.queue=[]  # Geordnete Warteschlange
        self.curriculum_progress=[]
        self.total_bugs=0
        self.ready_threshold=0.8  # Wann ist ein Stage "gemeistert"?
    
    def _compute_complexity(self, emb):
        """Embedding-Komplexität: Varianz der Features"""
        e=np.array(emb)[:64] if len(emb)>64 else emb
        return float(np.std(e))
    
    def _compute_novelty(self, bt):
        """Neuheit: 1/(1+count) — je öfter gesehen, desto weniger neu"""
        return 1.0/(1.0+self.patterns[bt]['total'])
    
    def _update_difficulty(self, bt, emb):
        """Schwierigkeit = α·(1-rate) + β·complexity + γ·novelty"""
        rate=self.patterns[bt]['success']/max(1,self.patterns[bt]['total'])
        comp=self._compute_complexity(emb)
        nov=self._compute_novelty(bt)
        
        self.complexity[bt]=comp
        self.novelty[bt]=nov
        self.difficulty[bt]=self.alpha*(1-rate)+self.beta*comp+self.gamma*nov
    
    def _advance_curriculum(self):
        """Prüfe ob aktueller Stage gemeistert → nächster Stage"""
        current_bugs=[bt for bt,p in self.patterns.items() if p['stage_learned']==self.current_stage]
        if not current_bugs: return
        avg_rate=np.mean([self.patterns[bt]['success']/max(1,self.patterns[bt]['total']) for bt in current_bugs])
        if avg_rate>=self.ready_threshold and self.current_stage<self.stages-1:
            self.current_stage+=1
            self.curriculum_progress.append(f'Stage {self.current_stage} at bug {self.total_bugs} (rate={avg_rate:.0%})')
    
    def _sort_queue(self):
        """Queue nach Difficulty sortieren"""
        self.queue=sorted(self.difficulty.keys(), key=lambda bt: self.difficulty[bt])
    
    def think(self,sig,emb):
        self.total_bugs+=1; bt=sig.split(':')[0] if ':' in sig else sig
        
        self._update_difficulty(bt, emb)
        self._sort_queue()
        self._advance_curriculum()
        
        # Ist dieser Bug-Typ im aktuellen Curriculum-Stage?
        if self.patterns[bt]['total']>=1:
            p=self.patterns[bt]
            rate=p['success']/max(1,p['total'])
            diff=self.difficulty[bt]
            stage=self.current_stage
            
            # Einfachere Bugs = höhere Konfidenz
            stage_boost=1.0-(stage/self.stages)*0.3
            conf=min(1.0, rate*stage_boost)
            
            return {'action':'APPLY_PATTERN' if conf>0.2 else 'EXPLORE',
                    'pattern':f'curriculum_{bt}','confidence':conf,
                    'difficulty':f'{diff:.2f}','stage':stage,
                    'queue_position':self.queue.index(bt)+1 if bt in self.queue else 0,
                    'reasoning':f'Curriculum: {bt} diff={diff:.2f} stage={stage}/{self.stages} conf={conf:.2f}'}
        
        # Neuer Bug → zum aktuellen Stage zuordnen
        self.patterns[bt]['stage_learned']=self.current_stage
        return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                'reasoning':f'Curriculum: {bt} neu. Stage={self.current_stage}.'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        p=self.patterns[bt]; p['total']+=1
        if success: p['success']+=1
        self._update_difficulty(bt, emb if emb else np.zeros(64))
    
    def stats(self):
        return {'brain_type':'Curriculum Learning','total_bugs':self.total_bugs,
                'stage':f'{self.current_stage+1}/{self.stages}',
                'curriculum_order':self.queue[:10],
                'difficulties':{bt:f'{v:.2f}' for bt,v in sorted(self.difficulty.items(),key=lambda x:x[1])[:5]},
                'progress':self.curriculum_progress[-3:]}
    def __repr__(self): return f"CurriculumBrain(stage={self.current_stage+1}/{self.stages})"

if __name__=="__main__":
    print("GEHIRN AY — Curriculum Learning"); b=CurriculumBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(30):
        bt=['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'][i%5]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<25,emb)
        if i%6==0: print(f"  Bug{i+1}: {dec['action']:15s} diff={dec.get('difficulty','?')} stage={dec.get('stage',0)}")
    print(b.stats()); print("✅ Gehirn AY läuft.")
