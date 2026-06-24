"""
SELF-OBSERVATION BRAIN — RC54
Von Foerster's Kybernetik 2. Ordnung: Das System beobachtet sich selbst.
Logs every decision. Detects bias, contradictions, overconfidence.
"""
from dataclasses import dataclass, field
import time


@dataclass
class DecisionStep:
    module: str
    decision: str  # ALLOW / BLOCK / WARN / GO / REQUEST_MORE / REJECT / APPROVE
    confidence: float
    reason: str


@dataclass
class SelfObservationReport:
    decision_trace: list = field(default_factory=list)
    module_contributions: dict = field(default_factory=dict)
    confidence_audit: dict = field(default_factory=dict)
    contradiction_flags: list = field(default_factory=list)
    bias_flags: list = field(default_factory=list)
    final_explanation: str = ''
    uncertainty_score: float = 0.0
    requires_review: bool = False


class SelfObservationBrain:
    """Observes CT's own decisions. Answers: WHY did we decide this?"""
    
    OVERCONFIDENCE_THRESHOLD = 0.85  # Confidence > this + test failed = overconfidence
    UNDERCONFIDENCE_THRESHOLD = 0.30  # Confidence < this + test passed = underconfidence
    LOW_TRUST_THRESHOLD = 0.15       # Engine trust below = risky routing
    
    def observe(self, decision_trace: list = None, bug_type: str = '',
                engine_used: str = '', engine_trust: float = 0.60,
                safety_warnings: list = None, skeptic_risk: float = 0.0,
                test_passed: bool = None, approval_status: str = '',
                root_cause: str = '', root_cause_repeat: int = 0) -> SelfObservationReport:
        """Analyze the decision process and produce an explanation."""
        report = SelfObservationReport()
        report.decision_trace = decision_trace or []
        
        # Build module contributions map
        for step in report.decision_trace:
            report.module_contributions[step.module] = {
                'decision': step.decision,
                'confidence': step.confidence,
                'reason': step.reason,
            }
        
        # ── Bias Detection ──
        
        # Bias 1: Low-trust engine still chosen
        if engine_trust < self.LOW_TRUST_THRESHOLD and engine_used:
            report.bias_flags.append(
                f'ENGINE_BIAS: {engine_used} chosen despite trust={engine_trust:.2f}')
        
        # Bias 2: Safety warnings ignored
        if safety_warnings and approval_status != 'BLOCK':
            report.bias_flags.append(
                f'SAFETY_OVERRIDE: {len(safety_warnings)} warnings present, but not BLOCKED')
        
        # Bias 3: Skeptic wanted review, but not flagged
        if skeptic_risk > 0.15 and 'REQUEST_MORE' not in str(report.decision_trace):
            report.bias_flags.append(
                f'SKEPTIC_OVERRIDE: risk={skeptic_risk:.2f} but no REQUEST_MORE')
        
        # Bias 4: Unknown bug type treated too aggressively
        if bug_type == 'Unknown' and engine_used:
            report.bias_flags.append(
                'UNKNOWN_BUG_RISK: engine called despite unknown bug type')
        
        # ── Contradiction Detection ──
        
        decisions = [s.decision for s in report.decision_trace]
        if 'BLOCK' in decisions and 'APPROVE' in decisions:
            report.contradiction_flags.append(
                'CONTRADICTION: BLOCK and APPROVE in same run')
        
        if 'WARN' in decisions and engine_used:
            report.contradiction_flags.append(
                'RISKY_EXECUTION: WARNING present but engine still called')
        
        # ── Confidence Calibration Audit ──
        
        if test_passed is not None:
            avg_conf = sum(s.confidence for s in report.decision_trace) / max(1, len(report.decision_trace))
            
            if avg_conf > self.OVERCONFIDENCE_THRESHOLD and not test_passed:
                report.confidence_audit['overconfidence'] = f'Confidence {avg_conf:.0%} but test FAILED'
            elif avg_conf < self.UNDERCONFIDENCE_THRESHOLD and test_passed:
                report.confidence_audit['underconfidence'] = f'Confidence {avg_conf:.0%} but test PASSED'
            else:
                report.confidence_audit['calibration'] = 'ok'
        
        # ── Root Cause Gap Detection ──
        
        if root_cause and root_cause_repeat >= 3:
            report.bias_flags.append(
                f'ROOT_CAUSE_REPEAT: {root_cause} seen {root_cause_repeat}x, no skill generated')
        
        # ── Uncertainty Score ──
        
        uncertainty_factors = 0
        if not report.decision_trace:
            uncertainty_factors += 1
        if bug_type == 'Unknown':
            uncertainty_factors += 1
        if engine_trust < 0.20:
            uncertainty_factors += 1
        if report.contradiction_flags:
            uncertainty_factors += len(report.contradiction_flags)
        
        report.uncertainty_score = min(1.0, uncertainty_factors * 0.20)
        
        # ── Requires Review ──
        
        if (report.contradiction_flags or 
            len(report.bias_flags) >= 2 or
            report.confidence_audit.get('overconfidence')):
            report.requires_review = True
        
        # ── Final Explanation ──
        
        parts = []
        if report.decision_trace:
            parts.append('Decision flow:')
            for s in report.decision_trace:
                parts.append(f'  {s.module}: {s.decision} ({s.confidence:.0%}) — {s.reason[:80]}')
        if report.bias_flags:
            parts.append('Bias detected:')
            for b in report.bias_flags:
                parts.append(f'  ⚠️ {b}')
        if report.contradiction_flags:
            parts.append('Contradictions:')
            for c in report.contradiction_flags:
                parts.append(f'  ❌ {c}')
        if report.confidence_audit:
            parts.append(f'Calibration: {report.confidence_audit}')
        parts.append(f'Uncertainty: {report.uncertainty_score:.0%}')
        parts.append(f'Review needed: {"YES" if report.requires_review else "no"}')
        
        report.final_explanation = '\n'.join(parts)
        
        return report


