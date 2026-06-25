"""
ROOT CAUSE BRAIN V1 — RC50
Goes beyond "what bug?" to "WHY does this bug exist?"
18 root cause classes. 5 analysis layers. BLM-similarity integration.

Working Copy. Do NOT modify frozen v0.9.0.
"""
import re, os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RootCauseReport:
    root_cause: str = ''
    confidence: float = 0.0
    affected_component: str = ''
    suspected_function: str = ''
    suspected_module: str = ''
    architectural_pattern: str = ''
    repeat_count: int = 0
    evidence: list = field(default_factory=list)
    recommendation: str = ''
    # P0.1: RootCauseMemory integration
    historical_matches: list = field(default_factory=list)
    recurrence_count: int = 0
    successful_fixes: list = field(default_factory=list)
    failed_fixes: list = field(default_factory=list)
    preferred_engine: str = ''
    avoid_engine: str = ''
    suggested_skill: str = ''
    confidence_adjustment: float = 0.0
    explanation: str = ''


class RootCauseBrain:
    """Analyzes WHY a bug exists, not just WHAT it is."""
    
    ROOT_CAUSE_CLASSES = {
        'MISSING_GUARD': {
            'bug_types': ['NullPointer', 'KeyError', 'IndexError'],
            'keywords': ['none', 'null', 'nil', 'undefined', 'not found', 'has no attribute'],
            'description': 'No null-check or guard clause before access',
            'fix_pattern': 'Add guard clause (if x is None: return/raise)',
        },
        'MISSING_VALIDATION': {
            'bug_types': ['NullPointer', 'ValueError', 'SecurityRisk'],
            'keywords': ['input', 'user', 'sanitize', 'validate', 'invalid', 'untrusted'],
            'description': 'User input reaches code without validation',
            'fix_pattern': 'Add input validation layer before processing',
        },
        'WRONG_TYPE_CONVERSION': {
            'bug_types': ['TypeError', 'ValueError'],
            'keywords': ['cannot convert', 'unsupported operand', 'int(', 'str(', 'cast', 'concatenate',
                         'float object cannot', 'list indices must', 'cannot be interpreted',
                         'expected string but got', 'expected.*got'],
            'description': 'Type mismatch — value used as wrong type',
            'fix_pattern': 'Add explicit type conversion (str(), int(), cast)',
        },
        'BAD_IMPORT_PATH': {
            'bug_types': ['ImportError', 'ModuleNotFoundError'],
            'keywords': ['cannot import', 'unresolved', 'circular import'],
            'description': 'Import path changed or module missing',
            'fix_pattern': 'Update import path or add dependency',
        },
        'MISSING_DEPENDENCY': {
            'bug_types': ['ImportError', 'FileNotFoundError'],
            'keywords': ['package', 'library', 'version', 'dependency', 'install', 'pip',
                         'no module named', 'modulenotfound', 'missing package'],
            'description': 'Required package not installed',
            'fix_pattern': 'Add to requirements.txt or install package',
        },
        'API_VERSION_MISMATCH': {
            'bug_types': ['ImportError', 'TypeError', 'AttributeError'],
            'keywords': ['deprecated', 'removed', 'version', 'upgrade', 'migrated',
                         'deprecated function', 'no longer supported'],
            'description': 'API changed between versions, old usage breaks',
            'fix_pattern': 'Update to new API or pin old version',
        },
        'BROKEN_CONFIG': {
            'bug_types': ['KeyError', 'FileNotFoundError', 'ValueError'],
            'keywords': ['config', 'yaml', 'json', 'toml', 'env', 'settings', '.conf'],
            'description': 'Configuration missing, wrong, or malformatted',
            'fix_pattern': 'Fix config file or add default values',
        },
        'BAD_STATE_TRANSITION': {
            'bug_types': ['ValueError', 'RuntimeError'],
            'keywords': ['state', 'transition', 'invalid state', 'not in state'],
            'description': 'Object in wrong state for requested operation',
            'fix_pattern': 'Add state check before operation',
        },
        'RACE_CONDITION': {
            'bug_types': ['RaceCondition', 'AttributeError'],
            'keywords': ['race', 'concurrent', 'thread', 'simultaneous', 'data race'],
            'description': 'Multiple threads/processes access shared state unsynchronized',
            'fix_pattern': 'Add lock, mutex, or atomic operation',
        },
        'TIMEOUT': {
            'bug_types': ['TimeoutError', 'ConnectionError'],
            'keywords': ['timeout', 'timed out', 'too long', 'deadline', 'slow'],
            'description': 'Operation exceeded time limit',
            'fix_pattern': 'Add timeout handling or optimize operation',
        },
        'DEADLOCK': {
            'bug_types': ['Deadlock', 'TimeoutError'],
            'keywords': ['deadlock', 'lock wait', 'acquired', 'transaction', 'dead', 'mutex'],
            'description': 'Two or more processes waiting on each other forever',
            'fix_pattern': 'Add timeout or reorder lock acquisition',
        },
        'RESOURCE_LEAK': {
            'bug_types': ['MemoryError', 'TimeoutError'],
            'keywords': ['leak', 'exhausted', 'pool', 'connection', 'memory', 'file handle'],
            'description': 'Resources not released after use',
            'fix_pattern': 'Add proper cleanup (with/close/finally)',
        },
        'PERMISSION_DENIED': {
            'bug_types': ['PermissionError'],
            'keywords': ['permission', 'denied', 'access', 'cannot write', 'read-only'],
            'description': 'Process lacks permission for operation',
            'fix_pattern': 'Check file permissions or use allowed path',
        },
        'BAD_ERROR_HANDLING': {
            'bug_types': ['RuntimeError', 'UnhandledError'],
            'keywords': ['exception', 'catch', 'error', 'swallow', 'bare except'],
            'description': 'Error swallowed, missing, or incorrectly handled',
            'fix_pattern': 'Add specific exception handler or log the error',
        },
        'UNSAFE_EVAL': {
            'bug_types': ['SecurityRisk'],
            'keywords': ['eval(', 'exec(', 'compile(', '__import__', 'pickle', 'marshal',
                         'deserializ', 'loads', 'code execution'],
            'description': 'Code execution from untrusted source',
            'fix_pattern': 'Replace with safe parser or sandboxed execution',
        },
        'UNSAFE_SHELL': {
            'bug_types': ['SecurityRisk'],
            'keywords': ['os.system', 'subprocess', 'shell=True', 'popen', 'rm -rf'],
            'description': 'Shell command constructed from user input',
            'fix_pattern': 'Use subprocess.run with list args (shell=False)',
        },
        'DATA_SHAPE_MISMATCH': {
            'bug_types': ['ValueError', 'TypeError', 'KeyError'],
            'keywords': ['shape', 'dimension', 'columns', 'rows', 'schema', 'expected'],
            'description': 'Data structure has unexpected format',
            'fix_pattern': 'Add schema validation before processing',
        },
        'UNKNOWN_ROOT_CAUSE': {
            'bug_types': ['*'],
            'keywords': [],
            'description': 'Cannot determine root cause from available evidence',
            'fix_pattern': 'Request more context from human',
        },
    }
    
    def analyze(self, bug_type, bug_report='', diff='', 
                impacted_files=None, blm_similar=None) -> RootCauseReport:
        """Determine root cause from bug type, context, and history."""
        report = RootCauseReport()
        text = (bug_report + ' ' + (diff or '')).lower()
        impacted = impacted_files or []
        
        # Find matching root cause classes
        candidates = []
        for rc_name, rc_data in self.ROOT_CAUSE_CLASSES.items():
            if bug_type in rc_data['bug_types'] or '*' in rc_data['bug_types']:
                score = 0.0
                evidence = []
                
                # Keyword matching
                kw_hits = [kw for kw in rc_data['keywords'] if kw in text]
                if kw_hits:
                    score += min(0.30, len(kw_hits) * 0.10)
                    evidence.append(f"Keywords matched: {kw_hits[:3]}")
                
                # Impact-based boost
                if len(impacted) > 3:
                    score += 0.15
                    evidence.append(f"High impact: {len(impacted)} files affected")
                
                # BLM similarity boost
                if blm_similar:
                    similar_count = len(blm_similar)
                    if similar_count >= 3:
                        score += 0.25
                        evidence.append(f"BLM: {similar_count} similar bugs in history")
                    elif similar_count >= 1:
                        score += 0.10
                        evidence.append(f"BLM: {similar_count} similar bug found")
                
                # Direct evidence from description
                if rc_data['description'].split()[0].lower() in text:
                    score += 0.10
                
                if score > 0:
                    # SecurityRisk boost: UNSAFE_EVAL/UNSAFE_SHELL dominate
                    if bug_type == 'SecurityRisk' and rc_name in ('UNSAFE_EVAL', 'UNSAFE_SHELL'):
                        score += 0.25
                    candidates.append((rc_name, rc_data, score, evidence))
        
        if not candidates:
            candidates = [('UNKNOWN_ROOT_CAUSE', self.ROOT_CAUSE_CLASSES['UNKNOWN_ROOT_CAUSE'], 0.15, [])]
        
        candidates.sort(key=lambda x: -x[2])
        best = candidates[0]
        
        report.root_cause = best[0]
        report.confidence = min(0.95, best[2])
        report.evidence = best[3]
        report.architectural_pattern = best[1]['description']
        report.recommendation = best[1]['fix_pattern']
        report.repeat_count = len(blm_similar) if blm_similar else 0
        
        # P0.1: RootCauseMemory integration
        rc_mem = RootCauseMemory()
        if report.root_cause != 'UNKNOWN_ROOT_CAUSE':
            affected = impacted[0] if impacted else 'unknown'
            rc_repeats = rc_mem.get_repeat_count(report.root_cause, affected)
            report.recurrence_count = rc_repeats
            
            if rc_repeats >= 3:
                report.confidence_adjustment = min(0.20, rc_repeats * 0.05)
                report.confidence = min(0.95, report.confidence + report.confidence_adjustment)
                report.explanation = (f'Seen this root cause {rc_repeats}x before in {affected}. '
                                     f'Confidence boosted by {report.confidence_adjustment:.0%}.')
                report.suggested_skill = self._skill_for_root_cause(report.root_cause)
                report.preferred_engine = 'opencode'  # Default, override if data available
            
            if rc_repeats > 0:
                report.historical_matches.append({
                    'root_cause': report.root_cause,
                    'file': affected,
                    'recurrence_count': rc_repeats,
                })
        
        return report
    
    def _skill_for_root_cause(self, root_cause: str) -> str:
        """Map root cause to suggested skill."""
        skill_map = {
            'MISSING_GUARD': 'add_guard_clause',
            'MISSING_VALIDATION': 'add_input_validator',
            'WRONG_TYPE_CONVERSION': 'add_type_normalization',
            'BAD_IMPORT_PATH': 'fix_missing_import',
            'UNSAFE_EVAL': 'replace_eval_with_safe_parser',
            'UNSAFE_SHELL': 'use_subprocess_with_list_args',
            'RACE_CONDITION': 'add_lock_or_queue',
            'DEADLOCK': 'add_timeout_or_reorder_locks',
            'TIMEOUT': 'add_timeout_handling',
        }
        return skill_map.get(root_cause, '')
        
        if impacted:
            report.affected_component = impacted[0] if isinstance(impacted[0], str) else str(impacted[0])
        
        return report


