"""
20 GEHIRNE — 10 NEUE TEST-ARTEN (Research-basiert)
Tests aus: AgentMemoryBench (2026), Agentic Confidence Calibration (2026),
Continual Learning Benchmarks (BWT/FWT), OOD Detection Standards.

10 Test-Typen:
1. Transfer (FWT)      6. Interferenz
2. Forgetting (BWT)    7. Skalierbarkeit
3. Kalibrierung (ECE)  8. Diversität
4. Zero-Shot OOD       9. Recovery
5. Persistenz          10. Cross-Modal
"""
import sys,os,time,math,random,json,numpy as np
from collections import defaultdict, Counter

# ALLE 20 laden
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/01_bayesian'); from bayesian_brain import BayesianBrain
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/02_shannon_entropie'); from shannon_brain import ShannonBrain
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/03_graph_struktur'); from graph_brain import GraphBrain
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/04_reinforcement'); from rl_brain import RLBrain
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/05_kybernetisch'); from kybernetisch_brain import KybernetischBrain
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/06_act_r_spreading')
from actr_brain import ACTRBrain; from friston_brain import PredictiveCodingBrain
from causal_brain import CausalBrain; from kolmogorov_brain import KolmogorovBrain, ncd_distance
from mandelbrot_brain import MandelbrotBrain, hurst_exponent
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/11_hebbian'); from hebbian_brain import HebbianBrain
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/12_genetisch'); from genetic_brain import GeneticBrain
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/13_attention'); from attention_brain import AttentionBrain
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/14_fuzzy'); from fuzzy_brain import FuzzyBrain
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/15_ensemble'); from ensemble_brain import EnsembleBrain
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/16_game_theory'); from game_theory_brain import GameTheoryBrain
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/17_gradient'); from gradient_brain import GradientBrain
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/18_nearest_neighbor'); from nn_brain import NearestNeighborBrain
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/19_markov'); from markov_brain import MarkovBrain
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/20_contrastive'); from contrastive_brain import ContrastiveBrain

from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')

BRAINS = {
    'A_Bayesian': lambda: BayesianBrain(k=0.5),
    'B_Shannon': lambda: ShannonBrain(explore_threshold=2.0),
    'C_Graph': lambda: GraphBrain(0.3),
    'D_RL': lambda: RLBrain(alpha=0.1, gamma=0.9, epsilon=0.3),
    'E_Kybernetisch': lambda: KybernetischBrain(),
    'F_ACTR': lambda: ACTRBrain(decay=0.5, threshold=-3.0),
    'G_Friston': lambda: PredictiveCodingBrain(384, 0.1),
    'H_Causal': lambda: CausalBrain(),
    'I_Kolmogorov': lambda: KolmogorovBrain(0.15),
    'J_Mandelbrot': lambda: MandelbrotBrain(0.3),
    'K_Hebbian': lambda: HebbianBrain(lr=0.15, decay=0.0001, threshold=0.15),
    'L_Genetisch': lambda: GeneticBrain(pop_size=30),
    'M_Attention': lambda: AttentionBrain(d_k=64),
    'N_Fuzzy': lambda: FuzzyBrain(),
    'O_Ensemble': lambda: EnsembleBrain(),
    'P_GameTheory': lambda: GameTheoryBrain(),
    'Q_Gradient': lambda: GradientBrain(lr=0.1),
    'R_NearestNeighbor': lambda: NearestNeighborBrain(k=5),
    'S_Markov': lambda: MarkovBrain(gamma=0.9),
    'T_Contrastive': lambda: ContrastiveBrain(temperature=0.1, lr=0.1),
}
results = {}; all_brain_results = defaultdict(dict)

def learn_brain(brain, bt, sig, pat, ok, emb=None):
    try: brain.learn(sig, pat, ok, emb)
    except: brain.learn(sig, pat, ok)

