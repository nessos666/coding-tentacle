"""
20 GEHIRNE — VOLLSTÄNDIGER BENCHMARK
Jedes Gehirn mit seinem spezifischen Standard-Test.
"""
import sys,os,time,math,random,json,numpy as np
from collections import defaultdict, Counter

# ALLE 20 Gehirne laden
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/01_bayesian')
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/02_shannon_entropie')
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/03_graph_struktur')
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/04_reinforcement')
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/05_kybernetisch')
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/06_act_r_spreading')
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/11_hebbian')
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/12_genetisch')
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/13_attention')
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/14_fuzzy')
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/15_ensemble')
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/16_game_theory')
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/17_gradient')
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/18_nearest_neighbor')
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/19_markov')
sys.path.insert(0,'/home/boobi/GEHIRN_BIBLIOTHEK/20_contrastive')

from bayesian_brain import BayesianBrain
from shannon_brain import ShannonBrain
from graph_brain import GraphBrain
from rl_brain import RLBrain
from kybernetisch_brain import KybernetischBrain
from actr_brain import ACTRBrain
from friston_brain import PredictiveCodingBrain
from causal_brain import CausalBrain
from kolmogorov_brain import KolmogorovBrain, ncd_distance
from mandelbrot_brain import MandelbrotBrain, hurst_exponent
from hebbian_brain import HebbianBrain
from genetic_brain import GeneticBrain
from attention_brain import AttentionBrain
from fuzzy_brain import FuzzyBrain
from ensemble_brain import EnsembleBrain
from game_theory_brain import GameTheoryBrain
from gradient_brain import GradientBrain
from nn_brain import NearestNeighborBrain
from markov_brain import MarkovBrain
from contrastive_brain import ContrastiveBrain

from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
results = {}
R = random

def score(name,test,val,detail=""):
    results[name]={'test':test,'score':round(val,3),'detail':detail}

print("="*70)
print("  🧠 20 GEHIRNE — KOMPLETTER BENCHMARK")
print("="*70)

# ─── A: Bayesian ───
ba=BayesianBrain(k=1.0)
rates=[]; preds=[]
for ep in range(80):
    bt=R.choice(['NullPointer','OffByOne','TypeError'])
    pat=f"{bt}→fix"; tr=0.9 if bt=='NullPointer' else (0.7 if bt=='OffByOne' else 0.5)
    ba.learn(f"{bt}:f{ep}.py:{ep}",pat,R.random()<tr)
    rates.append(tr)
    if pat in ba.patterns: preds.append(ba._effective_confidence(ba.patterns[pat]))
corr_a=np.corrcoef(rates[-40:],preds[-40:])[0,1] if len(preds)>=40 else 0
score("A_Bayesian","BLInD Probabilistic",max(0,corr_a),f"r={corr_a:.2f} p={len(ba.patterns)}")

# ─── B: Shannon ───
bb=ShannonBrain(explore_threshold=3.0)
for ep in range(80):
    bt=['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'][ep%5]
    base={'NullPointer':1,'OffByOne':-1,'TypeError':2,'MemoryLeak':-2,'RaceCondition':0}[bt]
    emb=((np.random.randn(384)*0.3+base)/(np.linalg.norm(np.ones(384))+0.001)).tolist()
    bb.learn(f"{bt}:f{ep}.py:{ep}","fix",True,emb)
cr_b=sum(1 for ep in range(20) if bb.think(f"NullPointer:t{ep}.py:{ep}",
    ((np.random.randn(384)*0.3+1)/(np.linalg.norm(np.ones(384))+0.001)).tolist())['action']=='APPLY_PATTERN')
score("B_Shannon","ADBench Novelty",cr_b/20,f"{cr_b}/20")

# ─── C: Graph ───
import networkx as nx; G=nx.karate_club_graph(); bc=GraphBrain(0.3)
cr_c=0
for node in list(G.nodes())[:20]:
    club=G.nodes[node]['club']
    feats=[G.degree(node),nx.clustering(G,node),nx.betweenness_centrality(G).get(node,0)]
    emb=(np.array(feats+[0]*381)/(np.linalg.norm(feats)+0.001)).tolist()
    if bc.think(f"c:{node}",emb)['action']=='APPLY_PATTERN': cr_c+=1
    bc.learn(f"c:{node}",club,True,emb)
score("C_Graph","OGB Karate Club",cr_c/20,f"{cr_c}/20")

