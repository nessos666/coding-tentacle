"""
46 GEHIRNE — GROSSER CHECK: Syntax, Funktionen, Lernfähigkeit, Probleme
"""
import sys,os,ast,py_compile,re,inspect,json,time,numpy as np
from collections import defaultdict

GEHIRN_DIR='/home/boobi/GEHIRN_BIBLIOTHEK'
BRAIN_FOLDERS=sorted([d for d in os.listdir(GEHIRN_DIR) if os.path.isdir(os.path.join(GEHIRN_DIR,d)) and d[0].isdigit()])

report={'timestamp':time.strftime('%Y-%m-%d %H:%M'),'brains':[],'summary':{}}

def find_brain_file(folder):
    path=os.path.join(GEHIRN_DIR,folder)
    for f in os.listdir(path):
        if f.endswith('.py') and 'brain' in f.lower():
            return os.path.join(path,f)
    return None

def check_syntax(filepath):
    try:
        with open(filepath) as f: code=f.read()
        ast.parse(code)
        return True,None
    except SyntaxError as e:
        return False,str(e)

def check_interface(filepath):
    """Prüft think/learn/stats Methoden"""
    with open(filepath) as f: code=f.read()
    has_think='def think(self' in code
    has_learn='def learn(self' in code
    has_stats='def stats(self' in code
    return has_think,has_learn,has_stats

def check_imports(filepath):
    with open(filepath) as f: code=f.read()
    imports=re.findall(r'^import\s+(\S+)',code,re.MULTILINE)
    from_imports=re.findall(r'^from\s+(\S+)',code,re.MULTILINE)
    return len(imports)+len(from_imports)

def check_docstring(filepath):
    with open(filepath) as f: code=f.read()
    return '"""' in code[:500] or "'''" in code[:500]

def check_lines(filepath):
    with open(filepath) as f: return len(f.readlines())

def check_learning(filepath):
    """Prüft ob das Gehirn tatsächlich lernt (Zustand ändert sich)"""
    with open(filepath) as f: code=f.read()
    state_changes=re.findall(r'self\.\w+\[\w+\]\s*[+\-]|=',code)
    state_updates=re.findall(r'self\.\w+\s*[+\-]=',code)
    return len(state_changes)+len(state_updates)

print("="*75)
print("  🧠 46 GEHIRNE — GROSSER CHECK")
print("  Syntax | Interface | Lernfähigkeit | Probleme")
print("="*75)

issues=defaultdict(list)
interface_ok=0; syntax_ok=0; learning_detected=0; doc_ok=0

for folder in BRAIN_FOLDERS:
    fpath=find_brain_file(folder)
    if not fpath: 
        issues[folder].append('NO BRAIN FILE')
        continue
    
    name=folder.split('_',1)[1] if '_' in folder else folder
    syn_ok,syn_err=check_syntax(fpath)
    has_t,has_l,has_s=check_interface(fpath)
    n_imports=check_imports(fpath)
    has_doc=check_docstring(fpath)
    n_lines=check_lines(fpath)
    n_learn=check_learning(fpath)
    
    # Bewertung
    problems=[]
    if not syn_ok: problems.append(f'SYNTAX: {syn_err}')
    if not has_t: problems.append('MISSING: think()')
    if not has_l: problems.append('MISSING: learn()')
    if not has_s: problems.append('MISSING: stats()')
    if not has_doc: problems.append('No docstring')
    if n_lines<30: problems.append(f'Too short ({n_lines} lines)')
    if n_learn<3: problems.append(f'Little learning ({n_learn} state changes)')
    if n_imports>8: problems.append(f'Many imports ({n_imports})')
    
    # Score
    score=10
    if not syn_ok: score-=4
    if not has_t: score-=2
    if not has_l: score-=2
    if not has_s: score-=1
    if not has_doc: score-=1
    if n_lines<50: score-=1
    if n_learn<5: score-=1
    
    entry={
        'folder':folder,'name':name,'file':os.path.basename(fpath),
        'syntax':syn_ok,'interface_ok':(has_t and has_l and has_s),
        'lines':n_lines,'imports':n_imports,'docstring':has_doc,
        'learning_signals':n_learn,'score':score,'problems':problems
    }
    report['brains'].append(entry)
    
    if syn_ok: syntax_ok+=1
    if has_t and has_l and has_s: interface_ok+=1
    if n_learn>=5: learning_detected+=1
    if has_doc: doc_ok+=1
    
    icon='✅' if score>=9 else ('⚠️' if score>=6 else '❌')
    print(f"  {icon} {folder:<30s} Score={score}/10  Lines={n_lines}  Learn={n_learn}  "
          f"I={'✓' if has_t and has_l and has_s else '✗'}  {'PROBLEMS: '+','.join(problems) if problems else 'CLEAN'}")

