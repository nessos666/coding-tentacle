"""
VITAL INTERACTION MATRIX — RC62
Detects dangerous vital sign COMBINATIONS — more than the sum of parts.
Kaskadeneffekte. Korrelation. Multi-Faktor-Risiko-Erkennung.
"""
from dataclasses import dataclass, field


@dataclass
class InteractionReport:
    detected_patterns: list = field(default_factory=list)
    interaction_score: float = 1.0  # 1.0 = healthy, 0.0 = critical
    global_system_health: float = 1.0
    dominant_failure_mode: str = ''
    cascading_risks: list = field(default_factory=list)
    recommended_actions: list = field(default_factory=list)
    explanation: str = ''


class VitalInteractionMatrix:
    """Detects dangerous vital sign combinations (not just individual values)."""
    
    # Pattern definitions: (condition_fn, severity, action, cascade_targets, description)
    INTERACTION_PATTERNS = [
        # Pattern A: Trust↓ + Calibration↑ = Mislearning
        ('trust_collapse_calibration', {
            'severity': 'CRITICAL',
            'condition': lambda v: (v.get('engine_trust', 0.6) < 0.15 and 
                                    v.get('calibration_gap', 0) > 0.30),
            'actions': ['EXPLORE_ALTERNATIVE_ENGINES', 'HUMAN_REVIEW_REQUIRED', 'RESET_TRUST_0.30'],
            'cascade': ['EngineLearning quality', 'Future routing decisions'],
            'description': 'TRUST COLLAPSE + CALIBRATION DRIFT: Engine abandoned while model is wrong',
            'score_impact': 0.30,
        }),
        # Pattern B: Unknown↑ + Diversity↓ = Blindness
        ('unknown_blindness', {
            'severity': 'WARNING',
            'condition': lambda v: (v.get('unknown_rate', 0) > 0.25 and 
                                    v.get('engine_usage_ratio', 0.5) > 0.80),
            'actions': ['TEST_ALTERNATIVE_ENGINE', 'RESEARCH_FLAG', 'VARIETY_CHECK_STRICT'],
            'cascade': ['Classification confidence', 'Fix quality'],
            'description': 'HIGH UNKNOWN + MONOCULTURE: Only one engine seeing unfamiliar bugs',
            'score_impact': 0.20,
        }),
        # Pattern C: Audit↓ + Safety↓ = Unaufiable
        ('unauditable_execution', {
            'severity': 'CRITICAL',
            'condition': lambda v: (v.get('audit_score', 1.0) < 0.60 and 
                                    not v.get('safety_active', True)),
            'actions': ['SAFE_MODE', 'HUMAN_REVIEW_REQUIRED', 'NO_AUTO_EXECUTION'],
            'cascade': ['All decisions', 'Legal compliance'],
            'description': 'LOW AUDIT + SAFETY GAP: Decisions cannot be verified and are unsafe',
            'score_impact': 0.35,
        }),
        # Pattern D: Error↑ + Response↑ = Engine Failure
        ('engine_degradation', {
            'severity': 'CRITICAL',
            'condition': lambda v: (v.get('error_rate', 0) > 0.20 and 
                                    v.get('response_time', 10) > 45.0),
            'actions': ['CIRCUIT_BREAKER_OPEN', 'SWITCH_ENGINE', 'REDUCE_RETRY'],
            'cascade': ['Pipeline throughput', 'System reliability'],
            'description': 'HIGH ERRORS + SLOW RESPONSE: Engine is failing and timing out',
            'score_impact': 0.30,
        }),
        # Pattern E: Consolidation↓ + BLM↓ = Stagnation
        ('learning_stagnation', {
            'severity': 'WARNING',
            'condition': lambda v: (v.get('last_consolidation_age', 0) > 86400 and 
                                    v.get('blm_entries', 100) < 10),
            'actions': ['RUN_CONSOLIDATION_CYCLE', 'LEARNING_WARNING', 'SKILL_AUDIT'],
            'cascade': ['Long-term learning', 'Knowledge degradation'],
            'description': 'CONSOLIDATION OVERDUE + LOW BLM: System not consolidating and low on data',
            'score_impact': 0.20,
        }),
        # Pattern F: Error↑ + Trust↓ = Dangerous Routing
        ('dangerous_routing', {
            'severity': 'CRITICAL',
            'condition': lambda v: (v.get('error_rate', 0) > 0.30 and 
                                    v.get('engine_trust', 0.6) > 0.70),
            'actions': ['PAUSE_ENGINE', 'HUMAN_REVIEW_REQUIRED', 'LOWER_TRUST'],
            'cascade': ['Fix quality', 'Safety integrity'],
            'description': 'HIGH ERRORS + HIGH TRUST: Engine trusted despite frequent failures',
            'score_impact': 0.35,
        }),
        # Pattern G: Response↑ + Timeout trend = Engine Hang
        ('engine_hang_risk', {
            'severity': 'WARNING',
            'condition': lambda v: v.get('response_time', 10) > 60.0,
            'actions': ['TIMEOUT_WARNING', 'PREPARE_FALLBACK', 'MONITOR_LATENCY'],
            'cascade': ['Pipeline latency', 'User experience'],
            'description': 'SLOW RESPONSE: Engine approaching timeout, prepare fallback',
            'score_impact': 0.15,
        }),
        # Pattern H: All green
        ('all_healthy', {
            'severity': 'STABLE',
            'condition': lambda v: True,  # Fallback
            'actions': ['CONTINUE_NORMAL'],
            'cascade': [],
            'description': 'All vital signs within healthy ranges',
            'score_impact': 0.0,
        }),
    ]
    
    def analyze(self, vitals: dict = None) -> InteractionReport:
        """Detect dangerous vital sign combinations."""
        report = InteractionReport()
        vitals = vitals or {}
        
        remaining_score = 1.0
        highest_severity = 'STABLE'
        severity_rank = {'STABLE': 0, 'WARNING': 1, 'CRITICAL': 2}
        
        for pattern_name, pattern in self.INTERACTION_PATTERNS:
            if pattern_name == 'all_healthy':
                continue  # Handle as fallback
            
            try:
                if pattern['condition'](vitals):
                    report.detected_patterns.append({
                        'name': pattern_name,
                        'severity': pattern['severity'],
                        'description': pattern['description'],
                        'actions': pattern['actions'],
                        'cascade_effects': pattern['cascade'],
                    })
                    remaining_score -= pattern['score_impact']
                    
                    if severity_rank.get(pattern['severity'], 0) > severity_rank.get(highest_severity, 0):
                        highest_severity = pattern['severity']
                        report.dominant_failure_mode = pattern_name
                    
                    report.cascading_risks.extend(pattern['cascade'])
                    report.recommended_actions.extend(pattern['actions'])
            except:
                pass
        
        # Fallback: all healthy
        if not report.detected_patterns:
            report.detected_patterns.append({
                'name': 'all_healthy',
                'severity': 'STABLE',
                'description': 'All vital signs within healthy ranges',
                'actions': [],
                'cascade_effects': [],
            })
        
        report.interaction_score = max(0.0, remaining_score)
        report.global_system_health = report.interaction_score
        
        # Build explanation
        report.explanation = '\n'.join(
            f"[{p['severity']}] {p['description']}" for p in report.detected_patterns
        )
        
        return report


