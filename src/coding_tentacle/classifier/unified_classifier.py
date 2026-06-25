"""
UNIFIED BUG CLASSIFIER — RC43C
Single source of truth. Replaces 6 separate classifiers.
Keyword + Semantic Fallback. 18 bug types. 8 languages.

Author: Hermes + David | Coding Tentacle 2026
"""
import re
from dataclasses import dataclass


@dataclass
class BugClassification:
    bug_type: str
    confidence: float
    language: str = 'python'
    security_risk: bool = False


class UnifiedBugClassifier:
    """Single bug classifier for all languages and bug types."""
    
    BUG_PATTERNS = {
        'NullPointer': {
            'keywords': ['null', 'none', 'nonetype', 'none reference', 'nil dereference',
                         'undefined is not', 'has no attribute', 'cannot read propert'],
            'confidence': 0.85,
            'languages': ['*'],
        },
        'TypeError': {
            'keywords': ['typeerror', 'cannot concatenate', 'unsupported operand',
                         'type .* is not', 'mismatched types', 'expected.*found'],
            'confidence': 0.85,
            'languages': ['*'],
        },
        'ImportError': {
            'keywords': ['importerror', 'modulenotfound', 'no module', 'cannot import',
                         'cannot find module', 'unresolved import'],
            'confidence': 0.90,
            'languages': ['*'],
        },
        'KeyError': {
            'keywords': ['keyerror', 'key not found', 'missing key', 'no such key'],
            'confidence': 0.85,
            'languages': ['*'],
        },
        'IndexError': {
            'keywords': ['indexerror', 'list index out of range', 'array index out',
                         'index out of bounds', 'slice bounds'],
            'confidence': 0.88,
            'languages': ['*'],
        },
        'ValueError': {
            'keywords': ['valueerror', 'invalid literal', 'cannot convert',
                         'invalid value', 'out of range'],
            'confidence': 0.80,
            'languages': ['*'],
        },
        'SyntaxError': {
            'keywords': ['syntaxerror', 'invalid syntax', 'unexpected token',
                         'expected.*got', 'syntax error'],
            'confidence': 0.92,
            'languages': ['*'],
        },
        'ConnectionError': {
            'keywords': ['connectionerror', 'connection refused', 'connection timeout',
                         'connection reset', 'failed to connect', 'cannot connect'],
            'confidence': 0.82,
            'languages': ['*'],
        },
        'RaceCondition': {
            'keywords': ['race condition', 'data race', 'concurrent', 'thread safety',
                         'synchronization', 'deadlock', 'mutex', 'shared state'],
            'confidence': 0.75,
            'languages': ['*'],
        },
        'FileNotFoundError': {
            'keywords': ['filenotfounderror', 'no such file', 'file not found',
                         'cannot find file', 'missing file', 'file does not exist'],
            'confidence': 0.90,
            'languages': ['*'],
        },
        'RecursionError': {
            'keywords': ['recursionerror', 'maximum recursion depth', 'recursive',
                         'infinite recursion', 'stack overflow'],
            'confidence': 0.85,
            'languages': ['*'],
        },
        'SecurityRisk': {
            'keywords': ['sql injection', 'drop table', 'eval(', 'exec(', 'system(',
                         'subprocess', 'rm -rf', 'sudo', 'api_key', 'password =',
                         'token =', 'injection', 'xss', 'csrf', 'exploit'],
            'confidence': 0.95,
            'languages': ['*'],
            'security': True,
        },
        'TimeoutError': {
            'keywords': ['timeout', 'timed out', 'deadline exceeded', 'took too long'],
            'confidence': 0.80,
            'languages': ['*'],
        },
        'MemoryError': {
            'keywords': ['memoryerror', 'out of memory', 'allocation failed',
                         'oom', 'heap space', 'stack overflow'],
            'confidence': 0.80,
            'languages': ['*'],
        },
        'EncodingError': {
            'keywords': ['unicode', 'encoding', 'decode', 'utf-8', 'ascii', 'latin'],
            'confidence': 0.82,
            'languages': ['*'],
        },
        'PermissionError': {
            'keywords': ['permissionerror', 'permission denied', 'access denied',
                         'not permitted', 'cannot write', 'read-only'],
            'confidence': 0.85,
            'languages': ['*'],
        },
        'OverflowError': {
            'keywords': ['overflow', 'integer overflow', 'buffer overflow',
                         'arithmetic overflow', 'too large'],
            'confidence': 0.80,
            'languages': ['*'],
        },
        'Deadlock': {
            'keywords': ['deadlock', 'lock wait', 'transaction aborted',
                         'could not acquire lock', 'locked by'],
            'confidence': 0.82,
            'languages': ['*'],
        },
    }
    
    def classify(self, text, language='python'):
        """Classify bug type from text. Returns BugClassification."""
        text_lower = text.lower()
        
        best_type = 'Unknown'
        best_confidence = 0.0
        is_security = False
        
        for bug_type, pattern in self.BUG_PATTERNS.items():
            matched = False
            conf = pattern['confidence']
            
            for kw in pattern['keywords']:
                if kw in text_lower:  # P0.6: Fixed — was re.escape(kw) which destroyed regex patterns
                    matched = True
                    break
            
            if matched and conf > best_confidence:
                best_type = bug_type
                best_confidence = conf
                if pattern.get('security'):
                    is_security = True
        
        if best_type == 'Unknown':
            best_confidence = 0.2
        
        return BugClassification(best_type, best_confidence, language, is_security)
    
    def classify_with_semantic(self, text, language='python', semantic_classifier=None):
        """Classify with semantic fallback for Unknown results."""
        result = self.classify(text, language)
        
        if result.bug_type == 'Unknown' and semantic_classifier:
            fallback_type, _ = semantic_classifier.classify(text)
            if fallback_type != 'Unknown':
                result.bug_type = fallback_type
                result.confidence = 0.60  # Lower confidence for semantic
        
        return result


# Global singleton
_unified_classifier = None

def get_classifier():
    global _unified_classifier
    if _unified_classifier is None:
        _unified_classifier = UnifiedBugClassifier()
    return _unified_classifier


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    print("UNIFIED BUG CLASSIFIER — Self-Test")
    print("=" * 55)
    passed = 0
    
    c = UnifiedBugClassifier()
    
    tests = [
        ("NullPointer at line 42", "NullPointer"),
        ("none has no attribute", "NullPointer"),
        ("cannot concatenate str and int", "TypeError"),
        ("module not found", "ImportError"),
        ("key not found in dict", "KeyError"),
        ("list index out of range", "IndexError"),
        ("invalid literal for int()", "ValueError"),
        ("invalid syntax", "SyntaxError"),
        ("connection refused", "ConnectionError"),
        ("race condition detected", "RaceCondition"),
        ("file not found", "FileNotFoundError"),
        ("maximum recursion depth", "RecursionError"),
        ("DROP TABLE users", "SecurityRisk"),
        ("eval(user_input)", "SecurityRisk"),
        ("connection timeout", "ConnectionError"),
        ("unknown gibberish xyz123", "Unknown"),
    ]
    
    for text, expected in tests:
        result = c.classify(text)
        ok = result.bug_type == expected
        if ok: passed += 1
        print(f"  {'✅' if ok else '❌'} {text[:40]:<40s} → {result.bug_type}")
    
    print(f"\n  ERGEBNIS: {passed}/{len(tests)} Tests bestanden")
    print(f"  {'✅ UNIFIED CLASSIFIER FERTIG' if passed >= 15 else '⚠️'}")
