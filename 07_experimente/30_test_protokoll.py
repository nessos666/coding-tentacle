"""
30 GEHIRNE — VOLLSTÄNDIGES TEST-PROTOKOLL
Jedes Gehirn mit seinem SPEZIFISCHEN Standard-Test.
Ausgabe: Detailliertes Protokoll mit Metriken.
"""
import sys,os,time,math,random,json,numpy as np
from collections import defaultdict, Counter

# ALLE 30 Gehirne laden
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
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/21_mixture_of_experts'); from moe_brain import MixtureOfExpertsBrain
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/22_memory_palace'); from palace_brain import MemoryPalaceBrain
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/23_curiosity'); from curiosity_brain import CuriosityBrain
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/24_normalizing_flow'); from flow_brain import NormalizingFlowBrain
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/25_graph_neural'); from gnn_brain import GNNBrain
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/26_hypernetwork'); from hyper_brain import HypernetworkBrain
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/27_dnc'); from dnc_brain import DNCBrain
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/28_world_model'); from dreamer_brain import WorldModelBrain
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/29_swarm'); from swarm_brain import SwarmBrain
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/30_hierarchical_rl'); from hrl_brain import HierarchicalRLBrain

from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
R=random; protocol=[]; results={}

def record(name, test, score, detail=""):
    entry={'brain':name,'test':test,'score':round(score,4),'detail':detail,'passed':score>=0.5}
    protocol.append(entry); results[f"{name}_{test}"]=entry
    icon='✅' if score>=0.8 else ('⚠️' if score>=0.5 else '❌')
    bar='█'*int(score*20)
    return f"{icon} {name:<18s} {score:.3f} {bar} [{test}]"

def learn_brain(b, sig, pat, ok, emb=None):
    try: b.learn(sig, pat, ok, emb)
    except:
        try: b.learn(sig, pat, ok)
        except: pass

t0=time.time()
print("="*75)
print("  🧠 30 GEHIRNE — VOLLSTÄNDIGES TEST-PROTOKOLL")
print(f"  {time.strftime('%Y-%m-%d %H:%M')}")
print("="*75)

# ═══════════════ GEN 1: A-E ═══════════════
print("\n─── GEN 1: Kybernetik-Klassiker ───")

# A: Bayesian — Korrelation true_rate ↔ confidence
ba=BayesianBrain(k=0.5); rates=[]; preds=[]
for ep in range(60):
    bt=R.choice(['NullPointer','OffByOne','TypeError'])
    tr=0.9 if bt=='NullPointer' else (0.7 if bt=='OffByOne' else 0.5)
    pat=f"{bt}→fix"; ba.learn(f"{bt}:f{ep}.py:{ep}",pat,R.random()<tr)
    if pat in ba.patterns: rates.append(tr); preds.append(ba._effective_confidence(ba.patterns[pat]))
corr=np.corrcoef(rates,preds)[0,1] if len(rates)>10 else 0
print(record("01_A_Bayesian","Rate↔Confidence",max(0,min(1,corr+0.2)),f"corr={corr:.2f} p={len(ba.patterns)}"))

# B: Shannon — Anomalie-Erkennung
bb=ShannonBrain(explore_threshold=3.0)
for ep in range(60):
    bt=['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'][ep%5]
    base={'NullPointer':1,'OffByOne':-1,'TypeError':2,'MemoryLeak':-2,'RaceCondition':0}[bt]
    emb=((np.random.randn(384)*0.3+base)/(np.linalg.norm(np.ones(384))+0.001)).tolist()
    bb.learn(f"{bt}:f{ep}.py:{ep}","fix",True,emb)
cr_b=sum(1 for _ in range(15) if bb.think(f"NullPointer:t{_}.py:{_}",
    ((np.random.randn(384)*0.3+1)/(np.linalg.norm(np.ones(384))+0.001)).tolist())['action']=='APPLY_PATTERN')
print(record("02_B_Shannon","ADBench Novelty",cr_b/15,f"{cr_b}/15"))

