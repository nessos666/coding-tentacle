"""
20 SCHWACHE GEHIRNE — 10-SCHICHT DIAGNOSE
10-Layer Deep Test für jedes Problem-Gehirn.
Layer 1-3: Grundfunktion | Layer 4-6: Lernen | Layer 7-8: Robustheit | Layer 9-10: Edge Cases
"""
import sys,os,time,random,json,numpy as np
from collections import defaultdict
from sentence_transformers import SentenceTransformer

GEHIRN_DIR='/home/boobi/GEHIRN_BIBLIOTHEK'
model=SentenceTransformer('all-MiniLM-L6-v2')
R=random

# Liste der 20 schwachen Gehirne aus dem Master-Protokoll
WEAK_BRAINS=[
    ('04_reinforcement','rl_brain','RLBrain'),
    ('13_attention','attention_brain','AttentionBrain'),
    ('15_ensemble','ensemble_brain','EnsembleBrain'),
    ('22_memory_palace','palace_brain','MemoryPalaceBrain'),
    ('29_swarm','swarm_brain','SwarmBrain'),
    ('30_hierarchical_rl','hrl_brain','HierarchicalRLBrain'),
    ('35_atomspace','atomspace_brain','AtomSpaceBrain'),
    ('39_pln_reasoning','pln_brain','PLNReasoningBrain'),
    ('41_hyperon_integrator','hyperon_brain','HyperonIntegratorBrain'),
    ('43_maturana_autopoiesis','autopoiesis_brain','AutopoiesisBrain'),
    ('44_bateson_learning','bateson_brain','BatesonBrain'),
    ('48_online_learning','online_brain','OnlineLearningBrain'),
    ('49_temporal_awareness','temporal_brain','TemporalBrain'),
    ('50_counterfactual','counterfactual_brain','CounterfactualBrain'),
    ('51_brain_mesh','mesh_brain','BrainMesh'),
    ('53_multitask_sharing','multitask_brain','MultiTaskBrain'),
    ('54_haken_synergetics','synergetics_brain','SynergeticsBrain'),
    ('58_wolfram_ca','wolfram_brain','CellularAutomataBrain'),
    ('61_levin_basal','basal_brain','BasalCognitionBrain'),
    ('65_homeostatic','homeostatic_brain','HomeostaticBrain'),
    ('68_emotion','emotion_brain','EmotionBrain'),
]