# ═══════════ SELF-TEST ═══════════
if __name__ == "__main__":
    brain = SelfObservationBrain()
    passed = 0
    
    tests = [
        # T1: Normal run with explanation
        ("T1: Normal explanation", 
         [DecisionStep("ReflexLayer", "ALLOW", 0.95, "No danger"),
          DecisionStep("Classifier", "GO", 0.85, "NullPointer detected")],
         dict(bug_type="NullPointer", engine_used="opencode", engine_trust=0.80,
              test_passed=True), "Normal"),
        
        # T2: Low trust + engine chosen = bias
        ("T2: Engine bias",
         [DecisionStep("EngineRouter", "GO", 0.70, "Routing to opencode")],
         dict(engine_trust=0.05, engine_used="opencode"), "EngineBias"),
        
        # T3: Safety warnings ignored
        ("T3: Safety override",
         [DecisionStep("SafetyBrain", "WARN", 0.90, "Dangerous pattern")],
         dict(safety_warnings=["drop table"], approval_status="APPROVE"), "SafetyOverride"),
        
        # T4: Overconfidence
        ("T4: Overconfidence",
         [DecisionStep("Classifier", "GO", 0.95, "NullPointer"),
          DecisionStep("EngineRouter", "GO", 0.90, "OpenCode")],
         dict(test_passed=False), "Overconfidence"),
        
        # T5: Unknown bug + engine = bias
        ("T5: Unknown risk",
         [DecisionStep("Classifier", "GO", 0.30, "Unknown bug")],
         dict(bug_type="Unknown", engine_used="opencode"), "UnknownBias"),
        
        # T6: Contradiction BLOCK + APPROVE
        ("T6: Contradiction",
         [DecisionStep("SafetyBrain", "BLOCK", 1.0, "DROP TABLE"),
          DecisionStep("ApprovalGate", "APPROVE", 0.50, "Human approved")],
         dict(), "Contradiction"),
        
        # T7: No crash on empty
        ("T7: Empty trace",
         [], dict(), "Empty"),
    ]
    
    print("SELF-OBSERVATION BRAIN — Self-Test")
    print("=" * 55)
    
    for name, trace, params, expected_flag in tests:
        r = brain.observe(decision_trace=trace, **params)
        
        flags = []
        if r.bias_flags: flags.append('Bias')
        if r.contradiction_flags: flags.append('Contradiction')
        if r.confidence_audit.get('overconfidence'): flags.append('Overconfidence')
        if r.requires_review: flags.append('Review')
        
        ok = False
        if expected_flag == 'Normal' and not flags and r.final_explanation:
            ok = True
        elif expected_flag == 'EngineBias' and 'ENGINE_BIAS' in str(r.bias_flags):
            ok = True
        elif expected_flag == 'SafetyOverride' and 'SAFETY_OVERRIDE' in str(r.bias_flags):
            ok = True
        elif expected_flag == 'Overconfidence' and r.confidence_audit.get('overconfidence'):
            ok = True
        elif expected_flag == 'UnknownBias' and 'UNKNOWN_BUG_RISK' in str(r.bias_flags):
            ok = True
        elif expected_flag == 'Contradiction' and r.contradiction_flags:
            ok = True
        elif expected_flag == 'Empty':
            ok = True
        
        if ok: passed += 1
        print(f"  {'✅' if ok else '❌'} {name:<22s} flags={flags} explanation={len(r.final_explanation)} chars")
    
    print(f"\n  ERGEBNIS: {passed}/{len(tests)} Tests")
    print(f"  {'✅ SELF-OBSERVATION BRAIN FERTIG' if passed >= 5 else '⚠️'}")