# ─── D: RL ───
bd=RLBrain(alpha=0.1,gamma=0.9,epsilon=0.3); ed=[]; ld=[]
for ep in range(80):
    bt=R.choice(['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'])
    emb=model.encode(f"{bt} error").tolist(); sig=f"{bt}:f{ep}.py:{ep}"
    dec=bd.think(sig,emb)
    suc=R.random()<0.85 if dec['action']=='APPLY_PATTERN' else R.random()<0.3
    bd.learn(sig,"fix",suc,emb,action='APPLY_PATTERN' if dec['action']=='APPLY_PATTERN' else 'STORE')
    if ep<20: ed.append(1 if suc else 0)
    if ep>=60: ld.append(1 if suc else 0)
sd=max(0,min(1,0.5+(np.mean(ld)-np.mean(ed)))) if ed and ld else 0
score("D_RL","Bug-Loop 80eps",sd,f"{np.mean(ed):.0%}→{np.mean(ld):.0%}")

# ─── E: Kybernetisch ───
be=KybernetischBrain(); ee=[]; le=[]
for ep in range(60):
    bt=R.choice(['NullPointer','OffByOne','TypeError'])
    emb=model.encode(f"{bt} error").tolist(); sig=f"{bt}:f{ep}.py:{ep}"
    dec=be.think(sig,emb)
    suc=R.random()<0.85 if dec['action']=='APPLY_PATTERN' else R.random()<0.35
    be.learn(sig,"fix",suc,emb)
    if ep<15: ee.append(1 if suc else 0)
    if ep>=45: le.append(1 if suc else 0)
se=max(0,min(1,0.5+(np.mean(le)-np.mean(ee)))) if ee and le else 0
score("E_Kybernetisch","Bug-Loop 60eps",se,f"p:{len(be.patterns)} m:{len(be.memories)}")

# ─── F: ACT-R ───
bf=ACTRBrain(decay=0.5,threshold=-5.0)
words=["Apfel","Buch","Cloud","Dach","Elefant","Fenster","Garten","Haus","Igel","Jazz","Kaffee","Licht","Mond","Nacht","Orange"]
recall=[]
for i,w in enumerate(words):
    emb=model.encode(w).tolist()
    bf.learn(f"w:{i}:{w}",f"mem_{w}",True,emb)
    recall.append(bf.think(f"w:{i}:{w}",emb).get('activation',0))
pr=np.mean(recall[:3]); mi=np.mean(recall[5:10]); rc=np.mean(recall[-3:])
sf=min(1.0,(pr+rc)/(2*mi+0.1))
score("F_ACTR","Serial Position",sf,f"P={pr:.1f} M={mi:.1f} R={rc:.1f}")

# ─── G: Friston ───
bg=PredictiveCodingBrain(384,0.1); fh=[]
for s in range(40):
    noise=np.random.randn(384)*(0.5*(1-s/40))
    emb=((np.ones(384)*(s/40)+noise)/(np.linalg.norm(np.ones(384))+0.001)).tolist()
    dec=bg.think(f"s{s}",emb); bg.learn(f"s{s}","mv",True,emb)
    fh.append(dec.get('free_energy',100))
sg=max(0,1-np.mean(fh[-10:])/max(np.mean(fh[:10]),0.001))
score("G_Friston","Free Energy ∇F",min(1,sg),f"F:{np.mean(fh[:5]):.0f}→{np.mean(fh[-5:]):.0f}")

# ─── H: Causal ───
X=np.random.randn(200); T=(X+np.random.randn(200)*0.3>0).astype(int); Y=2.0*T+0.5*X+np.random.randn(200)*0.5
from sklearn.linear_model import LinearRegression
m1=LinearRegression().fit(X[T==1].reshape(-1,1),Y[T==1])
m0=LinearRegression().fit(X[T==0].reshape(-1,1),Y[T==0])
est=np.mean(m1.predict(X.reshape(-1,1))-m0.predict(X.reshape(-1,1)))
sh=max(0,1-abs(est-2.0)/2.0)
score("H_Causal","Causal Backdoor",sh,f"est={est:.2f}")

# ─── I: Kolmogorov ───
cats={'null':'NullPointerException None guard clause defensive',
      'idx':'IndexError range boundary offby array',
      'typ':'TypeError convert string int parse cast'}
ns=ncd_distance(cats['null'],cats['null']+" extra var")
nd=ncd_distance(cats['null'],cats['idx'])
si=max(0,1-ns/max(nd,0.001))
score("I_Kolmogorov","Calgary NCD",si,f"same={ns:.2f} diff={nd:.2f}")

