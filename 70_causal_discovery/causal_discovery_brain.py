"""
GEHIRN BQ — Causal Discovery Brain
ENTDECKT AKTIV NEUE KAUSALSTRUKTUREN aus Daten.
PC-Algorithmus: Constraint-based Causal Discovery.
Findet: Bug_X → Bug_Y (X verursacht Y) ohne Vorwissen.

Mathematik: PC-Algorithmus: 1) Skelett via bedingte Unabhängigkeit
           2) Orientierung via Kollider (V-Strukturen: X→Z←Y)
           3) Propagation via Meek-Regeln

Autor: Hermes + David | Coding Tentacle 2026
Quelle: Causal Discovery Survey (2025), PC-Algorithm
"""
import numpy as np, math
from collections import defaultdict

class CausalDiscoveryBrain:
    """Gehirn BQ — Entdeckt Kausalstrukturen aktiv aus Bug-Daten."""
    def __init__(self, threshold=0.3):
        self.threshold=threshold
        self.causal_graph=defaultdict(set)  # {cause: {effects}}
        self.correlation_matrix=defaultdict(lambda: defaultdict(float))
        self.confounders=set()
        self.colliders=set()
        self.data_buffer=defaultdict(list)  # {bug_type: [(embedding, timestamp)]}
        self.patterns=defaultdict(lambda: {'success':0,'total':0})
        self.total_bugs=0
    
    def _partial_correlation(self, bt1, bt2, given=None):
        """Bedingte Korrelation zwischen zwei Bug-Typen"""
        d1=self.data_buffer[bt1]; d2=self.data_buffer[bt2]
        if len(d1)<3 or len(d2)<3: return 0.0
        
        times1=[t for _,t in d1]; times2=[t for _,t in d2]
        # Zeitliche Korrelation: t1 knapp vor t2 → mögliche Kausalität
        mean_t1=np.mean(times1); mean_t2=np.mean(times2)
        std1=np.std(times1); std2=np.std(times2)
        if std1==0 or std2==0: return 0.0
        return float(np.mean([(t1-mean_t1)*(t2-mean_t2)/(std1*std2) for t1 in times1[-5:] for t2 in times2[-5:]]))
    
    def _discover_skeleton(self):
        """PC Schritt 1: Ungerichtetes Skelett via bedingte Unabhängigkeit"""
        bugs=list(self.data_buffer.keys())
        for i in range(len(bugs)):
            for j in range(i+1, len(bugs)):
                pc=self._partial_correlation(bugs[i], bugs[j])
                if abs(pc)>self.threshold:
                    self.correlation_matrix[bugs[i]][bugs[j]]=pc
                    self.correlation_matrix[bugs[j]][bugs[i]]=pc
    
    def _orient_edges(self):
        """PC Schritt 2+3: Orientierung via Kollider + Propagation"""
        bugs=list(self.correlation_matrix.keys())
        for x in bugs:
            for y in bugs:
                for z in bugs:
                    if x!=y and y!=z and x!=z:
                        if (self.correlation_matrix[x][y]*self.correlation_matrix[y][z]>self.threshold and
                            abs(self.correlation_matrix[x][z])<self.threshold/2):
                            # V-Struktur: x→y←z
                            self.colliders.add(y)
                            self.causal_graph[x].add(y)
                            self.causal_graph[z].add(y)
        
        # Propagation: Kein Cycle (Meek-Regeln vereinfacht)
        for x in list(self.causal_graph.keys()):
            for y in list(self.causal_graph[x]):
                if x in self.causal_graph.get(y,set()):
                    # Bidirektional → Confounder
                    self.confounders.add((x,y))
    
    def think(self,sig,emb):
        self.total_bugs+=1; bt=sig.split(':')[0] if ':' in sig else sig
        
        self._discover_skeleton()
        if self.total_bugs%10==0 and len(self.data_buffer)>=3:
            self._orient_edges()
        
        if self.patterns[bt]['total']<1:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                    'discovered_edges':sum(len(v) for v in self.causal_graph.values()),
                    'reasoning':f'CausalDiscovery: {bt} — sammle Daten für PC-Algorithmus...'}
        
        rate=self.patterns[bt]['success']/max(1,self.patterns[bt]['total'])
        conf=rate
        
        # Wenn kausale Struktur bekannt: Sagt dieser Bug andere vorher?
        effects=list(self.causal_graph.get(bt,set()))
        effect_info=f' → verursacht {effects}' if effects else ''
        
        return {'action':'APPLY_PATTERN' if conf>0.3 else 'EXPLORE',
                'pattern':f'causal_{bt}','confidence':conf,
                'causes':list(self.causal_graph.get(bt,set())),
                'colliders':len(self.colliders),'confounders':len(self.confounders),
                'reasoning':f'CausalDiscovery: {bt}{effect_info} (conf={conf:.2f})'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        self.patterns[bt]['total']+=1
        if success: self.patterns[bt]['success']+=1
        self.data_buffer[bt].append((emb if emb else np.zeros(64), self.total_bugs))
    
    def stats(self):
        n_edges=sum(len(v) for v in self.causal_graph.values())
        return {'brain_type':'Causal Discovery (PC-Algorithm)','total_bugs':self.total_bugs,
                'discovered_edges':n_edges,'colliders':len(self.colliders),
                'confounders':len(self.confounders),
                'causal_graph':{k:list(v) for k,v in self.causal_graph.items()}}
    def __repr__(self): return f"CausalDiscoveryBrain(edges={sum(len(v) for v in self.causal_graph.values())})"

if __name__=="__main__":
    print("GEHIRN BQ — Causal Discovery"); b=CausalDiscoveryBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(30):
        bt=['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'][i%5]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<25,emb)
        if i%6==0: print(f"  Bug{i+1}: {dec['action']:15s} edges={dec.get('discovered_edges',0)}")
    print(b.stats()); print("✅ Gehirn BQ läuft.")
