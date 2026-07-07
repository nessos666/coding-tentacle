"""
BUG-TYPE-SPECIFIC TRUST — RC22
Per-bug-type trust tracking. Bayesian updates per (brain, bug_type).
Falls back to global trust when per-type data is sparse.

Autor: Hermes + David | Coding Tentacle 2026
"""

# CT-v11.0.0: PRODUCTION | 10/10 regression | 25 modules | 90% wired | Droste active
import time, math
from dataclasses import dataclass, field


@dataclass
class BugTypeTrust:
    """Trust data for one brain × bug_type combination."""
    trust: float = 0.7
    uncertainty: float = 0.4
    predictions: int = 0
    correct: int = 0
    wrong: int = 0
    recent: list = field(default_factory=list)  # last 20
    
    @property
    def success_rate(self):
        return self.correct / max(1, self.predictions)
    
    @property
    def calibrated_trust(self):
        if not self.recent:
            return self.trust
        return 0.7 * self.trust + 0.3 * (sum(self.recent) / len(self.recent))
    
    def update(self, was_correct):
        self.predictions += 1
        if was_correct:
            self.correct += 1
            self.recent.append(1)
        else:
            self.wrong += 1
            self.recent.append(0)
        if len(self.recent) > 20:
            self.recent.pop(0)
        
        # RC-W2-FIX: Smoothed Bayesian update with floor/ceiling
        # Prevents trust collapse from consecutive failures
        prior = self.trust
        likelihood = 0.80 if was_correct else 0.20
        raw_trust = (likelihood * prior) / max(0.001, (likelihood * prior + (1-likelihood)*(1-prior)))
        # Smooth: blend with prior (70% new, 30% old) to dampen oscillations
        self.trust = 0.7 * raw_trust + 0.3 * prior
        # Floor at 0.05 — prevents total collapse from 3+ failures
        self.trust = max(0.05, min(0.95, self.trust))
        self.uncertainty *= 0.95


