"""
METACOGNITIVE EVALUATOR — RC20
Trust-weighted consensus for MetaBrain V2.
Bayesian trust updates + Kalman consensus + Self-calibration.

Safety VETO is ABSOLUTE — never overriden by trust weights.

Autor: Hermes + David | Coding Tentacle 2026
Research: SOFAI + POMDP + Kalman Consensus + Bayesian Belief
"""
import time, math, json, os
from dataclasses import dataclass, field, asdict


@dataclass
class BrainTrust:
    """Trust profile for one brain."""
    name: str
    trust: float = 0.7          # Bayesian posterior trust [0-1]
    uncertainty: float = 0.3    # σ — shrinks with evidence
    total_predictions: int = 0
    correct_predictions: int = 0
    wrong_predictions: int = 0
    recent_window: list = field(default_factory=list)  # last 20 outcomes
    priority: int = 50          # For ordering (Safety=100)
    is_veto: bool = False        # Safety gets VETO
    
    @property
    def success_rate(self):
        total = self.total_predictions
        return self.correct_predictions / max(1, total)
    
    @property
    def recent_success_rate(self):
        if not self.recent_window:
            return 0.5
        return sum(self.recent_window) / len(self.recent_window)
    
    @property
    def calibrated_trust(self):
        """Weighted blend of long-term trust and recent performance."""
        return 0.7 * self.trust + 0.3 * self.recent_success_rate


