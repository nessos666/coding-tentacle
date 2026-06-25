"""
DEUTERO-LEARNING BRAIN — RC57
Bateson's "Learning to learn": observes CT's learning process itself.
Detects: trust collapse, engine monoculture, skill stagnation, calibration drift.
"""
from dataclasses import dataclass, field


@dataclass
class DeuteroLearningReport:
    status: str = 'HEALTHY'  # HEALTHY / SLOW_LEARNING / OVERFITTING / MISLEARNING / STAGNANT / CRITICAL
    learning_score: float = 1.0
    trust_drift_report: dict = field(default_factory=dict)
    learning_velocity_report: dict = field(default_factory=dict)
    calibration_report: dict = field(default_factory=dict)
    skill_formation_report: dict = field(default_factory=dict)
    detected_pathologies: list = field(default_factory=list)
    recommended_adjustments: list = field(default_factory=list)
    requires_human_review: bool = False


class DeuteroLearningBrain:
    """Learning about learning. Second-order cybernetics in action."""
    
    PATHOLOGY_THRESHOLDS = {
        'trust_collapse_max': 0.05,       # Trust below = collapse
        'trust_inflation_min': 0.90,      # Trust above with failures = inflation
        'monoculture_ratio': 0.80,        # One engine used >80% = monoculture
        'stagnation_min_repeats': 3,       # Same root cause 3x without skill
        'noise_min_entries': 50,           # BLM >50 with <10% reuse = noise
        'calibration_gap': 0.30,           # Confidence - actual >30% = drift
        'unknown_blindness_rate': 0.20,    # >20% unknown without review
    }
    
    def evaluate(self, engine_trusts: dict = None, engine_usage: dict = None,
                 recent_successes: int = 0, recent_failures: int = 0,
                 blm_entries: int = 0, blm_reuse_count: int = 0,
                 root_cause_repeats: dict = None, skill_candidates_count: int = 0,
                 avg_confidence: float = 0.60, actual_success_rate: float = 0.50,
                 unknown_rate: float = 0.0, unknown_reviewed: int = 0) -> DeuteroLearningReport:
        """Evaluate the quality of CT's learning process."""
        report = DeuteroLearningReport()
        engine_trusts = engine_trusts or {}
        engine_usage = engine_usage or {}
        root_cause_repeats = root_cause_repeats or {}
        
        # 1. Trust Drift Analysis
        trust_report = {}
        for engine, trust in engine_trusts.items():
            if trust < self.PATHOLOGY_THRESHOLDS['trust_collapse_max']:
                trust_report[engine] = {'status': 'COLLAPSED', 'trust': trust,
                                        'recommendation': 'Reset trust to 0.30 + re-explore'}
            elif trust > self.PATHOLOGY_THRESHOLDS['trust_inflation_min'] and recent_failures > 0:
                trust_report[engine] = {'status': 'INFLATED', 'trust': trust,
                                        'recommendation': 'Reduce trust by 0.15 (failures present)'}
            else:
                trust_report[engine] = {'status': 'HEALTHY', 'trust': trust}
        report.trust_drift_report = trust_report
        
        # 2. Engine Monoculture Detection
        total_usage = sum(engine_usage.values()) if engine_usage else 1
        for engine, count in engine_usage.items():
            ratio = count / max(1, total_usage)
            if ratio > self.PATHOLOGY_THRESHOLDS['monoculture_ratio']:
                report.detected_pathologies.append(
                    f'ENGINE_MONOCULTURE: {engine} used {ratio:.0%} of time — explore alternatives')
        
        # 3. Trust Collapse / Inflation
        for engine, data in trust_report.items():
            if data['status'] == 'COLLAPSED':
                report.detected_pathologies.append(
                    f'TRUST_COLLAPSE: {engine} trust={data["trust"]:.2f} — permanently abandoned')
                report.recommended_adjustments.append(data['recommendation'])
            elif data['status'] == 'INFLATED':
                report.detected_pathologies.append(
                    f'TRUST_INFLATION: {engine} trust={data["trust"]:.2f} but failures exist')
        
        # 4. Calibration Drift
        calibration_gap = abs(avg_confidence - actual_success_rate)
        report.calibration_report = {
            'avg_confidence': avg_confidence,
            'actual_success_rate': actual_success_rate,
            'gap': calibration_gap,
        }
        if calibration_gap > self.PATHOLOGY_THRESHOLDS['calibration_gap']:
            direction = 'overconfident' if avg_confidence > actual_success_rate else 'underconfident'
            report.detected_pathologies.append(
                f'CALIBRATION_DRIFT: {direction} — conf={avg_confidence:.0%} vs actual={actual_success_rate:.0%}')
            report.recommended_adjustments.append(
                f'Recalibrate: adjust confidence baseline by {calibration_gap:.0%} toward actual')
        
        # 5. Skill Stagnation
        report.skill_formation_report = {
            'root_cause_repeats': root_cause_repeats,
            'skill_candidates': skill_candidates_count,
        }
        for rc, count in root_cause_repeats.items():
            if count >= self.PATHOLOGY_THRESHOLDS['stagnation_min_repeats'] and skill_candidates_count == 0:
                report.detected_pathologies.append(
                    f'SKILL_STAGNATION: {rc} repeated {count}× but no skill candidate generated')
        
        # 6. BLM Noise
        if blm_entries > self.PATHOLOGY_THRESHOLDS['noise_min_entries']:
            reuse_rate = blm_reuse_count / max(1, blm_entries)
            if reuse_rate < 0.10:
                report.detected_pathologies.append(
                    f'BLM_NOISE: {blm_entries} entries but only {reuse_rate:.0%} reused — storing noise')
        
        # 7. Unknown Blindness
        if unknown_rate > self.PATHOLOGY_THRESHOLDS['unknown_blindness_rate'] and unknown_reviewed == 0:
            report.detected_pathologies.append(
                f'UNKNOWN_BLINDNESS: {unknown_rate:.0%} unknown bugs but none flagged for review')
        
        # 8. Learning Velocity
        total_events = blm_entries + skill_candidates_count
        report.learning_velocity_report = {
            'blm_entries': blm_entries,
            'blm_reuse': blm_reuse_count,
            'skill_candidates': skill_candidates_count,
            'total_learning_events': total_events,
        }
        if total_events == 0:
            report.detected_pathologies.append('NO_LEARNING: zero experiences stored')
        
        # Status determination
        if report.detected_pathologies:
            critical_count = sum(1 for p in report.detected_pathologies 
                               if any(kw in p for kw in ['COLLAPSE', 'INFLATION', 'DRIFT']))
            if critical_count >= 2:
                report.status = 'CRITICAL'
                report.learning_score = 0.2
            elif critical_count >= 1:
                report.status = 'MISLEARNING'
                report.learning_score = 0.4
            elif 'SKILL_STAGNATION' in str(report.detected_pathologies):
                report.status = 'STAGNANT'
                report.learning_score = 0.5
            elif 'BLM_NOISE' in str(report.detected_pathologies):
                report.status = 'SLOW_LEARNING'
                report.learning_score = 0.6
            elif 'ENGINE_MONOCULTURE' in str(report.detected_pathologies):
                report.status = 'OVERFITTING'
                report.learning_score = 0.6
            else:
                report.status = 'SLOW_LEARNING'
                report.learning_score = 0.7
        else:
            report.status = 'HEALTHY'
            report.learning_score = 1.0
        
        report.requires_human_review = report.status in ('CRITICAL', 'MISLEARNING')
        return report


