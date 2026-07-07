"""
RC12 EXPLAINABILITY — Decision Trace pro Repair

Generiert eine vollständige, nachvollziehbare Entscheidungskette
für jeden einzelnen Repair-Durchlauf. Keine Black Box mehr.

Output: Strukturiertes dict + formatierte Markdown-String.
"""

from dataclasses import dataclass, field
from typing import Optional
import time


@dataclass
class DecisionStep:
    """Ein einzelner Schritt in der Entscheidungskette."""
    phase: str           # 'CLASSIFY', 'SECURITY', 'METABRAIN', 'ROUTING', etc.
    decision: str        # Was wurde entschieden?
    reason: str          # Warum?
    evidence: dict = field(default_factory=dict)  # Belegdaten
    confidence: float = 0.0


@dataclass
class DecisionTrace:
    """Vollständige Entscheidungskette eines Repairs."""
    repair_id: str
    timestamp: float = 0.0
    bug_type: str = ''
    steps: list[DecisionStep] = field(default_factory=list)
    final_outcome: str = ''
    total_duration_ms: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()
    
    def add_step(self, phase: str, decision: str, reason: str,
                 evidence: dict = None, confidence: float = 0.0):
        self.steps.append(DecisionStep(
            phase=phase, decision=decision, reason=reason,
            evidence=evidence or {}, confidence=confidence,
        ))
    
    def to_dict(self) -> dict:
        return {
            'repair_id': self.repair_id,
            'timestamp': self.timestamp,
            'bug_type': self.bug_type,
            'final_outcome': self.final_outcome,
            'total_duration_ms': self.total_duration_ms,
            'steps': [
                {
                    'phase': s.phase,
                    'decision': s.decision,
                    'reason': s.reason,
                    'evidence': s.evidence,
                    'confidence': s.confidence,
                }
                for s in self.steps
            ],
        }
    
    def to_markdown(self) -> str:
        """Generiert lesbare Markdown-Erklärung."""
        lines = [
            f"# Decision Trace — {self.repair_id}",
            f"**Bug Type:** {self.bug_type}  ",
            f"**Outcome:** {self.final_outcome}  ",
            f"**Duration:** {self.total_duration_ms:.0f}ms  ",
            "",
        ]
        
        icons = {
            'CLASSIFY': '🔍',
            'SECURITY': '🛡️',
            'METABRAIN': '🧠',
            'ROUTING': '🔧',
            'EXPERIENCE': '📚',
            'SKEPTIC': '🔬',
            'RESULT': '✅' if 'SUCCESS' in self.final_outcome else '❌',
        }
        
        for step in self.steps:
            icon = icons.get(step.phase, '•')
            lines.append(f"### {icon} {step.phase}")
            lines.append(f"**Decision:** {step.decision}")
            lines.append(f"**Reason:** {step.reason}")
            if step.confidence > 0:
                lines.append(f"**Confidence:** {step.confidence:.0%}")
            if step.evidence:
                lines.append("**Evidence:**")
                for k, v in step.evidence.items():
                    lines.append(f"  - {k}: {v}")
            lines.append("")
        
        return '\n'.join(lines)


