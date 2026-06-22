"""66 BRAINS RE-AUDIT for Coding Tentacle RC6"""
import json

BRAINS = [
    ("VSM","Viable System Model","Rekursive Systemstruktur",8),
    ("Hebbian","Hebbian Learning","Fire together wire together",3),
    ("Homeostatic","Homeostatic Regulation","Inneres Gleichgewicht",5),
    ("SelfOrganize","Self-Organization","Ordnung spontan",7),
    ("Feedback1","First-Order Feedback","Einfache Rückkopplung",2),
    ("Feedback2","Deutero-Learning","Lernen über Lernen",5),
    ("SOAR","SOAR Architecture","Chunking+Problem-Space",9),
    ("ACT-R","ACT-R","Declarative+Procedural Memory",9),
    ("NARS","Non-Axiomatic Reasoning","Unified uncertainty",8),
    ("CogPrime","OpenCog","Integrative AGI",10),
    ("Predictive","Predictive Coding","Brain as prediction machine",7),
    ("Hopfield","Hopfield Networks","Associative memory",6),
    ("HTM","Hierarchical Temporal Memory","Sparse distributed reps",9),
    ("Attention","Attention Mechanisms","Dynamic focus",5),
    ("BrainMesh","BrainMesh","Specialized brains+msg passing",8),
    ("Neuromod","Neuromodulation","Dynamic learning rate",5),
    ("FreeEnergy","Free Energy Principle","Minimize surprise",8),
    ("ActiveInf","Active Inference","Action as hypothesis testing",9),
    ("CausalDisc","Causal Discovery","Cause-effect inference",7),
    ("GraphBrain","Graph Neural Networks","Relational reasoning",7),
    ("BayesProgram","Bayesian Program Learning","Few-shot composition",8),
    ("MetaLearn","Meta-Learning MAML","Learning to learn",7),
    ("Curiosity","Curiosity-Driven","Intrinsic motivation",6),
    ("Contrastive","Contrastive Learning","Learn representations",4),
    ("JEPA","JEPA","Predict in latent space",7),
    ("Experience","Experience Replay","Store+replay past experiences",6),
    ("ModelBased","Model-Based RL","World model+planning",8),
    ("Hindsight","Hindsight Experience","Learn from failure",5),
    ("Imitation","Imitation Learning","Learn from demonstrations",5),
    ("CurrLearn","Curriculum Learning","Easy→hard",4),
    ("MultiTask","Multi-Task Learning","Share representations",5),
    ("Transfer","Transfer Learning","Domain transfer",4),
    ("Continual","Continual Learning","No catastrophic forgetting",8),
    ("Lifelong","Lifelong Learning","Accumulate forever",8),
    ("CaseBased","Case-Based Reasoning","Reuse old solutions",6),
    ("Analogical","Analogical Reasoning","Structure mapping",8),
    ("Abductive","Abductive Reasoning","Best explanation",5),
    ("Default","Default Logic","Assumptions+exceptions",6),
    ("NonMonotonic","Non-Monotonic Reasoning","Retractable conclusions",7),
    ("Defeasible","Defeasible Reasoning","Defeatable rules",6),
    ("Argumentation","Argumentation Theory","Structured conflicts",7),
    ("FuzzyLogic","Fuzzy Logic","Degrees of truth",4),
    ("ProbLog","Probabilistic Logic","Logic+Probabilities",7),
    ("InductiveLP","Inductive Logic Prog","Learn logic from examples",8),
    ("GameTheory","Game Theory Agents","Strategic interaction",6),
    ("Swarm","Swarm Intelligence","Emergent collective",7),
    ("Blackboard","Blackboard Architecture","Shared knowledge space",5),
    ("Emergence","Emergent Coordination","Simple rules→complex",8),
    ("Stigmergy","Stigmergy","Environment coordination",5),
    ("SemanticMem","Semantic Memory","Structured knowledge",7),
    ("EpisodicMem","Episodic Memory","Personal experiences",6),
    ("Procedural","Procedural Memory","Skill memory",6),
    ("Forgetting","Adaptive Forgetting","Strategic forgetting",5),
    ("Consolidation","Memory Consolidation","Sleep/Replay",7),
    ("Constructive","Constructive Memory","Reconstruction",6),
    ("Shielding","Safe RL Shielding","Hard safety constraints",6),
    ("Uncertainty","Uncertainty Quant","Know when you don't know",5),
    ("Anomaly","Anomaly Detection","OOD detection",5),
    ("Sandboxing","Sandboxing/Isolation","Restricted execution",4),
    ("Monitor","Runtime Monitoring","Verify during execution",6),
    ("Guardrails","Guardrails/Nanny","LLM boundary enforcement",5),
]

