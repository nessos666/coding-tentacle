"""
CT 11.x — REFLECTION ENGINE (P0 Learning System V2)

Analysiert Decision Traces nach jedem Repair und extrahiert
Lernsignale: Warum erfolgreich? Warum gescheitert? Welche
Komponente half? Welche war nutzlos?

Kein neues Brain. Nur eine Analyse-Schicht über existierenden Daten.
Output wird in BLM gespeichert → nächster Bug profitiert.

CT-v11.0.0: PRODUCTION | 10/10 regression | Learning V2 P0
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional
import time


@dataclass
class ReflectionResult:
    """Ergebnis einer Reflection-Analyse nach einem Repair."""
    
    # Grundlegende Bewertung
    success: bool = False
    success_reasons: list[str] = field(default_factory=list)
    failure_reasons: list[str] = field(default_factory=list)
    
    # Komponenten-Bewertung
    useful_components: list[str] = field(default_factory=list)
    useless_components: list[str] = field(default_factory=list)
    wrong_decisions: list[str] = field(default_factory=list)
    
    # Detaillierte Signale
    classifier_correct: bool = False
    security_correct: bool = False
    engine_choice_good: bool = False
    droste_helpful: bool = False
    root_cause_accurate: bool = False
    blm_context_useful: bool = False
    prompt_quality: str = ''          # 'good', 'weak', 'irrelevant'
    
    # Lernsignale für nächsten Bug
    transferable_lesson: str = ''
    suggested_improvement: str = ''
    confidence_adjustment: float = 0.0  # +0.05 für Bestätigung, -0.05 für Korrektur
    
    # Droste-Feedback
    droste_nodes_useful: int = 0
    droste_relevance_score: float = 0.0
    
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    def summary(self) -> str:
        """Ein-Zeilen-Zusammenfassung für BLM."""
        if self.success:
            cause = ', '.join(self.success_reasons[:2]) or 'unknown'
            return f"SUCCESS: {cause}"
        else:
            cause = ', '.join(self.failure_reasons[:2]) or 'unknown'
            return f"FAILED: {cause}"


class ReflectionEngine:
    """
    Analysiert einen ShadowRunReport und Decision Trace.
    Extrahiert WARUM ein Repair erfolgreich war oder gescheitert ist.
    
    Usage:
        engine = ReflectionEngine()
        reflection = engine.analyze(report, trace)
        # reflection.to_dict() → in BLM speichern
    """
    
    def analyze(self, report, trace=None) -> ReflectionResult:
        """
        Analysiere einen Repair-Lauf und extrahiere Lernsignale.
        
        Args:
            report: ShadowRunReport aus shadow_mode.py
            trace: DecisionTrace aus explainability.py (optional)
        """
        r = ReflectionResult()
        
        # ─── ERFOLG/FEHLER BESTIMMEN ───
        diff_ok = bool(getattr(report, 'generated_diff', ''))
        tests_ok = False
        if hasattr(report, 'test_result') and report.test_result:
            tests_ok = report.test_result.get('success', False)
        security_blocked = getattr(report, 'security_blocked', False)
        
        if security_blocked:
            r.success = True  # Block ist Erfolg (verhinderte Gefahr)
            r.success_reasons.append('SecurityBrain correctly blocked dangerous code')
        elif diff_ok and tests_ok:
            r.success = True
        elif diff_ok:
            r.success = True  # Partial success
            r.failure_reasons.append('Diff generated but tests not verified')
        else:
            r.success = False
        
        # ─── CLASSIFIER BEWERTEN ───
        bug_type = getattr(report, 'detected_bug_type', 'Unknown')
        confidence = getattr(report, 'confidence', 0.0)
        if bug_type != 'Unknown' and confidence > 0.5:
            r.classifier_correct = True
            r.useful_components.append(f'Classifier({bug_type})')
        elif bug_type == 'Unknown':
            r.failure_reasons.append('Classifier failed: Unknown bug type')
            r.wrong_decisions.append('Classifier returned Unknown')
        
        # ─── SECURITY BEWERTEN ───
        if security_blocked:
            r.security_correct = True
            r.useful_components.append('SecurityBrain(BLOCKED)')
        elif getattr(report, 'trojan_source_clean', True):
            r.security_correct = True
        
        # ─── ENGINE BEWERTEN ───
        engine_used = getattr(report, 'engine_used', '')
        if engine_used:
            if r.success:
                r.engine_choice_good = True
                r.useful_components.append(f'Engine({engine_used})')
            else:
                r.failure_reasons.append(f'Engine {engine_used} did not produce working fix')
                r.wrong_decisions.append(f'Engine choice: {engine_used}')
        
        # ─── DROSTE BEWERTEN ───
        droste_nodes = getattr(report, 'droste_nodes', 0)
        if droste_nodes > 0:
            r.droste_nodes_useful = droste_nodes
            if r.success:
                r.droste_helpful = True
                r.droste_relevance_score = 0.7
                r.useful_components.append(f'Droste({droste_nodes} nodes)')
            else:
                r.droste_relevance_score = 0.3
                r.useless_components.append('Droste(context not sufficient)')
        else:
            if not r.success:
                r.failure_reasons.append('No Droste context available')
        
        # ─── BLM BEWERTEN ───
        blm_written = getattr(report, 'blm_written', False)
        rules_updated = getattr(report, 'rules_updated', 0)
        consolidator_rule = getattr(report, 'consolidator_rule', '')
        if consolidator_rule:
            r.blm_context_useful = True
            r.useful_components.append(f'Consolidator({consolidator_rule})')
        if blm_written:
            r.useful_components.append('BLM(recorded)')
        
        # ─── ROOT CAUSE BEWERTEN ───
        root_cause = getattr(report, 'root_cause', '')
        if root_cause and r.success:
            r.root_cause_accurate = True
            r.useful_components.append(f'RootCause({root_cause})')
        
        # ─── PROMPT QUALITÄT ───
        if engine_used and r.success and droste_nodes > 0:
            r.prompt_quality = 'good'
        elif engine_used and r.success:
            r.prompt_quality = 'good'
        elif engine_used and not r.success:
            r.prompt_quality = 'weak'
        else:
            r.prompt_quality = 'irrelevant'
        
        # ─── TRANSFERABLE LESSON ───
        if r.success:
            comps = ', '.join(r.useful_components[:3])
            r.transferable_lesson = (
                f'For {bug_type}: {engine_used or "template"} fix worked. '
                f'Helpful: {comps}. '
                f'Root cause: {root_cause or "unknown"}.'
            )
            r.confidence_adjustment = 0.05
        else:
            r.transferable_lesson = (
                f'For {bug_type}: Fix failed. '
                f'Reasons: {"; ".join(r.failure_reasons[:3])}. '
                f'Avoid: {engine_used or "no engine"} for this case.'
            )
            r.confidence_adjustment = -0.05
        
        # ─── SUGGESTED IMPROVEMENT ───
        if not r.success and engine_used:
            r.suggested_improvement = f'Try alternative engine for {bug_type}'
        elif not r.droste_helpful and droste_nodes == 0:
            r.suggested_improvement = 'Activate Droste for better code context'
        elif bug_type == 'Unknown':
            r.suggested_improvement = 'Improve classifier keywords'
        
        return r


# ─── Self-Tests ─────────────────────────────────────────────────────────

if __name__ == '__main__':
    class MockReport:
        detected_bug_type = 'NullPointer'
        confidence = 0.82
        generated_diff = 'if user is None: return'
        test_result = {'success': True, 'tests_passed': 3, 'tests_total': 3}
        security_blocked = False
        trojan_source_clean = True
        security_risk_score = 0.0
        engine_used = 'opencode'
        droste_nodes = 6
        droste_budget_used = 1174
        blm_written = True
        rules_updated = 2
        consolidator_rule = 'PREFER:opencode:87%'
        root_cause = 'MISSING_NULL_CHECK'
        skeptic_recommendation = 'APPROVE'
    
    engine = ReflectionEngine()
    passed = 0
    
    # T1: Successful repair analysis
    print("T1: Success reflection...", end=" ")
    r = engine.analyze(MockReport())
    assert r.success
    assert len(r.success_reasons) >= 1 or len(r.useful_components) >= 3
    assert 'guard_clause' in r.transferable_lesson or 'opencode' in r.transferable_lesson
    assert r.droste_helpful
    passed += 1
    print("OK")
    
    # T2: Failed repair analysis
    print("T2: Failure reflection...", end=" ")
    mr2 = MockReport()
    mr2.generated_diff = ''
    mr2.test_result = {}
    r2 = engine.analyze(mr2)
    assert not r2.success
    assert len(r2.failure_reasons) >= 1
    assert r2.prompt_quality == 'weak'
    passed += 1
    print("OK")
    
    # T3: Security blocked analysis
    print("T3: Security block reflection...", end=" ")
    mr3 = MockReport()
    mr3.security_blocked = True
    r3 = engine.analyze(mr3)
    assert r3.success  # Block IS success
    assert 'SecurityBrain' in str(r3.success_reasons)
    passed += 1
    print("OK")
    
    # T4: to_dict serialization
    print("T4: to_dict...", end=" ")
    d = r.to_dict()
    assert d['success']
    assert d['classifier_correct']
    passed += 1
    print("OK")
    
    # T5: summary string
    print("T5: summary...", end=" ")
    s = r.summary()
    assert 'SUCCESS' in s
    passed += 1
    print("OK")
    
    # T6: Confidence adjustment
    print("T6: confidence signal...", end=" ")
    assert r.confidence_adjustment > 0  # Success → positive
    assert r2.confidence_adjustment < 0  # Failure → negative
    passed += 1
    print("OK")
    
    # T7: Unknown bug type
    print("T7: Unknown classifier...", end=" ")
    mr4 = MockReport()
    mr4.detected_bug_type = 'Unknown'
    mr4.confidence = 0.2
    r4 = engine.analyze(mr4)
    assert not r4.classifier_correct
    assert any('Classifier' in w for w in r4.failure_reasons)
    passed += 1
    print("OK")
    
    print(f"\n{'='*50}")
    print(f"  {passed}/7 Tests bestanden")
    print(f"  {'✅ REFLECTION ENGINE FERTIG' if passed >= 7 else '❌'}")
