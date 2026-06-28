"""
HOMEOSTASIS BRAIN — RC53
Monitors 5 vital signs. Auto-corrects imbalances. Oktopus: Körpertemperatur-Regelung.
"""
from dataclasses import dataclass, field


@dataclass
class HomeostasisReport:
    status: str = 'STABLE'  # STABLE / WARNING / CRITICAL
    vital_scores: dict = field(default_factory=dict)
    overall_score: float = 1.0
    detected_imbalances: list = field(default_factory=list)
    recommended_actions: list = field(default_factory=list)
    automatic_adjustments: list = field(default_factory=list)
    requires_human_review: bool = False


class HomeostasisBrain:
    """Keeps CT in balance. Auto-corrects deviations."""
    
    def __init__(self, engine_learning=None):
        self.engine_learning = engine_learning
        self.thresholds = {
            # Vital 1-2: Engine Trust
            'trust_min': 0.15,      # Below = WARNING
            'trust_critical': 0.05,  # Below = CRITICAL
            # Vital 3-4: Error Rate
            'error_max': 0.20,       # Above = WARNING
            'error_critical': 0.40,  # Above = CRITICAL
            # Vital 5: BLM Health
            'blm_min_entries': 3,    # Below = WARNING
            # Vital 6-7: Response Time
            'response_max': 45.0,    # Seconds, above = WARNING
            'response_critical': 90.0,
            # Vital 8: Confidence Calibration
            'calibration_gap_max': 0.30,  # |confidence - actual| > 30% = WARNING
            # Vital 9: Consolidation Health
            'consolidation_max_age': 86400,  # 24h since last consolidation = WARNING
            # Vital 10: Engine Diversity
            'monoculture_ratio': 0.80,  # One engine >80% usage = WARNING
            # Vital 11: Unknown Rate
            'unknown_rate_max': 0.25,  # >25% unknown bugs = WARNING
            # Vital 12: Evidence Completeness
            'audit_score_min': 0.60,  # Below 60% audit score = WARNING
        }
    
    def adjust_thresholds(self, reflection_confidence: float = 0.0,
                          engine_trust_trend: float = 0.0,
                          error_rate_trend: float = 0.0):
        """RC96: Adaptive thresholds within safe bounds. No sudden jumps."""
        # Trust threshold: adapt between 0.15 and 0.35
        if reflection_confidence > 0.7:
            self.thresholds['trust_min'] = max(0.15, self.thresholds['trust_min'] - 0.01)
            self.thresholds['trust_critical'] = min(0.35, self.thresholds['trust_critical'] + 0.01)
        elif reflection_confidence < 0.3:
            self.thresholds['trust_min'] = min(0.35, self.thresholds['trust_min'] + 0.01)
        
        # Error rate: tighten if improving, loosen if worsening
        if error_rate_trend < 0:
            self.thresholds['error_rate_max'] = min(0.20, self.thresholds['error_rate_max'] + 0.01)
        elif error_rate_trend > 0:
            self.thresholds['error_rate_max'] = max(0.05, self.thresholds['error_rate_max'] - 0.01)
        
        # BLM entries: scale with experience (max 15)
        if self.thresholds['blm_min'] < 100:
            self.thresholds['blm_min'] = min(15, self.thresholds['blm_min'] + 1)
        
        # Response time: relax if system is stable
        self.thresholds['response_time_max'] = min(10.0, max(3.0,
            self.thresholds['response_time_max'] + (0.1 if engine_trust_trend > 0 else -0.1)))
        
        # Audit score: slightly relax if everything is healthy
        if reflection_confidence > 0.8 and engine_trust_trend > 0:
            self.thresholds['audit_score_min'] = min(0.75, self.thresholds['audit_score_min'] + 0.02)
    
    def check(self, engine_trust=0.60, error_rate=0.0, blm_entries=0,
              response_time=0.0, safety_active=True, approval_active=True,
              reflex_active=True, injection_active=True,
              # RC61: 5 → 12 Vital Signs
              calibration_gap=0.0, last_consolidation_age=0,
              engine_usage_ratio=0.0, unknown_rate=0.0,
              audit_score=1.0) -> HomeostasisReport:
        """Evaluate all 5 vital signs."""
        report = HomeostasisReport()
        
        # Vital 1: Trust health
        report.vital_scores['trust'] = engine_trust
        if engine_trust < self.thresholds['trust_critical']:
            report.detected_imbalances.append(f'Trust critical: {engine_trust:.2f}')
            report.recommended_actions.append('SWITCH_ENGINE: trust too low, use alternative')
            report.automatic_adjustments.append('FORCE_ALTERNATIVE_ENGINE')
        elif engine_trust < self.thresholds['trust_min']:
            report.detected_imbalances.append(f'Trust low: {engine_trust:.2f}')
            report.recommended_actions.append('CONSERVATIVE_ROUTE: low trust, prefer fallback')
        
        # Vital 2: Error rate
        report.vital_scores['error_rate'] = error_rate
        if error_rate > self.thresholds['error_critical']:
            report.detected_imbalances.append(f'Error rate critical: {error_rate:.0%}')
            report.recommended_actions.append('HUMAN_ONLY_MODE: errors too high, pause engines')
            report.automatic_adjustments.append('PAUSE_ALL_ENGINES')
        elif error_rate > self.thresholds['error_max']:
            report.detected_imbalances.append(f'Error rate high: {error_rate:.0%}')
            report.recommended_actions.append('INCREASE_SAFETY: higher error rate, be more conservative')
        
        # Vital 3: BLM health
        report.vital_scores['blm_entries'] = blm_entries
        if blm_entries < self.thresholds['blm_min_entries']:
            report.detected_imbalances.append(f'BLM cold start: only {blm_entries} entries')
            report.recommended_actions.append('CONSERVATIVE: low experience, prefer REQUEST_MORE')
        
        # Vital 4: Response time
        report.vital_scores['response_time'] = response_time
        if response_time > self.thresholds['response_critical']:
            report.detected_imbalances.append(f'Response critical: {response_time:.0f}s')
            report.recommended_actions.append('SWITCH_ENGINE: too slow, try faster engine')
        elif response_time > self.thresholds['response_max']:
            report.detected_imbalances.append(f'Response slow: {response_time:.0f}s')
        
        # Vital 5: Safety integrity (highest priority)
        safety_checks = {'SafetyBrain': safety_active, 'ApprovalGate': approval_active,
                        'ReflexLayer': reflex_active, 'InjectionBrain': injection_active}
        report.vital_scores['safety_integrity'] = safety_checks
        missing = [k for k, v in safety_checks.items() if not v]
        if missing:
            report.detected_imbalances.append(f'SAFETY GAP: {missing} inactive')
            report.automatic_adjustments.append('SAFE_MODE: block all engine calls')
            report.requires_human_review = True
        
        # Vital 8: Confidence Calibration (RC61)
        report.vital_scores['calibration_gap'] = calibration_gap
        if calibration_gap > self.thresholds['calibration_gap_max']:
            report.detected_imbalances.append(f'CALIBRATION DRIFT: gap={calibration_gap:.0%}')
            report.recommended_actions.append('RECALIBRATE: confidence vs actual mismatch')
        
        # Vital 9: Consolidation Health (RC61)
        report.vital_scores['last_consolidation_age'] = last_consolidation_age
        if last_consolidation_age > self.thresholds['consolidation_max_age']:
            hours = last_consolidation_age / 3600
            report.detected_imbalances.append(f'CONSOLIDATION OVERDUE: {hours:.0f}h since last')
            report.recommended_actions.append('RUN_CONSOLIDATION: start ConsolidationCycle')
        
        # Vital 10: Engine Diversity (RC61)
        report.vital_scores['engine_usage_ratio'] = engine_usage_ratio
        if engine_usage_ratio > self.thresholds['monoculture_ratio']:
            report.detected_imbalances.append(f'ENGINE MONOCULTURE: {engine_usage_ratio:.0%} single engine')
            report.recommended_actions.append('DIVERSIFY: explore alternative engines')
        
        # Vital 11: Unknown Rate (RC61)
        report.vital_scores['unknown_rate'] = unknown_rate
        if unknown_rate > self.thresholds['unknown_rate_max']:
            report.detected_imbalances.append(f'HIGH UNKNOWN RATE: {unknown_rate:.0%} unclassified')
            report.recommended_actions.append('RESEARCH: too many unknown bugs, need more context')
        
        # Vital 12: Evidence Completeness (RC61)
        report.vital_scores['audit_score'] = audit_score
        if audit_score < self.thresholds['audit_score_min']:
            report.detected_imbalances.append(f'LOW AUDIT SCORE: {audit_score:.0%} evidence missing')
            report.recommended_actions.append('IMPROVE_EVIDENCE: missing test results or root cause')
        
        # Determine overall status
        if missing:
            report.status = 'CRITICAL'
            report.overall_score = 0.0
        elif (engine_trust < self.thresholds['trust_critical'] or 
              error_rate > self.thresholds['error_critical'] or
              response_time > self.thresholds['response_critical']):
            report.status = 'CRITICAL'
            report.overall_score = max(0.0, 1.0 - len(report.detected_imbalances) * 0.25)
        elif report.detected_imbalances:
            report.status = 'WARNING'
            report.overall_score = max(0.3, 1.0 - len(report.detected_imbalances) * 0.15)
        else:
            report.status = 'STABLE'
            report.overall_score = 1.0
        
        return report


