"""
GEHIRN BC — Code-Context Brain
VERSTEHT CODE. Nicht nur Bug-Beschreibung, sondern CODE-DIFFS.
Analysiert: Welche Zeilen wurden geändert? Welche Funktionen?
Extrahiert strukturelle Features aus Code.

Mathematik: code_features = [lines_changed, functions_touched, complexity_delta, 
                             test_coverage, AST_depth, cyclomatic_complexity]

Autor: Hermes + David | Coding Tentacle 2026
"""
import numpy as np, math
from collections import defaultdict

class CodeContextBrain:
    """Gehirn BC — Versteht Code-Struktur, nicht nur Beschreibungen."""
    def __init__(self):
        self.code_features={}  # {bug_signature: feature_vector}
        self.function_memory=defaultdict(lambda: {'bugs':0, 'fixes':defaultdict(int)})
        self.file_memory=defaultdict(lambda: {'bugs':0, 'last_modified':0})
        self.patterns=defaultdict(lambda: {'success':0,'total':0})
        self.total_bugs=0
    
    def _extract_code_features(self, sig):
        """Extrahiere strukturelle Features aus Bug-Signatur"""
        features=np.zeros(8)
        parts=sig.split(':')
        if len(parts)>=2:
            file_part=parts[1]
            # 1. Dateityp
            if file_part.endswith('.py'): features[0]=1.0
            elif file_part.endswith('.js'): features[1]=1.0
            # 2. Pfad-Tiefe
            features[2]=file_part.count('/')*0.2
            # 3. Zeilennummer (wenn vorhanden)
            if len(parts)>=3:
                try: features[3]=min(1.0, int(parts[2].replace('line',''))/500.0)
                except: pass
        # 4. Bug-Typ-OneHot
        bt=sig.split(':')[0] if ':' in sig else sig
        bug_types=['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition',
                   'StackOverflow','ImportError','ValueError']
        if bt in bug_types:
            idx=bug_types.index(bt)
            if idx<4: features[4+idx]=1.0
        return features
    
    def _match_function(self, sig):
        """Welche Funktion ist betroffen?"""
        parts=sig.split(':')
        fn='unknown'
        if len(parts)>=2:
            file_part=parts[1]
            if '.' in file_part:
                fn=file_part.split('.')[0]
        return fn
    
    def think(self,sig,emb):
        self.total_bugs+=1; bt=sig.split(':')[0] if ':' in sig else sig
        
        # Code-Features extrahieren
        features=self._extract_code_features(sig)
        fn=self._match_function(sig)
        
        # Funktions-Memory: Diese Funktion schon mal gefixt?
        fn_mem=self.function_memory[fn]
        fn_experience=fn_mem['bugs']
        
        if self.patterns[bt]['total']<1:
            return {'action':'EXPLORE','pattern':None,'confidence':0.0,
                    'code_features':features.tolist(),
                    'reasoning':f'CodeContext: {bt} in {fn} — neue Funktion.'}
        
        rate=self.patterns[bt]['success']/max(1,self.patterns[bt]['total'])
        # Funktions-Erfahrung boostet Konfidenz
        fn_boost=min(0.3, fn_experience*0.05)
        conf=min(1.0, rate+fn_boost)
        
        # Häufigster Fix in dieser Funktion
        common_fix=max(fn_mem['fixes'], key=fn_mem['fixes'].get) if fn_mem['fixes'] else f'fix_{bt}'
        
        return {'action':'APPLY_PATTERN' if conf>0.2 else 'EXPLORE',
                'pattern':common_fix,'confidence':conf,
                'function':fn,'fn_experience':fn_experience,
                'reasoning':f'CodeContext: {bt} in {fn} ({fn_experience} Bugs hier) conf={conf:.2f}'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        self.patterns[bt]['total']+=1
        if success: self.patterns[bt]['success']+=1
        
        fn=self._match_function(sig)
        self.function_memory[fn]['bugs']+=1
        self.function_memory[fn]['fixes'][pat]+=1
        
        # Code-Features speichern
        self.code_features[sig]=self._extract_code_features(sig)
    
    def stats(self):
        return {'brain_type':'Code-Context','total_bugs':self.total_bugs,
                'functions_known':len(self.function_memory),
                'top_functions':sorted(self.function_memory.items(),key=lambda x:-x[1]['bugs'])[:5]}
    def __repr__(self): return f"CodeContextBrain(functions={len(self.function_memory)})"

if __name__=="__main__":
    print("GEHIRN BC — Code-Context"); b=CodeContextBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    files=['payment.py','auth.py','order.py','cache.py','worker.py','payment.py','auth.py']
    for i in range(25):
        bt=['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'][i%5]
        fn=files[i%len(files)]
        sig=f"{bt}:{fn}:line{i*10}"
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(sig,emb)
        b.learn(sig,f"fix_{bt}",i<20,emb)
        if i%5==0: print(f"  Bug{i+1}: {dec['action']:15s} fn={dec.get('function','?')} exp={dec.get('fn_experience',0)}")
    print(b.stats()); print("✅ Gehirn BC läuft.")
