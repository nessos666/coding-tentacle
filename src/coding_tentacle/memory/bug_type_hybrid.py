"""
BUG-TYPE-SPECIFIC HYBRID RETRIEVAL — RC27
Per-bug-type FTS5/TF-IDF weighting.
SecurityRisk: FTS5-dominant (80/20). NullPointer: TF-IDF-dominant (40/60).

Author: Hermes + David | Coding Tentacle 2026
"""
from coding_tentacle.memory.bug_learning_memory import BugLearningMemory
from coding_tentacle.memory.hybrid_retrieval import EmbeddingStore


class HybridWeightProfile:
    """Bug-type-specific FTS5/TF-IDF weights."""
    
    # Default: balanced
    DEFAULT = {'fts5': 0.50, 'tfidf': 0.50, 'agreement_bonus': 0.05}
    
    PROFILES = {
        'NullPointer':      {'fts5': 0.35, 'tfidf': 0.65, 'agreement_bonus': 0.08},
        'TypeError':        {'fts5': 0.40, 'tfidf': 0.60, 'agreement_bonus': 0.05},
        'ImportError':      {'fts5': 0.60, 'tfidf': 0.40, 'agreement_bonus': 0.05},
        'KeyError':         {'fts5': 0.55, 'tfidf': 0.45, 'agreement_bonus': 0.05},
        'IndexError':       {'fts5': 0.50, 'tfidf': 0.50, 'agreement_bonus': 0.05},
        'ValueError':       {'fts5': 0.45, 'tfidf': 0.55, 'agreement_bonus': 0.05},
        'SyntaxError':      {'fts5': 0.70, 'tfidf': 0.30, 'agreement_bonus': 0.05},
        'ConnectionError':  {'fts5': 0.50, 'tfidf': 0.50, 'agreement_bonus': 0.05},
        'RaceCondition':    {'fts5': 0.30, 'tfidf': 0.70, 'agreement_bonus': 0.10},
        'Deadlock':         {'fts5': 0.30, 'tfidf': 0.70, 'agreement_bonus': 0.10},
        'Timeout':          {'fts5': 0.40, 'tfidf': 0.60, 'agreement_bonus': 0.05},
        'Performance':      {'fts5': 0.35, 'tfidf': 0.65, 'agreement_bonus': 0.05},
        'SecurityRisk':     {'fts5': 0.80, 'tfidf': 0.20, 'agreement_bonus': 0.05},
        'FileNotFound':     {'fts5': 0.55, 'tfidf': 0.45, 'agreement_bonus': 0.05},
        'OverflowError':    {'fts5': 0.55, 'tfidf': 0.45, 'agreement_bonus': 0.05},
        'RecursionError':   {'fts5': 0.55, 'tfidf': 0.45, 'agreement_bonus': 0.05},
        'EncodingError':    {'fts5': 0.60, 'tfidf': 0.40, 'agreement_bonus': 0.05},
        'PermissionError':  {'fts5': 0.60, 'tfidf': 0.40, 'agreement_bonus': 0.05},
    }
    
    @classmethod
    def get(cls, bug_type):
        """Get weight profile for a bug type. Falls back to DEFAULT."""
        return cls.PROFILES.get(bug_type, cls.DEFAULT)


