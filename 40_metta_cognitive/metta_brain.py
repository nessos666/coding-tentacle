"""
GEHIRN AN — MeTTa Cognitive Brain
Deklarative kognitive Regeln im MeTTa-Stil.
Regeln werden als Pattern-Matching definiert (nicht prozedural).
Funktioniert wie ein Mini-Theorem-Beweiser für Bug-Fixes.

MeTTa-Syntax (vereinfacht):
  (= (fixFor $bug $fix) (and (hasPattern $bug $fix) (successRate $fix >0.7)))
  (similarTo NullPointer AttributeError <TV 0.6 0.7>)

Autor: Hermes + David | Coding Tentacle 2026
Quelle: OpenCog Hyperon / MeTTa Language
"""
import numpy as np, re
from collections import defaultdict

class MeTTaCognitiveBrain:
    """Gehirn AN — Regel-basierte Kognition im MeTTa-Stil."""
    def __init__(self):
        self.facts=defaultdict(dict)  # {predicate: {subject: value}}
        self.rules=[]  # [(pattern, result_template, condition_fn)]
        self.total_bugs=0
        self._init_rules()
    
    def _init_rules(self):
        """Vordefinierte kognitive Regeln"""
        # Regel 1: Direkter Fix
        self.rules.append(('direct_fix', 
            lambda bt, ctx: ctx.get(f'fix_{bt}')))
        # Regel 2: Transfer via Ähnlichkeit
        self.rules.append(('transfer_fix',
            lambda bt, ctx: self._transfer_fix(bt, ctx)))
        # Regel 3: Fallback auf häufigsten Fix
        self.rules.append(('fallback_fix',
            lambda bt, ctx: ctx.get('most_common_fix')))
    
    def _transfer_fix(self, bt, ctx):
        similar=ctx.get('similar_to',{}).get(bt,[])
        for sib in similar:
            fix=ctx.get(f'fix_{sib}')
            if fix and ctx.get(f'success_{sib}',0)>0.6:
                return fix
        return None
    
    def _assert(self, predicate, subject, value):
        self.facts[predicate][subject]=value
    
    def _query(self, predicate, subject):
        return self.facts.get(predicate,{}).get(subject)
    
    def think(self,sig,emb):
        self.total_bugs+=1
        bt=sig.split(':')[0] if ':' in sig else sig
        
        # Kontext aufbauen (Working Memory)
        ctx={
            f'fix_{bt}': self._query('fix', bt),
            f'success_{bt}': self._query('success_rate', bt),
            'most_common_fix': self._query('most_common', 'fix'),
            'similar_to': self._query('similar_to', 'all') or {}
        }
        
        # Regeln der Reihe nach anwenden
        for rule_name, rule_fn in self.rules:
            fix=rule_fn(bt, ctx)
            if fix:
                conf=self._query('success_rate', bt) or 0.5
                return {'action':'APPLY_PATTERN','pattern':fix,
                        'confidence':conf,'rule':rule_name,
                        'reasoning':f'MeTTa: {rule_name} → {fix} (conf={conf:.2f})'}
        
        return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                'reasoning':f'MeTTa: Keine Regel für {bt} gefeuert.'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        self._assert('fix', bt, pat)
        self._assert('success_count', bt, self._query('success_count', bt) or 0 + (1 if success else 0))
        self._assert('total_count', bt, self._query('total_count', bt) or 0 + 1)
        
        sc=self._query('success_count', bt) or 0
        tc=self._query('total_count', bt) or 1
        self._assert('success_rate', bt, sc/tc)
        
        # Similarity-Netzwerk aufbauen
        sim=self._query('similar_to', 'all') or {}
        for other_bt in self.facts.get('fix',{}):
            if other_bt!=bt and other_bt not in sim.get(bt,[]):
                if bt not in sim: sim[bt]=[]
                sim[bt].append(other_bt)
        self._assert('similar_to','all', sim)
    
    def stats(self):
        return {'brain_type':'MeTTa Cognitive','total_bugs':self.total_bugs,
                'facts':sum(len(v) for v in self.facts.values()),
                'rules':len(self.rules),
                'fixes_known':list(self.facts.get('fix',{}).keys())}
    def __repr__(self): return f"MeTTaBrain(facts={sum(len(v) for v in self.facts.values())})"

if __name__=="__main__":
    print("GEHIRN AN — MeTTa Cognitive"); b=MeTTaCognitiveBrain()
    for i in range(25):
        bt=['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'][i%5]
        dec=b.think(f"{bt}:f{i}.py:{i}",[0]*384)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<20)
        if i%5==0: print(f"  Bug{i+1}: {dec['action']:15s} rule={dec.get('rule','?')}")
    print(b.stats()); print("✅ Gehirn AN läuft.")
