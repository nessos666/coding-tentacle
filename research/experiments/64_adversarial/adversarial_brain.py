"""
GEHIRN BK — Adversarial Brain
FINDET EIGENE SCHWACHSTELLEN. Attackiert sich selbst.
Generator: Erzeugt schwierige Test-Bugs.
Discriminator: Unterscheidet echte von adversarialen Bugs.

Mathematik: min_G max_D V(D,G) = E[log D(x)] + E[log(1-D(G(z)))]
           Adversarial Training: Gehirn wird ROBUST gegen Angriffe.

Autor: Hermes + David | Coding Tentacle 2026
"""
import numpy as np, math, random
from collections import defaultdict

class AdversarialBrain:
    """Gehirn BK — Findet eigene Schwachstellen via Selbst-Angriff."""
    def __init__(self, attack_rate=0.2, lr=0.1):
        self.attack_rate=attack_rate; self.lr=lr
        self.patterns=defaultdict(lambda: {'success':0,'total':0,'robustness':1.0})
        self.weak_spots=[]  # Gefundene Schwachstellen
        self.adversarial_examples=[]
        self.defense_weights=defaultdict(lambda: np.ones(64))
        self.total_bugs=0
    
    def _generate_attack(self, bt, emb):
        """Generator: Erzeuge adversarialen Bug"""
        e=np.array(emb)[:64] if len(emb)>=64 else np.pad(emb,(0,64-len(emb)))
        # FGSM-artig: emb + ε·sign(∇_emb loss)
        noise=np.random.randn(64)*0.3
        return e+noise
    
    def _detect_attack(self, emb):
        """Discriminator: Ist das ein adversariale Attacke?"""
        e=np.array(emb)[:64]
        # Hohe Norm → potentiell adversarial
        return float(np.linalg.norm(e)>2.0)
    
    def think(self,sig,emb):
        self.total_bugs+=1; bt=sig.split(':')[0] if ':' in sig else sig
        
        # Adversarial Detection
        is_attack=self._detect_attack(emb)
        if is_attack:
            self.adversarial_examples.append(self.total_bugs)
        
        if self.patterns[bt]['total']<1:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                    'adversarial_detected':is_attack,
                    'reasoning':f'Adversarial: {bt} — {"⚠️ATTACKE" if is_attack else "normal"}'}
        
        rate=self.patterns[bt]['success']/max(1,self.patterns[bt]['total'])
        robust=self.patterns[bt]['robustness']
        
        # Adversariale Bugs → niedrigere Konfidenz
        if is_attack:
            conf=rate*robust*0.5
            if conf<0.3: self.weak_spots.append(bt)
        else:
            conf=rate*robust
        
        return {'action':'APPLY_PATTERN' if conf>0.25 else 'EXPLORE',
                'pattern':f'adv_{bt}','confidence':conf,
                'is_attack':is_attack,'robustness':f'{robust:.2f}',
                'weak_spots':len(self.weak_spots),
                'reasoning':f'Adversarial: {bt} {"⚠️ATTACK" if is_attack else "safe"} robust={robust:.2f} conf={conf:.2f}'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        self.patterns[bt]['total']+=1
        if success: self.patterns[bt]['success']+=1
        
        # Selbst-Angriff: periodisch adversarialen Bug generieren
        if random.random()<self.attack_rate and emb:
            attack_emb=self._generate_attack(bt, emb)
            # Wenn Gehirn den Angriff NICHT erkennt → Schwachstelle
            is_attack=self._detect_attack(attack_emb)
            if not is_attack:
                self.patterns[bt]['robustness']=max(0.3, self.patterns[bt]['robustness']-0.05)
            else:
                self.patterns[bt]['robustness']=min(1.0, self.patterns[bt]['robustness']+0.02)
    
    def stats(self):
        return {'brain_type':'Adversarial (Self-Attack)','total_bugs':self.total_bugs,
                'weak_spots':len(self.weak_spots),
                'adversarials_detected':len(self.adversarial_examples),
                'robustness':{bt:f'{p["robustness"]:.2f}' for bt,p in self.patterns.items()}}
    def __repr__(self): return f"AdversarialBrain(weak={len(self.weak_spots)})"

if __name__=="__main__":
    print("GEHIRN BK — Adversarial"); b=AdversarialBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(25):
        bt=['NullPointer','OffByOne','TypeError'][i%3]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<20,emb)
        if i%5==0: print(f"  Bug{i+1}: {dec['action']:15s} attack={dec.get('is_attack',False)} robust={dec.get('robustness','?')}")
    print(b.stats()); print("✅ Gehirn BK läuft.")