class MetacognitiveEvaluator:
    """Trust-weighted consensus from multiple brains.
    
    Uses:
    - Bayesian update: P(Trust|Evidence) ∝ P(Evidence|Trust) × P(Trust)
    - Kalman consensus: Σ(score_i / σ_i) / Σ(1/σ_i)
    - Self-calibration: uncertainty shrinks with evidence
    """
    
    def __init__(self, brains=None):
        self.brains = {}  # name → BrainTrust
        self.history = []  # all observations
        
        # Register default brains
        self.register('Safety', is_veto=True, priority=100, trust=1.0, uncertainty=0.0)
        self.register('Teacher', priority=90, trust=0.70, uncertainty=0.30)
        self.register('Planning', priority=80, trust=0.60, uncertainty=0.40)
        self.register('Learning', priority=70, trust=0.50, uncertainty=0.50)
        
        # Optional: register analysis brains
        if brains:
            for name, profile in brains.items():
                self.register(name, **profile)
        
        self.decisions = 0
        self.approvals = 0
        self.escalations = 0
    
    def register(self, name, is_veto=False, priority=50, trust=0.7, uncertainty=0.3):
        """Register a brain for trust tracking."""
        self.brains[name] = BrainTrust(
            name=name, trust=trust, uncertainty=uncertainty, 
            is_veto=is_veto, priority=priority
        )
    
    def observe(self, brain_name, was_correct):
        """Bayesian update: P(Trust|Evidence)."""
        if brain_name not in self.brains:
            self.register(brain_name)
        
        bt = self.brains[brain_name]
        bt.total_predictions += 1
        
        if was_correct:
            bt.correct_predictions += 1
            bt.recent_window.append(1)
        else:
            bt.wrong_predictions += 1
            bt.recent_window.append(0)
        
        # Keep window at 20
        if len(bt.recent_window) > 20:
            bt.recent_window.pop(0)
        
        # Bayesian update
        prior = bt.trust
        likelihood = 0.80 if was_correct else 0.20
        posterior = (likelihood * prior) / max(0.001, (likelihood * prior + (1 - likelihood) * (1 - prior)))
        bt.trust = posterior
        
        # Shrink uncertainty with evidence
        bt.uncertainty *= 0.95
        
        self.history.append((brain_name, was_correct, time.time()))
    
    def evaluate(self, scores):
        """Kalman Consensus: weighted voting from all brains.
        
        Args:
            scores: dict of {brain_name: score_0_to_1}
        
        Returns:
            decision: APPROVE | REQUEST_MORE | ESCALATE | REJECT
            consensus: 0-1 score
            reason: str
        """
        # 1. Safety VETO
        safety = self.brains.get('Safety')
        if safety and safety.is_veto:
            safety_score = scores.get('Safety', 1.0)
            if safety_score < 0.3:
                return 'REJECT', 0.0, 'Safety VETO: dangerous operation'
        
        # 2. Filter to brains with scores
        active = {k: v for k, v in scores.items() if k in self.brains}
        if not active:
            return 'ESCALATE', 0.0, 'No brain scores available'
        
        # 3. Kalman Consensus: weight by inverse uncertainty
        total_weight = 0.0
        weighted_sum = 0.0
        
        for name, score in active.items():
            bt = self.brains[name]
            # Safety VETO brain: only dominant when REJECTING
            if bt.is_veto and score >= 0.5:
                # Safety says GO — let other brains decide
                weight = 1.0 / max(0.1, bt.uncertainty)  # Still present, not dominant
            else:
                weight = 1.0 / max(0.01, bt.uncertainty)
            trusted_score = score * bt.calibrated_trust
            weighted_sum += trusted_score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 'ESCALATE', 0.0, 'No trust data available'
        
        consensus = weighted_sum / max(0.01, total_weight)
        
        # 4. Decision gate
        self.decisions += 1
        
        if consensus >= 0.70:
            self.approvals += 1
            return 'APPROVE', round(consensus, 2), f'Consensus {consensus:.0%}'
        elif consensus >= 0.40:
            return 'REQUEST_MORE', round(consensus, 2), f'Need more data ({consensus:.0%})'
        else:
            self.escalations += 1
            return 'ESCALATE', round(consensus, 2), f'Low confidence ({consensus:.0%})'
    
    def get_brain_ranking(self):
        """Return brains sorted by calibrated trust (highest first)."""
        ranked = sorted(self.brains.values(), 
                       key=lambda b: b.calibrated_trust if not b.is_veto else 2.0, 
                       reverse=True)
        return [(b.name, round(b.calibrated_trust, 2), b.total_predictions, 
                 round(b.uncertainty, 3)) for b in ranked]
    
    def stats(self):
        """Summary statistics."""
        return {
            'decisions': self.decisions,
            'approvals': self.approvals,
            'escalations': self.escalations,
            'approval_rate': round(self.approvals / max(1, self.decisions), 2),
            'brains': {name: {
                'trust': round(bt.trust, 3),
                'uncertainty': round(bt.uncertainty, 3),
                'success_rate': round(bt.success_rate, 3),
                'predictions': bt.total_predictions,
                'calibrated': round(bt.calibrated_trust, 3),
            } for name, bt in self.brains.items()}
        }


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    print("METACOGNITIVE EVALUATOR — Self-Test")
    print("=" * 55)
    passed = 0
    
    mce = MetacognitiveEvaluator()
    
    # T1: Default brains registered
    t1 = len(mce.brains) >= 4
    print(f"  T1: {'✅' if t1 else '❌'} {len(mce.brains)} brains registered")
    
    # T2: Safety has VETO
    safety = mce.brains['Safety']
    t2 = safety.is_veto and safety.trust == 1.0
    print(f"  T2: {'✅' if t2 else '❌'} Safety VETO={safety.is_veto} trust={safety.trust}")
    
    # T3: Bayesian update increases trust on success
    prev = mce.brains['Teacher'].trust
    mce.observe('Teacher', True)  # success
    t3 = mce.brains['Teacher'].trust > prev
    print(f"  T3: {'✅' if t3 else '❌'} Teacher trust: {prev:.2f} → {mce.brains['Teacher'].trust:.2f}")
    
    # T4: Bayesian update decreases trust on failure
    mce.observe('Teacher', False)  # failure
    t4 = mce.brains['Teacher'].trust < 0.72  # should drop from success level
    print(f"  T4: {'✅' if t4 else '❌'} After failure → {mce.brains['Teacher'].trust:.2f}")
    
    # T5: Uncertainty shrinks with observations
    prev_unc = mce.brains['Planning'].uncertainty
    for _ in range(5):
        mce.observe('Planning', True)
    t5 = mce.brains['Planning'].uncertainty < prev_unc
    print(f"  T5: {'✅' if t5 else '❌'} Planning σ: {prev_unc:.3f} → {mce.brains['Planning'].uncertainty:.3f}")
    
    # T6: APPROVE with high consensus
    scores = {'Safety': 1.0, 'Teacher': 0.85, 'Planning': 0.80, 'Learning': 0.90}
    decision, conf, reason = mce.evaluate(scores)
    t6 = decision == 'APPROVE' and conf > 0.6
    print(f"  T6: {'✅' if t6 else '❌'} {decision} conf={conf:.2f} ({reason})")
    
    # T7: ESCALATE with low consensus
    scores_low = {'Safety': 1.0, 'Teacher': 0.3, 'Planning': 0.2, 'Learning': 0.25}
    decision7, conf7, _ = mce.evaluate(scores_low)
    t7 = decision7 in ('ESCALATE', 'REQUEST_MORE')
    print(f"  T7: {'✅' if t7 else '❌'} {decision7} conf={conf7:.2f}")
    
    # T8: Safety VETO blocks everything
    scores_danger = {'Safety': 0.0, 'Teacher': 0.9, 'Planning': 0.9, 'Learning': 0.9}
    decision8, _, _ = mce.evaluate(scores_danger)
    t8 = decision8 == 'REJECT'
    print(f"  T8: {'✅' if t8 else '❌'} Safety VETO → {decision8}")
    
    # T9: Brain ranking
    ranking = mce.get_brain_ranking()
    t9 = ranking[0][0] == 'Safety'  # Safety always #1
    print(f"  T9: {'✅' if t9 else '❌'} #1 = {ranking[0][0]}")
    
    # T10: Stats summary
    st = mce.stats()
    t10 = st['decisions'] >= 2
    print(f"  T10: {'✅' if t10 else '❌'} Decisions: {st['decisions']}, Approval rate: {st['approval_rate']}")
    
    passed = sum([t1,t2,t3,t4,t5,t6,t7,t8,t9,t10])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/10 Tests bestanden")
    print(f"  {'✅ METACOGNITIVE EVALUATOR FERTIG' if passed >= 9 else '⚠️'}")
