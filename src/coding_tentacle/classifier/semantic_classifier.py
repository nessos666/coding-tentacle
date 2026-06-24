"""
SEMANTIC BUG CLASSIFIER — RC18
Fallback when keyword classifier returns Unknown or low confidence.
Uses weighted keyword similarity (TF-IDF-like) for fuzzy matching.

Does NOT replace keyword classifier. Does NOT handle SecurityRisk.

Autor: Hermes + David | Coding Tentacle 2026
"""
import re, math, json, os
from collections import defaultdict


# ═══════════ BUG TYPE SIGNATURES (weighted keywords) ═══════════
BUG_SIGNATURES = {
    'RecursionError': {
        'keywords': {'recursion': 3.0, 'depth': 2.5, 'exceeded': 2.5, 
                     'stack': 2.0, 'infinite': 2.0, 'loop': 1.0,
                     'maximum': 2.0, 'overflow.*stack': 3.0, 'recursive': 3.0},
        'description': 'RecursionError — maximum recursion depth exceeded',
    },
    'OverflowError': {
        'keywords': {'overflow': 3.0, 'large': 2.0, 'convert': 1.5, 
                     'int': 1.5, 'too large': 3.0, 'big': 1.5,
                     'integer': 1.5, 'long': 1.5, 'exceeded.*size': 2.5},
        'description': 'OverflowError — number too large to process',
    },
    'FileNotFoundError': {
        'keywords': {'file': 2.0, 'not found': 3.0, 'no such': 3.0, 
                     'missing': 2.0, 'path': 1.5, 'directory': 1.5,
                     'config': 1.5, 'exist': 1.0, 'cannot find': 3.0,
                     'missing file': 3.0, 'deploy': 1.0},
        'description': 'FileNotFoundError — missing file or directory',
    },
    'FixtureScopeError': {
        'keywords': {'fixture': 3.0, 'scope': 3.0, 'pytest': 2.0,
                     'session': 2.0, 'function': 2.0, 'mismatch': 2.5,
                     'test': 1.0, 'config': 1.0},
        'description': 'FixtureScopeError — test fixture scope mismatch',
    },
    'DeadlockError': {
        'keywords': {'deadlock': 4.0, 'locked': 3.0, 'mutex': 2.5,
                     'wait': 1.5, 'blocked': 2.0, 'stuck': 1.5,
                     'dependency': 1.5, 'resolve': 1.0, 'graph': 1.0},
        'description': 'Deadlock — circular dependency or lock conflict',
    },
    'EncodingError': {
        'keywords': {'encoding': 3.0, 'decode': 2.5, 'encode': 2.5,
                     'utf': 2.0, 'bytes': 2.0, 'character': 2.0,
                     'unicode': 2.5, 'charset': 2.0},
        'description': 'EncodingError — character encoding/decoding issue',
    },
    'TimeoutError': {
        'keywords': {'timeout': 4.0, 'timed out': 4.0, 'slow': 1.5,
                     'wait': 1.0, 'response': 1.0, 'abort': 2.0,
                     'deadline': 2.0, 'hang': 2.0, 'frozen': 1.5},
        'description': 'TimeoutError — operation timed out',
    },
    'PermissionError': {
        'keywords': {'permission': 4.0, 'denied': 3.5, 'access': 2.0,
                     'forbidden': 2.5, 'unauthorized': 2.5, 'permit': 2.0,
                     'sudo': 1.5, 'root': 1.5, 'chmod': 1.5},
        'description': 'PermissionError — access denied',
    },
}


class SemanticBugClassifier:
    """Weighted keyword similarity fallback for unknown bugs."""
    
    def __init__(self, min_confidence=1.5):
        self.min_confidence = min_confidence
        self.queries = 0
        self.semantic_hits = 0
    
    def classify(self, bug_report, keyword_result=None):
        """Classify a bug report using weighted similarity.
        Only used when keyword classifier returns Unknown or low confidence."""
        self.queries += 1
        
        text = bug_report.lower()
        scores = {}
        
        for bug_type, signature in BUG_SIGNATURES.items():
            score = 0.0
            for keyword, weight in signature['keywords'].items():
                # Count occurrences (with regex for multi-word patterns)
                if ' ' in keyword or '*' in keyword:
                    count = len(re.findall(keyword, text, re.IGNORECASE))
                else:
                    count = text.count(keyword.lower())
                score += count * weight
            
            if score > 0:
                scores[bug_type] = score
        
        if not scores:
            return 'Unknown', 0.0
        
        # Find best match
        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]
        
        # Normalize to 0-1 confidence
        # Max possible score ~15, min ~1.5
        confidence = min(0.85, best_score / 10.0)
        
        if confidence >= 0.15:  # threshold
            self.semantic_hits += 1
            return best_type, round(confidence, 2)
        
        return 'Unknown', 0.0
    
    def stats(self):
        return {
            'queries': self.queries,
            'semantic_hits': self.semantic_hits,
            'hit_rate': round(self.semantic_hits / max(1, self.queries), 2),
        }