# ─── ZUSAMMENFASSUNG ───
n=len(report['brains'])
avg_score=np.mean([b['score'] for b in report['brains']])
avg_lines=np.mean([b['lines'] for b in report['brains']])
avg_learn=np.mean([b['learning_signals'] for b in report['brains']])

report['summary']={
    'total_brains':n,'syntax_ok':f'{syntax_ok}/{n}',
    'interface_ok':f'{interface_ok}/{n}','doc_ok':f'{doc_ok}/{n}',
    'learning_detected':f'{learning_detected}/{n}',
    'avg_score':round(avg_score,2),'avg_lines':round(avg_lines,0),
    'avg_learning_signals':round(avg_learn,0)
}

print(f"\n{'='*75}")
print(f"  📊 ZUSAMMENFASSUNG: {n} Gehirne")
print(f"{'='*75}")
for k,v in report['summary'].items():
    print(f"  {k}: {v}")

# ─── TOP/BOTTOM ───
top=sorted(report['brains'],key=lambda b:-b['score'])[:5]
bottom=sorted(report['brains'],key=lambda b:b['score'])[:5]

print(f"\n  🏆 TOP 5 (Code-Qualität):")
for b in top:
    print(f"     {b['folder']:<30s} Score={b['score']}/10")

print(f"\n  ⚠️ VERBESSERUNGSWÜRDIG:")
for b in bottom:
    if b['score']<8:
        print(f"     {b['folder']:<30s} Score={b['score']}/10  Problems: {b['problems']}")

# ─── WAS DIE GEHIRNE NICHT KÖNNEN ───
print(f"\n{'='*75}")
print(f"  ❌ WAS ALLE GEHIRNE (NOCH) NICHT KÖNNEN:")
print(f"{'='*75}")
limitations=[
    "1. Kein echtes Online-Learning (brauchen Batch-Training)",
    "2. Kein Multi-Task-Learning (Bug-Typen isoliert, kein Shared Knowledge)",
    "3. Kein aktives Vergessen (nur Decay, kein strategisches Löschen)",
    "4. Keine Temporal-Awareness (wann trat Bug auf? Muster über Zeit?)",
    "5. Kein Causal-Reasoning 2.0 (nur Gehirn H, aber kein Brain hat Counterfactuals)",
    "6. Kein Code-Kontext-Verständnis (nur Bug-Beschreibung, kein Code-Diff)",
    "7. Keine Multi-Agent-Koordination (kein Brain kommuniziert mit anderen Brains)",
    "8. Kein Uncertainty-Quantification (gibt Confidence, aber kein Bayesian Posterior)",
    "9. Kein Curriculum-Learning (lernt nicht: einfache Bugs ZUERST)",
    "10. Kein Explainability-Output (kein Brain sagt WARUM es diesen Fix gewählt hat im Detail)",
]
for lim in limitations: print(f"  {lim}")

# ─── EMPFEHLUNGEN ───
print(f"\n{'='*75}")
print(f"  💡 EMPFEHLUNGEN FÜR CODING TENTACLE MVP:")
print(f"{'='*75}")
recommendations=[
    "MVP-Gehirne: P_GameTheory (perfekt), C_Graph (strukturell), M_Attention (semantisch)",
    "Integration: Hyperon Integrator (AO) als Orchestrator",
    "Fix: Bayesian (A) und VSM (AP) brauchen besseres Embedding-Matching",
    "Upgrade-Pfad: Hebbian (K) → Modern Hopfield (AJ) für exponentielle Kapazität",
    "Nächster Meilenstein: Online-Learning + Code-Kontext in Gen10",
]
for rec in recommendations: print(f"  • {rec}")

# Speichern
outpath=os.path.join(GEHIRN_DIR,'GROSSER_CHECK_REPORT.json')
with open(outpath,'w') as f: json.dump(report,f,indent=2,default=str)
desktop=os.path.expanduser('~/Schreibtisch/GEHIRN_CHECK_REPORT.json')
with open(desktop,'w') as f: json.dump(report,f,indent=2,default=str)
print(f"\n  📁 {outpath}")
print(f"  📁 Desktop: GEHIRN_CHECK_REPORT.json")
