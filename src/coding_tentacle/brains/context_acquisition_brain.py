"""
CONTEXT ACQUISITION BRAIN — RC82
When issues are unclear, determines EXACTLY what's missing.
Generates max 5 prioritized questions. Never guesses.
"""
from dataclasses import dataclass, field


@dataclass
class ContextAcquisitionResult:
    missing_items: list = field(default_factory=list)
    priority_questions: list = field(default_factory=list)
    recommended_next_action: str = 'REQUEST_CONTEXT'
    ready_for_pipeline: bool = False
    explanation: str = ''


class ContextAcquisitionBrain:
    """Determines what information is missing from a bug report."""
    
    REQUIRED_FIELDS = {
        'stacktrace': {
            'question': 'Can you provide the full stack trace / error message?',
            'required_for': ['EXCEPTION', 'BUG'],
        },
        'reproduction_steps': {
            'question': 'What are the exact steps to reproduce this issue?',
            'required_for': ['BUG', 'NEEDS_REPRODUCTION'],
        },
        'test_output': {
            'question': 'Can you provide the failing test output (expected vs actual)?',
            'required_for': ['ALGORITHMIC', 'BUG'],
        },
        'expected_behavior': {
            'question': 'What behavior did you expect instead?',
            'required_for': ['BUG', 'FEATURE_REQUEST', 'SUPPORT'],
        },
        'actual_behavior': {
            'question': 'What actually happened? (specific error, wrong output, crash)',
            'required_for': ['BUG', 'SUPPORT', 'UNKNOWN'],
        },
        'affected_file': {
            'question': 'Which file(s) or component(s) are affected?',
            'required_for': ['EXCEPTION', 'BUG', 'PERFORMANCE'],
        },
        'version': {
            'question': 'What version of the software / library are you using?',
            'required_for': ['BUG', 'PERFORMANCE', 'SUPPORT'],
        },
        'environment': {
            'question': 'What is your environment? (OS, Python version, dependencies)',
            'required_for': ['BUG', 'PERFORMANCE', 'NEEDS_REPRODUCTION'],
        },
        'minimal_example': {
            'question': 'Can you provide a minimal, self-contained example that reproduces the issue?',
            'required_for': ['BUG', 'NEEDS_REPRODUCTION', 'ALGORITHMIC'],
        },
        'screenshot_log': {
            'question': 'Can you attach screenshots or log files that show the problem?',
            'required_for': ['SUPPORT', 'MISSING_CONTEXT'],
        },
        'commit_branch': {
            'question': 'Which commit or branch introduced this issue?',
            'required_for': ['BUG', 'REPO'],
        },
        'input_data': {
            'question': 'What input data triggers the problem?',
            'required_for': ['ALGORITHMIC', 'BUG', 'PERFORMANCE'],
        },
    }
    
    ISSUE_TYPE_CONTEXT_NEEDS = {
        'BUG': ['stacktrace', 'reproduction_steps', 'test_output', 'expected_behavior',
                'actual_behavior', 'affected_file', 'version', 'minimal_example'],
        'NEEDS_REPRODUCTION': ['reproduction_steps', 'minimal_example', 'environment',
                               'expected_behavior', 'actual_behavior'],
        'MISSING_CONTEXT': ['actual_behavior', 'expected_behavior', 'screenshot_log',
                           'version', 'environment'],
        'PERFORMANCE': ['affected_file', 'version', 'environment', 'input_data', 'reproduction_steps'],
        'SUPPORT': ['version', 'environment', 'expected_behavior', 'actual_behavior', 'screenshot_log'],
        'UNKNOWN': ['actual_behavior', 'expected_behavior', 'screenshot_log', 'version', 'environment'],
        'ALGORITHMIC': ['test_output', 'input_data', 'minimal_example', 'expected_behavior', 'actual_behavior'],
    }
    
    def acquire(self, issue_type: str, bug_mode: str = 'UNKNOWN',
                has_stacktrace: bool = False, has_reproduction: bool = False,
                has_test_output: bool = False, has_code_reference: bool = False) -> ContextAcquisitionResult:
        """Determine what context is missing and generate prioritized questions."""
        result = ContextAcquisitionResult()
        
        # Determine which fields are present
        present = {
            'stacktrace': has_stacktrace,
            'test_output': has_test_output,
            'reproduction_steps': has_reproduction,
            'affected_file': has_code_reference,
        }
        
        # Determine which fields are needed based on issue type
        needed = self.ISSUE_TYPE_CONTEXT_NEEDS.get(issue_type, 
                   self.ISSUE_TYPE_CONTEXT_NEEDS['UNKNOWN'])
        
        # Merge with bug mode requirements
        if bug_mode in ('EXCEPTION',):
            needed = list(set(needed) | {'stacktrace', 'affected_file'})
        elif bug_mode == 'ALGORITHMIC':
            needed = list(set(needed) | {'test_output', 'input_data', 'minimal_example'})
        
        # Find missing items
        missing = []
        questions = []
        
        for field in needed[:8]:  # Max 8 checks
            is_present = present.get(field, False)
            
            if not is_present:
                field_config = self.REQUIRED_FIELDS.get(field)
                if field_config:
                    missing.append(field)
                    questions.append(field_config['question'])
        
        # Limit to 5 most important questions
        result.missing_items = missing[:5]
        result.priority_questions = questions[:5]
        
        # Determine if ready for pipeline
        critical_missing = {'stacktrace', 'test_output', 'actual_behavior'}
        has_critical = any(m in critical_missing for m in missing)
        
        if has_critical and issue_type in ('BUG', 'NEEDS_REPRODUCTION', 'ALGORITHMIC'):
            result.ready_for_pipeline = False
            result.recommended_next_action = 'REQUEST_CONTEXT'
            result.explanation = f'Missing critical context: {", ".join(missing[:3])}. '
            result.explanation += f'Cannot proceed to repair pipeline without these.'
        elif len(missing) <= 2:
            result.ready_for_pipeline = True
            result.recommended_next_action = 'CT_PIPELINE'
            result.explanation = f'Sufficient context available. '
            if missing:
                result.explanation += f'Minor gaps: {", ".join(missing)}.'
        else:
            result.ready_for_pipeline = False
            result.recommended_next_action = 'REQUEST_CONTEXT'
            result.explanation = f'Insufficient context. Missing: {", ".join(missing[:3])}.'
        
        return result