class ExplainabilityEngine:
    """
    Erzeugt Decision Traces aus ShadowRunReports.
    
    Usage:
        engine = ExplainabilityEngine()
        trace = engine.trace(report, case_id)
        print(trace.to_markdown())
    """
    
    def trace(self, report, case_id: str = '',
              engine_name: str = '', route_reason: str = '',
              duration_ms: float = 0.0) -> DecisionTrace:
        """
        Baut Decision Trace aus einem ShadowRunReport.
        """
        trace = DecisionTrace(
            repair_id=case_id or f"repair_{int(time.time())}",
            bug_type=getattr(report, 'detected_bug_type', 'Unknown'),
            total_duration_ms=duration_ms,
        )
        
        # STEP 1: Classification
        bug_type = getattr(report, 'detected_bug_type', 'Unknown')
        confidence = getattr(report, 'confidence', 0.0)
        trace.add_step(
            'CLASSIFY',
            f'Classified as {bug_type}',
            f'Keyword-based classification matched {bug_type} patterns',
            {'bug_type': bug_type, 'classifier': 'keyword'},
            confidence,
        )
        
        # STEP 2: SecurityBrain
        blocked = getattr(report, 'security_blocked', False)
        trojan_clean = getattr(report, 'trojan_source_clean', True)
        risk = getattr(report, 'security_risk_score', 0.0)
        if blocked:
            trace.add_step('SECURITY', 'BLOCKED',
                'SecurityBrain detected critical issue',
                {'trojan_clean': trojan_clean, 'risk_score': risk})
            trace.final_outcome = 'BLOCKED_BY_SECURITY'
            return trace
        else:
            trace.add_step('SECURITY', 'PASS',
                f'No security issues (Trojan: {"OK" if trojan_clean else "FAIL"}, Risk: {risk:.2f})',
                {'trojan_clean': trojan_clean, 'risk_score': risk})
        
        # STEP 3: MetaBrain
        skeptic_risk = getattr(report, 'skeptic_risk', 0.0)
        skeptic_rec = getattr(report, 'skeptic_recommendation', '')
        trace.add_step('METABRAIN',
            f'SafetyBrain: GO, SkepticBrain: {skeptic_rec or "N/A"}',
            f'Risk assessment: {skeptic_risk:.2f}',
            {'skeptic_risk': skeptic_risk, 'recommendation': skeptic_rec})
        
        # STEP 4: Engine Routing
        trust_source = getattr(report, 'bug_type_trust_source', '')
        trust_val = getattr(report, 'skeptic_risk', 0.0)
        trace.add_step('ROUTING',
            f'Engine: {engine_name or "none"}',
            route_reason or f'Selected {engine_name} (trust={trust_source})',
            {'engine': engine_name, 'trust_source': trust_source,
             'route_reason': route_reason})
        
        # STEP 5: Experience (BLM + Consolidator)
        blm_written = getattr(report, 'blm_written', False)
        rules_updated = getattr(report, 'rules_updated', 0)
        consolidator_rule = getattr(report, 'consolidator_rule', '')
        trace.add_step('EXPERIENCE',
            f'BLM: {"recorded" if blm_written else "failed"}, Rules: {rules_updated}',
            f'Consolidator rule: {consolidator_rule or "none"}',
            {'blm_written': blm_written, 'rules_updated': rules_updated,
             'consolidator_rule': consolidator_rule})
        
        # STEP 6: Result
        diff = getattr(report, 'generated_diff', '')
        test = getattr(report, 'test_result', {}) or {}
        tests_ok = test.get('success', False) or test.get('tests_passed', 0) > 0
        
        if diff and tests_ok:
            outcome = 'SUCCESS'
        elif diff:
            outcome = 'PARTIAL (diff generated, tests not verified)'
        elif blocked:
            outcome = 'BLOCKED'
        else:
            outcome = 'FAILED'
        
        trace.final_outcome = outcome
        trace.add_step('RESULT',
            outcome,
            f'Diff: {len(diff)} bytes, Tests: {"PASS" if tests_ok else "N/A"}',
            {'diff_bytes': len(diff), 'tests_ok': tests_ok})
        
        return trace


# ─── Self-Tests ─────────────────────────────────────────────────────────

if __name__ == '__main__':
    class MockReport:
        detected_bug_type = 'NullPointer'
        confidence = 0.82
        security_blocked = False
        trojan_source_clean = True
        security_risk_score = 0.0
        skeptic_risk = 0.08
        skeptic_recommendation = 'APPROVE'
        bug_type_trust_source = 'specific'
        blm_written = True
        rules_updated = 2
        consolidator_rule = 'PREFER:opencode:87%'
        generated_diff = 'def fix(): return None'
        test_result = {'success': True, 'tests_passed': 3, 'tests_total': 3}
        safety_events = []

    engine = ExplainabilityEngine()
    passed = 0

    # T1: Full trace
    print("T1: Full trace...", end=" ")
    trace = engine.trace(MockReport(), case_id='bug_001', engine_name='opencode',
                         route_reason='Routed to opencode (priority 0.5 trust=0.91)')
    assert len(trace.steps) >= 5
    assert trace.final_outcome == 'SUCCESS'
    passed += 1
    print("OK")

    # T2: Security blocked
    print("T2: Security blocked trace...", end=" ")
    mr2 = MockReport()
    mr2.security_blocked = True
    trace2 = engine.trace(mr2, case_id='bug_002')
    assert trace2.final_outcome == 'BLOCKED_BY_SECURITY'
    assert len(trace2.steps) <= 3  # Short trace — blocked early
    passed += 1
    print("OK")

    # T3: to_dict
    print("T3: to_dict...", end=" ")
    d = trace.to_dict()
    assert d['final_outcome'] == 'SUCCESS'
    assert len(d['steps']) >= 5
    passed += 1
    print("OK")

    # T4: to_markdown
    print("T4: to_markdown...", end=" ")
    md = trace.to_markdown()
    assert '## Decision Trace' in md or '# Decision Trace' in md
    assert 'NullPointer' in md
    assert 'SUCCESS' in md
    passed += 1
    print("OK")

    # T5: Failed repair trace
    print("T5: Failed repair...", end=" ")
    mr3 = MockReport()
    mr3.generated_diff = ''
    mr3.test_result = {}
    trace3 = engine.trace(mr3, case_id='bug_003')
    assert trace3.final_outcome == 'FAILED'
    passed += 1
    print("OK")

    print(f"\n{'='*50}")
    print(f"  {passed}/5 Tests bestanden")
    print(f"  {'✅ EXPLAINABILITY ENGINE FERTIG' if passed >= 5 else '❌'}")