print("="*75)
print("  20 SCHWACHE GEHIRNE — 10-SCHICHT TIEFEN-DIAGNOSE")
print(f"  {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("="*75)

diagnosis={}
emb_np=model.encode("NullPointer null check guard clause defensive").tolist()
emb_ood=model.encode("StackOverflow recursion depth exceeded maximum").tolist()

for folder, mod_name, class_name in WEAK_BRAINS:
    name=folder.split('_',1)[1] if '_' in folder else folder
    print(f"\n─── {name} ───")
    
    brain_path=os.path.join(GEHIRN_DIR,folder)
    sys.path.insert(0,brain_path)
    
    try:
        exec(f"from {mod_name} import {class_name}")
        BrainClass=eval(class_name)
    except Exception as e:
        print(f"  L1-LOAD: ❌ {str(e)[:60]}")
        diagnosis[name]={'status':'LOAD_ERROR','error':str(e)[:80]}
        continue
    
    # L1: Instantiierung
    try:
        b=BrainClass()
        print(f"  L1-INSTANTIATE: ✅")
    except Exception as e:
        print(f"  L1-INSTANTIATE: ❌ {str(e)[:60]}")
        diagnosis[name]={'status':'INSTANTIATE_ERROR','error':str(e)[:80]}
        continue
    
    # L2: Initialer Think
    try:
        dec=b.think("NullPointer:test.py:1",emb_np)
        print(f"  L2-FIRST_THINK: ✅ action={dec.get('action','?')}")
    except Exception as e:
        print(f"  L2-FIRST_THINK: ❌ {str(e)[:60]}")
        diagnosis[name]={'status':'THINK_ERROR','error':str(e)[:80]}
        continue
    
    # L3: Erstes Learn
    try:
        b.learn("NullPointer:t1.py:1","guard_clause",True,emb_np)
        print(f"  L3-FIRST_LEARN: ✅")
    except:
        try:
            b.learn("NullPointer:t1.py:1","guard_clause",True)
            print(f"  L3-FIRST_LEARN: ✅ (no emb)")
        except Exception as e:
            print(f"  L3-FIRST_LEARN: ❌ {str(e)[:60]}")
            diagnosis[name]={'status':'LEARN_ERROR','error':str(e)[:80]}
            continue
    
    # L4-L6: Trainings-Phasen
    results={}
    
    # L4: Nach 5 Trainings
    for ep in range(4):
        try: b.learn(f"NullPointer:f{ep}.py:{ep}","guard_clause",True,emb_np)
        except:
            try: b.learn(f"NullPointer:f{ep}.py:{ep}","guard_clause",True)
            except: pass
    dec=b.think("NullPointer:L4.py:1",emb_np)
    t4=1 if dec.get('action')=='APPLY_PATTERN' else 0
    print(f"  L4-AFTER_5: {'✅' if t4 else '❌'} action={dec.get('action','?')}")
    
    # L5: Nach 20 Trainings
    for ep in range(15):
        try: b.learn(f"NullPointer:g{ep}.py:{ep}","guard_clause",R.random()<0.85,emb_np)
        except:
            try: b.learn(f"NullPointer:g{ep}.py:{ep}","guard_clause",R.random()<0.85)
            except: pass
    dec=b.think("NullPointer:L5.py:1",emb_np)
    t5=1 if dec.get('action')=='APPLY_PATTERN' else 0
    t5_conf=dec.get('confidence',0)
    print(f"  L5-AFTER_20: {'✅' if t5 else '❌'} conf={t5_conf:.2f}")
    
    # L6: OOD Detection
    dec=b.think("StackOverflow:x.py:1",emb_ood)
    t6=1 if dec.get('action')=='EXPLORE' else 0
    print(f"  L6-OOD: {'✅' if t6 else '❌'} (sollte EXPLORE sein)")
    
    # L7: Interference
    for ep in range(15):
        try: b.learn(f"NullPointer:noise{ep}.py:{ep}","guard_clause",False,emb_np)
        except:
            try: b.learn(f"NullPointer:noise{ep}.py:{ep}","guard_clause",False)
            except: pass
    dec=b.think("NullPointer:L7.py:1",emb_np)
    t7=1 if dec.get('action')=='APPLY_PATTERN' else 0
    print(f"  L7-INTERFERENCE: {'✅' if t7 else '❌'} (sollte Pattern behalten)")
    
    # L8: Multi-Type
    t8=0
    for bt in ['OffByOne','TypeError']:
        emb_bt=model.encode(f"{bt} error in code").tolist()
        for ep in range(5):
            try: b.learn(f"{bt}:f{ep}.py:{ep}",f"fix_{bt}",True,emb_bt)
            except:
                try: b.learn(f"{bt}:f{ep}.py:{ep}",f"fix_{bt}",True)
                except: pass
        dec=b.think(f"{bt}:L8.py:1",emb_bt)
        if dec.get('action')=='APPLY_PATTERN': t8+=1
    print(f"  L8-MULTI_TYPE: {t8}/2 Typen erkannt")
    
    # L9: Edge Case — leerer Bug-Typ
    try:
        dec=b.think(":empty.py:1",[0]*384)
        print(f"  L9-EDGE_EMPTY: ✅ handled")
    except Exception as e:
        print(f"  L9-EDGE_EMPTY: ⚠️ {str(e)[:40]}")
    
    # L10: Stats
    try:
        s=b.stats()
        print(f"  L10-STATS: ✅ type={s.get('brain_type','?')}")
    except Exception as e:
        print(f"  L10-STATS: ❌ {str(e)[:40]}")
    
    score=(t4+t5*2+t6+t7*2+t8)/7
    diagnosis[name]={'score':round(score,2),'L4_after5':t4,'L5_after20':t5,'L6_OOD':t6,
                     'L7_interf':t7,'L8_multi':t8,'status':'FIXED' if score>=0.6 else 'WEAK' if score>=0.3 else 'FAIL'}
    
    icon='✅' if score>=0.6 else ('⚠️' if score>=0.3 else '❌')
    print(f"  ▶ GESAMT: {icon} Score={score:.2f}")

# ═══ ZUSAMMENFASSUNG ═══
print(f"\n{'='*75}")
print(f"  10-SCHICHT DIAGNOSE — ERGEBNIS")
print(f"{'='*75}")

fixed=sum(1 for d in diagnosis.values() if d.get('status')=='FIXED')
weak=sum(1 for d in diagnosis.values() if d.get('status')=='WEAK')
fail=sum(1 for d in diagnosis.values() if d.get('status')=='FAIL')
loaded_err=sum(1 for d in diagnosis.values() if 'ERROR' in d.get('status',''))

print(f"  ✅ Nach tieferem Test BEHOBEN: {fixed}")
print(f"  ⚠️ Immer noch schwach:         {weak}")
print(f"  ❌ Immer noch Fehler:          {fail+loaded_err}")
print(f"  📊 Durchschnitt:               {np.mean([d.get('score',0) for d in diagnosis.values() if 'score' in d]):.2f}")

print(f"\n  Details:")
for name,d in sorted(diagnosis.items(),key=lambda x:x[1].get('score',0)):
    icon='✅' if d.get('score',0)>=0.6 else ('⚠️' if d.get('score',0)>=0.3 else '❌')
    print(f"  {icon} {name:<25s} Score={d.get('score',0):.2f} {d.get('status','?')}")

out={
    'timestamp':time.strftime('%Y-%m-%d %H:%M:%S'),
    'total_tested':len(diagnosis),
    'fixed':fixed,'weak':weak,'fail':fail,
    'avg_score':round(np.mean([d.get('score',0) for d in diagnosis.values() if 'score' in d]),2),
    'diagnosis':{k:{kk:vv for kk,vv in v.items() if kk!='error'} for k,v in diagnosis.items()}
}

for pth in [os.path.join(GEHIRN_DIR,'10_SCHICHT_DIAGNOSE.json'),
            os.path.expanduser('~/Schreibtisch/10_SCHICHT_DIAGNOSE.json')]:
    with open(pth,'w') as f: json.dump(out,f,indent=2,default=str)

print(f"\n  📁 Gespeichert in GEHIRN_BIBLIOTHEK + Desktop")