def classify_with_fallback(bug_report, keyword_classifier, semantic_classifier):
    """Classify with keyword first, semantic fallback if Unknown."""
    # Try keyword classifier
    bt = keyword_classifier(bug_report) if callable(keyword_classifier) else 'Unknown'
    
    if bt == 'Unknown':
        bt, conf = semantic_classifier.classify(bug_report)
        return bt, conf, 'semantic'
    
    return bt, 0.7, 'keyword'


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    print("SEMANTIC BUG CLASSIFIER — Self-Test")
    print("=" * 55)
    passed = 0
    
    sc = SemanticBugClassifier()
    
    # T1: RecursionError
    bt, conf = sc.classify("RecursionError: maximum recursion depth exceeded in tree traversal")
    t1 = bt == 'RecursionError' and conf > 0.1
    print(f"  T1: {'✅' if t1 else '❌'} Recursion → {bt} (conf={conf})")
    
    # T2: FileNotFound
    bt2, conf2 = sc.classify("FileNotFoundError: config.yaml not found after deploy")
    t2 = bt2 == 'FileNotFoundError' and conf2 > 0.3
    print(f"  T2: {'✅' if t2 else '❌'} FileNotFound → {bt2} (conf={conf2})")
    
    # T3: Overflow
    bt3, conf3 = sc.classify("OverflowError: int too large to convert")
    t3 = bt3 == 'OverflowError' and conf3 > 0.1
    print(f"  T3: {'✅' if t3 else '❌'} Overflow → {bt3} (conf={conf3})")
    
    # T4: Deadlock
    bt4, _ = sc.classify("Deadlock detected: circular dependency in dependency graph")
    t4 = bt4 == 'DeadlockError'
    print(f"  T4: {'✅' if t4 else '❌'} Deadlock → {bt4}")
    
    # T5: Timeout
    bt5, _ = sc.classify("TimeoutError: operation timed out after 30 seconds")
    t5 = bt5 == 'TimeoutError'
    print(f"  T5: {'✅' if t5 else '❌'} Timeout → {bt5}")
    
    # T6: Encoding
    bt6, _ = sc.classify("UnicodeDecodeError: utf-8 codec can't decode byte")
    t6 = bt6 == 'EncodingError'
    print(f"  T6: {'✅' if t6 else '❌'} Encoding → {bt6}")
    
    # T7: Permission
    bt7, _ = sc.classify("PermissionError: access denied to /etc/config")
    t7 = bt7 == 'PermissionError'
    print(f"  T7: {'✅' if t7 else '❌'} Permission → {bt7}")
    
    # T8: Unknown stays Unknown
    bt8, _ = sc.classify("xyzzy frobnicate the widget")
    t8 = bt8 == 'Unknown'
    print(f"  T8: {'✅' if t8 else '❌'} Gibberish → {bt8}")
    
    # T9: Fixture scope
    bt9, _ = sc.classify("FixtureScopeError: fixture 'db' has session scope but used in function scope")
    t9 = bt9 == 'FixtureScopeError'
    print(f"  T9: {'✅' if t9 else '❌'} Fixture → {bt9}")
    
    # T10: Stats
    st = sc.stats()
    t10 = st['semantic_hits'] >= 7
    print(f"  T10: {'✅' if t10 else '❌'} Hits → {st['semantic_hits']}/{st['queries']}")
    
    passed = sum([t1,t2,t3,t4,t5,t6,t7,t8,t9,t10])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/10 Tests bestanden")
    print(f"  {'✅ SEMANTIC CLASSIFIER FERTIG' if passed >= 9 else '⚠️'}")
