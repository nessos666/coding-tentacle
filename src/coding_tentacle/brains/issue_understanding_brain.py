"""
ISSUE UNDERSTANDING BRAIN — RC81
Classifies GitHub issues into concrete types, not just UNKNOWN.
BUG · FEATURE_REQUEST · ENHANCEMENT · DOCUMENTATION · PERFORMANCE
SECURITY · SUPPORT · MISSING_CONTEXT · NEEDS_REPRODUCTION · UNKNOWN
"""
import re
from dataclasses import dataclass, field


@dataclass
class IssueUnderstandingResult:
    issue_type: str = 'UNKNOWN'  # BUG, FEATURE_REQUEST, DOCUMENTATION, etc.
    confidence: float = 0.0
    reasoning: list = field(default_factory=list)
    missing_information: list = field(default_factory=list)
    recommended_bug_mode: str = 'UNKNOWN'
    next_action: str = 'HUMAN_TRIAGE'
    has_stacktrace: bool = False
    has_reproduction: bool = False
    has_test_output: bool = False
    has_code_reference: bool = False


class IssueUnderstandingBrain:
    """Classifies GitHub issues beyond simple UNKNOWN."""
    
    ISSUE_TYPES = {
        'FEATURE_REQUEST': {
            'keywords': ['feature request', 'would be nice', 'please add', 'support for',
                        'it would be great', 'wish', 'new feature', 'could you add',
                        'add support for', 'should support', 'it would be helpful',
                        'would like to see', 'please implement', 'feature proposal',
                        'enhancement request', 'suggestion', 'proposal'],
            'next_action': 'ROUTE_TO_PLANNING',
            'description': 'A request for new functionality, not a bug fix',
        },
        'ENHANCEMENT': {
            'keywords': ['improve', 'better', 'faster', 'optimize', 'refactor',
                        'make it faster', 'speed up',
                        'could be improved', 'needs refactoring', 'should be faster'],
            'next_action': 'ROUTE_TO_PLANNING',
            'description': 'Improvement to existing functionality (not a new feature)',
        },
        'DOCUMENTATION': {
            'keywords': ['documentation', 'docstring', 'readme', 'docs', 'typo',
                        'should be documented', 'missing documentation', 'outdated docs',
                        'doc update', 'document this', 'undocumented', 'clarify docs'],
            'next_action': 'ROUTE_TO_DOCS',
            'description': 'Documentation issue — no code change needed',
        },
        'PERFORMANCE': {
            'keywords': ['performance', 'slow', 'timeout', 'too slow', 'bottleneck',
                        'profiling', 'memory usage', 'cpu', 'latency', 'throughput',
                        'takes too long', 'extremely slow', 'memory leak', 'oom'],
            'next_action': 'PERFORMANCE_ANALYSIS',
            'description': 'Performance issue — needs profiling, not a bug',
        },
        'SECURITY': {
            'keywords': ['security', 'vulnerability', 'cve', 'injection', 'xss',
                        'csrf', 'exploit', 'unauthorized', 'sql injection',
                        'privilege escalation', 'data leak', 'sensitive data',
                        'eval(', 'exec(', 'pickle', 'unsafe', 'sandbox escape'],
            'next_action': 'SECURITY_VETO',
            'description': 'Security vulnerability — block and escalate',
        },
        'SUPPORT': {
            'keywords': ['how do i', 'help', 'question', 'how can i', 'what is',
                        'where is', 'why does', 'how to', 'doesnt work', 'not working',
                        'broken', 'error when i', 'cant figure out', 'how should i'],
            'next_action': 'SUPPORT_RESPONSE',
            'description': 'User support question — not necessarily a bug',
        },
        'NEEDS_REPRODUCTION': {
            'keywords': ['cannot reproduce', 'unable to reproduce', 'works for me',
                        'sometimes', 'intermittent', 'randomly', 'occasionally',
                        'race condition', 'flaky', 'non-deterministic'],
            'next_action': 'REQUEST_REPRODUCTION',
            'description': 'Bug report missing minimal reproduction steps',
        },
        'MISSING_CONTEXT': {
            'keywords': ['no stacktrace', 'no error message', 'no logs', 'not sure',
                        'unknown', 'unclear', 'vague', '???', 'need more info'],
            'next_action': 'REQUEST_CONTEXT',
            'description': 'Report lacks sufficient information to classify',
        },
        'BUG': {
            'keywords': ['bug', 'error', 'exception', 'traceback', 'crash',
                        'broken', 'incorrect', 'wrong', 'should return',
                        'expected', 'assertionerror', 'null pointer', 'none type',
                        'key error', 'type error', 'value error', 'import error',
                        'index error', 'attribute error', 'cannot', 'failed',
                        'does not', 'should not', 'incorrectly', 'incorrect result',
                        'fails', 'failing', 'failure', 'segfault', 'abort'],
            'next_action': 'CT_PIPELINE',
            'description': 'Confirmed or likely bug — route to CT pipeline',
        },
    }
    
    # Signals that help disambiguate
    SIGNALS = {
        'has_stacktrace': [r'Traceback\s*\(most recent', r'File\s+"[^"]+",\s*line\s+\d+',
                          r'\w+Error\s*:', r'\w+Exception\s*:'],
        'has_reproduction': [r'reproduce', r'steps to reproduce', r'how to reproduce',
                            r'to reproduce:?', r'reproduction', r'minimal.*example'],
        'has_test_output': [r'assert', r'AssertionError', r'expected.*but.*got',
                           r'FAILED', r'PASSED', r'test_', r'pytest'],
        'has_code_reference': [r'File\s+"[^"]+"', r'\.py:', r'def\s+\w+', r'class\s+\w+',
                              r'in\s+\w+\.py', r'line\s+\d+', r'\.js:', r'\.ts:'],
    }
    
    def analyze(self, issue_text: str, labels: list = None, 
                issue_title: str = '') -> IssueUnderstandingResult:
        """Classify a GitHub issue into its concrete type."""
        result = IssueUnderstandingResult()
        text = (issue_title + ' ' + issue_text).lower()
        original = issue_title + ' ' + issue_text
        
        # Detect structural signals
        result.has_stacktrace = any(re.search(p, original, re.IGNORECASE)
                                    for p in self.SIGNALS['has_stacktrace'])
        result.has_reproduction = any(re.search(p, original, re.IGNORECASE)
                                      for p in self.SIGNALS['has_reproduction'])
        result.has_test_output = any(re.search(p, original, re.IGNORECASE)
                                     for p in self.SIGNALS['has_test_output'])
        result.has_code_reference = any(re.search(p, original, re.IGNORECASE)
                                        for p in self.SIGNALS['has_code_reference'])
        
        # Score each issue type by keyword match count
        scores = {}
        reasons = {}
        for issue_type, config in self.ISSUE_TYPES.items():
            matches = [kw for kw in config['keywords']
                      if re.search(kw, text, re.IGNORECASE)]
            if matches:
                scores[issue_type] = len(matches)
                reasons[issue_type] = matches[:3]
        
        if not scores:
            result.issue_type = 'UNKNOWN'
            result.confidence = 0.0
            result.reasoning = ['No recognizable keywords in issue text']
            result.next_action = 'HUMAN_TRIAGE'
        else:
            # Priority: SECURITY > BUG > FEATURE_REQUEST > ENHANCEMENT > others
            priority = ['SECURITY', 'BUG', 'FEATURE_REQUEST', 'ENHANCEMENT',
                       'DOCUMENTATION', 'PERFORMANCE', 'SUPPORT',
                       'NEEDS_REPRODUCTION', 'MISSING_CONTEXT']
            
            best = None
            for p in priority:
                if p in scores:
                    best = p
                    break
            
            config = self.ISSUE_TYPES[best]
            result.issue_type = best
            result.confidence = min(0.95, 0.3 + 0.05 * scores[best])
            result.reasoning = reasons[best]
            result.next_action = config['next_action']
            
            # Determine recommended bug mode
            if best in ('SECURITY',):
                result.recommended_bug_mode = 'SECURITY'
            elif best == 'PERFORMANCE':
                result.recommended_bug_mode = 'PERFORMANCE'
            elif best in ('FEATURE_REQUEST', 'ENHANCEMENT', 'DOCUMENTATION', 'SUPPORT'):
                result.recommended_bug_mode = 'UNKNOWN'
            elif best == 'BUG':
                if result.has_stacktrace:
                    result.recommended_bug_mode = 'EXCEPTION'
                elif result.has_test_output:
                    result.recommended_bug_mode = 'ALGORITHMIC'
                else:
                    result.recommended_bug_mode = 'UNKNOWN'
        
        # Determine missing information
        if not result.has_stacktrace:
            result.missing_information.append('stacktrace')
        if not result.has_reproduction:
            result.missing_information.append('reproduction_steps')
        if not result.has_test_output:
            result.missing_information.append('test_output')
        if not result.has_code_reference:
            result.missing_information.append('code_reference')
        
        return result


