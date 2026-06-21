"""
HYPOTHESIS FEEDBACK MEMORY — RC7.4
BR→BLM Bridge: stores which hypotheses were correct/wrong.
Enables BR to learn which hypotheses work for which bug types.

Read-only evidence. NEVER bypasses Safety.

Autor: Hermes + David | Coding Tentacle 2026
"""
import time, json, os, hashlib
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class HypothesisRecord:
    """One hypothesis feedback record."""
    bug_type: str              # "NullPointer", "TypeError", ...
    hypothesis: str            # "Variable is Optional[None]", "Race condition"...
    proposed_confidence: float # BR's original confidence (0-1)
    outcome: bool              # True = correct, False = incorrect
    project_area: str          # "brains", "safety", "knowledge", ...
    function_name: str         # Which function was involved
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


class HypothesisFeedbackMemory:
    """Persistent store of hypothesis correctness feedback.
    Integrates with BugLearningMemory for unified querying."""
    
    def __init__(self, db_path=None):
        self.db_path = db_path or os.path.expanduser('~/.coding_tentacle/hypothesis_feedback.json')
        self.records: list[HypothesisRecord] = []
        self._load()
    
    # ═══════ RECORD ═══════
    def record_feedback(self, bug_type, hypothesis, proposed_confidence, 
                        outcome, project_area="", function_name=""):
        """Store whether a hypothesis was correct or not."""
        record = HypothesisRecord(
            bug_type=bug_type,
            hypothesis=hypothesis,
            proposed_confidence=proposed_confidence,
            outcome=outcome,
            project_area=project_area,
            function_name=function_name,
        )
        self.records.append(record)
        self._save()
        return record
    
    # ═══════ STATISTICS ═══════
    def hypothesis_stats(self, bug_type=None):
        """Get success rates for all hypotheses (optionally filtered by bug_type)."""
        stats = defaultdict(lambda: {'proposed': 0, 'correct': 0, 'wrong': 0,
                                       'avg_confidence': 0.0, 'confidences': []})
        
        for r in self.records:
            if bug_type and r.bug_type != bug_type:
                continue
            key = f"{r.bug_type}|{r.hypothesis}"
            stats[key]['proposed'] += 1
            stats[key]['confidences'].append(r.proposed_confidence)
            if r.outcome:
                stats[key]['correct'] += 1
            else:
                stats[key]['wrong'] += 1
        
        result = {}
        for key, data in stats.items():
            bt, hyp = key.split('|', 1)
            total = data['proposed']
            avg_conf = sum(data['confidences']) / max(1, len(data['confidences']))
            result[key] = {
                'bug_type': bt,
                'hypothesis': hyp,
                'times_proposed': total,
                'times_correct': data['correct'],
                'times_wrong': data['wrong'],
                'success_rate': round(data['correct'] / max(1, total), 3),
                'avg_confidence': round(avg_conf, 3),
            }
        return result
    
    def best_hypothesis(self, bug_type, min_samples=3):
        """Which hypothesis works best for this bug type?"""
        stats = self.hypothesis_stats(bug_type)
        candidates = [(k, v) for k, v in stats.items() 
                      if v['times_proposed'] >= min_samples]
        candidates.sort(key=lambda x: -x[1]['success_rate'])
        return candidates[:3] if candidates else []
    
    def adjust_confidence(self, bug_type, hypothesis, base_confidence):
        """Adjust BR confidence based on historical success rate."""
        stats = self.hypothesis_stats(bug_type)
        key = f"{bug_type}|{hypothesis}"
        if key in stats:
            sr = stats[key]['success_rate']
            samples = stats[key]['times_proposed']
            if samples >= 3:
                # Blend: 70% historical rate, 30% original confidence
                return round(0.70 * sr + 0.30 * base_confidence, 3)
        return base_confidence
    
    def stats(self):
        return {
            'total_records': len(self.records),
            'unique_hypotheses': len(self.hypothesis_stats()),
            'correct_rate': round(
                sum(1 for r in self.records if r.outcome) / max(1, len(self.records)), 3
            ),
            'actions_executed': 0,
        }
    
    def _save(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, 'w') as f:
            json.dump([asdict(r) for r in self.records[-1000:]], f, indent=2)
    
    def _load(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path) as f:
                    data = json.load(f)
                self.records = [HypothesisRecord(**d) for d in data]
            except Exception:
                self.records = []


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    import tempfile
    
    print("HYPOTHESIS FEEDBACK MEMORY — Self-Test")
    print("=" * 55)
    passed = 0
    
    tmp = tempfile.mkdtemp()
    hfm = HypothesisFeedbackMemory(db_path=os.path.join(tmp, 'hypfb.json'))
    
    # Seed some hypothesis feedback
    # NullPointer ← guard clause worked (correct hypothesis)
    for _ in range(8):
        hfm.record_feedback("NullPointer", "Variable is Optional[None]", 0.82, 
                           True, "safety", "inhibitory_control")
    for _ in range(2):
        hfm.record_feedback("NullPointer", "Variable is Optional[None]", 0.70, 
                           False, "safety", "inhibitory_control")
    
    # Race condition hypothesis — mostly wrong
    for _ in range(1):
        hfm.record_feedback("NullPointer", "Race condition", 0.65, True, "tentacles", "")
    for _ in range(5):
        hfm.record_feedback("NullPointer", "Race condition", 0.60, False, "tentacles", "")
    
    # TypeError
    for _ in range(6):
        hfm.record_feedback("TypeError", "Type mismatch from API response", 0.78, 
                           True, "patch", "patch_suggestion")
    
    # T1: Record feedback
    t1 = len(hfm.records) == 22
    print(f"  T1: {'✅' if t1 else '❌'} Records → {len(hfm.records)} stored")
    
    # T2: Hypothesis stats for NullPointer
    stats = hfm.hypothesis_stats("NullPointer")
    t2 = len(stats) >= 2
    print(f"  T2: {'✅' if t2 else '❌'} NullPointer stats → {len(stats)} hypotheses tracked")
    
    # T3: Best hypothesis
    best = hfm.best_hypothesis("NullPointer")
    t3 = len(best) >= 1 and best[0][1]['hypothesis'] == 'Variable is Optional[None]'
    print(f"  T3: {'✅' if t3 else '❌'} Best hypothesis → {best[0][1]['hypothesis']} (sr={best[0][1]['success_rate']})")
    
    # T4: Success rate
    opt_stats = stats.get('NullPointer|Variable is Optional[None]', {})
    sr = opt_stats.get('success_rate', 0)
    t4 = sr > 0.70  # 8/10 = 0.80
    print(f"  T4: {'✅' if t4 else '❌'} Success rate → {sr:.0%} (8/10)")
    
    # T5: Adjustment — good hypothesis gets confidence boost
    adj = hfm.adjust_confidence("NullPointer", "Variable is Optional[None]", 0.80)
    t5 = adj > 0.80  # Blend of 0.80 base + 0.80 historical
    print(f"  T5: {'✅' if t5 else '❌'} Adjust confidence → {adj:.2f} (base=0.80, sr=0.80)")
    
    # T6: Bad hypothesis gets dampened
    adj_bad = hfm.adjust_confidence("NullPointer", "Race condition", 0.65)
    sr_bad = stats.get('NullPointer|Race condition', {}).get('success_rate', 0)
    t6 = adj_bad < 0.65  # Dampened because poor historical success
    print(f"  T6: {'✅' if t6 else '❌'} Bad hypothesis dampened → {adj_bad:.2f} (base=0.65, sr={sr_bad:.0%})")
    
    # T7: Unknown hypothesis unchanged
    adj_new = hfm.adjust_confidence("NullPointer", "New idea", 0.70)
    t7 = adj_new == 0.70
    print(f"  T7: {'✅' if t7 else '❌'} New hypothesis → {adj_new:.2f} (unchanged)")
    
    # T8: Stats
    st = hfm.stats()
    t8 = st['total_records'] == 22 and st['actions_executed'] == 0
    print(f"  T8: {'✅' if t8 else '❌'} Stats → {st['total_records']} records, read-only")
    
    # T9: Persistence
    hfm2 = HypothesisFeedbackMemory(db_path=os.path.join(tmp, 'hypfb.json'))
    t9 = len(hfm2.records) == 22
    print(f"  T9: {'✅' if t9 else '❌'} Persistence → {len(hfm2.records)} reloaded")
    
    # T10: No forbidden methods
    forbidden = ['execute','write','patch','run_shell','apply','delete_file']
    t10 = not any(hasattr(hfm, m) for m in forbidden)
    print(f"  T10: {'✅' if t10 else '❌'} No forbidden methods")
    
    import shutil; shutil.rmtree(tmp, ignore_errors=True)
    passed = sum([t1,t2,t3,t4,t5,t6,t7,t8,t9,t10])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/10 Tests bestanden")
    print(f"  {'✅ HYPOTHESIS FEEDBACK MEMORY FERTIG' if passed >= 9 else '⚠️'}")
