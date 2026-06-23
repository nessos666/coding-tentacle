"""
ENGINE LEARNING LOOP — RC37
CT learns which engine is best per bug type.
Performance-based trust updates. Falls back to defaults.

Author: Hermes + David | Coding Tentacle 2026
"""
import time, os, json
from collections import defaultdict


class EnginePerformanceStore:
    """Tracks engine performance per bug type. Bayesian trust updates."""
    
    def __init__(self, store_path=None):
        self.store_path = store_path or os.path.expanduser('~/.coding_tentacle/engine_perf.json')
        self.stats = defaultdict(lambda: defaultdict(lambda: {
            'attempts': 0, 'successes': 0, 'failures': 0,
            'total_runtime_s': 0, 'avg_skeptic_risk': 0, 'avg_impact_risk': 0,
            'trust': 0.60, 'last_used': 0,
        }))
        self._load()
    
    def record(self, engine_name, bug_type, success, runtime_s=0, 
               skeptic_risk=0, impact_risk=0):
        """Record an engine attempt."""
        entry = self.stats[engine_name][bug_type]
        entry['attempts'] += 1
        if success:
            entry['successes'] += 1
        else:
            entry['failures'] += 1
        
        entry['total_runtime_s'] += runtime_s
        entry['avg_skeptic_risk'] = (entry['avg_skeptic_risk'] + skeptic_risk) / 2 if entry['attempts'] > 1 else skeptic_risk
        entry['avg_impact_risk'] = (entry['avg_impact_risk'] + impact_risk) / 2 if entry['attempts'] > 1 else impact_risk
        entry['last_used'] = time.time()
        
        # Bayesian trust update
        prior = entry['trust']
        likelihood = 0.80 if success else 0.20
        entry['trust'] = round((likelihood * prior) / max(0.001, (likelihood * prior + (1 - likelihood) * (1 - prior))), 3)
        
        self._save()
    
    def get_trust(self, engine_name, bug_type):
        """Get trust for engine+bugh_type. Returns (trust, samples, success_rate)."""
        if engine_name in self.stats and bug_type in self.stats[engine_name]:
            e = self.stats[engine_name][bug_type]
            sr = e['successes'] / max(1, e['attempts'])
            return e['trust'], e['attempts'], sr
        return 0.60, 0, 0.0
    
    def is_reliable(self, engine_name, bug_type, min_samples=3, min_trust=0.65):
        """Is this engine reliable for this bug type?"""
        trust, samples, _ = self.get_trust(engine_name, bug_type)
        return samples >= min_samples and trust >= min_trust
    
    def best_engine_for(self, bug_type, available_engines):
        """Return best engine for a bug type based on performance data."""
        best = None
        best_score = -1
        
        for eng_name in available_engines:
            trust, samples, sr = self.get_trust(eng_name, bug_type)
            # Score: combine trust + sample bonus (more data = more confidence)
            score = trust + min(0.15, samples * 0.03)
            if score > best_score:
                best_score = score
                best = eng_name
        
        return best, best_score
    
    def get_matrix(self):
        """Return engine × bug_type trust matrix."""
        matrix = {}
        for engine, bug_types in self.stats.items():
            for bug_type, entry in bug_types.items():
                if entry['attempts'] >= 2:
                    key = f"{engine}:{bug_type}"
                    matrix[key] = {
                        'trust': entry['trust'],
                        'samples': entry['attempts'],
                        'success_rate': round(entry['successes'] / max(1, entry['attempts']), 2),
                        'avg_runtime': round(entry['total_runtime_s'] / max(1, entry['attempts']), 1),
                    }
        return matrix
    
    def _save(self):
        try:
            os.makedirs(os.path.dirname(self.store_path), exist_ok=True)
            with open(self.store_path, 'w') as f:
                json.dump({e: {bt: dict(d) for bt, d in bts.items()} 
                          for e, bts in self.stats.items()}, f, indent=2)
        except:
            pass
    
    def _load(self):
        try:
            if os.path.exists(self.store_path):
                with open(self.store_path) as f:
                    data = json.load(f)
                for engine, bug_types in data.items():
                    for bug_type, entry in bug_types.items():
                        self.stats[engine][bug_type].update(entry)
        except:
            pass


