"""
GEHIRN S — Markov Decision Process Brain
Bug-Fixing als sequenzielle Entscheidung: State→Action→Reward→Next State.
Value Iteration: V(s) = max_a Σ P(s'|s,a)[R + γ·V(s')]
Optimal Policy aus optimaler Value-Funktion ableiten.

Autor: Hermes + David | Coding Tentacle Gehirn Bibliothek
"""
import numpy as np
from collections import defaultdict

class MarkovBrain:
    """Gehirn S — MDP: Optimale Fix-Sequenz via Value-Iteration."""
    def __init__(self, gamma=0.9, theta=0.01):
        self.gamma=gamma; self.theta=theta
        self.transitions=defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        # {(state,action): {next_state: count}}
        self.rewards=defaultdict(lambda: defaultdict(float))  # {(state,action): avg_reward}
        self.values=defaultdict(float)
        self.total_bugs=0; self.policy=defaultdict(str)
    
    def think(self,sig,emb):
        self.total_bugs+=1
        bt=sig.split(':')[0] if ':' in sig else sig
        # Policy: Beste Aktion nach Value-Iteration
        if bt not in self.values:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                    'reasoning':f'Unbekannter State {bt}. Exploration.'}
        # Aktion mit höchstem Q-Wert
        best_action,max_q=None,-999
        for action in self.transitions[bt]:
            q=self.rewards[bt][action]
            for ns,cnt in self.transitions[bt][action].items():
                q+=self.gamma*self.values.get(ns,0)*cnt/sum(self.transitions[bt][action].values())
            if q>max_q: max_q=q; best_action=action
        if best_action:
            return {'action':'APPLY_PATTERN','pattern':best_action,
                    'confidence':min(1.0,max(0.1,max_q/10+0.5)),
                    'state_value':self.values[bt],
                    'reasoning':f"MDP: {bt}→{best_action} V={self.values[bt]:.2f} Q={max_q:.2f}"}
        return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                'reasoning':f'Keine gültige Aktion in State {bt}.'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        next_state=f"{bt}_solved" if success else f"{bt}_failed"
        self.transitions[bt][pat][next_state]+=1
        # Reward: +1 für success, -0.5 für failure
        r=1.0 if success else -0.5
        old_r=self.rewards[bt][pat]
        n=sum(self.transitions[bt][pat].values())
        self.rewards[bt][pat]=old_r+(r-old_r)/n
        # Value Iteration (inkrementell)
        self._value_iteration_step(bt)
    
    def _value_iteration_step(self,bt):
        max_v=-999
        for action in self.transitions[bt]:
            q=self.rewards[bt][action]
            total=sum(self.transitions[bt][action].values())
            for ns,cnt in self.transitions[bt][action].items():
                q+=self.gamma*self.values.get(ns,0)*cnt/total
            if q>max_v: max_v=q
        self.values[bt]=max(0,max_v)
    
    def stats(self):
        n_states=len(self.transitions)
        n_actions=sum(len(a) for a in self.transitions.values())
        return {'brain_type':'MDP Value-Iteration','total_bugs':self.total_bugs,
                'states':n_states,'actions':n_actions,
                'avg_value':f'{np.mean(list(self.values.values())):.2f}' if self.values else '0'}
    def __repr__(self): return f"MarkovBrain(states={len(self.transitions)})"

if __name__=="__main__":
    print("GEHIRN S — Markov Decision Process"); b=MarkovBrain()
    for i in range(15):
        bt=['NullPointer','OffByOne','TypeError'][i%3]
        pat={'NullPointer':'guard_clause','OffByOne':'boundary_check','TypeError':'type_convert'}[bt]
        dec=b.think(f"{bt}:file{i}.py:{i}",[0]*384)
        b.learn(f"{bt}:file{i}.py:{i}",pat,i<12 or i%3==1)
        if i%3==0: print(f"  Bug{i+1}: {dec['action']:15s} V={dec.get('state_value',0):.2f}")
    print(b.stats()); print("✅ Gehirn S läuft.")