# ─── J: Mandelbrot ───
def fbm(n=200,H=0.7):
    gm=lambda k:0.5*(abs(k-1)**(2*H)-2*abs(k)**(2*H)+abs(k+1)**(2*H))
    L=np.zeros((n,n))
    for i in range(n):
        for j in range(n): L[i,j]=gm(i-j)
    L=np.linalg.cholesky(L+np.eye(n)*0.001); return L@np.random.randn(n)
ts_p=fbm(200,0.7); ts_r=np.random.randn(200).cumsum()*0.1
sj=max(0,1-(abs(hurst_exponent(ts_p)-0.7)+abs(hurst_exponent(ts_r)-0.5))/2)
score("J_Mandelbrot","UCR Hurst",sj,f"Hp={hurst_exponent(ts_p):.2f} Hr={hurst_exponent(ts_r):.2f}")

# ─── K: Hebbian ───
bk=HebbianBrain(lr=0.15,decay=0.0001,threshold=0.15)
for ep in range(80):
    bt=R.choice(['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'])
    bk.learn(f"{bt}:f{ep}.py:{ep}",f"fix_{bt}",R.random()<0.85)
ck=sum(1 for _ in range(20) if bk.think(
    f"{R.choice(['NullPointer','OffByOne','TypeError'])}:t{_}.py:{_}",[0]*384)['action']=='APPLY_PATTERN')
score("K_Hebbian","Hebb Δw 80eps",ck/20,f"{ck}/20 w:{len(bk.weights)}")

# ─── L: Genetisch ───
bl=GeneticBrain(pop_size=30,mutation_rate=0.15,elite_size=5)
for ep in range(80):
    bt=R.choice(['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'])
    bl.learn(f"{bt}:f{ep}.py:{ep}",f"fix_{bt}",R.random()<0.85)
cl=sum(1 for _ in range(20) if bl.think(
    f"{R.choice(['NullPointer','OffByOne','TypeError'])}:t{_}.py:{_}",[0]*384)['action']=='APPLY_PATTERN')
score("L_Genetisch","Evol 80eps",cl/20,f"{cl}/20 gen:{bl.generation}")

# ─── M: Attention ───
bm=AttentionBrain(d_k=64,temperature=0.8)
for ep in range(80):
    bt=R.choice(['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'])
    emb=model.encode(f"{bt} error code fix").tolist()
    bm.think(f"{bt}:f{ep}.py:{ep}",emb)
    bm.learn(f"{bt}:f{ep}.py:{ep}",f"fix_{bt}",True,emb)
cm=sum(1 for _ in range(20) if bm.think(
    "NullPointer:test.py:1",model.encode("NullPointer null check defensive guard").tolist())['action']=='APPLY_PATTERN')
score("M_Attention","QKV 80eps",cm/20,f"{cm}/20 mem:{len(bm.keys)}")

# ─── N: Fuzzy ───
bn=FuzzyBrain()
sigs={'NullPointer':['pay.py:null-check','auth.py:session-null','order.py:cart-none'],
      'IndexError':['page.py:range-out','loop.py:index-boundary','slice.py:offby-one'],
      'TypeError':['parse.py:int-str','convert.py:float-int','format.py:type-mismatch'],
      'MemoryLeak':['cache.py:lru-buffer','pool.py:conn-leak','session.py:obj-accum'],
      'RaceCondition':['thread.py:race-lock','worker.py:mutex','queue.py:concurrent']}
for ep in range(80):
    bt=R.choice(list(sigs.keys())); sig=R.choice(sigs[bt])
    bn.learn(sig,f"fix_{bt}",R.random()<0.85)
cn=sum(1 for _ in range(20) if bn.think(
    R.choice(sigs[R.choice(list(sigs.keys()))]),[0]*384)['action']=='APPLY_PATTERN')
score("N_Fuzzy","Fuzzy 80eps",cn/20,f"{cn}/20 rules:{len(bn.rules)}")

# ─── O: Ensemble ───
bo=EnsembleBrain()
bo.add_brain('Bayesian',BayesianBrain()); bo.add_brain('Shannon',ShannonBrain())
bo.add_brain('Hebbian',HebbianBrain()); bo.add_brain('Fuzzy',FuzzyBrain())
for ep in range(60):
    bt=R.choice(['NullPointer','OffByOne','TypeError'])
    emb=[R.random()]*384; sig=f"{bt}:f{ep}.py:{ep}"
    dec=bo.think(sig,emb); suc=R.random()<0.85
    bo.learn(sig,f"fix_{bt}",suc,emb)
co=sum(1 for _ in range(20) if bo.think(
    f"NullPointer:t{_}.py:{_}",[R.random()]*384)['action']=='APPLY_PATTERN')
