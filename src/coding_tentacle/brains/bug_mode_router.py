"""
BUG MODE ROUTER — RC71
Classifies bugs into operational MODES and routes to appropriate subsystem.
Modes: EXCEPTION, SECURITY, ALGORITHMIC, REPO, UNKNOWN
"""
import re
from dataclasses import dataclass, field


@dataclass
class ModeDecision:
    mode: str = 'UNKNOWN'  # EXCEPTION / SECURITY / ALGORITHMIC / REPO / UNKNOWN
    confidence: float = 0.0
    signals: list = field(default_factory=list)
    recommended_pipeline: str = ''
    external_tools: list = field(default_factory=list)
    missing_context: list = field(default_factory=list)
    context_questions: list = field(default_factory=list)
    explanation: str = ''


class BugModeRouter:
    """Routes bugs to the right subsystem based on their operational MODE."""
    
    MODE_SIGNALS = {
        'EXCEPTION': {
            'patterns': [
                r'Traceback\s*\(most recent call last\)',
                r'File\s+"[^"]+",\s*line\s+\d+',
                r'(?:TypeError|ValueError|ImportError|KeyError|IndexError|'
                r'NullPointer|AttributeError|NameError|SyntaxError|'
                r'FileNotFoundError|PermissionError|RuntimeError|'
                r'ConnectionError|TimeoutError|MemoryError|RecursionError)',
                r'\w+Error\s*:', r'\w+Exception\s*:',
                r'has no attribute', r'cannot import', r'no module named',
                r'NoneType', r'unsupported operand',
            ],
            'pipeline': 'Classifier → RootCause → PatchEngine → Safety',
            'external_tools': [],
            'description': 'Stacktrace or error message present',
        },
        'SECURITY': {
            'patterns': [
                r'eval\s*\(', r'exec\s*\(', r'compile\s*\(',
                r'os\.system\s*\(', r'subprocess', r'shell\s*=\s*True',
                r'pickle', r'marshal', r'__import__\s*\(',
                r'DROP\s+TABLE', r'DELETE\s+FROM',
                r'rm\s+-rf', r'sudo\s+rm',
                r'api_key', r'secret', r'password\s*=',
                r'SQL\s+injection', r'XSS', r'CSRF',
            ],
            'pipeline': 'ASTSafety → Semgrep → Bandit → VETO',
            'external_tools': ['semgrep', 'bandit'],
            'description': 'Dangerous code patterns detected',
        },
        'ALGORITHMIC': {
            'patterns': [
                r'AssertionError', r'assert\s+\w+\s*==',
                r'expected\s+.*\s+but\s+got', r'actual\s+.*\s+expected',
                r'test.*fail', r'FAILED', r'assertEqual',
                r'Test\s+Failure', r'wrong\s+output',
                r'incorrect\s+result', r'expected.*found',
            ],
            'pipeline': 'TestAnalyzer → LLM Repair → Patch Tournament',
            'external_tools': ['pytest', 'hypothesis'],
            'description': 'Tests fail but no exception/stacktrace',
        },
        'REPO': {
            'patterns': [
                r'github\.com/[\w.-]+/[\w.-]+/issues?/\d+',
                r'#\d{1,6}\b', r'PR\s*#\d+', r'issue\s*#\d+',
                r'multi[-\s]file', r'several\s+files',
                r'merge\s+request', r'pull\s+request',
            ],
            'pipeline': 'ProjectMap → SpatialMem → External Agent → Evidence',
            'external_tools': ['opencode', 'claude-code'],
            'description': 'GitHub issue or multi-file repository bug',
        },
    }
    
    def route(self, bug_report: str, code_context: str = '') -> ModeDecision:
        """Classify bug by operational mode and route to subsystem."""
        report = ModeDecision()
        text = (bug_report + ' ' + code_context).lower()
        original = bug_report + ' ' + code_context
        
        scores = {}
        all_signals = []
        
        for mode, config in self.MODE_SIGNALS.items():
            mode_score = 0.0
            matched = []
            
            for pattern in config['patterns']:
                if re.search(pattern, original, re.IGNORECASE):
                    mode_score += 1.0
                    matched.append(pattern[:60])
            
            if matched:
                scores[mode] = min(1.0, mode_score / max(1, len(config['patterns']) * 0.3))
                all_signals.extend([f'{mode}: {m}' for m in matched[:3]])
        
        if not scores:
            # RC72: Check if test failure (algorithmic candidate)
            try:
                from coding_tentacle.analyzers.test_failure_analyzer import TestFailureAnalyzer
                tfa = TestFailureAnalyzer()
                tfa_result = tfa.analyze(test_output=original, bug_report=bug_report)
                if tfa_result.is_algorithmic_candidate:
                    report.mode = 'ALGORITHMIC'
                    report.confidence = tfa_result.confidence
                    report.signals = [f'ALGORITHMIC: {tfa_result.assertion_type}']
                    report.recommended_pipeline = 'TestAnalyzer → LLM Repair → Patch Tournament'
                    report.external_tools = ['pytest']
                    report.explanation = tfa_result.explanation
                    return report
            except:
                pass
            
            # RC81: Issue Understanding Brain — break down UNKNOWN
            try:
                from coding_tentacle.brains.issue_understanding_brain import IssueUnderstandingBrain
                iub = IssueUnderstandingBrain()
                issue_result = iub.analyze(issue_text=original, issue_title=bug_report[:100])
                if issue_result.issue_type != 'UNKNOWN':
                    # RC82: Context Acquisition — what's missing?
                    context_info = ''
                    try:
                        from coding_tentacle.brains.context_acquisition_brain import ContextAcquisitionBrain
                        cab = ContextAcquisitionBrain()
                        ctx = cab.acquire(issue_result.issue_type, issue_result.recommended_bug_mode,
                                        has_stacktrace=issue_result.has_stacktrace,
                                        has_reproduction=issue_result.has_reproduction,
                                        has_test_output=issue_result.has_test_output,
                                        has_code_reference=issue_result.has_code_reference)
                        if ctx.missing_items:
                            context_info = f' | Context needed: {", ".join(ctx.missing_items[:3])}'
                            report.missing_context = ctx.missing_items
                        if ctx.priority_questions:
                            report.context_questions = ctx.priority_questions
                    except:
                        pass
                    
                    report.mode = f'ISSUE:{issue_result.issue_type}'
                    report.confidence = issue_result.confidence
                    report.signals = issue_result.reasoning
                    report.recommended_pipeline = issue_result.next_action
                    report.explanation = issue_result.ISSUE_TYPES[issue_result.issue_type]['description'] if issue_result.issue_type in issue_result.ISSUE_TYPES else ''
                    if issue_result.missing_information:
                        report.explanation += f' | Missing: {", ".join(issue_result.missing_information)}'
                    if context_info:
                        report.explanation += context_info
                    return report
            except:
                pass
            report.confidence = 0.0
            report.recommended_pipeline = 'Human Triage Required'
            report.explanation = 'No recognizable bug pattern — human review needed'
            return report
        
        # Priority: SECURITY > EXCEPTION > ALGORITHMIC > REPO
        priority = ['SECURITY', 'EXCEPTION', 'ALGORITHMIC', 'REPO']
        best_mode = None
        for p in priority:
            if p in scores:
                best_mode = p
                break
        
        config = self.MODE_SIGNALS[best_mode]
        report.mode = best_mode
        report.confidence = round(min(0.95, scores[best_mode]), 2)
        report.signals = all_signals[:5]
        report.recommended_pipeline = config['pipeline']
        report.external_tools = config['external_tools']
        report.explanation = config['description']
        
        return report


