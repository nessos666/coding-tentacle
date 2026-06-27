"""
REFLECTION BRAIN — RC84
Meta-learning: analyzes WHY a repair succeeded or failed.
Detects patterns: wrong engine, bad prompt, hallucination, budget.
Generates PREFER/AVOID rules, prompt improvements, strategy adjustments.
"""
from dataclasses import dataclass, field


@dataclass
class ReflectionInput:
    bug_mode: str = 'UNKNOWN'
    root_cause: str = 'UNKNOWN'
    engine: str = ''
    prompt: str = ''
    patch: str = ''
    tests_before: int = 0
    tests_after: int = 0
    safety_result: str = 'CLEAN'
    tournament_score: float = 0.0
    human_review: str = 'PENDING'  # APPROVED / REJECTED / CHANGES_REQUESTED
    duration_s: float = 0.0
    cost: float = 0.0
    evidence_complete: bool = False


@dataclass
class ReflectionResult:
    success_reason: str = ''
    failure_reason: str = ''
    confidence_adjustment: float = 0.0
    engine_adjustment: str = ''
    prompt_adjustment: str = ''
    strategy_adjustment: str = ''
    reusable_lesson: str = ''
    recommended_rule: str = ''
    recommended_skill: str = ''
    severity: str = 'INFO'  # INFO / WARNING / CRITICAL
    confidence: float = 0.0