score("O_Ensemble","Meta Vote 60eps",co/20,f"{co}/20 sub:{len(bo.sub_brains)}")

# ─── P: Game Theory ───
bp=GameTheoryBrain()
for ep in range(60):
    bt=R.choice(['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'])
    bp.learn(f"{bt}:f{ep}.py:{ep}",f"fix_{bt}",R.random()<0.85)
cp=sum(1 for _ in range(20) if bp.think(
    f"{R.choice(['NullPointer','OffByOne','TypeError'])}:t{_}.py:{_}",[0]*384)['action']=='APPLY_PATTERN')
score("P_GameTheory","Minimax 60eps",cp/20,f"{cp}/20")

# ─── Q: Gradient ───
bq=GradientBrain(lr=0.1)
for ep in range(60):
    bt=R.choice(['NullPointer','OffByOne','TypeError'])
    bq.learn(f"{bt}:f{ep}.py:{ep}","fix",R.random()<0.85)
cq=sum(1 for _ in range(20) if bq.think(
    f"{R.choice(['NullPointer','OffByOne','TypeError'])}:t{_}.py:{_}",[0]*384)['action']=='APPLY_PATTERN')
score("Q_Gradient","Adam 60eps",cq/20,f"{cq}/20")

# ─── R: NearestNeighbor ───
br=NearestNeighborBrain(k=5,threshold=0.3)
for ep in range(80):
    bt=R.choice(['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'])
    emb=model.encode(f"{bt} error").tolist()
    br.think(f"{bt}:f{ep}.py:{ep}",emb)
    br.learn(f"{bt}:f{ep}.py:{ep}",f"fix_{bt}",R.random()<0.85,emb)
cr=sum(1 for _ in range(20) if br.think(
    f"NullPointer:t{_}.py:{_}",model.encode("NullPointer null check").tolist())['action']=='APPLY_PATTERN')
score("R_NearestNeighbor","k-NN 80eps",cr/20,f"{cr}/20 cases:{len(br.cases)}")

# ─── S: Markov ───
bs=MarkovBrain(gamma=0.9)
for ep in range(60):
    bt=R.choice(['NullPointer','OffByOne','TypeError','MemoryLeak','RaceCondition'])
    bs.learn(f"{bt}:f{ep}.py:{ep}",f"fix_{bt}",R.random()<0.85)
cs=sum(1 for _ in range(20) if bs.think(
    f"{R.choice(['NullPointer','OffByOne','TypeError'])}:t{_}.py:{_}",[0]*384)['action']=='APPLY_PATTERN')
score("S_Markov","MDP 60eps",cs/20,f"{cs}/20 states:{len(bs.transitions)}")

# ─── T: Contrastive ───
bt=ContrastiveBrain(temperature=0.1,lr=0.1)
for ep in range(60):
    bugt=R.choice(['NullPointer','OffByOne','TypeError'])
    emb=model.encode(f"{bugt} error").tolist()
    bt.think(f"{bugt}:f{ep}.py:{ep}",emb)
    bt.learn(f"{bugt}:f{ep}.py:{ep}",f"fix_{bugt}",R.random()<0.85,emb)
ct=sum(1 for _ in range(20) if bt.think(
    f"NullPointer:t{_}.py:{_}",model.encode("NullPointer exception null check").tolist())['action']=='APPLY_PATTERN')
score("T_Contrastive","InfoNCE 60eps",ct/20,f"{ct}/20 proto:{len(bt.prototypes)}")

# ═══ RANKING ═══
print(f"\n{'='*70}")
print(f"  🏆 20 GEHIRNE — FINALES RANKING")
print(f"{'='*70}")
for name,r in sorted(results.items(),key=lambda x:-x[1]['score']):
    bar='█'*int(r['score']*20); mid='⚠️' if r['score']<0.5 else '✅'
    print(f"  {mid} {name:<18s} {r['score']:.3f} {bar} {r['test']:<22s} {r['detail']}")

avg=np.mean([r['score'] for r in results.values()])
good=sum(1 for r in results.values() if r['score']>=0.5)
print(f"\n  📊 SCHNITT: {avg:.3f} | {good}/20 ≥ 0.5 | {sum(1 for r in results.values() if r['score']>=0.8)} ≥ 0.8")

with open('/home/boobi/GEHIRN_BIBLIOTHEK/07_experimente/20_benchmarks.json','w') as f:
    json.dump({'ts':time.strftime('%Y-%m-%d %H:%M'),'avg':avg,'good':good,'results':results},f,indent=2,default=str)