print("="*70)
print("  🧠 20 GEHIRNE × 10 NEUE TEST-ARTEN")
print("  AgentMemoryBench | ECE | BWT/FWT | OOD | Persistenz")
print("="*70)

# ═══ TEST 1: TRANSFER LERNING (FWT) ═══
print("\n─── Test 1: Transfer Learning (FWT) ───")
# Train auf NullPointer → Test auf AttributeError (ähnlicher Bug-Typ)
for name, factory in BRAINS.items():
    brain = factory()
    for ep in range(15):
        learn_brain(brain, 'NullPointer', f"NullPointer:f{ep}.py:{ep}", "guard", True,
                    model.encode("NullPointer null check guard").tolist())
    # Test auf ähnlichem Bug-Typ
    emb = model.encode("AttributeError attribute missing None").tolist()
    dec = brain.think("AttributeError:test.py:1", emb)
    hit = 1 if dec['action'] == 'APPLY_PATTERN' else 0
    all_brain_results[name]['Transfer'] = hit
hits = sum(v['Transfer'] for v in all_brain_results.values())
print(f"  Transfer (NullPointer→AttributeError): {hits}/20 Gehirne erkennen ähnlichen Typ")

# ═══ TEST 2: CATASTROPHIC FORGETTING (BWT) ═══
print("\n─── Test 2: Catastrophic Forgetting (BWT) ───")
for name, factory in BRAINS.items():
    brain = factory()
    emb_n = model.encode("NullPointer null check").tolist()
    # Phase A: NullPointer trainieren
    for ep in range(10):
        learn_brain(brain, 'NullPointer', f"NullPointer:f{ep}.py:{ep}", "guard", True, emb_n)
    dec_a = brain.think("NullPointer:test.py:1", emb_n)
    hit_a = 1 if dec_a['action'] == 'APPLY_PATTERN' else 0
    # Phase B: 3 andere Typen trainieren (Interferenz)
    for bt in ['OffByOne','TypeError','MemoryLeak']:
        for ep in range(8):
            emb = model.encode(f"{bt} error").tolist()
            learn_brain(brain, bt, f"{bt}:f{ep}.py:{ep}", f"fix_{bt}", True, emb)
    # Phase C: NullPointer erneut testen
    dec_c = brain.think("NullPointer:test.py:2", emb_n)
    hit_c = 1 if dec_c['action'] == 'APPLY_PATTERN' else 0
    # BWT: 0 = kein Vergessen (besser), -1 = vergessen
    bwt = hit_c - hit_a  
    all_brain_results[name]['Forgetting'] = hit_c
bwt_kept = sum(v['Forgetting'] for v in all_brain_results.values())
print(f"  BWT (NullPointer nach Interferenz): {bwt_kept}/20 behalten Pattern")

# ═══ TEST 3: CONFIDENCE CALIBRATION (ECE) ═══
print("\n─── Test 3: Confidence Calibration (ECE) ───")
ece_scores = {}
for name, factory in BRAINS.items():
    brain = factory()
    confs = []; accs = []
    for bt, true_rate in [('NullPointer',0.9),('OffByOne',0.7),('TypeError',0.5)]:
        for ep in range(25):
            emb = model.encode(f"{bt} error").tolist()
            sig = f"{bt}:f{ep}.py:{ep}"
            dec = brain.think(sig, emb)
            ok = random.random() < true_rate
            learn_brain(brain, bt, sig, f"fix_{bt}", ok, emb)
            if dec['action'] == 'APPLY_PATTERN' and ep > 5:
                confs.append(dec.get('confidence', 0.5))
                accs.append(1 if ok else 0)
    if confs:
        # ECE = mean(|conf - acc|) pro Bin
        bins = [0, 0.25, 0.5, 0.75, 1.0]
        ece = 0
        for i in range(len(bins)-1):
            mask = [(c >= bins[i] and c < bins[i+1]) for c in confs]
            if sum(mask) > 0:
                avg_conf = np.mean([confs[j] for j, m in enumerate(mask) if m])
                avg_acc = np.mean([accs[j] for j, m in enumerate(mask) if m])
                ece += (sum(mask)/len(confs)) * abs(avg_conf - avg_acc)
        ece_scores[name] = ece
        all_brain_results[name]['ECE'] = round(ece, 3)
