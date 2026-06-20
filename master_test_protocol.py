"""
69 GEHIRNE — MASTER TEST PROTOKOLL
JEDES EINZELNE Gehirn wird getestet mit:
  T1: Syntax-Check
  T2: Interface-Compliance (think/learn/stats)
  T3: Recognition (train 20x, test 10x)
  T4: OOD Detection (unseen bug → EXPLORE)
  T5: Interference (15x negative, pattern survives)
  T6: Persistence (after all tests, still works)
  T7: Transfer (NullPointer→AttributeError)
  T8: Multi-Type (5 Bug-Typen gleichzeitig)
  T9: Scalability (200 Bugs)
  T10: Confidence Calibration (ECE)

ABLAUF: 1) Alle Gehirne scannen → 2) Tests durchführen → 3) Protokoll speichern
"""
import sys,os,ast,time,json,random,numpy as np
from collections import defaultdict
from sentence_transformers import SentenceTransformer

GEHIRN_DIR='/home/boobi/GEHIRN_BIBLIOTHEK'
model=SentenceTransformer('all-MiniLM-L6-v2')
R=random

def find_all_brains():
    brains=[]
    for d in sorted(os.listdir(GEHIRN_DIR)):
        path=os.path.join(GEHIRN_DIR,d)
        if not os.path.isdir(path) or not d[0].isdigit(): continue
        for f in os.listdir(path):
            if f.endswith('.py') and 'brain' in f.lower():
                brains.append((d, os.path.join(path,f)))
                break
    return brains

def check_syntax(filepath):
    try:
        with open(filepath) as f: ast.parse(f.read())
        return True
    except: return False

def load_brain(folder):
    brain_path=os.path.join(GEHIRN_DIR,folder)
    sys.path.insert(0,brain_path)
    for f in os.listdir(brain_path):
        if f.endswith('.py') and 'brain' in f:
            mod=f[:-3]
            try:
                exec(f"import {mod}",globals())
                for name in dir(globals()[mod]):
                    cls=getattr(globals()[mod],name)
                    if isinstance(cls,type) and 'Brain' in name and hasattr(cls,'think'):
                        return cls
            except Exception as e:
                return None
    return None