class ReflectionBrain:
    """Analyzes why a repair succeeded or failed. Meta-learning."""
    
    SUCCESS_PATTERNS = {
        'small_patch': {
            'condition': lambda ri: len(ri.patch) < 200 and ri.tests_after > ri.tests_before,
            'reason': 'Small, focused patch fixed the issue — good precision',
            'rule': 'PREFER small targeted patches over large rewrites',
        },
        'fast_repair': {
            'condition': lambda ri: ri.duration_s < 15 and ri.tests_after > ri.tests_before,
            'reason': 'Quick repair — engine and approach were efficient',
            'rule': 'PREFER {engine} for {bug_mode} bugs',
        },
        'clean_safety': {
            'condition': lambda ri: ri.safety_result == 'CLEAN' and ri.tests_after > ri.tests_before,
            'reason': 'Safety-clean patch that fixes the bug — ideal outcome',
            'rule': '',
        },
    }
    
    FAILURE_PATTERNS = {
        'hallucination': {
            'condition': lambda ri: len(ri.patch) > 1000 and ri.tests_after <= ri.tests_before,
            'reason': 'Large patch with no improvement — likely hallucination',
            'rule': 'AVOID large untargeted patches from {engine}',
            'severity': 'CRITICAL',
        },
        'too_small': {
            'condition': lambda ri: 0 < len(ri.patch) < 10 and ri.tests_after <= ri.tests_before,
            'reason': 'Patch too small to fix anything — insufficient repair attempt',
            'rule': 'REQUEST_MORE when patch < 10 bytes',
            'severity': 'WARNING',
        },
        'safety_blocked': {
            'condition': lambda ri: ri.safety_result in ('BLOCKED', 'BLOCK'),
            'reason': 'Safety system blocked the repair — patch contained dangerous patterns',
            'rule': 'AVOID generating patches with dangerous code (eval, exec, shell)',
            'severity': 'CRITICAL',
        },
        'budget_exhausted': {
            'condition': lambda ri: ri.cost > 0.50 or ri.duration_s > 60,
            'reason': 'Repair consumed too many resources — budget exceeded',
            'rule': 'SET max_tokens=2000 for {engine} on {bug_mode}',
            'severity': 'WARNING',
        },
        'human_rejected': {
            'condition': lambda ri: ri.human_review == 'REJECTED',
            'reason': 'Patch rejected by human reviewer — quality or safety concern',
            'rule': 'REQUEST_MORE evidence before submitting to human review',
            'severity': 'WARNING',
        },
        'wrong_engine': {
            'condition': lambda ri: ri.tournament_score < 0.30 and ri.tests_after <= ri.tests_before,
            'reason': 'Low tournament score with no test improvement — wrong engine for this bug',
            'rule': 'AVOID {engine} for {bug_mode} bugs',
            'severity': 'WARNING',
        },
        'wrong_root_cause': {
            'condition': lambda ri: ri.root_cause == 'UNKNOWN_ROOT_CAUSE' and ri.tests_after <= ri.tests_before,
            'reason': 'Wrong root cause diagnosis led to ineffective repair',
            'rule': 'REQUEST_MORE context when root cause is unknown',
            'severity': 'WARNING',
        },
        'timeout': {
            'condition': lambda ri: ri.duration_s > 30 and ri.tests_after <= ri.tests_before,
            'reason': 'Repair timed out — engine took too long with no result',
            'rule': 'SET max_seconds=20 for {engine}',
            'severity': 'WARNING',
        },
    }
    
    def reflect(self, ri: ReflectionInput) -> ReflectionResult:
        """Analyze a repair attempt and produce meta-learning."""
        result = ReflectionResult()
        
        repair_succeeded = ri.tests_after > ri.tests_before
        
        if repair_succeeded:
            result = self._analyze_success(ri)
        else:
            result = self._analyze_failure(ri)
        
        # Generate engine-specific adjustments
        if ri.engine:
            result.engine_adjustment = self._engine_guidance(ri)
            result.prompt_adjustment = self._prompt_guidance(ri)
            result.strategy_adjustment = self._strategy_guidance(ri)
        
        # Confidence adjustments
        result.confidence_adjustment = self._confidence_delta(ri, repair_succeeded)
        result.confidence = min(0.95, 0.5 + 0.1 * len(result.recommended_rule))
        
        return result
    
    def _analyze_success(self, ri: ReflectionInput) -> ReflectionResult:
        """Determine WHY repair succeeded."""
        result = ReflectionResult()
        reasons = []
        rules = []
        
        for name, pattern in self.SUCCESS_PATTERNS.items():
            if pattern['condition'](ri):
                reasons.append(pattern['reason'])
                if pattern['rule']:
                    rules.append(
                        pattern['rule'].format(
                            engine=ri.engine, bug_mode=ri.bug_mode,
                            root_cause=ri.root_cause
                        )
                    )
        
        if reasons:
            result.success_reason = '; '.join(reasons)
            result.recommended_rule = '; '.join(rules)
            result.reusable_lesson = f'For {ri.bug_mode} bugs with {ri.root_cause}: {reasons[0]}'
            result.severity = 'INFO'
        else:
            # Implicit success — no clear pattern
            result.success_reason = f'Repair succeeded ({ri.tests_after - ri.tests_before} tests fixed)'
            result.reusable_lesson = f'Engine {ri.engine} can fix {ri.bug_mode} via {ri.root_cause}'
            result.severity = 'INFO'
        
        return result
    
    def _analyze_failure(self, ri: ReflectionInput) -> ReflectionResult:
        """Determine WHY repair failed."""
        result = ReflectionResult()
        reasons = []
        rules = []
        severity = 'INFO'
        
        for name, pattern in self.FAILURE_PATTERNS.items():
            if pattern['condition'](ri):
                reasons.append(f'[{name}] {pattern["reason"]}')
                if pattern['rule']:
                    rules.append(
                        pattern['rule'].format(
                            engine=ri.engine, bug_mode=ri.bug_mode,
                            root_cause=ri.root_cause
                        )
                    )
                if pattern.get('severity', 'INFO') == 'CRITICAL':
                    severity = 'CRITICAL'
                elif pattern.get('severity') == 'WARNING' and severity != 'CRITICAL':
                    severity = 'WARNING'
        
        if reasons:
            result.failure_reason = ' | '.join(reasons)
            result.recommended_rule = ' | '.join(rules)
            result.reusable_lesson = f'For {ri.bug_mode}: {reasons[0]}'
            result.severity = severity
        else:
            result.failure_reason = 'Unknown failure — no pattern matched'
            result.severity = 'WARNING'
        
        return result
    
    def _engine_guidance(self, ri: ReflectionInput) -> str:
        """Suggest engine adjustments."""
        if ri.tests_after > ri.tests_before:
            return f'PREFER {ri.engine} for {ri.bug_mode}'
        elif ri.tournament_score < 0.30:
            return f'AVOID {ri.engine} for {ri.bug_mode} — try alternative'
        return ''
    
    def _prompt_guidance(self, ri: ReflectionInput) -> str:
        """Suggest prompt improvements."""
        if ri.tests_after <= ri.tests_before:
            if ri.root_cause == 'UNKNOWN_ROOT_CAUSE':
                return 'ADD more context about error message and affected files'
            if len(ri.patch) > 1000:
                return 'REQUEST smaller, more focused patch (limit to 200 chars)'
            if ri.duration_s > 30:
                return 'ADD time limit instruction to prompt'
        return ''
    
    def _strategy_guidance(self, ri: ReflectionInput) -> str:
        """Suggest strategy changes."""
        if ri.safety_result in ('BLOCKED', 'BLOCK'):
            return 'SWITCH to template-based repair — LLM generated dangerous code'
        if ri.human_review == 'REJECTED':
            return 'REQUEST_MORE evidence before resubmitting'
        return ''
    
    def _confidence_delta(self, ri: ReflectionInput, succeeded: bool) -> float:
        """Calculate confidence adjustment for engine learning."""
        if succeeded:
            return min(0.05, 0.02 * (ri.tests_after - ri.tests_before))
        else:
            return -0.05 if ri.tests_after == ri.tests_before else -0.02


