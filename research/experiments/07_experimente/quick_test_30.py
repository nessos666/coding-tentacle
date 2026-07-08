"""
SCHNELLTEST: 30 Bugs mit echten Embeddings. 5 Gehirne vergleichen.
"""
import sys, time, json
sys.path.insert(0, '/home/boobi/GEHIRN_BIBLIOTHEK/01_bayesian')
sys.path.insert(0, '/home/boobi/GEHIRN_BIBLIOTHEK/02_shannon_entropie')
sys.path.insert(0, '/home/boobi/GEHIRN_BIBLIOTHEK/03_graph_struktur')
sys.path.insert(0, '/home/boobi/GEHIRN_BIBLIOTHEK/04_reinforcement')
sys.path.insert(0, '/home/boobi/GEHIRN_BIBLIOTHEK/05_kybernetisch')
from bayesian_brain import BayesianBrain
from shannon_brain import ShannonBrain
from graph_brain import GraphBrain
from rl_brain import RLBrain
from kybernetisch_brain import KybernetischBrain
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

# 30 Bugs: 5 Typen × 6 Wiederholungen
BUGS = [
    # NullPointer × 6 (guard clause gewinnt)
    ("NullPointer:pay.py:1","NullPointerException when payment is None","guard_clause",True),
    ("NullPointer:auth.py:2","NoneType error in authenticate session expired","guard_clause",True),
    ("NullPointer:user.py:3","AttributeError NoneType in get_profile","guard_clause",True),
    ("NullPointer:order.py:4","None in calculate_total empty cart","guard_clause",True),
    ("NullPointer:report.py:5","NoneType in generate_report no data","try_except",False),
    ("NullPointer:config.py:6","Null in load_config missing file","guard_clause",True),
    # OffByOne × 6
    ("OffByOne:page.py:1","IndexError list index out of range paginate","boundary_check",True),
    ("OffByOne:list.py:2","Off by one in array loop last element","boundary_check",True),
    ("OffByOne:counter.py:3","Counter shows 11 instead of 10 iterations","boundary_check",True),
    ("OffByOne:slice.py:4","String slice off by one character","boundary_check",True),
    ("OffByOne:range.py:5","Range goes one too far in loop","boundary_check",True),
    ("OffByOne:index.py:6","Index starting at 1 instead of 0","boundary_check",True),
    # TypeError × 6
    ("TypeError:parse.py:1","Cannot concatenate str and int in parser","type_convert",True),
    ("TypeError:convert.py:2","TypeError float expected got string","type_convert",True),
    ("TypeError:serialize.py:3","Cannot serialize datetime to JSON","type_convert",True),
    ("TypeError:calc.py:4","TypeError in calculation None + int","type_convert",True),
    ("TypeError:format.py:5","String formatting expects int got float","type_convert",True),
    ("TypeError:compare.py:6","Cannot compare str with int in sort","type_convert",True),
    # MemoryLeak × 6
    ("MemoryLeak:cache.py:1","Memory growing in LRU cache on miss","weakref",True),
    ("MemoryLeak:pool.py:2","Connection pool not releasing connections","weakref",True),
    ("MemoryLeak:buffer.py:3","ByteBuffer not freed after use","weakref",True),
    ("MemoryLeak:session.py:4","Session objects accumulating in memory","weakref",True),
    ("MemoryLeak:image.py:5","Image cache not evicting old entries","weakref",True),
    ("MemoryLeak:log.py:6","Log buffer growing without bound","weakref",True),
    # RaceCondition × 6
    ("RaceCondition:thread.py:1","Data corruption shared counter multithread","lock",True),
    ("RaceCondition:worker.py:2","Race in worker pool job assignment","lock",True),
    ("RaceCondition:queue.py:3","Concurrent queue push corrupts data","lock",True),
    ("RaceCondition:file.py:4","Multiple processes writing to same file","lock",True),
    ("RaceCondition:db.py:5","Concurrent database writes conflict","lock",True),
    ("RaceCondition:cache.py:6","Cache read-write race stale data","lock",True),
]

brains = {
    "A_Bayesian": BayesianBrain(k=1.0),
    "B_Shannon": ShannonBrain(explore_threshold=2.0),
    "C_Graph": GraphBrain(similarity_threshold=0.25),
    "D_RL": RLBrain(alpha=0.1, epsilon=0.15),
    "E_Kybernetisch": KybernetischBrain(),
}

results = {}
for name, brain in brains.items():
    correct = 0
    for i, (sig, text, pattern, success) in enumerate(BUGS):
        emb = model.encode(text).tolist()
        dec = brain.think(sig, emb)
        action = dec.get('action','')
        # Korrekt wenn APPLY_PATTERN mit richtigem Pattern ODER EXPLORE bei neuem Typ
        is_correct = (
            (action == 'APPLY_PATTERN' and pattern in str(dec.get('pattern',''))) or
            (action == 'EXPLORE' and i < 2)  # erste 2 Bugs eines Typs = EXPLORE ok
        )
        if is_correct:
            correct += 1
        try:
            brain.learn(sig, pattern, success, emb)
        except:
            brain.learn(sig, pattern, success)
    results[name] = {'correct': correct, 'pct': round(correct/len(BUGS)*100,1)}

print(f"\n{'='*60}")
print(f"  🏆 BENCHMARK: 30 Bugs, 5 Bug-Typen × 6 Wiederholungen")
print(f"{'='*60}")
for name, r in sorted(results.items(), key=lambda x: -x[1]['pct']):
    bar = '█' * (r['correct']//2)
    print(f"  {name:<20s} {r['correct']:>2d}/30 {r['pct']:>5.0f}%  {bar}")
