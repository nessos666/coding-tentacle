"""
GEHIRN AD — Hierarchical RL / Options Brain (Sutton 1999, Bacon 2017)
Temporale Abstraktionen: Options = wiederverwendbare Subroutinen.
Options können andere Options aufrufen. Hierarchische Planung.
Mathematik: Q_Ω(s,o) = E[R + γ·max_o' Q_Ω(s',o')]  (Option-level Q)

Autor: Hermes + David | Coding Tentacle 2026
"""
import numpy as np, math, random
from collections import defaultdict

class Option:
    def __init__(self, name, parent=None):
        self.name=name
        self.parent=parent
        self.sub_options=[]  # Kind-Optionen
        self.Q=defaultdict(float)  # State-Action values
        self.termination=defaultdict(float)  # P(terminate|state)
        self.success_count=0; self.total_count=0

class HierarchicalRLBrain:
    """Gehirn AD — Options-Framework. Hierarchische Bug-Fix-Strategien."""
    def __init__(self, gamma=0.9, alpha=0.1, epsilon=0.2):
        self.gamma=gamma; self.alpha=alpha; self.epsilon=epsilon
        self.root=Option("root")
        self.options={}  # {bug_type: Option}
        self.current_option=None
        self.total_bugs=0
    
    def _get_or_create_option(self, bt):
        if bt not in self.options:
            opt=Option(bt, self.root)
            self.root.sub_options.append(opt)
            # Sub-Options für diesen Bug-Typ
            for sub in ['analyze','generate_fix','validate','refine']:
                sub_opt=Option(f"{bt}_{sub}", opt)
                opt.sub_options.append(sub_opt)
            self.options[bt]=opt
        return self.options[bt]
    
    def think(self,sig,emb):
        self.total_bugs+=1
        bt=sig.split(':')[0] if ':' in sig else sig
        opt=self._get_or_create_option(bt)
        
        if opt.total_count<2:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                    'option':opt.name,'reasoning':f'HRL: Option {bt} neu. Sub-Options aufbauen...'}
        
        # ε-greedy auf Option-Ebene
        best_q=0; sub=None
        if random.random()<self.epsilon:
            sub=random.choice(opt.sub_options) if opt.sub_options else None
        else:
            for s in opt.sub_options:
                q=opt.Q[s.name]
                if q>best_q: best_q=q; sub=s
        
        if sub:
            rate=opt.success_count/max(1,opt.total_count)
            conf=min(1.0,rate*best_q/10)
            return {'action':'APPLY_PATTERN' if conf>0.3 else 'EXPLORE',
                    'pattern':sub.name,'confidence':conf,
                    'option':opt.name,'sub_option':sub.name,
                    'reasoning':f'HRL: {opt.name}→{sub.name} Q={best_q:.2f} conf={conf:.2f}'}
        return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                'reasoning':f'HRL: {bt} keine Sub-Option verfügbar.'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        opt=self._get_or_create_option(bt)
        opt.total_count+=1
        if success: opt.success_count+=1
        
        if emb:
            # Update Q-Werte für Sub-Options
            for sub in opt.sub_options:
                r=1.0 if success else -0.5
                old_q=opt.Q[sub.name]
                # Bellman-Update auf Option-Level
                next_qs=[opt.Q[s.name] for s in opt.sub_options]
                max_next_q=max(next_qs) if next_qs else 0
                opt.Q[sub.name]=old_q+self.alpha*(r+self.gamma*max_next_q-old_q)
    
    def stats(self):
        n=len(self.options)
        total_sub=sum(len(o.sub_options) for o in self.options.values())
        return {'brain_type':'Hierarchical RL (Options)','total_bugs':self.total_bugs,
                'options':n,'sub_options':total_sub,
                'option_tree':{bt:f"{o.success_count}/{o.total_count}" for bt,o in self.options.items()}}
    def __repr__(self): return f"HRLBrain(options={len(self.options)})"

if __name__=="__main__":
    print("GEHIRN AD — Hierarchical RL (Options)"); b=HierarchicalRLBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(15):
        bt=['NullPointer','OffByOne','TypeError'][i%3]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<12,emb)
        if i%4==0: print(f"  Bug{i+1}: {dec['action']:15s} sub={dec.get('sub_option','?')}")
    print(b.stats()); print("✅ Gehirn AD läuft.")
