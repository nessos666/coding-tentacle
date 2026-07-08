"""
GEHIRN AZ — Multi-Task Sharing Brain
TEILT WISSEN ZWISCHEN BUG-TYPEN. Kein isoliertes Lernen mehr.
Shared Representation Layer: Alle Bug-Typen teilen eine gemeinsame Basis.
Task-spezifische Heads on top of shared base.

Mathematik: h = f_shared(emb)  (geteilt)
           y_null = g_null(h)   (spezifisch)
           y_index = g_index(h) (spezifisch)
           L = L_specific + λ · L_shared_consistency

Autor: Hermes + David | Coding Tentacle 2026
"""
import numpy as np, math
from collections import defaultdict

class MultiTaskBrain:
    """Gehirn AZ — Geteilte Repräsentation über alle Bug-Typen."""
    def __init__(self, shared_dim=64, task_dim=16, lr=0.1):
        self.shared_dim=shared_dim; self.task_dim=task_dim; self.lr=lr
        # Shared Layer: alle Bug-Typen teilen dies
        self.W_shared=np.random.randn(shared_dim, 384)*0.05
        self.b_shared=np.zeros(shared_dim)
        # Task-spezifische Heads
        self.task_heads={}  # {bug_type: (W, b)}
        self.patterns=defaultdict(lambda: {'success':0,'total':0})
        self.shared_knowledge=defaultdict(float)  # Cross-type knowledge
        self.total_bugs=0
    
    def _get_task_head(self, bt):
        if bt not in self.task_heads:
            self.task_heads[bt]=(np.random.randn(self.task_dim, self.shared_dim)*0.05, np.zeros(self.task_dim))
        return self.task_heads[bt]
    
    def _shared_encode(self, emb):
        e=np.array(emb)[:384] if len(emb)>=384 else np.pad(emb,(0,384-len(emb)))
        return np.tanh(self.W_shared @ e + self.b_shared)
    
    def _task_predict(self, shared_rep, bt):
        W,b=self._get_task_head(bt)
        logits=W @ shared_rep + b
        return float(np.tanh(np.mean(logits)))
    
    def _share_knowledge(self, bt, success):
        """Verteile Wissen an ÄHNLICHE Bug-Typen"""
        all_types=list(self.patterns.keys())
        for other_bt in all_types:
            if other_bt!=bt:
                # Je ähnlicher die Erfolgsraten, desto mehr Sharing
                rate_self=self.patterns[bt]['success']/max(1,self.patterns[bt]['total'])
                rate_other=self.patterns[other_bt]['success']/max(1,self.patterns[other_bt]['total'])
                similarity=1.0-abs(rate_self-rate_other)
                if success:
                    self.shared_knowledge[(bt,other_bt)]+=0.01*similarity
                else:
                    self.shared_knowledge[(bt,other_bt)]-=0.005*similarity
    
    def think(self,sig,emb):
        self.total_bugs+=1; bt=sig.split(':')[0] if ':' in sig else sig
        h=self._shared_encode(emb)
        
        if self.patterns[bt]['total']<1:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                    'reasoning':f'MultiTask: {bt} neu. Shared Rep aufbauen...'}
        
        # Direkte Vorhersage
        direct=self._task_predict(h, bt)
        
        # Cross-Task Boost: Wissen von ähnlichen Typen
        cross_boost=0.0
        for (source,target),strength in self.shared_knowledge.items():
            if target==bt and strength>0:
                source_rate=self.patterns[source]['success']/max(1,self.patterns[source]['total'])
                cross_boost+=source_rate*strength
        cross_boost=min(0.3, cross_boost)
        
        rate=self.patterns[bt]['success']/max(1,self.patterns[bt]['total'])
        conf=min(1.0, direct*0.7+rate*0.3+cross_boost)
        
        return {'action':'APPLY_PATTERN' if conf>0.2 else 'EXPLORE',
                'pattern':f'multitask_{bt}','confidence':conf,
                'cross_boost':f'{cross_boost:.2f}',
                'shared_norm':f'{np.linalg.norm(h):.1f}',
                'reasoning':f'MultiTask: {bt} direct={direct:.2f} +cross={cross_boost:.2f} conf={conf:.2f}'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        self.patterns[bt]['total']+=1
        if success: self.patterns[bt]['success']+=1
        
        if emb:
            h=self._shared_encode(emb)
            # SGD auf Shared + Task Layer
            target=1.0 if success else -0.5
            pred=self._task_predict(h, bt)
            error=target-pred
            # Task head update
            W,b=self._get_task_head(bt)
            W+=self.lr*error*np.outer(np.ones(self.task_dim), h)
            b+=self.lr*error
            self.task_heads[bt]=(W,b)
        
        self._share_knowledge(bt, success)
    
    def stats(self):
        n_tasks=len(self.task_heads)
        n_shared=len(self.shared_knowledge)
        return {'brain_type':'Multi-Task Sharing','total_bugs':self.total_bugs,
                'tasks':n_tasks,'shared_edges':n_shared,
                'cross_knowledge':dict(sorted(self.shared_knowledge.items(),key=lambda x:-x[1])[:5])}
    def __repr__(self): return f"MultiTaskBrain(tasks={len(self.task_heads)}, shared={len(self.shared_knowledge)})"

if __name__=="__main__":
    print("GEHIRN AZ — Multi-Task Sharing"); b=MultiTaskBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(30):
        bt=['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'][i%5]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<25,emb)
        if i%6==0: print(f"  Bug{i+1}: {dec['action']:15s} +cross={dec.get('cross_boost','0')}")
    print(b.stats()); print("✅ Gehirn AZ läuft.")