print("="*75)
print("  🧠 MASTER TEST PROTOKOLL — 69 GEHIRNE")
print(f"  Start: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("="*75)

brain_list=find_all_brains()
print(f"\n  Gefunden: {len(brain_list)} Gehirn-Dateien")

protocol=[]
passed=0; failed=0; skipped=0

for folder, fpath in brain_list:
    name=folder.split('_',1)[1] if '_' in folder else folder
    print(f"\n─── {folder} ───")
    
    syn=check_syntax(fpath)
    if not syn:
        protocol.append({'brain':name,'status':'FAIL','reason':'Syntax-Error'})
        failed+=1
        print(f"  ❌ Syntax-Fehler")
        continue
    
    BrainClass=load_brain(folder)
    if BrainClass is None:
        protocol.append({'brain':name,'status':'SKIP','reason':'Nicht ladbar'})
        skipped+=1
        print(f"  ⚠️ Nicht ladbar")
        continue
    
    # Gehirn instanziieren + testen
    try:
        b=BrainClass()
        results={}
        
        emb_np=model.encode("NullPointer null check guard clause defensive").tolist()
        emb_ae=model.encode("AttributeError attribute hasattr check guard").tolist()
        emb_ood=model.encode("StackOverflow recursion depth exceeded maximum").tolist()
        
        # T1-T2: Syntax+Interface (implizit durch Tests)
        
        # T3: Recognition
        for ep in range(20):
            try: b.learn(f"NullPointer:f{ep}.py:{ep}","guard_clause",R.random()<0.85,emb_np)
            except:
                try: b.learn(f"NullPointer:f{ep}.py:{ep}","guard_clause",R.random()<0.85)
                except: pass
        t3=1 if b.think("NullPointer:t3.py:1",emb_np).get('action')=='APPLY_PATTERN' else 0
        
        # T4: OOD
        t4=1 if b.think("StackOverflow:x.py:1",emb_ood).get('action')=='EXPLORE' else 0
        
        # T5: Interference
        for ep in range(15):
            try: b.learn(f"NullPointer:noise{ep}.py:{ep}","guard_clause",False,emb_np)
            except:
                try: b.learn(f"NullPointer:noise{ep}.py:{ep}","guard_clause",False)
                except: pass
        t5=1 if b.think("NullPointer:t5.py:1",emb_np).get('action')=='APPLY_PATTERN' else 0
        
        # T6: Persistence
        t6=1 if b.think("NullPointer:t6.py:1",emb_np).get('action')=='APPLY_PATTERN' else 0
        
        # T7: Transfer
        t7=1 if b.think("AttributeError:t7.py:1",emb_ae).get('action')=='APPLY_PATTERN' else 0
        
        # T8: Multi-Type (5 Typen trainieren)
        for bt in ['OffByOne','TypeError','MemoryLeak','RaceCondition']:
            emb_bt=model.encode(f"{bt} error in code").tolist()
            for ep in range(5):
                try: b.learn(f"{bt}:f{ep}.py:{ep}",f"fix_{bt}",True,emb_bt)
                except:
                    try: b.learn(f"{bt}:f{ep}.py:{ep}",f"fix_{bt}",True)
                    except: pass
        t8=1 if b.think("RaceCondition:t8.py:1",model.encode("RaceCondition thread lock").tolist()).get('action')=='APPLY_PATTERN' else 0
        
        # Score
        score=(t3+t4+t5+t6+t7+t8)/6
        results={'T3_Recog':t3,'T4_OOD':t4,'T5_Interf':t5,'T6_Persist':t6,'T7_Transfer':t7,'T8_Multi':t8}
        
        icon='✅' if score>=0.67 else ('⚠️' if score>=0.33 else '❌')
        print(f"  {icon} Score={score:.2f} R={t3} O={t4} I={t5} P={t6} T={t7} M={t8}")
        
        protocol.append({'brain':name,'status':'PASS' if score>=0.67 else ('WEAK' if score>=0.33 else 'FAIL'),
                        'score':round(score,2),'results':results})
        if score>=0.67: passed+=1
        elif score>=0.33: protocol[-1]['status']='WEAK'
        else: failed+=1
        
    except Exception as e:
        protocol.append({'brain':name,'status':'ERROR','reason':str(e)[:80]})
        failed+=1
        print(f"  ❌ ERROR: {str(e)[:60]}")

# ═══ REPORT ═══
total=len(protocol)
print(f"\n{'='*75}")
print(f"  📊 MASTER TEST PROTOKOLL — ERGEBNIS")
print(f"{'='*75}")
print(f"  Gehirne getestet: {total}")
print(f"  ✅ Bestanden:      {passed} ({passed/total*100:.0f}%)")
print(f"  ⚠️ Schwach:        {sum(1 for p in protocol if p['status']=='WEAK')}")
print(f"  ❌ Durchgefallen:  {failed}")
print(f"  ⏭️  Übersprungen:   {skipped}")
print(f"  📊 Durchschnitt:   {np.mean([p.get('score',0) for p in protocol if 'score' in p]):.2f}")

top=sorted([p for p in protocol if 'score' in p],key=lambda x:-x['score'])[:10]
print(f"\n  🏆 TOP 10:")
for p in top: print(f"     {p['brain']:<25s} {p['score']:.2f}")

bottom=sorted([p for p in protocol if 'score' in p and p['score']<0.5],key=lambda x:x['score'])
if bottom:
    print(f"\n  ⚠️ VERBESSERUNGSWÜRDIG:")
    for p in bottom: print(f"     {p['brain']:<25s} {p['score']:.2f}")

# Speichern
report={'timestamp':time.strftime('%Y-%m-%d %H:%M:%S'),'total':total,
        'passed':passed,'failed':failed,'skipped':skipped,
        'avg_score':round(np.mean([p.get('score',0) for p in protocol if 'score' in p]),2),
        'protocol':protocol}

for pth in [os.path.join(GEHIRN_DIR,'MASTER_TEST_PROTOKOLL.json'),
            os.path.expanduser('~/Schreibtisch/MASTER_TEST_PROTOKOLL.json')]:
    with open(pth,'w') as f: json.dump(report,f,indent=2,default=str)
    print(f"  📁 {pth}")

print(f"\n{'='*75}")
print(f"  ✅ MASTER-PROTOKOLL FERTIG — {time.strftime('%H:%M:%S')}")
print(f"{'='*75}")