# ═══════════ SELF-TEST ═══════════
if __name__ == "__main__":
    brain = DeuteroLearningBrain()
    passed = 0
    
    print("DEUTERO-LEARNING BRAIN — Self-Test")
    print("=" * 55)
    
    # T1: All healthy
    r = brain.evaluate(engine_trusts={'oc': 0.75, 'ollama': 0.60}, engine_usage={'oc': 5, 'ollama': 3})
    t1 = r.status == 'HEALTHY'
    if t1: passed += 1
    print(f"  {'✅' if t1 else '❌'} T1: Healthy → {r.status} score={r.learning_score}")
    
    # T2: Trust collapse
    r = brain.evaluate(engine_trusts={'ollama': 0.02})
    t2 = 'TRUST_COLLAPSE' in str(r.detected_pathologies)
    if t2: passed += 1
    print(f"  {'✅' if t2 else '❌'} T2: Trust collapse → {r.detected_pathologies}")
    
    # T3: Trust inflation
    r = brain.evaluate(engine_trusts={'oc': 0.95}, recent_failures=3)
    t3 = 'TRUST_INFLATION' in str(r.detected_pathologies)
    if t3: passed += 1
    print(f"  {'✅' if t3 else '❌'} T3: Trust inflation → {r.detected_pathologies}")
    
    # T4: Engine monoculture
    r = brain.evaluate(engine_usage={'oc': 95, 'ollama': 2, 'claude': 3})
    t4 = 'ENGINE_MONOCULTURE' in str(r.detected_pathologies)
    if t4: passed += 1
    print(f"  {'✅' if t4 else '❌'} T4: Monoculture → {r.detected_pathologies}")
    
    # T5: Calibration drift
    r = brain.evaluate(avg_confidence=0.90, actual_success_rate=0.40)
    t5 = 'CALIBRATION_DRIFT' in str(r.detected_pathologies)
    if t5: passed += 1
    print(f"  {'✅' if t5 else '❌'} T5: Calibration drift → {r.calibration_report}")
    
    # T6: Skill stagnation
    r = brain.evaluate(root_cause_repeats={'MISSING_GUARD': 5}, skill_candidates_count=0)
    t6 = 'SKILL_STAGNATION' in str(r.detected_pathologies)
    if t6: passed += 1
    print(f"  {'✅' if t6 else '❌'} T6: Stagnation → {r.detected_pathologies}")
    
    # T7: BLM noise
    r = brain.evaluate(blm_entries=200, blm_reuse_count=5)
    t7 = 'BLM_NOISE' in str(r.detected_pathologies)
    if t7: passed += 1
    print(f"  {'✅' if t7 else '❌'} T7: BLM noise → {r.detected_pathologies}")
    
    # T8: Unknown blindness
    r = brain.evaluate(unknown_rate=0.35, unknown_reviewed=0)
    t8 = 'UNKNOWN_BLINDNESS' in str(r.detected_pathologies)
    if t8: passed += 1
    print(f"  {'✅' if t8 else '❌'} T8: Unknown blindness → {r.detected_pathologies}")
    
    # T9: Multiple pathologies = CRITICAL
    r = brain.evaluate(engine_trusts={'ollama': 0.02, 'oc': 0.94}, recent_failures=4,
                       engine_usage={'oc': 90}, avg_confidence=0.92, actual_success_rate=0.30)
    t9 = r.status == 'CRITICAL'
    if t9: passed += 1
    print(f"  {'✅' if t9 else '❌'} T9: Multi-pathology → {r.status} pathologies={len(r.detected_pathologies)}")
    
    print(f"\n  ERGEBNIS: {passed}/9 Tests")
    print(f"  {'✅ DEUTERO-LEARNING BRAIN FERTIG' if passed >= 7 else '⚠️'}")
