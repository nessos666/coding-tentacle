"""
66 GEHIRNE — VOLLSTÄNDIGER FORSCHUNGS-AUDIT
10 Dimensionen. Nur Messen. Keine Änderungen.
"""
import sys,os,ast,time,json,random,math,tracemalloc,gc
import numpy as np
from collections import defaultdict, deque
from sentence_transformers import SentenceTransformer

GEHIRN_DIR='/home/boobi/GEHIRN_BIBLIOTHEK'
model=SentenceTransformer('all-MiniLM-L6-v2')
R=random

def find_brains():
    brains=[]
    for d in sorted(os.listdir(GEHIRN_DIR)):
        if not d[0].isdigit(): continue
        path=os.path.join(GEHIRN_DIR,d)
        if not os.path.isdir(path): continue
        for f in os.listdir(path):
            if f.endswith('.py') and 'brain' in f.lower():
                brains.append((d,f))
                break
    return brains

def load_brain_instance(folder):
    brain_path=os.path.join(GEHIRN_DIR,folder)
    sys.path.insert(0,brain_path)
    for f in os.listdir(brain_path):
        if f.endswith('.py') and 'brain' in f:
            mod=f[:-3]
            try:
                exec(f"import {mod}")
                for name in dir(sys.modules[mod]):
                    cls=getattr(sys.modules[mod],name)
                    if isinstance(cls,type) and hasattr(cls,'think') and 'Brain' in name:
                        try: return cls()
                        except: return None
            except: return None
    return None

def smart_learn(b, sig, pat, ok, emb=None):
    try: b.learn(sig, pat, ok, emb)
    except:
        try: b.learn(sig, pat, ok)
        except: pass

EMB_CACHE={}
def get_emb(text):
    if text not in EMB_CACHE:
        EMB_CACHE[text]=model.encode(text).tolist()
    return EMB_CACHE[text]

brain_list=find_brains()
print(f"Audit: {len(brain_list)} Gehirne gefunden\n")

report={'timestamp':time.strftime('%Y-%m-%d %H:%M:%S'),'brains':[]}
all_scores=[]

for idx,(folder,fname) in enumerate(brain_list):
    name=folder.split('_',1)[1] if '_' in folder else folder
    gen=folder[:2]
    print(f"[{idx+1}/{len(brain_list)}] {name}...",end=' ',flush=True)
    
    r={'name':name,'folder':folder,'generation':gen}
    dims={}
    
    # 1. TECHNICAL
    fpath=os.path.join(GEHIRN_DIR,folder,fname)
    try:
        with open(fpath) as f: code=f.read()
        ast.parse(code); dims['syntax']=1
    except: dims['syntax']=0
    
    has_t='def think(self' in code; has_l='def learn(self' in code; has_s='def stats(self' in code
    dims['interface']=1 if (has_t and has_l and has_s) else 0
    dims['lines']=len(code.split('\n'))
    
    b=load_brain_instance(folder)
    if b is None: r['error']='LOAD_FAILED'; report['brains'].append(r); print("LOAD_FAILED"); continue
    
    # Memory
    gc.collect(); tracemalloc.start()
    t0=time.time(); b_think=b.think("NullPointer:x.py:1",get_emb("NullPointer error"))
    dt=time.time()-t0; _,peak=tracemalloc.get_traced_memory(); tracemalloc.stop()
    dims['runtime_ms']=round(dt*1000,1)
    dims['memory_kb']=round(peak/1024,1)
    
    # 2. LEARNING TEST
    emb_np=get_emb("NullPointer null check guard clause defensive programming error")
    emb_ae=get_emb("AttributeError attribute hasattr check guard clause defensive")
    emb_ie=get_emb("ImportError module not found cannot import name")
    emb_rc=get_emb("RaceCondition concurrent thread lock mutex shared state")
    emb_ml=get_emb("MemoryLeak unbounded growth cache not freed")
    
    learning_curve=[]
    for ep in range(30):
        try: b.learn(f"NullPointer:f{ep}.py:{ep}","guard_clause",R.random()<0.85,emb_np)
        except:
            try: b.learn(f"NullPointer:f{ep}.py:{ep}","guard_clause",R.random()<0.85)
            except: break
        if ep%3==0:
            dec=b.think("NullPointer:test.py:1",emb_np)
            learning_curve.append(1 if dec.get('action')=='APPLY_PATTERN' else 0)
    
    dims['learn_rate']=np.mean(learning_curve[-5:]) if learning_curve else 0
    dims['learn_converged']=1 if dims['learn_rate']>0.6 else 0
    
    # 3. GENERALIZATION (Transfer)
    dec_tr=b.think("AttributeError:transfer.py:1",emb_ae)
    dims['transfer']=1 if dec_tr.get('action')=='APPLY_PATTERN' else 0
    
    # 4. OOD
    dec_ood=b.think("StackOverflow:recursion.py:1",get_emb("StackOverflow recursion depth exceeded maximum limit"))
    dims['ood']=1 if dec_ood.get('action')=='EXPLORE' else 0
    dims['ood_overconfident']=1 if (dec_ood.get('action')=='APPLY_PATTERN' and dec_ood.get('confidence',0)>0.5) else 0
    
    # 5. INTERFERENCE
    for ep in range(15):
        try: b.learn(f"NullPointer:noise{ep}.py:{ep}","guard_clause",False,emb_np)
        except:
            try: b.learn(f"NullPointer:noise{ep}.py:{ep}","guard_clause",False)
            except: break
    dec_int=b.think("NullPointer:after_interf.py:1",emb_np)
    dims['interference_resistance']=1 if dec_int.get('action')=='APPLY_PATTERN' else 0
    
    # 6. MULTI-TASK
    multi_correct=0
    for bt,emb_bt,pat in [('ImportError',emb_ie,'fix_import'),('RaceCondition',emb_rc,'fix_race'),('MemoryLeak',emb_ml,'fix_memory')]:
        for ep in range(5):
            try: b.learn(f"{bt}:f{ep}.py:{ep}",pat,True,emb_bt)
            except:
                try: b.learn(f"{bt}:f{ep}.py:{ep}",pat,True)
                except: pass
        dec_mt=b.think(f"{bt}:test.py:1",emb_bt)
        if dec_mt.get('action')=='APPLY_PATTERN': multi_correct+=1
    dims['multi_task']=multi_correct/3
    
    # 7. TIME TEST
    t_start=time.time()
    for ep in range(200):
        try: b.learn(f"NullPointer:time{ep}.py:{ep}","guard",True,emb_np)
        except:
            try: b.learn(f"NullPointer:time{ep}.py:{ep}","guard",True)
            except: break
    dec_200=b.think("NullPointer:after_200.py:1",emb_np)
    dims['time_stable']=1 if dec_200.get('action')=='APPLY_PATTERN' else 0
    dims['time_200_ms']=round((time.time()-t_start)*1000,1)
    
    # 8. ROBUSTNESS (Noise)
    emb_noisy=get_emb("nUlLPoIntEr eRrOr nUlL cHeCk gUaRd")  # Tippfehler
    dec_noise=b.think("NullPointer:noisy.py:1",emb_noisy)
    dims['robustness']=1 if dec_noise.get('action')=='APPLY_PATTERN' else 0
    
    # 9. EXPLAINABILITY
    expl_score=0
    reasoning=dec_int.get('reasoning','')
    if len(reasoning)>20: expl_score+=1
    if 'conf' in reasoning.lower() or 'rate' in reasoning.lower(): expl_score+=1
    if 'pattern' in reasoning.lower() or 'fix' in reasoning.lower(): expl_score+=1
    dims['explainability']=expl_score/3
    
    # 10. PRODUCTION VALUE
    prod_scores={
        'pattern_recognition':dims['learn_rate'],
        'reasoning':dims['explainability'],
        'memory':dims['interference_resistance'],
        'transfer':dims['transfer'],
        'robustness':dims['robustness'],
        'interpretability':dims['explainability'],
        'scalability':dims['time_stable'],
        'coding_tentacle_relevance':(dims['learn_rate']+dims['transfer']+dims['multi_task'])/3
    }
    dims['production']=prod_scores
    
    # Gesamtscore
    total=sum([
        dims.get('syntax',0), dims.get('interface',0),
        dims['learn_rate']*2, dims['transfer']*2, dims['ood']*2, 
        dims['interference_resistance']*2, dims['multi_task']*2,
        dims['time_stable']*2, dims['robustness'], dims['explainability']
    ])/18  # Max ~1.0
    
    r['score']=round(total,3)
    r['dimensions']=dims
    r['strengths']=[k for k,v in dims.items() if isinstance(v,(int,float)) and v>0.8]
    r['weaknesses']=[k for k,v in dims.items() if isinstance(v,(int,float)) and v<0.3]
    r['keep_for_mvp']=total>0.5
    
    report['brains'].append(r)
    all_scores.append(total)
    
    icon='✅' if total>0.7 else ('⚠️' if total>0.4 else '❌')
    print(f"{icon} Score={total:.2f}")