avg_ece = np.mean(list(ece_scores.values())) if ece_scores else 0
print(f"  ECE (Expected Calibration Error): μ={avg_ece:.3f} (0=perfekt)")
print(f"  Best 3: {sorted(ece_scores.items(), key=lambda x: x[1])[:3]}")

# ═══ TEST 4: ZERO-SHOT OOD ═══
print("\n─── Test 4: Zero-Shot OOD Detection ───")
ood_hits = {}
for name, factory in BRAINS.items():
    brain = factory()
    # Trainiere auf 3 bekannten Typen
    for bt in ['NullPointer','OffByOne','TypeError']:
        for ep in range(8):
            learn_brain(brain, bt, f"{bt}:f{ep}.py:{ep}", f"fix_{bt}", True,
                       model.encode(f"{bt} error").tolist())
    # Teste auf KOMPLETT unbekanntem Typ
    dec = brain.think("StackOverflow:unknown.py:1", 
                      model.encode("StackOverflow recursion depth exceeded").tolist())
    hit = 1 if dec['action'] == 'EXPLORE' else 0  # RICHTIG: EXPLORE für unbekannt
    ood_hits[name] = hit
    all_brain_results[name]['OOD'] = hit
ood_correct = sum(ood_hits.values())
print(f"  OOD (richtig 'Weiß nicht'): {ood_correct}/20 Gehirne erkennen Unbekanntes")

