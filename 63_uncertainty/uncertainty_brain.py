"""
GEHIRN BJ — Uncertainty/Posterior Brain
VOLLE BAYESIANISCHE VERTEILUNG. Nicht nur Punkt-Konfidenz.
Beta-Distribution pro Pattern: Beta(α=successes+1, β=failures+1).
Posterior = P(success_rate | data) — nicht nur P(success).

Mathematik: θ ~ Beta(α, β)  wobei α=successes+1, β=failures+1
           HDI = [θ_low, θ_high]  (Highest Density Interval, 95%)
           P(better than threshold) = 1 - CDF_Beta(threshold)

Autor: Hermes + David | Coding Tentacle 2026
"""
import numpy as np, math
from collections import defaultdict

class UncertaintyBrain:
    """Gehirn BJ — Volle Bayesianische Posterior-Verteilung."""
    def __init__(self, prior_alpha=1.0, prior_beta=1.0):
        self.prior_a=prior_alpha; self.prior_b=prior_beta
        self.patterns=defaultdict(lambda: {'alpha':prior_alpha,'beta':prior_beta,'total':0})
        self.total_bugs=0
    
    def _get_posterior(self, bt):
        p=self.patterns[bt]
        return p['alpha'], p['beta']
    
    def _posterior_mean(self, alpha, beta):
        return alpha/(alpha+beta)
    
    def _posterior_std(self, alpha, beta):
        return math.sqrt(alpha*beta/((alpha+beta)**2*(alpha+beta+1)))
    
    def _hdi(self, alpha, beta, prob=0.95):
        """Highest Density Interval: wo liegen 95% der Wahrscheinlichkeit?"""
        mean=self._posterior_mean(alpha, beta)
        std=self._posterior_std(alpha, beta)
        return max(0,mean-2*std), min(1,mean+2*std)
    
    def _prob_better_than(self, alpha, beta, threshold=0.5):
        """P(success_rate > threshold) via Normal-Approximation"""
        mean=self._posterior_mean(alpha, beta)
        std=self._posterior_std(alpha, beta)
        if std<0.001: return 1.0 if mean>threshold else 0.0
        z=(threshold-mean)/std
        # Normal CDF Approximation
        return 0.5*math.erfc(z/math.sqrt(2))
    
    def think(self,sig,emb):
        self.total_bugs+=1; bt=sig.split(':')[0] if ':' in sig else sig
        
        if self.patterns[bt]['total']<1:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                    'reasoning':f'Uncertainty: {bt} — Prior Beta(1,1).'}
        
        alpha,beta=self._get_posterior(bt)
        mean=self._posterior_mean(alpha, beta)
        std=self._posterior_std(alpha, beta)
        low,high=self._hdi(alpha, beta)
        p_better=self._prob_better_than(alpha, beta, 0.5)
        
        action='APPLY_PATTERN' if mean>0.4 or p_better>0.7 else 'EXPLORE'
        
        return {'action':action,'pattern':f'uncertain_{bt}','confidence':mean,
                'posterior':f'Beta({alpha:.0f},{beta:.0f})',
                'hdi_95':f'[{low:.0%}, {high:.0%}]',
                'p_better_than_50':f'{p_better:.0%}',
                'std':f'{std:.3f}',
                'reasoning':f'Uncertainty: {bt} ~Beta({alpha:.0f},{beta:.0f}) mean={mean:.0%} '
                           f'HDI=[{low:.0%},{high:.0%}] P(>50%)={p_better:.0%}'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        p=self.patterns[bt]
        if success: p['alpha']+=1
        else: p['beta']+=1
        p['total']+=1
    
    def stats(self):
        return {'brain_type':'Uncertainty/Posterior (Beta)','total_bugs':self.total_bugs,
                'posteriors':{bt:f'Beta({p["alpha"]:.0f},{p["beta"]:.0f})' for bt,p in self.patterns.items() if p['total']>0}}
    def __repr__(self): return f"UncertaintyBrain(types={sum(1 for p in self.patterns.values() if p['total']>0)})"

if __name__=="__main__":
    print("GEHIRN BJ — Uncertainty/Posterior"); b=UncertaintyBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(20):
        bt=['NullPointer','OffByOne','TypeError'][i%3]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<16,emb)
        if i%5==0: print(f"  Bug{i+1}: {dec['action']:15s} {dec.get('posterior','?')} HDI={dec.get('hdi_95','?')}")
    print(b.stats()); print("✅ Gehirn BJ läuft.")
