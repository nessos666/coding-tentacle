"""
GEHIRN U — Mixture of Experts Brain (Jacobs 1991)
Mehrere Experten, jeder spezialisiert auf Bug-Typen.
Gating-Netzwerk: Softmax wählt besten Experten pro Input.
Mathematik: y = Σ g_i(x) · f_i(x) mit g = softmax(W_g · x)

Autor: Hermes + David | Coding Tentacle Gehirn Bibliothek
"""
import numpy as np, math
from collections import defaultdict

class MixtureOfExpertsBrain:
    """Gehirn U — Spezialisierte Experten + Gating-Netzwerk."""
    def __init__(self, n_experts=5, lr=0.1):
        self.n_experts=n_experts; self.lr=lr
        self.gate_weights=np.random.randn(n_experts, 64)*0.1  # 64dim gate
        self.experts=defaultdict(lambda: {'success':0,'total':0,'last_pattern':''})
        self.expert_map={}  # {bug_type: expert_idx}
        self.total_bugs=0
    
    def _gating(self, emb):
        e=np.array(emb)[:64] if len(emb)>64 else np.pad(emb,(0,max(0,64-len(emb))))
        logits=self.gate_weights @ e
        logits-=np.max(logits)
        probs=np.exp(logits)/np.sum(np.exp(logits))
        return probs
    
    def think(self,sig,emb):
        self.total_bugs+=1
        bt=sig.split(':')[0] if ':' in sig else sig
        probs=self._gating(emb)
        best_expert=np.argmax(probs)
        # Wenn dieser Bug-Typ schon einen Experten hat, nimm den
        if bt in self.expert_map: best_expert=self.expert_map[bt]
        exp_data=self.experts[best_expert]
        if exp_data['total']>0:
            rate=exp_data['success']/exp_data['total']
            conf=min(1.0,rate*exp_data['total']/(exp_data['total']+2))
            pat=exp_data['last_pattern'] if exp_data['last_pattern'] else f'expert_{best_expert}_fix'
            return {'action':'APPLY_PATTERN' if conf>0.3 else 'EXPLORE','pattern':pat,
                    'confidence':conf,'expert':int(best_expert),'gate_prob':float(probs[best_expert]),
                    'reasoning':f"MoE: Expert {best_expert} (gate={probs[best_expert]:.2f}) conf={conf:.2f}"}
        return {'action':'EXPLORE','pattern':None,'confidence':0.0,'expert':int(best_expert),
                'reasoning':f"MoE: Expert {best_expert} neu. Exploration."}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        probs=self._gating(emb) if emb else np.ones(self.n_experts)/self.n_experts
        best_expert=np.argmax(probs)
        if bt in self.expert_map: best_expert=self.expert_map[bt]
        else: self.expert_map[bt]=best_expert
        e=self.experts[best_expert]
        e['success']+=1 if success else 0
        e['total']+=1
        e['last_pattern']=pat
        # Gate updaten: verstärke richtige Zuordnung
        if emb:
            e_arr=np.array(emb)[:64] if len(emb)>64 else np.pad(emb,(0,max(0,64-len(emb))))
            self.gate_weights[best_expert]+=self.lr*(1 if success else 0.3)*e_arr
    
    def stats(self):
        active=sum(1 for e in self.experts.values() if e['total']>0)
        rates={i:f"{e['success']/max(1,e['total']):.0%}" for i,e in self.experts.items() if e['total']>0}
        return {'brain_type':'Mixture of Experts','total_bugs':self.total_bugs,
                'active_experts':active,'expert_rates':rates}
    def __repr__(self): return f"MoEBrain(experts={sum(1 for e in self.experts.values() if e['total']>0)})"

if __name__=="__main__":
    print("GEHIRN U — Mixture of Experts"); b=MixtureOfExpertsBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(15):
        bt=['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'][i%5]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<12,emb)
        if i%4==0: print(f"  Bug{i+1}: {dec['action']:15s} expert={dec.get('expert','?')}")
    print(b.stats()); print("✅ Gehirn U läuft.")