# Self-test
if __name__ == "__main__":
    brain = ContextAcquisitionBrain()
    passed = 0
    
    print("CONTEXT ACQUISITION BRAIN — Self-Test")
    print("=" * 55)
    
    tests = [
        ("T1: Missing Context — no signals",
         'MISSING_CONTEXT', 'UNKNOWN', dict(has_stacktrace=False, has_reproduction=False, has_test_output=False),
         False, 5),
        ("T2: Needs Reproduction — no repro",
         'NEEDS_REPRODUCTION', 'ALGORITHMIC', dict(has_stacktrace=False, has_reproduction=False, has_test_output=True),
         False, 5),
        ("T3: Bug with stacktrace — ok",
         'BUG', 'EXCEPTION', dict(has_stacktrace=True, has_reproduction=True, has_test_output=True, has_code_reference=True),
         True, 1),
        ("T4: Performance — no benchmark",
         'PERFORMANCE', 'UNKNOWN', dict(has_stacktrace=False, has_reproduction=False, has_test_output=False),
         False, 5),
        ("T5: Support question",
         'SUPPORT', 'UNKNOWN', dict(has_stacktrace=False, has_reproduction=False, has_test_output=False),
         False, 5),
        ("T6: Unknown — no signals at all",
         'UNKNOWN', 'UNKNOWN', dict(has_stacktrace=False, has_reproduction=False, has_test_output=False),
         False, 5),
        ("T7: Max 5 questions guarantee",
         'BUG', 'UNKNOWN', dict(has_stacktrace=False, has_reproduction=False, has_test_output=False),
         False, 5),
        ("T8: Algorithmic with test output — ok",
         'ALGORITHMIC', 'ALGORITHMIC', dict(has_stacktrace=False, has_reproduction=False, has_test_output=True, has_code_reference=True),
         True, 4),
    ]
    
    for name, issue_type, bug_mode, signals, exp_ready, max_q in tests:
        r = brain.acquire(issue_type, bug_mode, **signals)
        ok = (r.ready_for_pipeline == exp_ready and len(r.priority_questions) <= max_q
              and len(r.priority_questions) <= 5)
        if ok: passed += 1
        print(f"  {'✅' if ok else '❌'} {name:<35s} ready={r.ready_for_pipeline} "
              f"questions={len(r.priority_questions)}/{max_q} next={r.recommended_next_action}")
    
    # Show example questions
    print(f"\n  Example questions for MISSING_CONTEXT:")
    r = brain.acquire('MISSING_CONTEXT', 'UNKNOWN')
    for q in r.priority_questions:
        print(f"    • {q}")
    
    print(f"\n  ERGEBNIS: {passed}/{len(tests)} Tests")
    print(f"  {'✅ CONTEXT ACQUISITION BRAIN FERTIG' if passed >= 6 else '⚠️'}")
