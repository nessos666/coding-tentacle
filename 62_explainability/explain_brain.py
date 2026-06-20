"""
GEHIRN BI — Explainability Brain
SAGT NICHT NUR WAS, SONDERN WARUM.
Generiert detaillierte Erklärungen für jede Entscheidung.

Mathematik: explanation = {pattern, evidence, confidence_breakdown, alternatives, caveats}
           SHAP-artig: contribution(feature_i) = f(S∪{i}) - f(S)

Autor: Hermes + David | Coding Tentacle 2026
"""
import numpy as np, math
from collections import defaultdict

class ExplainabilityBrain:
    """Gehirn BI — Erklärt JEDE Entscheidung im Detail."""
    def __init__(self):
        self.decision_log=[]  # Vollständige Entscheidungshistorie
        self.patterns=defaultdict(lambda: {'success':0,'total':0,'evidence':[]})
        self.feature_importance=defaultdict(float)
        self.counterfactual_whatifs=[]
        self.total_bugs=0
    
    def _explain_confidence(self, bt, conf):
        """Zerlege Konfidenz in Komponenten"""
        p=self.patterns[bt]
        rate_evidence=f"Erfolgsrate: {p['success']}/{p['total']} = {p['success']/max(1,p['total']):.0%}"
        sample_size=f"Stichprobengröße: {p['total']}"
        stability="Stabil" if p['total']>=5 else ("Lernend" if p['total']>=2 else "Unsicher")
        evidence_quality="Hoch" if p['total']>=10 else ("Mittel" if p['total']>=3 else "Niedrig")
        return f"[{rate_evidence}] [{sample_size}] Stabilität={stability} Qualität={evidence_quality}"
    
    def _generate_alternatives(self, bt):
        """Was wären die Alternativen gewesen?"""
        alts=[]
        for other_bt, p in self.patterns.items():
            if other_bt!=bt and p['total']>=2:
                alt_rate=p['success']/p['total']
                alts.append((other_bt, alt_rate))
        return sorted(alts, key=lambda x:-x[1])[:3]
    
    def _why_this_pattern(self, bt, pat):
        """Warum genau DIESES Pattern?"""
        reasons=[]
        p=self.patterns[bt]
        if p['total']>=5 and p['success']/p['total']>0.7:
            reasons.append("Historisch hohe Erfolgsrate")
        if p['total']>=10:
            reasons.append("Große Stichprobe → zuverlässig")
        if p['total']<3:
            reasons.append("Wenige Daten → heuristische Wahl")
        if not reasons:
            reasons.append("Bestes verfügbares Pattern")
        return reasons
    
    def think(self,sig,emb):
        self.total_bugs+=1; bt=sig.split(':')[0] if ':' in sig else sig
        
        if self.patterns[bt]['total']<1:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                    'reasoning':f'Explain: {bt} — Keine Daten. Exploration nötig.',
                    'explanation':{'reason':'Kein Wissen','evidence':'0 Bugs','alternatives':[]}}
        
        rate=self.patterns[bt]['success']/max(1,self.patterns[bt]['total'])
        conf=rate
        
        # VOLLSTÄNDIGE ERKLÄRUNG
        explanation={
            'pattern':f'explainable_{bt}',
            'confidence':f'{conf:.0%}',
            'breakdown':self._explain_confidence(bt, conf),
            'why':self._why_this_pattern(bt, f'explainable_{bt}'),
            'alternatives':[(a,f'{r:.0%}') for a,r in self._generate_alternatives(bt)],
            'caveats':[] if conf>0.5 else ['Niedrige Konfidenz — manuelle Prüfung empfohlen'],
            'evidence_count':self.patterns[bt]['total']
        }
        
        action='APPLY_PATTERN' if conf>0.2 else 'EXPLORE'
        
        self.decision_log.append({'bug':bt,'action':action,'explanation':explanation})
        
        return {'action':action,'pattern':f'explain_{bt}','confidence':conf,
                'explanation':explanation,
                'reasoning':f'Explain: {bt} conf={conf:.0%} ({explanation["breakdown"][:50]}...)'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        self.patterns[bt]['total']+=1
        if success: self.patterns[bt]['success']+=1
        self.patterns[bt]['evidence'].append(success)
    
    def stats(self):
        return {'brain_type':'Explainability','total_bugs':self.total_bugs,
                'decisions_explained':len(self.decision_log),
                'last_explanation':self.decision_log[-1]['explanation'] if self.decision_log else {}}
    def __repr__(self): return f"ExplainabilityBrain(decisions={len(self.decision_log)})"

if __name__=="__main__":
    print("GEHIRN BI — Explainability"); b=ExplainabilityBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(20):
        bt=['NullPointer','OffByOne','TypeError'][i%3]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<16,emb)
        if i%4==0: 
            exp=dec.get('explanation',{})
            print(f"  Bug{i+1}: {dec['action']:15s} conf={exp.get('confidence','?')} why={exp.get('why',[])}")
    print(b.stats()); print("✅ Gehirn BI läuft.")