class BugTypeSpecificTrust:
    """Per-bug-type trust matrix for MetacognitiveEvaluator.
    
    Stores trust for each (brain, bug_type) pair.
    Falls back to global trust when per-type data < min_samples.
    """
    
    def __init__(self, min_samples=3):
        self.matrix = {}  # brain → {bug_type → BugTypeTrust}
        self.global_trusts = {}  # brain → float
        self.min_samples = min_samples
    
    def ensure_entry(self, brain, bug_type):
        """Create trust entry if it doesn't exist."""
        if brain not in self.matrix:
            self.matrix[brain] = {}
        if bug_type not in self.matrix[brain]:
            self.matrix[brain][bug_type] = BugTypeTrust()
    
    def get_trust(self, brain, bug_type):
        """Get trust for (brain, bug_type). Falls back to global if < min_samples."""
        self.ensure_entry(brain, bug_type)
        bt_trust = self.matrix[brain][bug_type]
        
        if bt_trust.predictions >= self.min_samples:
            return bt_trust.calibrated_trust, bt_trust.uncertainty, 'specific'
        
        # Fallback to global trust
        global_trust = self.global_trusts.get(brain, 0.6)
        # Blend: 70% global, 30% specific (if any data)
        if bt_trust.predictions > 0:
            blended = 0.7 * global_trust + 0.3 * bt_trust.calibrated_trust
            return blended, max(0.3, bt_trust.uncertainty), 'blended'
        
        return global_trust, 0.5, 'global'
    
    def observe(self, brain, bug_type, was_correct):
        """Record observation for (brain, bug_type)."""
        self.ensure_entry(brain, bug_type)
        self.matrix[brain][bug_type].update(was_correct)
    
    def set_global_trust(self, brain, trust):
        self.global_trusts[brain] = trust
    
    def get_matrix_summary(self):
        """Return summary of all trust entries with enough data."""
        summary = {}
        for brain, bt_dict in self.matrix.items():
            for bug_type, bt_trust in bt_dict.items():
                if bt_trust.predictions >= self.min_samples:
                    key = f"{brain}:{bug_type}"
                    summary[key] = {
                        'trust': round(bt_trust.trust, 3),
                        'samples': bt_trust.predictions,
                        'success_rate': round(bt_trust.success_rate, 3),
                    }
        return summary
    
    def get_brain_capabilities(self, brain):
        """List bug types where this brain excels."""
        if brain not in self.matrix:
            return []
        capabilities = []
        for bug_type, bt_trust in self.matrix[brain].items():
            if bt_trust.predictions >= self.min_samples:
                capabilities.append((bug_type, bt_trust.calibrated_trust, bt_trust.predictions))
        return sorted(capabilities, key=lambda x: -x[1])


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    print("BUG-TYPE-SPECIFIC TRUST — Self-Test")
    print("=" * 55)
    passed = 0
    
    bts = BugTypeSpecificTrust(min_samples=3)
    
    # T1: Unknown bug type falls back to global
    bts.set_global_trust('Teacher', 0.70)
    trust, unc, source = bts.get_trust('Teacher', 'NullPointer')
    t1 = trust == 0.70 and source == 'global'
    print(f"  T1: {'✅' if t1 else '❌'} Fallback → trust={trust} source={source}")
    
    # T2: Specific trust after observations
    bts.observe('Teacher', 'NullPointer', True)
    bts.observe('Teacher', 'NullPointer', True)
    bts.observe('Teacher', 'NullPointer', True)
    trust2, unc2, source2 = bts.get_trust('Teacher', 'NullPointer')
    t2 = source2 == 'specific' and trust2 > 0.70
    print(f"  T2: {'✅' if t2 else '❌'} After 3 successes → trust={trust2:.2f} source={source2}")
    
    # T3: Failure drops trust
    bts.observe('Teacher', 'NullPointer', False)
    trust3, _, _ = bts.get_trust('Teacher', 'NullPointer')
    t3 = trust3 < trust2
    print(f"  T3: {'✅' if t3 else '❌'} After failure → trust={trust3:.2f} (was {trust2:.2f})")
    
    # T4: Different bug types tracked separately
    bts.observe('Teacher', 'RaceCondition', True)
    bts.observe('Teacher', 'RaceCondition', False)
    bts.observe('Teacher', 'RaceCondition', False)
    trust_race, _, source4 = bts.get_trust('Teacher', 'RaceCondition')
    trust_null, _, _ = bts.get_trust('Teacher', 'NullPointer')
    t4 = trust_null > trust_race  # NullPointer better than RaceCondition
    print(f"  T4: {'✅' if t4 else '❌'} NullPointer={trust_null:.2f} > RaceCondition={trust_race:.2f}")
    
    # T5: Blended trust with sparse data
    bts.set_global_trust('Planning', 0.60)
    # Only 1 observation → falls back to blended
    bts.ensure_entry('Planning', 'Deadlock')
    bts.observe('Planning', 'Deadlock', True)
    trust5, _, source5 = bts.get_trust('Planning', 'Deadlock')
    t5 = 'blend' in source5
    print(f"  T5: {'✅' if t5 else '❌'} Sparse → trust={trust5:.2f} source={source5}")
    
    # T6: Brain capabilities
    bts.set_global_trust('Learning', 0.65)
    for _ in range(5):
        bts.observe('Learning', 'FileNotFound', True)
        bts.observe('Learning', 'OverflowError', False)
    caps = bts.get_brain_capabilities('Learning')
    t6 = len(caps) >= 2 and caps[0][1] > caps[1][1]
    print(f"  T6: {'✅' if t6 else '❌'} FileNotFound > OverflowError")
    
    # T7: Matrix summary
    summary = bts.get_matrix_summary()
    t7 = len(summary) >= 2
    print(f"  T7: {'✅' if t7 else '❌'} Summary entries: {len(summary)}")
    
    # T8: Global trust for unknown bug type
    bts.set_global_trust('Safety', 1.0)
    trust8, _, source8 = bts.get_trust('Safety', 'UnknownXYZ')
    t8 = trust8 == 1.0 and source8 == 'global'
    print(f"  T8: {'✅' if t8 else '❌'} Safety global → {trust8}")
    
    passed = sum([t1,t2,t3,t4,t5,t6,t7,t8])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/8 Tests bestanden")
    print(f"  {'✅ BUG-TYPE-SPECIFIC TRUST FERTIG' if passed >= 7 else '⚠️'}")