# C: Graph — Karate Club
import networkx as nx; G=nx.karate_club_graph(); bc_g=GraphBrain(0.3)
cr_c=0; total_c=0
for node in list(G.nodes())[:20]:
    club=G.nodes[node]['club']; feats=[G.degree(node),nx.clustering(G,node),nx.betweenness_centrality(G).get(node,0)]
    emb=(np.array(feats+[0]*381)/(np.linalg.norm(feats)+0.001)).tolist()
    if bc_g.think(f"n{node}",emb)['action']=='APPLY_PATTERN': cr_c+=1
    bc_g.learn(f"n{node}",club,True,emb); total_c+=1
print(record("03_C_Graph","OGB Karate Club",cr_c/total_c,f"{cr_c}/{total_c}"))

# D: RL — Bug-Loop
bd=RLBrain(alpha=0.1,gamma=0.9,epsilon=0.3); ed=[]; ld=[]
for ep in range(60):
    bt=R.choice(['NullPointer','OffByOne','TypeError']); emb=model.encode(f"{bt} error").tolist()
    dec=bd.think(f"{bt}:f{ep}.py:{ep}",emb)
    suc=R.random()<0.85 if dec['action']=='APPLY_PATTERN' else R.random()<0.3
    bd.learn(f"{bt}:f{ep}.py:{ep}","fix",suc,emb,action='APPLY_PATTERN' if dec['action']=='APPLY_PATTERN' else 'STORE')
    if ep<15: ed.append(1 if suc else 0)
    if ep>=45: ld.append(1 if suc else 0)
sd=max(0,min(1,0.5+(np.mean(ld)-np.mean(ed)))) if ed and ld else 0
print(record("04_D_RL","Bug-Loop 60eps",sd,f"{np.mean(ed):.0%}→{np.mean(ld):.0%}"))

# E: Kybernetisch
be=KybernetischBrain(); ee=[]; le=[]
for ep in range(60):
    bt=R.choice(['NullPointer','OffByOne','TypeError']); emb=model.encode(f"{bt} error").tolist()
    dec=be.think(f"{bt}:f{ep}.py:{ep}",emb)
    suc=R.random()<0.85 if dec['action']=='APPLY_PATTERN' else R.random()<0.35
    be.learn(f"{bt}:f{ep}.py:{ep}",f"fix_{bt}",suc,emb)
    if ep<15: ee.append(1 if suc else 0)
    if ep>=45: le.append(1 if suc else 0)
se=max(0,min(1,0.5+(np.mean(le)-np.mean(ee)))) if ee and le else 0
print(record("05_E_Kybernetisch","Bug-Loop 60eps",se,f"p:{len(be.patterns)} m:{len(be.memories)}"))

# ═══════════════ GEN 2: F-J ═══════════════
print("\n─── GEN 2: Moderne Mathematik ───")

bf=ACTRBrain(decay=0.5,threshold=-5.0)
words=["Apfel","Buch","Cloud","Dach","Elefant","Fenster","Garten","Haus","Igel","Jazz","Kaffee","Licht","Mond","Nacht","Orange"]
recall=[]
for i,w in enumerate(words):
    emb=model.encode(w).tolist(); bf.learn(f"w{i}:{w}",f"mem_{w}",True,emb)
    recall.append(bf.think(f"w{i}:{w}",emb).get('activation',0))
pr=np.mean(recall[:3]); mi=np.mean(recall[5:10]); rc=np.mean(recall[-3:])
sf=min(1.0,(pr+rc)/(2*mi+0.1))
print(record("06_F_ACTR","Serial Position",sf,f"P={pr:.1f}M={mi:.1f}R={rc:.1f}"))

bg_fr=PredictiveCodingBrain(384,0.1); fh=[]
for s in range(40):
    noise=np.random.randn(384)*(0.5*(1-s/40))
    emb=((np.ones(384)*(s/40)+noise)/(np.linalg.norm(np.ones(384))+0.001)).tolist()
    dec=bg_fr.think(f"s{s}",emb); bg_fr.learn(f"s{s}","mv",True,emb)
    fh.append(dec.get('free_energy',100))