# Self-test
if __name__ == "__main__":
    brain = ReflectionBrain()
    passed = 0
    
    print("REFLECTION BRAIN — Self-Test")
    print("=" * 55)
    
    tests = [
        # (name, input, expected_reason_contains, is_success)
        ("T1: Successful small patch",
         ReflectionInput(bug_mode='EXCEPTION', root_cause='MISSING_GUARD', engine='opencode',
                        patch='if x is None: return', tests_before=0, tests_after=1,
                        safety_result='CLEAN', duration_s=8),
         'small', True),
        ("T2: Failed hallucination",
         ReflectionInput(bug_mode='ALGORITHMIC', root_cause='UNKNOWN_ROOT_CAUSE', engine='ollama',
                        patch='x' * 2000, tests_before=2, tests_after=2,
                        safety_result='CLEAN', duration_s=45),
         'hallucination', False),
        ("T3: Safety blocked",
         ReflectionInput(bug_mode='SECURITY', engine='opencode', patch='eval(user)',
                        safety_result='BLOCKED'),
         'Safety', False),
        ("T4: Human rejected",
         ReflectionInput(bug_mode='EXCEPTION', engine='opencode', patch='fix',
                        tests_before=0, tests_after=0, human_review='REJECTED'),
         'rejected', False),
        ("T5: Wrong engine",
         ReflectionInput(bug_mode='ALGORITHMIC', engine='ollama', patch='fix',
                        tests_before=1, tests_after=1, tournament_score=0.15),
         'wrong_engine', False),
        ("T6: Too small patch",
         ReflectionInput(bug_mode='EXCEPTION', engine='opencode', patch='x',
                        tests_before=1, tests_after=1),
         'too_small', False),
        ("T7: Timeout",
         ReflectionInput(bug_mode='EXCEPTION', engine='opencode', patch='fix',
                        tests_before=1, tests_after=1, duration_s=45),
         'timeout', False),
        ("T8: Success generates rules",
         ReflectionInput(bug_mode='EXCEPTION', root_cause='MISSING_GUARD', engine='opencode',
                        patch='if x: return x', tests_before=0, tests_after=2,
                        safety_result='CLEAN', duration_s=5),
         'PREFER', True),
    ]
    
    for name, ri, expected, success in tests:
        r = brain.reflect(ri)
        if success:
            ok = expected.lower() in r.success_reason.lower() or expected in str(r.recommended_rule)
        else:
            ok = expected.lower() in r.failure_reason.lower() or expected in r.recommended_rule.lower()
        
        if ok: passed += 1
        print(f"  {'✅' if ok else '❌'} {name:<25s} "
              f"{'SUCCESS:' + r.success_reason[:50] if success else 'FAIL:' + r.failure_reason[:50]}")
    
    print(f"\n  ERGEBNIS: {passed}/{len(tests)} Tests")
    print(f"  {'✅ REFLECTION BRAIN FERTIG' if passed >= 6 else '⚠️'}")
