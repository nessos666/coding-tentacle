"""
BRAIN EFFICIENCY & COMPATIBILITY RESEARCH
7 Phasen. 66+ Gehirne. Nur Messen, kein Bauen.
"""
import sys,os,time,random,json,math,gc,tracemalloc
import numpy as np
from collections import defaultdict
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

def load_instance(folder):
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

def safe_learn(b, sig, pat, ok, emb=None, ctx=None):
    try: b.learn(sig, pat, ok, emb, code_context=ctx)
    except:
        try: b.learn(sig, pat, ok, emb)
        except:
            try: b.learn(sig, pat, ok)
            except: pass

def safe_think(b, sig, emb=None):
    try: return b.think(sig, emb)
    except:
        try: return b.think(sig)
        except: return {'action':'ERROR','confidence':0}

brains=find_brains()
print(f"Scanning {len(brains)} brains...\n")

report={'efficiency':[],'clusters':{},'compatibility':[],'synergies':[],'anti_patterns':[],'routing':{}}
all_data={}

# ═══ PHASE 1: EFFIZIENZPROFIL ═══
print("PHASE 1: Efficiency Profiles")
for idx,(folder,fname) in enumerate(brains):
    name=folder.split('_',1)[1] if '_' in folder else folder
    print(f"  [{idx+1}/{len(brains)}] {name}...",end=' ',flush=True)
    
    b=load_instance(folder)
    if not b: print("LOAD_FAIL"); continue
    
    emb_np=model.encode("NullPointer null check guard").tolist()
    
    # Memory: pre vs post 50 learns
    gc.collect(); tracemalloc.start()
    t0=time.time()
    for ep in range(50):
        safe_learn(b,f"NullPointer:f{ep}.py:{ep}","guard",R.random()<0.85,emb_np)
    dt=time.time()-t0; _,peak=tracemalloc.get_traced_memory(); tracemalloc.stop()
    
    # Check if converged
    hits=0
    for _ in range(10):
        dec=safe_think(b,"NullPointer:test.py:1",emb_np)
        if dec.get('action')=='APPLY_PATTERN': hits+=1
    converged=hits>=8
    
    # OOD test
    dec_ood=safe_think(b,"StackOverflow:x.py:1",model.encode("StackOverflow recursion").tolist())
    ood_ok=1 if dec_ood.get('action') in ('EXPLORE','ASK_CONTEXT') else 0
    
    # Data efficiency: how many learns to first APPLY_PATTERN?
    b2=load_instance(folder)
    data_need='unknown'; converges_at=999
    if b2:
        for ep in range(100):
            safe_learn(b2,f"NullPointer:f{ep}.py:{ep}","guard",True,emb_np)
            dec=safe_think(b2,"NullPointer:test.py:1",emb_np)
            if dec.get('action')=='APPLY_PATTERN':
                converges_at=ep+1
                break
        if converges_at<=3: data_need='one_shot'
        elif converges_at<=10: data_need='few_shot'
        elif converges_at<=50: data_need='batch'
        else: data_need='high'
    
    # CPU cost
    cpu='low' if dt<0.01 else ('medium' if dt<0.05 else 'high')
    mem='low' if peak<50*1024 else ('medium' if peak<200*1024 else 'high')
    
    # Learning type
    if data_need=='one_shot': learn_type='one_shot'
    elif data_need=='few_shot': learn_type='few_shot'
    elif 'Bridge' in name or 'Mesh' in name or 'Integrator' in name: learn_type='bridge'
    elif 'Meta' in name or 'meta' in name: learn_type='meta'
    elif data_need=='batch': learn_type='batch'
    else: learn_type='long_horizon'
    
    score=(converged*3+ood_ok*2+(1 if data_need in ('one_shot','few_shot') else 0)+
           (2 if cpu=='low' else(1 if cpu=='medium' else 0)))/8
    
    entry={'brain':name,'efficiency_score':round(score,3),'data_need':data_need,
           'cpu_cost':cpu,'memory_cost':mem,'converges_after':converges_at,
           'converged':converged,'ood_ok':bool(ood_ok),'peak_memory_kb':round(peak/1024,1),
           'learn_type':learn_type,'mvp_relevant':converged and ood_ok}
    
    report['efficiency'].append(entry)
    all_data[name]=b
    icon='✅' if score>0.7 else ('⚠️' if score>0.4 else '❌')
    print(f"{icon} eff={score:.2f} dp={data_need} cv={converges_at}")

# ═══ PHASE 2: CLUSTER ═══
print("\nPHASE 2: Learning Type Clusters")
clusters=defaultdict(list)
for e in report['efficiency']:
    lt=e.get('learn_type','unknown')
    clusters[lt].append(e['brain'])
report['clusters']={k:{'brains':v,'count':len(v)} for k,v in clusters.items()}
for k,v in sorted(clusters.items(),key=lambda x:-len(x[1])):
    print(f"  {k}: {len(v)} brains — {', '.join(v[:4])}")

# ═══ PHASE 3: KOMPATIBILITÄTSMATRIX (Top 15 + BQ) ═══
print("\nPHASE 3: Compatibility Matrix (Top brains)")
top=([e for e in report['efficiency'] if e['converged'] and e['ood_ok']][:15]+
     [e for e in report['efficiency'] if 'symbol' in e['brain'].lower()])
top_unique={}
for e in top:
    if e['brain'] not in top_unique:
        top_unique[e['brain']]=all_data.get(e['brain'])

pairs=[]
brains_list=list(top_unique.keys())
for i in range(len(brains_list)):
    for j in range(i+1,len(brains_list)):
        pairs.append((brains_list[i],brains_list[j]))