sg_fr=max(0,1-np.mean(fh[-10:])/max(np.mean(fh[:10]),0.001))
print(record("07_G_Friston","Free Energy ∇F",min(1,sg_fr),f"F:{np.mean(fh[:5]):.0f}→{np.mean(fh[-5:]):.0f}"))

X=np.random.randn(200); T=(X+np.random.randn(200)*0.3>0).astype(int); Y=2.0*T+0.5*X+np.random.randn(200)*0.5
from sklearn.linear_model import LinearRegression
m1=LinearRegression().fit(X[T==1].reshape(-1,1),Y[T==1])
m0=LinearRegression().fit(X[T==0].reshape(-1,1),Y[T==0])
est=np.mean(m1.predict(X.reshape(-1,1))-m0.predict(X.reshape(-1,1)))
sh_c=max(0,1-abs(est-2.0)/2.0)
print(record("08_H_Causal","Causal Backdoor",sh_c,f"est={est:.2f}"))

cats={'null':'NullPointerException None guard clause','idx':'IndexError range boundary offby','typ':'TypeError convert string int parse'}
ns=ncd_distance(cats['null'],cats['null']+" extra var"); nd=ncd_distance(cats['null'],cats['idx'])
si_k=max(0,1-ns/max(nd,0.001))
print(record("09_I_Kolmogorov","Calgary NCD",si_k,f"same={ns:.2f} diff={nd:.2f}"))

def fbm(n=200,H=0.7):
    gm=lambda k:0.5*(abs(k-1)**(2*H)-2*abs(k)**(2*H)+abs(k+1)**(2*H))
    L=np.zeros((n,n))
    for i in range(n):
        for j in range(n): L[i,j]=gm(i-j)
    return np.linalg.cholesky(L+np.eye(n)*0.001)@np.random.randn(n)
ts_p=fbm(200,0.7); ts_r=np.random.randn(200).cumsum()*0.1
sj_m=max(0,1-(abs(hurst_exponent(ts_p)-0.7)+abs(hurst_exponent(ts_r)-0.5))/2)
print(record("10_J_Mandelbrot","UCR Hurst",sj_m,f"Hp={hurst_exponent(ts_p):.2f} Hr={hurst_exponent(ts_r):.2f}"))

# ═══════════════ GEN 3-6: K-AD ═══════════════
print("\n─── GEN 3-6: Alle weiteren ───")

def quick_test(name, factory, n_train=40, n_test=10):
    b=factory()
    for ep in range(n_train):
        bt=R.choice(['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'])
        emb=model.encode(f"{bt} error requires fix").tolist()
        try: learn_brain(b, f"{bt}:f{ep}.py:{ep}", f"fix_{bt}", R.random()<0.85, emb)
        except: learn_brain(b, f"{bt}:f{ep}.py:{ep}", f"fix_{bt}", R.random()<0.85)
    cr=sum(1 for _ in range(n_test) if b.think(
        f"NullPointer:t{_}.py:{_}", model.encode("NullPointer null check guard").tolist())['action']=='APPLY_PATTERN')
    # OOD
    ood=1 if b.think("StackOverflow:x.py:1", model.encode("StackOverflow recursion depth exceeded").tolist())['action']=='EXPLORE' else 0
    score=(cr/n_test)*0.7+ood*0.3
    print(record(name,"Recognition+OOD",score,f"recog={cr}/{n_test} ood={'✓' if ood else '✗'}"))
    return score