# ═══════════ SELF-TEST ═══════════
if __name__ == "__main__":
    router = BugModeRouter()
    passed = 0
    
    print("BUG MODE ROUTER — Self-Test")
    print("=" * 55)
    
    tests = [
        # (name, bug_report, expected_mode)
        ("T1: NullPointer", "Traceback:\n  File views.py:42\nNullPointer: NoneType has no attribute", "EXCEPTION"),
        ("T2: eval injection", "eval(user_input) in login handler — security risk", "SECURITY"),
        ("T3: os.system", "os.system('rm -rf ' + user_path) — dangerous", "SECURITY"),
        ("T4: Test failure", "AssertionError: expected 42 but got 0 — test_foo.py:15", "ALGORITHMIC"),
        ("T5: Wrong output", "FAILED test_calculate — expected 100 but got None", "ALGORITHMIC"),
        ("T6: GitHub issue", "#42: Multiple files broken after refactor", "REPO"),
        ("T7: TypeError", "TypeError: cannot concatenate str and int in calc.py:10", "EXCEPTION"),
        ("T8: Unknown", "something strange happened, no idea what", "UNKNOWN"),
        ("T9: Security+Exception", "Traceback... File auth.py:10 — eval(user_input) crashed", "SECURITY"),
        ("T10: pickle", "pickle.loads(user_data) in deserialize.py", "SECURITY"),
        ("T11: ImportError", "ImportError: cannot import url_quote from werkzeug\n  File config.py:5", "EXCEPTION"),
        ("T12: Empty", "", "UNKNOWN"),
    ]
    
    for name, bug_report, expected_mode in tests:
        r = router.route(bug_report)
        ok = r.mode == expected_mode
        if ok: passed += 1
        print(f"  {'✅' if ok else '❌'} {name:<25s} → {r.mode:<12s} conf={r.confidence:.2f} (expected {expected_mode})")
    
    print(f"\n  ERGEBNIS: {passed}/{len(tests)} Tests")
    print(f"  {'✅ BUG MODE ROUTER FERTIG' if passed >= 10 else '⚠️'}")