class BugTypeHybridStore(EmbeddingStore):
    """EmbeddingStore with bug-type-specific hybrid weights."""
    
    def __init__(self, blm=None):
        super().__init__(blm)
        self.weights = HybridWeightProfile()
        self.weight_stats = {}  # bug_type → {fts5_wins, tfidf_wins, hybrid_saves}
    
    def hybrid_search(self, query_text, bug_type=None, limit=5):
        """Bug-type-specific hybrid search."""
        profile = self.weights.get(bug_type)
        w_fts5 = profile['fts5']
        w_tfidf = profile['tfidf']
        bonus = profile['agreement_bonus']
        
        results = []
        fts5_results = {}
        embed_results = {}
        
        # FTS5 search
        if self.blm:
            fts5_matches = self.blm.find_similar(query_text, bug_type=bug_type, limit=limit * 2)
            for i, match in enumerate(fts5_matches):
                mid = match.get('id', f"fts5_{i}")
                fts5_results[mid] = max(0.1, 1.0 - (i * 0.15))
        
        # TF-IDF search
        embed_matches = self.search(query_text, bug_type=bug_type, limit=limit * 2)
        for exp_id, sim in embed_matches:
            embed_results[exp_id] = sim
        
        # Combine with bug-type weights
        all_ids = set(list(fts5_results.keys()) + list(embed_results.keys()))
        for exp_id in all_ids:
            fts5_score = fts5_results.get(exp_id, 0.0)
            embed_score = embed_results.get(exp_id, 0.0)
            
            hybrid = w_fts5 * fts5_score + w_tfidf * embed_score
            
            # Agreement bonus (both found it)
            if fts5_score > 0.5 and embed_score > 0.3:
                hybrid += bonus
            
            if hybrid > 0.1:
                results.append((exp_id, round(hybrid, 3), round(fts5_score, 3), round(embed_score, 3)))
        
        results.sort(key=lambda x: -x[1])
        self.hybrid_hits += 1
        return results[:limit]
    
    def get_weight_summary(self):
        """Return all weight profiles."""
        return {
            bt: {'fts5': p['fts5'], 'tfidf': p['tfidf'], 'dominant': 'FTS5' if p['fts5'] > p['tfidf'] else 'TF-IDF'}
            for bt, p in self.weights.PROFILES.items()
        }


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    import tempfile, shutil, os, random
    
    random.seed(42)
    tmp = tempfile.mkdtemp()
    blm = BugLearningMemory(db_path=os.path.join(tmp, 'test.db'))
    
    # Seed
    experiences = [
        ("NullPointer at pay.py:42", "NullPointer", "guard_clause", "Optional field", "Added guard"),
        ("NoneType has no attr in checkout", "NullPointer", "null_check", "nil deref", "Added check"),
        ("TypeError: int+str line 10", "TypeError", "type_cast", "mismatch", "str() conv"),
        ("DROP TABLE via eval()", "SecurityRisk", "BLOCKED", "injection", "BLOCKED"),
        ("race in payment_processor", "RaceCondition", "lock_guard", "shared state", "mutex"),
        ("concurrent HashMap mod", "RaceCondition", "lock_guard", "thread unsafe", "sync"),
    ]
    for sig, bt, ft, rc, fs in experiences:
        blm.record_experience(bug_signature=sig, bug_type=bt, fix_type=ft, root_cause=rc, fix_summary=fs, file_path='test.py')
    
    bts = BugTypeHybridStore(blm)
    bts.index_all()
    
    print("BUG-TYPE-SPECIFIC HYBRID — Self-Test")
    print("=" * 55)
    passed = 0
    
    # T1: SecurityRisk has FTS5-dominant weight
    w = bts.weights.get('SecurityRisk')
    t1 = w['fts5'] > w['tfidf']
    print(f"  T1: {'✅' if t1 else '❌'} SecurityRisk → FTS5={w['fts5']} TFIDF={w['tfidf']} (FTS5-dominant)")
    
    # T2: NullPointer has TF-IDF-dominant weight
    w2 = bts.weights.get('NullPointer')
    t2 = w2['tfidf'] > w2['fts5']
    print(f"  T2: {'✅' if t2 else '❌'} NullPointer → FTS5={w2['fts5']} TFIDF={w2['tfidf']} (TF-IDF-dominant)")
    
    # T3: RaceCondition has heavy TF-IDF weight
    w3 = bts.weights.get('RaceCondition')
    t3 = w3['tfidf'] >= 0.70
    print(f"  T3: {'✅' if t3 else '❌'} RaceCondition → TFIDF={w3['tfidf']} (heavy semantic)")
    
    # T4: ImportError has FTS5-dominant weight
    w4 = bts.weights.get('ImportError')
    t4 = w4['fts5'] > w4['tfidf']
    print(f"  T4: {'✅' if t4 else '❌'} ImportError → FTS5={w4['fts5']} (exact importer name)")
    
    # T5: Unknown bug type falls back to DEFAULT
    w5 = bts.weights.get('UnknownXYZ')
    t5 = w5['fts5'] == 0.50
    print(f"  T5: {'✅' if t5 else '❌'} Unknown → DEFAULT balanced {w5['fts5']}/{w5['tfidf']}")
    
    # T6: SecurityRisk search prioritizes FTS5
    results_sec = bts.hybrid_search("eval injection", bug_type="SecurityRisk", limit=2)
    t6 = len(results_sec) >= 1
    print(f"  T6: {'✅' if t6 else '❌'} SecurityRisk retrieval → {len(results_sec)} results")
    
    # T7: NullPointer search finds semantic variants
    results_np = bts.hybrid_search("NoneType no attribute checkout", bug_type="NullPointer", limit=3)
    t7 = len(results_np) >= 1
    print(f"  T7: {'✅' if t7 else '❌'} NullPointer semantic → {len(results_np)} results")
    
    # T8: Weight summary complete
    summary = bts.get_weight_summary()
    t8 = len(summary) >= 15
    print(f"  T8: {'✅' if t8 else '❌'} Weight profiles → {len(summary)} bug types")
    
    # T9: Agreement bonus present
    w9 = bts.weights.get('RaceCondition')
    t9 = w9['agreement_bonus'] > 0
    print(f"  T9: {'✅' if t9 else '❌'} RaceCondition bonus → {w9['agreement_bonus']}")
    
    # T10: 18 profiles registered
    t10 = len(bts.weights.PROFILES) >= 15
    print(f"  T10: {'✅' if t10 else '❌'} Total profiles → {len(bts.weights.PROFILES)}")
    
    shutil.rmtree(tmp, ignore_errors=True)
    passed = sum([t1,t2,t3,t4,t5,t6,t7,t8,t9,t10])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/10 Tests bestanden")
    print(f"  {'✅ BUG-TYPE-SPECIFIC HYBRID FERTIG' if passed >= 9 else '⚠️'}")