# ═══ FINALER REPORT ═══
report['summary']={
    'total':len(report['brains']),
    'avg_score':round(np.mean(all_scores),3),
    'above_07':sum(1 for s in all_scores if s>0.7),
    'above_04':sum(1 for s in all_scores if s>0.4),
    'below_04':sum(1 for s in all_scores if s<=0.4),
    'mvp_candidates':sum(1 for b in report['brains'] if b.get('keep_for_mvp')),
}

sorted_brains=sorted(report['brains'],key=lambda x:-x['score'])
report['top10']=[{'name':b['name'],'score':b['score'],'gen':b['generation']} for b in sorted_brains[:10]]
report['bottom10']=[{'name':b['name'],'score':b['score'],'gen':b['generation']} for b in sorted_brains[-10:]]
report['unique_abilities']={}
report['redundant']=[]

# Empfehlung
report['mvp_recommendation']={
    'pattern_matching':sorted_brains[0]['name'] if sorted_brains else 'N/A',
    'ood_detection':max(report['brains'],key=lambda b:b['dimensions'].get('ood',0))['name'],
    'transfer':max(report['brains'],key=lambda b:b['dimensions'].get('transfer',0))['name'],
    'robustness':max(report['brains'],key=lambda b:b['dimensions'].get('robustness',0))['name'],
    'multi_task':max(report['brains'],key=lambda b:b['dimensions'].get('multi_task',0))['name'],
}

# Speichern
for pth in [os.path.join(GEHIRN_DIR,'FORSCHUNGS_AUDIT.json'),
            os.path.expanduser('~/Schreibtisch/FORSCHUNGS_AUDIT_66_GEHIRNE.json')]:
    with open(pth,'w') as f:
        json.dump(report,f,indent=2,default=str)

print(f"\n{'='*60}")
print(f"FORSCHUNGS-AUDIT FERTIG")
print(f"{'='*60}")
print(f"Gehirne: {report['summary']['total']}")
print(f"Schnitt:  {report['summary']['avg_score']:.3f}")
print(f">0.7:    {report['summary']['above_07']}")
print(f"0.4-0.7: {report['summary']['above_04']-report['summary']['above_07']}")
print(f"<0.4:    {report['summary']['below_04']}")
print(f"MVP:     {report['summary']['mvp_candidates']}")
print(f"\nTOP 3:")
for b in sorted_brains[:3]:
    print(f"  {b['name']:<25s} {b['score']:.3f}")