# ═══════════ SELF-TEST ═══════════
if __name__ == "__main__":
    vim = VitalInteractionMatrix()
    passed = 0
    
    print("VITAL INTERACTION MATRIX — Self-Test")
    print("=" * 55)
    
    # T1: Trust collapse + Calibration drift
    r = vim.analyze({'engine_trust': 0.05, 'calibration_gap': 0.45})
    t1 = any('trust_collapse_calibration' in str(p) for p in r.detected_patterns)
    if t1: passed += 1
    print(f"  {'✅' if t1 else '❌'} T1: Trust↓+Calib↑ → {'CRITICAL' if t1 else 'MISSED'}")
    
    # T2: Unknown + Monoculture
    r = vim.analyze({'unknown_rate': 0.35, 'engine_usage_ratio': 0.90})
    t2 = any('unknown_blindness' in str(p) for p in r.detected_patterns)
    if t2: passed += 1
    print(f"  {'✅' if t2 else '❌'} T2: Unknown↑+Mono → {'WARNING' if t2 else 'MISSED'}")
    
    # T3: Audit low + Safety off
    r = vim.analyze({'audit_score': 0.30, 'safety_active': False})
    t3 = any('unauditable_execution' in str(p) for p in r.detected_patterns)
    if t3: passed += 1
    print(f"  {'✅' if t3 else '❌'} T3: Audit↓+Safety↓ → {'CRITICAL' if t3 else 'MISSED'}")
    
    # T4: Error high + Response slow
    r = vim.analyze({'error_rate': 0.35, 'response_time': 55.0})
    t4 = any('engine_degradation' in str(p) for p in r.detected_patterns)
    if t4: passed += 1
    print(f"  {'✅' if t4 else '❌'} T4: Error↑+Slow → {'CRITICAL' if t4 else 'MISSED'}")
    
    # T5: Consolidation overdue + BLM low
    r = vim.analyze({'last_consolidation_age': 100000, 'blm_entries': 2})
    t5 = any('learning_stagnation' in str(p) for p in r.detected_patterns)
    if t5: passed += 1
    print(f"  {'✅' if t5 else '❌'} T5: Cons↓+BLM↓ → {'WARNING' if t5 else 'MISSED'}")
    
    # T6: Error high + Trust high
    r = vim.analyze({'error_rate': 0.40, 'engine_trust': 0.85})
    t6 = any('dangerous_routing' in str(p) for p in r.detected_patterns)
    if t6: passed += 1
    print(f"  {'✅' if t6 else '❌'} T6: Error↑+Trust↑ → {'CRITICAL' if t6 else 'MISSED'}")
    
    # T7: All healthy
    r = vim.analyze({'engine_trust': 0.80, 'calibration_gap': 0.05, 'audit_score': 0.95,
                      'safety_active': True, 'error_rate': 0.05, 'response_time': 12.0,
                      'blm_entries': 100, 'unknown_rate': 0.05})
    t7 = r.interaction_score > 0.90 and 'all_healthy' in str(r.detected_patterns)
    if t7: passed += 1
    print(f"  {'✅' if t7 else '❌'} T7: All healthy → score={r.interaction_score:.2f}")
    
    # T8: Multiple patterns detected
    r = vim.analyze({'engine_trust': 0.04, 'calibration_gap': 0.50, 'audit_score': 0.20,
                      'safety_active': False, 'unknown_rate': 0.45})
    t8 = len(r.detected_patterns) >= 2 and r.interaction_score < 0.50
    if t8: passed += 1
    print(f"  {'✅' if t8 else '❌'} T8: Multi-pattern → {len(r.detected_patterns)} patterns, score={r.interaction_score:.2f}")
    
    print(f"\n  ERGEBNIS: {passed}/8 Tests")
    print(f"  {'✅ VITAL INTERACTION MATRIX FERTIG' if passed >= 7 else '⚠️'}")