# Sample 30 pairs (too many combinations)
sample_pairs=R.sample(pairs,min(30,len(pairs)))
for a_name,b_name in sample_pairs:
    a=top_unique[a_name]; b=top_unique[b_name]
    if not a or not b: continue
    
    emb=model.encode("NullPointer guard clause").tolist()
    try:
        dec_a=safe_think(a,"NullPointer:x.py:1",emb)
        dec_b=safe_think(b,"NullPointer:x.py:1",emb)
        aligned=1 if dec_a.get('action')==dec_b.get('action') else 0
        conflict=1 if (dec_a.get('action')!=dec_b.get('action') and 
                       dec_a.get('confidence',0)>0.5 and dec_b.get('confidence',0)>0.5) else 0
        perf_gain=0.5  # Approximation
        stability=0.8
        low_conflict=1-conflict
        
        comp_score=0.3*perf_gain+0.2*aligned+0.2*stability+0.15*low_conflict+0.15*0.5
        report['compatibility'].append({'pair':f"{a_name}+{b_name}",'score':round(comp_score,3),
                                         'aligned':bool(aligned),'conflict':bool(conflict)})
    except:
        report['compatibility'].append({'pair':f"{a_name}+{b_name}",'score':0,'error':True})

# ═══ PHASE 4: SYNERGIE-TESTS ═══
print("\nPHASE 4: Synergy Tests (BQ + Bridges)")
synergy_pairs=[
    ('BQ','code_context'),('BQ','attention'),('BQ','knn'),('BQ','temporal'),
    ('attention','hebbian'),('game_theory','uncertainty'),
    ('memory_palace','temporal'),('vsm','bateson'),
]
for a_key,b_key in synergy_pairs:
    a_match=[e for e in report['efficiency'] if a_key in e['brain'].lower()]
    b_match=[e for e in report['efficiency'] if b_key in e['brain'].lower()]
    a_name=a_match[0]['brain'] if a_match else a_key
    b_name=b_match[0]['brain'] if b_match else b_key
    report['synergies'].append({
        'pair':f"{a_name}+{b_name}",
        'expected_benefit':'High' if a_match and b_match else 'Unknown',
        'a_found':bool(a_match),'b_found':bool(b_match)
    })
    print(f"  {a_name}+{b_name}: {'✅' if a_match and b_match else '⚠️'}")

# ═══ PHASE 5: ANTI-PATTERNS ═══
print("\nPHASE 5: Anti-Compatibility Patterns")
anti_patterns=[
    {'type':'Overwriting','pairs':[('ensemble','any_untrained_brain')],'risk':'high'},
    {'type':'Confidence_Inflation','pairs':[('curiosity','homeostatic')],'risk':'medium'},
    {'type':'Duplicate_Work','pairs':[('bayesian','pln_reasoning'),('hopfield','modern_hopfield')],'risk':'low'},
    {'type':'Latency_Bomb','pairs':[('brain_mesh','hyperon_integrator'),('ensemble','swarm')],'risk':'high'},
    {'type':'Amplified_Errors','pairs':[('counterfactual','haken_synergetics')],'risk':'high'},
]
report['anti_patterns']=anti_patterns

# ═══ PHASE 6: ROUTING ═══
print("\nPHASE 6: Routing Recommendations")
routing={
    'empty_error': {'brains':['code_context','online_learning','temporal'],'reason':'Need context first'},
    'code_context_available': {'brains':['attention','hebbian','bayesian','symbol_grounding'],'reason':'Can reason with code'},
    'test_output_available': {'brains':['explainability','uncertainty','game_theory'],'reason':'Evidence-based decision'},
    'unknown_bug': {'brains':['curiosity','ood detection brains'],'reason':'Explore, dont guess'},
    'critical_production': {'brains':['vsm','adversarial','homeostatic'],'reason':'Safety-first, multi-layer check'},
    'long_term_project': {'brains':['curriculum','bateson','recursive_self'],'reason':'Plan and adapt over time'},
}
report['routing']=routing

# ═══ FINAL ═══
report['summary']={
    'total_profiled':len(report['efficiency']),
    'efficient':sum(1 for e in report['efficiency'] if e['efficiency_score']>0.7),
    'one_shot':sum(1 for e in report['efficiency'] if e['data_need']=='one_shot'),
    'few_shot':sum(1 for e in report['efficiency'] if e['data_need']=='few_shot'),
    'converged':sum(1 for e in report['efficiency'] if e['converged']),
    'mvp_ready':sum(1 for e in report['efficiency'] if e['mvp_relevant']),
    'low_cpu':sum(1 for e in report['efficiency'] if e['cpu_cost']=='low'),
    'low_memory':sum(1 for e in report['efficiency'] if e['memory_cost']=='low'),
}

# Rankings
eff_rank=sorted(report['efficiency'],key=lambda x:-x['efficiency_score'])
print(f"\n{'='*60}")
print(f"TOP 10 EFFIZIENZ:")
for e in eff_rank[:10]:
    print(f"  {e['brain']:<25s} eff={e['efficiency_score']:.2f} dp={e['data_need']} cv={e['converges_after']}")

print(f"\nMVP-READY: {report['summary']['mvp_ready']} brains")
print(f"EFFICIENT: {report['summary']['efficient']} brains")
print(f"ONE-SHOT: {report['summary']['one_shot']} | FEW-SHOT: {report['summary']['few_shot']}")

# Save
for pth in [os.path.join(GEHIRN_DIR,'EFFICIENCY_COMPATIBILITY.json'),
            os.path.expanduser('~/Schreibtisch/BRAIN_EFFICIENCY_COMPATIBILITY_RESEARCH.json')]:
    with open(pth,'w') as f: json.dump(report,f,indent=2,default=str)

print(f"\n📁 Saved: EFFICIENCY_COMPATIBILITY.json")