# ═══════════ SELF-TEST ═══════════
if __name__ == "__main__":
    brain = HomeostasisBrain()
    passed = 0
    
    tests = [
        # (name, params, expected_status)
        ("T1: All stable", dict(engine_trust=0.75, error_rate=0.05, blm_entries=100, 
                                response_time=12.0, safety_active=True, approval_active=True,
                                reflex_active=True, injection_active=True), "STABLE"),
        ("T2: Low trust", dict(engine_trust=0.08, error_rate=0.05, blm_entries=100,
                               response_time=12.0, safety_active=True, approval_active=True,
                               reflex_active=True, injection_active=True), "WARNING"),
        ("T3: High error", dict(engine_trust=0.75, error_rate=0.45, blm_entries=100,
                                response_time=12.0, safety_active=True, approval_active=True,
                                reflex_active=True, injection_active=True), "CRITICAL"),
        ("T4: Cold start", dict(engine_trust=0.60, error_rate=0.05, blm_entries=1,
                                response_time=12.0, safety_active=True, approval_active=True,
                                reflex_active=True, injection_active=True), "WARNING"),
        ("T5: Slow response", dict(engine_trust=0.75, error_rate=0.05, blm_entries=100,
                                   response_time=95.0, safety_active=True, approval_active=True,
                                   reflex_active=True, injection_active=True), "CRITICAL"),
        ("T6: Missing SafetyBrain", dict(engine_trust=0.75, error_rate=0.05, blm_entries=100,
                                         response_time=12.0, safety_active=False, approval_active=True,
                                         reflex_active=True, injection_active=True), "CRITICAL"),
        ("T7: Missing Approval", dict(engine_trust=0.75, error_rate=0.05, blm_entries=100,
                                      response_time=12.0, safety_active=True, approval_active=False,
                                      reflex_active=True, injection_active=True), "CRITICAL"),
        # RC61: New 12-vital-sign tests
        ("T8: Calibration drift", dict(engine_trust=0.75, error_rate=0.05, blm_entries=100,
                                       response_time=12.0, safety_active=True, approval_active=True,
                                       reflex_active=True, injection_active=True,
                                       calibration_gap=0.45), "WARNING"),
        ("T9: Consolidation overdue", dict(engine_trust=0.75, error_rate=0.05, blm_entries=100,
                                           response_time=12.0, safety_active=True, approval_active=True,
                                           reflex_active=True, injection_active=True,
                                           last_consolidation_age=100000), "WARNING"),
        ("T10: Engine monoculture", dict(engine_trust=0.75, error_rate=0.05, blm_entries=100,
                                         response_time=12.0, safety_active=True, approval_active=True,
                                         reflex_active=True, injection_active=True,
                                         engine_usage_ratio=0.92), "WARNING"),
        ("T11: High unknown rate", dict(engine_trust=0.75, error_rate=0.05, blm_entries=100,
                                        response_time=12.0, safety_active=True, approval_active=True,
                                        reflex_active=True, injection_active=True,
                                        unknown_rate=0.40), "WARNING"),
        ("T12: Low audit score", dict(engine_trust=0.75, error_rate=0.05, blm_entries=100,
                                      response_time=12.0, safety_active=True, approval_active=True,
                                      reflex_active=True, injection_active=True,
                                      audit_score=0.30), "WARNING"),
    ]
    
    print("HOMEOSTASIS BRAIN — Self-Test")
    print("=" * 55)
    
    for name, params, exp_status in tests:
        r = brain.check(**params)
        ok = r.status == exp_status
        if ok: passed += 1
        status_mark = '✅' if ok else '❌'
        print(f"  {status_mark} {name:<22s} status={r.status:<8s} → {exp_status}")
    
    print(f"\n  ERGEBNIS: {passed}/{len(tests)} Tests")
    print(f"  {'✅ HOMEOSTASIS BRAIN FERTIG' if passed >= 6 else '⚠️'}")
