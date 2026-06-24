"""
FIX OUTCOME LEARNING — RC39
CT learns WHY fixes succeed/fail, not just THAT they did.
Extracts success/failure patterns, updates engine trust.

Author: Hermes + David | Coding Tentacle 2026
"""
import time, os, json
from collections import Counter, defaultdict


class FixOutcomeAnalyzer:
    """Analyzes fix outcomes to extract success/failure patterns."""
    
    def __init__(self, store_path=None):
        self.store_path = store_path or os.path.expanduser('~/.coding_tentacle/outcome_patterns.json')
        self.outcomes = []  # List of outcome records
        self.patterns = {
            'success': defaultdict(list),  # bug_type → [{engine, diff_size, ...}]
            'failure': defaultdict(list),
        }
        self._load()
    
    def analyze(self, bug_type, engine_name, diff, tests_passed, 
                skeptic_risk, impact_risk, runtime_s, failure_reason=''):
        """Record and analyze one fix outcome."""
        outcome = {
            'bug_type': bug_type,
            'engine': engine_name,
            'diff_size': len(diff) if diff else 0,
            'tests_passed': tests_passed,
            'skeptic_risk': round(skeptic_risk, 2),
            'impact_risk': round(impact_risk, 2),
            'runtime_s': runtime_s,
            'timestamp': time.time(),
            'failure_reason': failure_reason,
        }
        self.outcomes.append(outcome)
        
        category = 'success' if tests_passed else 'failure'
        self.patterns[category][bug_type].append(outcome)
        
        # Keep only last 200 outcomes
        if len(self.outcomes) > 200:
            self.outcomes = self.outcomes[-200:]
        
        self._save()
        
        # Extract learnings
        return self.extract_learnings(bug_type, engine_name)
    
    def extract_learnings(self, bug_type=None, engine_name=None):
        """Extract actionable learnings from patterns."""
        learnings = {'bug_type': bug_type or 'all', 'engine': engine_name or 'all'}
        
        # Filter outcomes
        relevant = self.outcomes
        if bug_type:
            relevant = [o for o in relevant if o['bug_type'] == bug_type]
        if engine_name:
            relevant = [o for o in relevant if o['engine'] == engine_name]
        
        if len(relevant) < 2:
            learnings['conclusion'] = 'Not enough data (<2 outcomes)'
            return learnings
        
        successes = [o for o in relevant if o['tests_passed']]
        failures = [o for o in relevant if not o['tests_passed']]
        
        # Success rate
        learnings['total'] = len(relevant)
        learnings['success_rate'] = round(len(successes) / max(1, len(relevant)), 2)
        
        # Preferred diff size range (median of successes)
        if successes:
            diffs = sorted(o['diff_size'] for o in successes)
            median_diff = diffs[len(diffs)//2] if diffs else 0
            learnings['preferred_diff_size'] = median_diff
            learnings['diff_size_range'] = f"{diffs[0]}-{diffs[-1]}B" if diffs else 'N/A'
        
        # Risk profiles
        if successes:
            learnings['avg_skeptic_risk_success'] = round(sum(o['skeptic_risk'] for o in successes) / len(successes), 2)
            learnings['avg_impact_risk_success'] = round(sum(o['impact_risk'] for o in successes) / len(successes), 2)
        
        if failures:
            learnings['avg_skeptic_risk_failure'] = round(sum(o['skeptic_risk'] for o in failures) / len(failures), 2)
            learnings['avg_impact_risk_failure'] = round(sum(o['impact_risk'] for o in failures) / len(failures), 2)
            
            # Top failure reasons
            reasons = Counter(o.get('failure_reason', 'unknown') for o in failures)
            learnings['top_failure_reasons'] = reasons.most_common(3)
        
        # Conclusion
        if learnings['success_rate'] >= 0.80:
            learnings['conclusion'] = f"STRONG: {learnings['success_rate']:.0%} success rate — continue using"
        elif learnings['success_rate'] >= 0.50:
            learnings['conclusion'] = f"MODERATE: {learnings['success_rate']:.0%} — ensemble or improve"
        else:
            learnings['conclusion'] = f"WEAK: {learnings['success_rate']:.0%} — consider alternative engine"
        
        return learnings
    
    def get_best_engine_for(self, bug_type, available_engines=None):
        """Recommend the best engine for a bug type based on outcome data."""
        scores = {}
        for outcome in self.outcomes:
            if outcome['bug_type'] != bug_type:
                continue
            eng = outcome['engine']
            if available_engines and eng not in available_engines:
                continue
            if eng not in scores:
                scores[eng] = {'success': 0, 'total': 0}
            scores[eng]['total'] += 1
            if outcome['tests_passed']:
                scores[eng]['success'] += 1
        
        if not scores:
            return None, 0
        
        best = max(scores, key=lambda e: scores[e]['success'] / max(1, scores[e]['total']))
        sr = scores[best]['success'] / max(1, scores[best]['total'])
        return best, round(sr, 2)
    
    def get_success_rules(self, min_samples=3, min_rate=0.70):
        """Extract rules: "Engine X succeeds at BugType Y when Z"."""
        rules = []
        for bug_type, outcomes in self.patterns['success'].items():
            if len(outcomes) < min_samples:
                continue
            
            by_engine = defaultdict(list)
            for o in outcomes:
                by_engine[o['engine']].append(o)
            
            for eng, eng_outcomes in by_engine.items():
                if len(eng_outcomes) >= min_samples:
                    rate = len(eng_outcomes) / max(1, len(eng_outcomes) + 
                           len(self.patterns['failure'].get(bug_type, [])))
                    if rate >= min_rate:
                        avg_diff = sum(o['diff_size'] for o in eng_outcomes) / len(eng_outcomes)
                        rules.append({
                            'rule': f"{eng.upper()} excels at {bug_type}",
                            'engine': eng,
                            'bug_type': bug_type,
                            'success_rate': round(rate, 2),
                            'samples': len(eng_outcomes),
                            'avg_diff_size': round(avg_diff),
                        })
        
        return sorted(rules, key=lambda r: -r['success_rate'])
    
    def _save(self):
        try:
            os.makedirs(os.path.dirname(self.store_path), exist_ok=True)
            with open(self.store_path, 'w') as f:
                json.dump({
                    'outcomes': self.outcomes[-100:],
                    'pattern_summary': {
                        cat: {bt: len(items) for bt, items in bugs.items()}
                        for cat, bugs in self.patterns.items()
                    }
                }, f, indent=2, default=str)
        except:
            pass
    
    def _load(self):
        try:
            if os.path.exists(self.store_path):
                with open(self.store_path) as f:
                    data = json.load(f)
                self.outcomes = data.get('outcomes', [])
        except:
            pass


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    import tempfile, shutil
    
    print("FIX OUTCOME LEARNING — Self-Test")
    print("=" * 55)
    passed = 0
    
    tmp = tempfile.mkdtemp()
    foa = FixOutcomeAnalyzer(store_path=os.path.join(tmp, 'outcomes.json'))
    
    # Feed 10 outcomes
    for _ in range(7):
        foa.analyze('NullPointer', 'opencode', 'if x is not None:', True, 0.05, 0.10, 8)
    for _ in range(3):
        foa.analyze('NullPointer', 'ollama', 'if x:', False, 0.30, 0.40, 25, 'wrong approach')
    for _ in range(5):
        foa.analyze('RaceCondition', 'opencode', 'mutex.lock()', False, 0.50, 0.60, 30, 'complex fix')
    for _ in range(3):
        foa.analyze('RaceCondition', 'ollama', 'sync.Mutex', True, 0.20, 0.25, 15)
    
    # T1: Success rate for NullPointer + OpenCode
    l1 = foa.extract_learnings('NullPointer', 'opencode')
    t1 = l1['success_rate'] >= 0.80
    print(f"  T1: {'✅' if t1 else '❌'} OpenCode NP → success_rate={l1['success_rate']}")
    
    # T2: Success rate for NullPointer + Ollama
    l2 = foa.extract_learnings('NullPointer', 'ollama')
    t2 = l2['success_rate'] < 0.50
    print(f"  T2: {'✅' if t2 else '❌'} Ollama NP → success_rate={l2['success_rate']}")
    
    # T3: Preferred diff size
    t3 = 'preferred_diff_size' in l1
    print(f"  T3: {'✅' if t3 else '❌'} Preferred diff → {l1.get('preferred_diff_size')}")
    
    # T4: Top failure reasons
    l4 = foa.extract_learnings('RaceCondition', 'opencode')
    t4 = 'top_failure_reasons' in l4
    print(f"  T4: {'✅' if t4 else '❌'} Failure reasons → {l4.get('top_failure_reasons')}")
    
    # T5: Conclusion generation
    t5 = 'STRONG' in l1.get('conclusion', '')
    print(f"  T5: {'✅' if t5 else '❌'} STRONG conclusion → {l1.get('conclusion')}")
    
    # T6: WEAK conclusion for failing engine
    l6 = foa.extract_learnings('RaceCondition', 'opencode')
    t6 = 'WEAK' in l6.get('conclusion', '')
    print(f"  T6: {'✅' if t6 else '❌'} WEAK conclusion → {l6.get('conclusion')}")
    
    # T7: get_best_engine_for
    best, sr = foa.get_best_engine_for('NullPointer')
    t7 = best == 'opencode' and sr > 0.70
    print(f"  T7: {'✅' if t7 else '❌'} Best for NP → {best} (sr={sr})")
    
    # T8: get_best_engine_for RaceCondition
    best8, sr8 = foa.get_best_engine_for('RaceCondition')
    t8 = best8 == 'ollama' and sr8 >= 0.50
    print(f"  T8: {'✅' if t8 else '❌'} Best for RC → {best8} (sr={sr8})")
    
    # T9: Success rules extracted
    rules = foa.get_success_rules()
    t9 = len(rules) >= 1
    print(f"  T9: {'✅' if t9 else '❌'} Success rules → {len(rules)} extracted")
    for r in rules[:3]:
        print(f"      {r['rule']} (rate={r['success_rate']}, n={r['samples']})")
    
    # T10: Not enough data
    l10 = foa.extract_learnings('Deadlock', 'nonexistent')
    t10 = 'Not enough data' in l10.get('conclusion', '')
    print(f"  T10: {'✅' if t10 else '❌'} No data → {l10.get('conclusion')}")
    
    shutil.rmtree(tmp, ignore_errors=True)
    passed = sum([t1,t2,t3,t4,t5,t6,t7,t8,t9,t10])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/10 Tests bestanden")
    print(f"  {'✅ FIX OUTCOME LEARNING FERTIG' if passed >= 9 else '⚠️'}")