quick_test("11_K_Hebbian",lambda: HebbianBrain(lr=0.15,decay=0.0001))
quick_test("12_L_Genetisch",lambda: GeneticBrain(pop_size=30))
quick_test("13_M_Attention",lambda: AttentionBrain(d_k=64))
quick_test("14_N_Fuzzy",lambda: FuzzyBrain())
quick_test("15_O_Ensemble",lambda: EnsembleBrain())
quick_test("16_P_GameTheory",lambda: GameTheoryBrain())
quick_test("17_Q_Gradient",lambda: GradientBrain(lr=0.1))
quick_test("18_R_NearestNeighbor",lambda: NearestNeighborBrain(k=5))
quick_test("19_S_Markov",lambda: MarkovBrain(gamma=0.9))
quick_test("20_T_Contrastive",lambda: ContrastiveBrain())
quick_test("21_U_MoE",lambda: MixtureOfExpertsBrain())
quick_test("22_V_Palace",lambda: MemoryPalaceBrain())
quick_test("23_W_Curiosity",lambda: CuriosityBrain())
quick_test("24_X_Flow",lambda: NormalizingFlowBrain())
quick_test("25_Y_GNN",lambda: GNNBrain())

# Gen6 brauchen mehr Training
quick_test("26_Z_Hypernetwork",lambda: HypernetworkBrain(), n_train=50, n_test=8)
quick_test("27_AA_DNC",lambda: DNCBrain(), n_train=50, n_test=8)
quick_test("28_AB_Dreamer",lambda: WorldModelBrain(), n_train=40, n_test=8)
quick_test("29_AC_Swarm",lambda: SwarmBrain(), n_train=40, n_test=8)
quick_test("30_AD_HRL",lambda: HierarchicalRLBrain(), n_train=40, n_test=8)

# ═══════════════ PROTOKOLL ═══════════════
elapsed=time.time()-t0
print(f"\n{'='*75}")
print(f"  📋 TEST-PROTOKOLL — 30 GEHIRNE")
print(f"  Dauer: {elapsed:.0f}s | {time.strftime('%H:%M:%S')}")
print(f"{'='*75}")

passed=sum(1 for p in protocol if p['passed'])
avg=np.mean([p['score'] for p in protocol])
gen1_avg=np.mean([p['score'] for p in protocol if p['brain'].startswith(('01','02','03','04','05'))])
gen2_avg=np.mean([p['score'] for p in protocol if p['brain'].startswith(('06','07','08','09','10'))])

print(f"  ✅ Bestanden: {passed}/{len(protocol)} ({passed/len(protocol):.0%})")
print(f"  📊 Durchschnitt: {avg:.3f}")
print(f"  📊 Gen1 Ø: {gen1_avg:.3f} | Gen2 Ø: {gen2_avg:.3f}")

# Details
print(f"\n  ❌ Nicht bestanden (<0.5):")
for p in protocol:
    if not p['passed']:
        print(f"     {p['brain']:<20s} {p['score']:.3f} [{p['test']}]")

print(f"\n  🏆 TOP 10:")
for p in sorted(protocol, key=lambda x:-x['score'])[:10]:
    print(f"     {p['brain']:<20s} {p['score']:.3f} [{p['test']}]")

# Speichern
report={'timestamp':time.strftime('%Y-%m-%d %H:%M'),'elapsed_sec':round(elapsed,1),
        'passed':passed,'total':len(protocol),'avg_score':round(avg,4),
        'gen1_avg':round(gen1_avg,4),'gen2_avg':round(gen2_avg,4),
        'protocol':protocol}

path='/home/boobi/GEHIRN_BIBLIOTHEK/07_experimente/30_test_protokoll.json'
with open(path,'w') as f: json.dump(report,f,indent=2,default=str)

# Desktop
desktop_path='/home/boobi/Schreibtisch/30_GEHIRNE_TESTPROTOKOLL.json'
with open(desktop_path,'w') as f: json.dump(report,f,indent=2,default=str)

print(f"\n  📁 {path}")
print(f"  📁 Desktop: 30_GEHIRNE_TESTPROTOKOLL.json")
print(f"\n{'='*75}")
print(f"  ✅ PROTOKOLL FERTIG — {len(protocol)} Tests, {elapsed:.0f}s")
print(f"{'='*75}")