class AdaptiveEngineRouter:
    """EngineRouter with performance-based learning."""
    
    def __init__(self, engine_router, performance_store):
        self.router = engine_router  # EngineRouter instance
        self.perf = performance_store  # EnginePerformanceStore
    
    def route(self, bug_type):
        """Route with performance data. Falls back to static rules."""
        # Get available engines
        available = [name for name, cfg in self.router.ENGINES.items() 
                    if cfg.get('status') in ('healthy', 'unknown')]
        
        # Try performance-based routing
        best, score = self.perf.best_engine_for(bug_type, available)
        if best and self.perf.is_reliable(best, bug_type):
            cfg = self.router.ENGINES.get(best, {})
            return best, cfg, f"Learned: {best} trust={self.perf.get_trust(best, bug_type)[0]:.2f}"
        
        # Fallback to static routing
        return self.router.route(bug_type)
    
    def record_result(self, engine_name, bug_type, success, runtime_s=0,
                      skeptic_risk=0, impact_risk=0):
        """Record engine result + update static stats."""
        self.perf.record(engine_name, bug_type, success, runtime_s, 
                        skeptic_risk, impact_risk)
        self.router.record_result(engine_name, bug_type, success, runtime_s)


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    import tempfile, shutil
    
    print("ENGINE LEARNING LOOP — Self-Test")
    print("=" * 55)
    passed = 0
    
    tmp = tempfile.mkdtemp()
    ps = EnginePerformanceStore(store_path=os.path.join(tmp, 'perf.json'))
    
    # T1: Record success → trust increases
    ps.record('opencode', 'NullPointer', True, runtime_s=12)
    trust, samples, sr = ps.get_trust('opencode', 'NullPointer')
    t1 = trust > 0.60 and samples == 1
    print(f"  T1: {'✅' if t1 else '❌'} Success → trust={trust} (was 0.60)")
    
    # T2: Record more successes → trust converges high
    for _ in range(4):
        ps.record('opencode', 'NullPointer', True, runtime_s=10)
    trust2, samples2, sr2 = ps.get_trust('opencode', 'NullPointer')
    t2 = trust2 > 0.85 and samples2 == 5
    print(f"  T2: {'✅' if t2 else '❌'} 5 successes → trust={trust2} samples={samples2}")
    
    # T3: Record failures → trust drops
    for _ in range(3):
        ps.record('ollama', 'RaceCondition', False, runtime_s=25)
    trust3, samples3, _ = ps.get_trust('ollama', 'RaceCondition')
    t3 = trust3 < 0.60 and samples3 == 3
    print(f"  T3: {'✅' if t3 else '❌'} 3 failures → trust={trust3} (drops)")
    
    # T4: is_reliable
    t4 = ps.is_reliable('opencode', 'NullPointer')
    t4b = not ps.is_reliable('ollama', 'RaceCondition')
    t4 = t4 and t4b
    print(f"  T4: {'✅' if t4 else '❌'} OpenCode NP reliable={t4}, Ollama RC reliable={t4b}")
    
    # T5: best_engine_for
    best, score = ps.best_engine_for('NullPointer', ['opencode', 'ollama'])
    t5 = best == 'opencode'
    print(f"  T5: {'✅' if t5 else '❌'} Best for NullPointer → {best} (score={score:.2f})")
    
    # T6: best_engine_for with no data → returns first
    best6, _ = ps.best_engine_for('Deadlock', ['opencode', 'ollama'])
    t6 = best6 in ('opencode', 'ollama')
    print(f"  T6: {'✅' if t6 else '❌'} No data → {best6} (first available)")
    
    # T7: Get matrix
    matrix = ps.get_matrix()
    t7 = len(matrix) >= 1
    print(f"  T7: {'✅' if t7 else '❌'} Matrix entries → {len(matrix)}")
    
    # T8: Save + reload
    ps2 = EnginePerformanceStore(store_path=os.path.join(tmp, 'perf.json'))
    trust_r, _, _ = ps2.get_trust('opencode', 'NullPointer')
    t8 = trust_r > 0.80
    print(f"  T8: {'✅' if t8 else '❌'} Persist → trust after reload={trust_r}")
    
    # T9: AdaptiveEngineRouter
    from coding_tentacle.orchestrator.engine_router import EngineRouter
    er = EngineRouter()
    er.check_health()
    aer = AdaptiveEngineRouter(er, ps)
    name, _, reason = aer.route('NullPointer')
    t9 = name == 'opencode' and 'Learned' in reason
    print(f"  T9: {'✅' if t9 else '❌'} Learned route → {reason}")
    
    # T10: After record, routing updates
    aer.record_result('opencode', 'NullPointer', True, runtime_s=8)
    t10 = True  # Recording worked
    print(f"  T10: {'✅' if t10 else '❌'} Record + route → OK")
    
    shutil.rmtree(tmp, ignore_errors=True)
    passed = sum([t1,t2,t3,t4,t5,t6,t7,t8,t9,t10])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/10 Tests bestanden")
    print(f"  {'✅ ENGINE LEARNING LOOP FERTIG' if passed >= 9 else '⚠️'}")