# ═══ TEST 5: MEMORY PERSISTENZ ═══
print("\n─── Test 5: Memory Persistence ───")
persist_hits = {}
for name, factory in BRAINS.items():
    brain = factory()
    emb = model.encode("NullPointer null check guard").tolist()
    for ep in range(20):
        learn_brain(brain, 'NullPointer', f"NullPointer:f{ep}.py:{ep}", "guard", True, emb)
    dec_before = brain.think("NullPointer:test.py:1", emb)
    # Simuliere Teil-Amnesie: NUR Gehirne mit memories/cases/chunks betroffen
    # (lösche älteste 50% der Einträge)
    if hasattr(brain, 'memories') and brain.memories:
        brain.memories = brain.memories[len(brain.memories)//2:]
    elif hasattr(brain, 'cases') and brain.cases:
        brain.cases = brain.cases[len(brain.cases)//2:]
    elif hasattr(brain, 'chunks') and brain.chunks:
        oldest = sorted(brain.chunks.keys())[:len(brain.chunks)//2]
        for k in oldest: del brain.chunks[k]
    # Auch ohne manipulierte Struktur: nur think-Test
    dec_after = brain.think("NullPointer:test.py:2", emb)
    hit = 1 if dec_after['action'] == 'APPLY_PATTERN' else 0
    persist_hits[name] = hit
    all_brain_results[name]['Persistenz'] = hit
persist_correct = sum(persist_hits.values())
print(f"  Persistenz (nach 50% Amnesie): {persist_correct}/20 behalten Pattern")

# ═══ TEST 6: INTERFERENZ-ROBUSTHEIT ═══
print("\n─── Test 6: Interference Robustness ───")
interf_hits = {}
for name, factory in BRAINS.items():
    brain = factory()
    # Gutes Pattern trainieren
    emb = model.encode("NullPointer null check").tolist()
    for ep in range(10):
        learn_brain(brain, 'NullPointer', f"NullPointer:f{ep}.py:{ep}", "guard", True, emb)
    dec_before = brain.think("NullPointer:test.py:1", emb)
    # Flood mit NEGATIVEN Beispielen
    for ep in range(15):
        learn_brain(brain, 'NullPointer', f"NullPointer:noise{ep}.py:{ep}", "guard", False, emb)
    dec_after = brain.think("NullPointer:test.py:2", emb)
    hit = 1 if dec_after['action'] == 'APPLY_PATTERN' else 0
    interf_hits[name] = hit
    all_brain_results[name]['Interferenz'] = hit
interf_kept = sum(interf_hits.values())
print(f"  Interferenz (15× negativ, Pattern hält): {interf_kept}/20 resistent")

# ═══ TEST 7: SKALIERBARKEIT ═══
print("\n─── Test 7: Scalability (50→200 Bugs) ───")
scale_scores = {}
for name, factory in BRAINS.items():
    brain = factory()
    # 50 Bugs
    for ep in range(50):
        bt = ['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'][ep%5]
        learn_brain(brain, bt, f"{bt}:f{ep}.py:{ep}", f"fix_{bt}", True,
                   model.encode(f"{bt} error").tolist())
    dec1 = brain.think("NullPointer:test.py:1", model.encode("NullPointer error").tolist())
    # 150 weitere
    for ep in range(150):
        bt = ['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'][ep%5]
        learn_brain(brain, bt, f"{bt}:f2_{ep}.py:{ep}", f"fix_{bt}", True,
                   model.encode(f"{bt} error").tolist())
    dec2 = brain.think("NullPointer:test.py:2", model.encode("NullPointer error").tolist())
    # Skaliert? (beide sollten APPLY sein)
    hit = 1 if (dec1['action'] == 'APPLY_PATTERN' and dec2['action'] == 'APPLY_PATTERN') else 0
    scale_scores[name] = hit
    all_brain_results[name]['Skalierbarkeit'] = hit
scale_ok = sum(scale_scores.values())
print(f"  Skalierbarkeit (50→200 Bugs, Pattern bleibt): {scale_ok}/20 skalieren sauber")

# ═══ TEST 8: ENSEMBLE DIVERSITÄT ═══
print("\n─── Test 8: Diversity (5 Gehirne, 1 Bug) ───")
# Teste: Geben Baye/Shannon/Graph/ACTR/Hebb unterschiedliche Antworten?
test_brains = {'Bayesian': BayesianBrain(k=0.5), 'Shannon': ShannonBrain(), 
               'Graph': GraphBrain(0.3), 'ACTR': ACTRBrain(threshold=-5.0),
               'Hebbian': HebbianBrain()}
for bt in ['NullPointer','OffByOne','TypeError']:
    for ep in range(5):
        emb = model.encode(f"{bt} error").tolist()
        for nb, nb_brain in test_brains.items():
            learn_brain(nb_brain, bt, f"{bt}:f{ep}.py:{ep}", f"fix_{bt}", True, emb)

emb = model.encode("NullPointer null check guard clause").tolist()
answers = {}
for nb, nb_brain in test_brains.items():
    dec = nb_brain.think("NullPointer:test.py:1", emb)
    answers[nb] = dec['action']

unique = len(set(answers.values()))
all_brain_results['ENSEMBLE_Diversity'] = {'Diversität': unique}
print(f"  Diversität: {unique} verschiedene Antworten auf 5 Gehirne (max=5, min=1)")

# ═══ TEST 9: RECOVERY ═══
print("\n─── Test 9: Recovery from Mistakes ───")
recov_hits = {}
for name, factory in BRAINS.items():
    brain = factory()
    emb = model.encode("NullPointer null check").tolist()
    # Gutes Pattern lernen
    for ep in range(5):
        learn_brain(brain, 'NullPointer', f"NullPointer:f{ep}.py:{ep}", "guard", True, emb)
    # Fehler simulieren: 10× negatives Feedback
    for ep in range(10):
        learn_brain(brain, 'NullPointer', f"NullPointer:bad{ep}.py:{ep}", "guard", False, emb)
    # Re-Lernen mit positivem Feedback
    for ep in range(10):
        learn_brain(brain, 'NullPointer', f"NullPointer:recover{ep}.py:{ep}", "guard", True, emb)
    dec = brain.think("NullPointer:test.py:1", emb)
    hit = 1 if dec['action'] == 'APPLY_PATTERN' else 0
    recov_hits[name] = hit
    all_brain_results[name]['Recovery'] = hit
recov_ok = sum(recov_hits.values())
print(f"  Recovery (neg→pos re-lernen): {recov_ok}/20 erholen sich")

# ═══ TEST 10: CROSS-MODAL ═══
print("\n─── Test 10: Cross-Modal Transfer ───")
cross_hits = {}
for name, factory in BRAINS.items():
    brain = factory()
    # Trainiere auf Bug-BESCHREIBUNGEN
    for ep in range(10):
        emb = model.encode("NullPointerException: object reference is None, needs null check before access").tolist()
        learn_brain(brain, 'NullPointer', f"NullPointer:desc{ep}.py:{ep}", "guard", True, emb)
    # Teste auf CODE-KONTEXT (anderes Embedding)
    emb_test = model.encode("if obj != None: obj.process() else: raise ValueError('obj is None')").tolist()
    dec = brain.think("NullPointer:code_test.py:1", emb_test)
    hit = 1 if dec['action'] == 'APPLY_PATTERN' else 0
    cross_hits[name] = hit
    all_brain_results[name]['CrossModal'] = hit
cross_ok = sum(cross_hits.values())
print(f"  Cross-Modal (Beschreibung→Code): {cross_ok}/20 transferieren")

# ═══ FINALES RANKING ═══
print(f"\n{'='*70}")
print(f"  🏆 10 NEUE TEST-ARTEN — ZUSAMMENFASSUNG")
print(f"{'='*70}")
print(f"  {'Gehirn':<20s} {'T1':>3s} {'T2':>3s} {'T3':>5s} {'T4':>3s} {'T5':>3s} {'T6':>3s} {'T7':>3s} {'T9':>3s} {'T10':>3s}")
print(f"  {'-'*60}")
for name in sorted(all_brain_results.keys()):
    if name == 'ENSEMBLE_Diversity': continue
    r = all_brain_results[name]
    print(f"  {name:<20s} {r.get('Transfer',0):>3d} {r.get('Forgetting',0):>3d} {r.get('ECE',0):>5.3f} "
          f"{r.get('OOD',0):>3d} {r.get('Persistenz',0):>3d} {r.get('Interferenz',0):>3d} "
          f"{r.get('Skalierbarkeit',0):>3d} {r.get('Recovery',0):>3d} {r.get('CrossModal',0):>3d}")

# Gesamtscore (höher=besser, ECE invertiert)
totals = {}
for name, r in all_brain_results.items():
    if name == 'ENSEMBLE_Diversity': continue
    score = (r.get('Transfer',0) + r.get('Forgetting',0) + (1-min(r.get('ECE',1),1)) 
             + r.get('OOD',0) + r.get('Persistenz',0) + r.get('Interferenz',0)
             + r.get('Skalierbarkeit',0) + r.get('Recovery',0) + r.get('CrossModal',0))
    totals[name] = round(score/9, 3)

print(f"\n  🏆 TOP 10 NACH 9 KATEGORIEN:")
for name, score in sorted(totals.items(), key=lambda x: -x[1])[:10]:
    print(f"  {name:<20s} {score:.3f}")

with open('/home/boobi/GEHIRN_BIBLIOTHEK/07_experimente/10_neue_tests.json','w') as f:
    json.dump({'ts':time.strftime('%Y-%m-%d %H:%M'), 'totals':totals, 'results':all_brain_results}, f, indent=2, default=str)
print(f"\n  📁 /home/boobi/GEHIRN_BIBLIOTHEK/07_experimente/10_neue_tests.json")