WEAK = ["Bug-Klassifikation","Python-Fixes","Multi-Language","Projektverständnis","Autonome Reparatur","Lernfähigkeit"]

def score(name, idea):
    s=[0]*6; il=idea.lower()
    # Bug-Klassifikation
    if any(w in il for w in ['pattern','classify','detect','recognize','match','case','reason']): s[0]=min(3,s[0]+2)
    if name in ['CaseBased','Analogical','Abductive','CausalDisc','Hopfield','SOAR']: s[0]=min(3,s[0]+1)
    # Python-Fixes
    if any(w in il for w in ['repair','patch','generat','template','fix','code','procedur']): s[1]=min(3,s[1]+2)
    if name in ['CaseBased','Procedural','Analogical','InductiveLP']: s[1]=min(3,s[1]+1)
    # Multi-Language
    if any(w in il for w in ['transfer','domain','generaliz','language','multi','share']): s[2]=min(3,s[2]+2)
    # Projektverständnis
    if any(w in il for w in ['graph','structur','relat','depend','map','project','spatial','space']): s[3]=min(3,s[3]+2)
    if name in ['GraphBrain','BrainMesh','Blackboard','SemanticMem','VSM']: s[3]=min(3,s[3]+1)
    # Autonome Reparatur
    if any(w in il for w in ['execut','action','repair','apply','test','verif','shield','sandbox']): s[4]=min(3,s[4]+2)
    if name in ['Procedural','Experience','SOAR','Shielding','Sandboxing','Monitor','Guardrails']: s[4]=min(3,s[4]+1)
    # Lernfähigkeit
    if any(w in il for w in ['learn','memor','experien','replay','consolid','adapt','continual','lifelong']): s[5]=min(3,s[5]+2)
    if name in ['Experience','Consolidation','Continual','Lifelong','Hebbian','EpisodicMem','SOAR']: s[5]=min(3,s[5]+1)
    return s

scored = [(n,i,c,sum(score(n,i+d)),round(sum(score(n,i+d))/max(1,c),2),score(n,i+d)) for n,i,d,c in BRAINS]
scored.sort(key=lambda x:-x[4])

with open('/home/boobi/Schreibtisch/66_BRAINS_REAUDIT.json','w') as f:
    json.dump({
        'top15':[{'name':n,'idea':i,'roi':r,'total':t} for n,i,c,t,r,s in scored[:15]],
        'top5_practical':[{'name':n,'idea':i,'roi':r} for n,i,c,t,r,s in scored if c<=6 and t>=8][:5],
        'top3_learning':sorted([(n,i,r,s[5]) for n,i,c,t,r,s in scored if s[5]>=3],key=lambda x:-x[2])[:3],
        'total':len(BRAINS)
    },f,indent=2)

print("TOP 15 by ROI:")
for i,(n,idea,c,t,r,s) in enumerate(scored[:15],1):
    print(f"  {i:2d}. {n:<16s} ROI={r:4.1f}  T={t}  C={c}")
print(f"\nSaved: 66_BRAINS_REAUDIT.json")
