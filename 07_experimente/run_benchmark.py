"""
GEHIRN BENCHMARK — 10 Szenarien, 5 Gehirne, echte Embeddings
"""

import sys, os, time, json
import numpy as np

# Pfad zu den Gehirnen
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

# ─── ECHTE EMBEDDINGS ───
print("Lade Embedding-Modell...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print(f"  all-MiniLM-L6-v2: {model.get_sentence_embedding_dimension()}dim")

# ─── 10 TEST-SZENARIEN ───
SCENARIOS = [
    # (signature, bug_text, pattern, success)
    # Szenario 1-3: NullPointer (guard clause gewinnt)
    ("NullPointer:payment.py:123", 
     "NullPointerException when payment object is None in process() method",
     "NullPointer→guard_clause", True),
    ("NullPointer:auth.py:89",
     "AttributeError NoneType in authenticate() when user session expired",
     "NullPointer→guard_clause", True),
    ("NullPointer:order.py:45",
     "NoneType error in calculate_total() when order is empty",
     "NullPointer→guard_clause", True),
    
    # Szenario 4: NullPointer mit falschem Fix
    ("NullPointer:config.py:200",
     "NoneType in load_config() when config file missing",
     "NullPointer→try_except", False),
    
    # Szenario 5-6: OffByOne
    ("OffByOne:paginator.py:67",
     "IndexError list index out of range in paginate() page=0",
     "OffByOne→boundary_check", True),
    ("OffByOne:counter.py:90",
     "Loop runs one time too many in count_items() when list is empty",
     "OffByOne→boundary_check", True),
    
    # Szenario 7: TypeError
    ("TypeError:parser.py:34",
     "TypeError cannot concatenate str and int in parse_line()",
     "TypeError→type_conversion", True),
    
    # Szenario 8: MemoryLeak
    ("MemoryLeak:cache.py:12",
     "Memory growing unbounded in LRUCache.get() when cache misses",
     "MemoryLeak→weak_reference", True),
    
    # Szenario 9: RaceCondition
    ("RaceCondition:worker.py:56",
     "Data corruption when multiple threads write to shared counter",
     "RaceCondition→lock", True),
    
    # Szenario 10: ImportError
    ("ImportError:module.py:3",
     "ModuleNotFoundError for optional dependency in production",
     "ImportError→conditional_import", True),
]

# ─── ALLE GEHIRNE TESTEN ───
brains = {
    "A_Bayesian": BayesianBrain(k=1.0),
    "B_Shannon": ShannonBrain(explore_threshold=3.0),
    "C_Graph": GraphBrain(similarity_threshold=0.3),
    "D_RL": RLBrain(alpha=0.1, epsilon=0.2),
    "E_Kybernetisch": KybernetischBrain(),
}

results = {}

for brain_name, brain in brains.items():
    print(f"\n{'='*60}")
    print(f"  TESTE GEHIRN {brain_name}")
    print(f"{'='*60}")
    
    brain_results = {
        'correct_applies': 0,
        'correct_explores': 0,
        'wrong_actions': 0,
        'total': len(SCENARIOS),
        'details': []
    }
    
    for i, (sig, bug_text, pattern, success) in enumerate(SCENARIOS):
        emb = model.encode(bug_text).tolist()
        
        # Denken
        decision = brain.think(sig, emb)
        
        # Bewerten
        action = decision.get('action', 'UNKNOWN')
        suggested = decision.get('pattern', 'NONE')
        reasoning = decision.get('reasoning', '')
        
        # Was waere korrekt?
        correct_action = 'APPLY_PATTERN' if pattern else 'EXPLORE'
        
        is_correct = False
        if correct_action == 'APPLY_PATTERN':
            if action == 'APPLY_PATTERN' and pattern in str(suggested):
                is_correct = True
                brain_results['correct_applies'] += 1
                status = '✅'
            elif action == 'EXPLORE':
                status = '⚠️ (zu vorsichtig)'
                brain_results['wrong_actions'] += 1
            else:
                status = '❌'
                brain_results['wrong_actions'] += 1
        else:
            if action == 'EXPLORE':
                is_correct = True
                brain_results['correct_explores'] += 1
                status = '✅'
            else:
                status = '❌ (falsches Pattern)'
                brain_results['wrong_actions'] += 1
        
        round_num = i + 1
        conf = decision.get('confidence', 0)
        print(f"  Bug {round_num:2d}: {status} | {action:15s} | {reasoning[:60]}")
        
        brain_results['details'].append({
            'bug': sig,
            'action': action,
            'is_correct': is_correct,
            'confidence': conf if isinstance(conf, float) else 0
        })
        
        # Lernen — manche Gehirne brauchen embedding, andere nicht
        try:
            brain.learn(sig, pattern, success, emb)
        except TypeError:
            brain.learn(sig, pattern, success)
    
    results[brain_name] = brain_results

# ─── ZUSAMMENFASSUNG ───
print(f"\n\n{'='*70}")
print(f"  🏆 BENCHMARK-ERGEBNIS: 10 Bug-Szenarien")
print(f"{'='*70}")
print(f"  {'Gehirn':<20s} {'Richtig':>8s} {'%':>6s} {'Falsch':>8s} {'Status':>20s}")
print(f"  {'-'*60}")

for brain_name, r in results.items():
    correct = r['correct_applies'] + r['correct_explores']
    pct = correct / r['total'] * 100
    wrong = r['wrong_actions']
    
    if pct >= 80:
        status = '🔥 SEHR GUT'
    elif pct >= 60:
        status = '✅ GUT'
    elif pct >= 40:
        status = '⚠️ MITTEL'
    else:
        status = '❌ SCHLECHT'
    
    print(f"  {brain_name:<20s} {correct:>3d}/{r['total']} {pct:>5.0f}% {wrong:>8d} {status:>20s}")

# Zeige Stats
print(f"\n{'='*70}")
print(f"  📊 DETAILLIERTE STATISTIKEN")
print(f"{'='*70}")
for brain_name, brain in brains.items():
    stats = brain.stats()
    print(f"\n  🧠 {brain_name}:")
    for k, v in stats.items():
        if k != 'brain_type':
            print(f"     {k}: {v}")

# Speichere Ergebnisse
output = {
    'timestamp': time.strftime('%Y-%m-%d %H:%M'),
    'embedding_model': 'all-MiniLM-L6-v2',
    'num_scenarios': len(SCENARIOS),
    'results': {k: {
        'correct': r['correct_applies'] + r['correct_explores'],
        'pct': round((r['correct_applies'] + r['correct_explores']) / r['total'] * 100, 1),
        'wrong': r['wrong_actions'],
        'details': r['details']
    } for k, r in results.items()}
}

out_path = '/home/boobi/GEHIRN_BIBLIOTHEK/07_experimente/benchmark_10_szenarien.json'
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\n📁 Ergebnisse gespeichert: {out_path}")
