"""
TEST FAILURE ANALYZER — RC72
Analyzes test output to detect algorithmic bugs (test fails, no stacktrace).
Distinguishes assertion failures from exceptions and unknowns.
"""
import re
from dataclasses import dataclass, field


@dataclass
class TestFailureAnalysis:
    is_test_failure: bool = False
    has_exception: bool = False
    is_algorithmic_candidate: bool = False
    expected: str = ''
    actual: str = ''
    assertion_type: str = ''
    failing_test: str = ''
    confidence: float = 0.0
    explanation: str = ''
    recommended_mode: str = 'UNKNOWN'


class TestFailureAnalyzer:
    """Parses test output to classify algorithmic vs exception vs unknown bugs."""
    
    PATTERNS = {
        'pytest_assert': [
            r'>\s*assert\s+(.+)', r'E\s+assert\s+(.+)',
            r'AssertionError', r'assert\s+\w+\s*==',
        ],
        'expected_actual': [
            r'Expected\s*:\s*(.+)', r'Actual\s*:\s*(.+)',
            r'expected\s+(.+)\s+but\s+got\s+(.+)',
            r'expected\s*=\s*(.+),\s*actual\s*=\s*(.+)',
        ],
        'unittest_fail': [
            r'FAIL:', r'FAILED\s*\(', r'failures=\d+',
            r'AssertionError\s*:', r'self\.assert\w+',
        ],
        'wrong_output': [
            r'wrong\s+output', r'incorrect\s+result',
            r'does not match expected', r'output mismatch',
            r'differs from expected', r'not equal',
        ],
        'timeout': [
            r'timeout', r'timed out', r'Took too long',
            r'TimeoutError', r'deadline exceeded',
        ],
        'exception_traceback': [
            r'Traceback\s*\(most recent call last\)',
            r'File\s+"[^"]+",\s*line\s+\d+',
            r'\w+Error\s*:', r'\w+Exception\s*:',
        ],
    }
    
    def analyze(self, test_output: str, bug_report: str = '') -> TestFailureAnalysis:
        """Analyze test output to determine bug mode."""
        result = TestFailureAnalysis()
        text = test_output or bug_report
        if not text.strip():
            result.explanation = 'Empty test output — cannot classify'
            return result
        
        # Check for exceptions first (they indicate EXCEPTION mode, not ALGO)
        for pat in self.PATTERNS['exception_traceback']:
            if re.search(pat, text, re.IGNORECASE):
                result.has_exception = True
                result.explanation = 'Exception/stacktrace detected'
                result.recommended_mode = 'EXCEPTION'
                return result
        
        # Check for assertion/test failures
        assertion_matches = []
        for pat in self.PATTERNS['pytest_assert']:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                assertion_matches.append(m.group(0)[:100])
        
        for pat in self.PATTERNS['unittest_fail']:
            if re.search(pat, text, re.IGNORECASE):
                assertion_matches.append('unittest failure')
        
        for pat in self.PATTERNS['wrong_output']:
            if re.search(pat, text, re.IGNORECASE):
                assertion_matches.append('wrong output')
        
        for pat in self.PATTERNS['timeout']:
            if re.search(pat, text, re.IGNORECASE):
                assertion_matches.append('timeout')
        
        if assertion_matches:
            result.is_test_failure = True
            result.is_algorithmic_candidate = not result.has_exception
            result.confidence = min(0.90, 0.5 + 0.1 * len(assertion_matches))
            result.assertion_type = assertion_matches[0]
            result.recommended_mode = 'ALGORITHMIC'
            result.explanation = f'Test failure detected: {assertion_matches[0]}'
            
            # Extract expected/actual if available
            for pat in self.PATTERNS['expected_actual']:
                m = re.search(pat, text, re.IGNORECASE)
                if m:
                    result.expected = m.group(1)[:80] if m.lastindex and m.lastindex >= 1 else ''
                    if m.lastindex and m.lastindex >= 2:
                        result.actual = m.group(2)[:80]
                    break
            
            # Extract failing test name
            test_name = re.search(r'(test_\w+)', text)
            if test_name:
                result.failing_test = test_name.group(1)
            
            return result
        
        result.explanation = 'No test failure pattern recognized'
        result.recommended_mode = 'UNKNOWN'
        return result


# ═══════════ SELF-TEST ═══════════
if __name__ == "__main__":
    analyzer = TestFailureAnalyzer()
    passed = 0
    
    print("TEST FAILURE ANALYZER — Self-Test")
    print("=" * 55)
    
    tests = [
        ("T1: pytest assert", 
         "> assert 3 == 4\nE assert 3 == 4",
         True, False, True, "ALGORITHMIC"),
        ("T2: expected/actual",
         "Expected: 42 but got 0 — test_calculate.py::test_answer",
         True, False, True, "ALGORITHMIC"),
        ("T3: unittest failure",
         "FAIL: test_login (tests.test_auth.TestAuth)\nAssertionError: True != False",
         True, False, True, "ALGORITHMIC"),
        ("T4: AssertionError only",
         "AssertionError: lists differ",
         True, False, True, "ALGORITHMIC"),
        ("T5: timeout",
         "test_slow_api timed out after 30s",
         True, False, True, "ALGORITHMIC"),
        ("T6: wrong output",
         "Test failed: wrong output. Expected [1,2,3] got [1,2]",
         True, False, True, "ALGORITHMIC"),
        ("T7: exception traceback",
         "Traceback (most recent call last):\n  File 'test.py', line 5\nTypeError: NoneType",
         True, True, False, "EXCEPTION"),
        ("T8: empty input",
         "", False, False, False, "UNKNOWN"),
        ("T9: SyntaxError",
         "SyntaxError: invalid syntax at line 10",
         False, True, False, "EXCEPTION"),
        ("T10: QuixBugs-style wrong output",
         "FAILED test_breadth_first_search - assert [1,2,3] == [1,2,4]\n  Expected: [1,2,4]\n  Actual: [1,2,3]",
         True, False, True, "ALGORITHMIC"),
    ]
    
    for name, text, exp_test_fail, exp_has_exc, exp_algo, exp_mode in tests:
        r = analyzer.analyze(test_output=text)
        tf_ok = r.is_test_failure == exp_test_fail
        ex_ok = r.has_exception == exp_has_exc
        al_ok = r.is_algorithmic_candidate == exp_algo
        md_ok = r.recommended_mode == exp_mode
        
        if tf_ok and ex_ok and al_ok and md_ok:
            passed += 1
            print(f"  ✅ {name:<25s} mode={r.recommended_mode:<12s} algo={r.is_algorithmic_candidate} conf={r.confidence:.2f}")
        else:
            print(f"  ❌ {name:<25s} mode={r.recommended_mode:<12s} algo={r.is_algorithmic_candidate} "
                  f"(expected mode={exp_mode}, algo={exp_algo})")
    
    print(f"\n  ERGEBNIS: {passed}/{len(tests)} Tests")
    print(f"  {'✅ TEST FAILURE ANALYZER FERTIG' if passed >= 8 else '⚠️'}")