# Self-test
if __name__ == "__main__":
    brain = IssueUnderstandingBrain()
    passed = 0
    
    print("ISSUE UNDERSTANDING BRAIN — Self-Test")
    print("=" * 55)
    
    tests = [
        ("T1: Feature Request",
         "It would be great if the library could support reading CSV files with custom delimiters. Right now only comma is supported. Could you add support for tab-delimited files?",
         "FEATURE_REQUEST"),
        ("T2: Real Bug",
         "Traceback (most recent call last):\n  File views.py, line 42\nTypeError: cannot concatenate str and int\n\nThis is a bug in the payment calculation. The function should return the correct total.",
         "BUG"),
        ("T3: Documentation",
         "The documentation for the API endpoint is missing. The README file should be updated to include the new parameters. There are several typos in the docstring as well.",
         "DOCUMENTATION"),
        ("T4: Performance",
         "The query takes 45 seconds to complete. This is extremely slow and causing timeouts in production. We need to optimize the database access and add better caching.",
         "PERFORMANCE"),
        ("T5: Missing Context",
         "Something is wrong with the login page. I'm not sure what happened. There was no error message. It doesn't work after the last update. Need more info please.",
         "MISSING_CONTEXT"),
        ("T6: Security",
         "There is a SQL injection vulnerability in the search endpoint. An attacker can inject arbitrary SQL commands through the 'query' parameter. This allows unauthorized access to the database.",
         "SECURITY"),
        ("T7: Support Question",
         "How do I configure the logging to output JSON format? I've tried several things but it doesn't work. Can someone help me set this up correctly?",
         "SUPPORT"),
        ("T8: Needs Reproduction",
         "The application crashes sometimes when multiple users are logged in simultaneously. I cannot reproduce this error consistently. It seems to be a race condition that only happens under heavy load.",
         "NEEDS_REPRODUCTION"),
        ("T9: Enhancement",
         "The current sorting algorithm could be improved to handle edge cases better. We should refactor the comparison logic and make it faster for large datasets. This is not a bug, just room for improvement.",
         "ENHANCEMENT"),
        ("T10: SWE-bench-like vague bug",
         "\"Modeling's separability_matrix does not compute separability correctly for nested CompoundModels. The expected output should be a 2D array but it returns a 1D array in some cases.\"",
         "BUG"),
    ]
    
    for name, text, expected_type in tests:
        r = brain.analyze(issue_text=text)
        ok = r.issue_type == expected_type
        if ok: passed += 1
        print(f"  {'✅' if ok else '❌'} {name:<25s} → {r.issue_type:<20s} conf={r.confidence:.2f} "
              f"missing={r.missing_information} (expected {expected_type})")
    
    print(f"\n  ERGEBNIS: {passed}/{len(tests)} Tests")
    print(f"  {'✅ ISSUE UNDERSTANDING BRAIN FERTIG' if passed >= 8 else '⚠️'}")