class RootCauseMemory:
    """Persistent storage for root cause patterns."""
    
    def __init__(self, store_path=None):
        self.store_path = store_path or os.path.expanduser('~/.coding_tentacle/root_causes.json')
        self.patterns = {}  # root_cause_class → {count, bug_types, files, strategies}
        self._load()
    
    def record(self, root_cause_class, bug_type, file_path, strategy):
        """Record a root cause occurrence."""
        key = f"{root_cause_class}:{file_path}"
        if key not in self.patterns:
            self.patterns[key] = {
                'root_cause': root_cause_class,
                'file_pattern': file_path,
                'bug_types': [],
                'strategies': [],
                'count': 0,
                'confidence': 0.5,
            }
        entry = self.patterns[key]
        entry['count'] += 1
        if bug_type not in entry['bug_types']:
            entry['bug_types'].append(bug_type)
        if strategy not in entry['strategies']:
            entry['strategies'].append(strategy)
        entry['confidence'] = min(0.95, entry['confidence'] + 0.05 * (1 - entry['confidence']))
        self._save()
    
    def get_repeat_count(self, root_cause_class, file_path=None):
        """How many times has this root cause appeared?"""
        if file_path:
            key = f"{root_cause_class}:{file_path}"
            return self.patterns.get(key, {}).get('count', 0)
        return sum(v['count'] for k, v in self.patterns.items() 
                  if k.startswith(root_cause_class))
    
    def _save(self):
        try:
            import json
            os.makedirs(os.path.dirname(self.store_path), exist_ok=True)
            with open(self.store_path, 'w') as f:
                json.dump(self.patterns, f, indent=2)
        except:
            pass
    
    def _load(self):
        try:
            import json
            if os.path.exists(self.store_path):
                with open(self.store_path) as f:
                    self.patterns = json.load(f)
        except:
            pass


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    import tempfile, shutil
    
    print("ROOT CAUSE BRAIN — Self-Test")
    print("=" * 55)
    passed = 0
    
    brain = RootCauseBrain()
    tmp = tempfile.mkdtemp()
    rc_mem = RootCauseMemory(store_path=os.path.join(tmp, 'rc_test.json'))
    
    tests = [
        # (bug_type, bug_report, expected_rc)
        ("NullPointer", "NoneType has no attribute at views.py:42", "MISSING_GUARD"),
        ("NullPointer", "user input not validated in handler", "MISSING_VALIDATION"),
        ("TypeError", "cannot concatenate str and int at line 15", "WRONG_TYPE_CONVERSION"),
        ("ImportError", "cannot import url_quote from werkzeug", "BAD_IMPORT_PATH"),
        ("ImportError", "package numpy not installed", "MISSING_DEPENDENCY"),
        ("ImportError", "deprecated function removed in v2", "API_VERSION_MISMATCH"),
        ("SecurityRisk", "eval(user_input) in login handler", "UNSAFE_EVAL"),
        ("SecurityRisk", "os.system('rm -rf ' + user_path)", "UNSAFE_SHELL"),
        ("RaceCondition", "concurrent requests cause data race", "RACE_CONDITION"),
        ("Deadlock", "transaction aborted: lock wait timeout", "DEADLOCK"),
        ("TimeoutError", "connection timeout after 30s", "TIMEOUT"),
        ("PermissionError", "permission denied writing to /etc", "PERMISSION_DENIED"),
    ]
    
    for bug_type, report_text, expected_rc in tests:
        result = brain.analyze(bug_type, bug_report=report_text)
        ok = result.root_cause == expected_rc
        if ok: passed += 1
        print(f"  {'✅' if ok else '❌'} {bug_type:<20s} rc={result.root_cause:<22s} conf={result.confidence:.2f}")
    
    # T13: Repeat count
    rc_mem.record('MISSING_GUARD', 'NullPointer', 'views.py', 'guard clause')
    rc_mem.record('MISSING_GUARD', 'NullPointer', 'views.py', 'guard clause')
    rc_mem.record('MISSING_GUARD', 'KeyError', 'views.py', 'guard clause')
    repeat = rc_mem.get_repeat_count('MISSING_GUARD', 'views.py')
    t13 = repeat == 3
    if t13: passed += 1
    print(f"  {'✅' if t13 else '❌'} Repeat count → {repeat} (expected 3)")
    
    # T14: RootCauseMemory persistence
    rc_mem2 = RootCauseMemory(store_path=os.path.join(tmp, 'rc_test.json'))
    repeat2 = rc_mem2.get_repeat_count('MISSING_GUARD', 'views.py')
    t14 = repeat2 == 3
    if t14: passed += 1
    print(f"  {'✅' if t14 else '❌'} Persistence → {repeat2} after reload")
    
    # T15: RootCauseMemory integration (P0.1)
    rc_mem.record('MISSING_GUARD', 'NullPointer', 'views.py', 'guard clause')
    rc_mem.record('MISSING_GUARD', 'NullPointer', 'views.py', 'guard clause')
    rc_mem.record('MISSING_GUARD', 'KeyError', 'views.py', 'guard clause')
    result_rc_mem = brain.analyze('NullPointer', bug_report='NoneType has no attribute', 
                                    impacted_files=['views.py'])
    t15 = result_rc_mem.recurrence_count >= 3 and result_rc_mem.confidence_adjustment > 0
    if t15: passed += 1
    print(f"  {'✅' if t15 else '❌'} RC Memory → recurrences={result_rc_mem.recurrence_count} "
          f"adj={result_rc_mem.confidence_adjustment:.2f} skill={result_rc_mem.suggested_skill}")
    
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n  ERGEBNIS: {passed}/15 Tests bestanden")
    print(f"  {'✅ ROOT CAUSE BRAIN FERTIG' if passed >= 13 else '⚠️'}")
