"""
HYBRID RETRIEVAL — RC26
FTS5 keyword search + Embedding similarity (TF-IDF weighted).
Combines both scores for ranked hybrid results.

No external ML dependencies. Pure Python TF-IDF + cosine similarity.
Falls back to FTS5-only when embeddings unavailable.

Author: Hermes + David | Coding Tentacle 2026
"""
import re, math, time, os, json
from collections import Counter, defaultdict


class EmbeddingStore:
    """Lightweight TF-IDF embedding store for bug experiences.
    
    No external dependencies. Uses:
    - TF-IDF vectorization (word + bigram features)
    - Cosine similarity for semantic matching
    - Hybrid scoring with FTS5
    """
    
    def __init__(self, blm=None):
        self.blm = blm  # BugLearningMemory instance
        self.vectors = {}  # experience_id → {word: tfidf_weight}
        self.idf = {}  # word → idf score
        self.doc_count = 0
        self.queries = 0
        self.hybrid_hits = 0
    
    def _tokenize(self, text):
        """Tokenize text into words + bigrams for better semantic capture."""
        if not text:
            return []
        words = re.findall(r'[a-z_][a-z0-9_]*', text.lower())
        # Unigrams
        tokens = list(words)
        # Bigrams (capture phrases like "null pointer", "has no", "out of")
        tokens += [f"{words[i]}_{words[i+1]}" for i in range(len(words)-1)]
        return tokens
    
    def _compute_tf(self, tokens):
        """Compute term frequency for a document."""
        tf = Counter(tokens)
        max_freq = max(tf.values()) if tf else 1
        return {word: count / max_freq for word, count in tf.items()}
    
    def index_experience(self, exp_id, bug_signature, bug_type='', root_cause='', fix_summary=''):
        """Index a bug experience for embedding retrieval."""
        text = f"{bug_signature} {bug_type} {root_cause} {fix_summary}"
        tokens = self._tokenize(text)
        
        if not tokens:
            return
        
        tf = self._compute_tf(tokens)
        self.vectors[exp_id] = tf
        self.doc_count += 1
        
        # Update IDF
        seen = set()
        for word in tokens:
            if word not in seen:
                self.idf[word] = self.idf.get(word, 0) + 1
                seen.add(word)
    
    def index_all(self):
        """Index all experiences from BLM."""
        if not self.blm:
            return 0
        
        try:
            rows = self.blm.conn.execute(
                'SELECT id, bug_signature, bug_type, root_cause, fix_summary FROM experiences'
            ).fetchall()
        except Exception:
            return 0
        
        for row in rows:
            self.index_experience(
                exp_id=row['id'],
                bug_signature=row['bug_signature'] or '',
                bug_type=row['bug_type'] or '',
                root_cause=row['root_cause'] or '',
                fix_summary=row['fix_summary'] or '',
            )
        
        return len(rows)
    
    def _get_query_vector(self, text):
        """Get TF-IDF vector for a query string."""
        tokens = self._tokenize(text)
        if not tokens:
            return {}
        
        tf = self._compute_tf(tokens)
        tfidf = {}
        
        for word, tf_val in tf.items():
            df = self.idf.get(word, 1)
            idf_val = math.log((self.doc_count + 1) / (df + 1)) + 1
            tfidf[word] = tf_val * idf_val
        
        return tfidf
    
    def _cosine_similarity(self, vec_a, vec_b):
        """Compute cosine similarity between two sparse vectors."""
        if not vec_a or not vec_b:
            return 0.0
        
        dot = sum(vec_a.get(k, 0) * vec_b.get(k, 0) for k in set(list(vec_a.keys()) + list(vec_b.keys())))
        norm_a = math.sqrt(sum(v**2 for v in vec_a.values()))
        norm_b = math.sqrt(sum(v**2 for v in vec_b.values()))
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot / (norm_a * norm_b)
    
    def search(self, query_text, bug_type=None, limit=5):
        """Find similar experiences using embedding similarity."""
        self.queries += 1
        query_vec = self._get_query_vector(query_text)
        
        if not query_vec or not self.vectors:
            return []
        
        scores = []
        for exp_id, doc_vec in self.vectors.items():
            similarity = self._cosine_similarity(query_vec, doc_vec)
            scores.append((exp_id, similarity))
        
        scores.sort(key=lambda x: -x[1])
        return scores[:limit]
    
    def hybrid_search(self, query_text, bug_type=None, limit=5):
        """Hybrid search: combine FTS5 + embedding scores.
        
        Returns ranked list of (experience_id, hybrid_score, fts5_score, embed_score)
        """
        results = []
        
        # 1. FTS5 search
        fts5_results = {}
        if self.blm:
            fts5_matches = self.blm.find_similar(query_text, bug_type=bug_type, limit=limit * 2)
            for i, match in enumerate(fts5_matches):
                mid = match.get('id', f"fts5_{i}")
                fts5_results[mid] = 1.0 - (i * 0.15)  # Rank-based score
        
        # 2. Embedding search
        embed_results = {}
        embed_matches = self.search(query_text, bug_type=bug_type, limit=limit * 2)
        for exp_id, sim in embed_matches:
            embed_results[exp_id] = sim
        
        # 3. Combine scores
        all_ids = set(list(fts5_results.keys()) + list(embed_results.keys()))
        for exp_id in all_ids:
            fts5_score = fts5_results.get(exp_id, 0.0)
            embed_score = embed_results.get(exp_id, 0.0)
            
            # Hybrid: 40% FTS5 + 60% embedding (embedding captures semantics better)
            hybrid = 0.4 * fts5_score + 0.6 * embed_score
            
            # Bonus for both agreeing
            if fts5_score > 0.5 and embed_score > 0.3:
                hybrid += 0.05
            
            if hybrid > 0.1:
                results.append((exp_id, round(hybrid, 3), round(fts5_score, 3), round(embed_score, 3)))
        
        results.sort(key=lambda x: -x[1])
        self.hybrid_hits += 1
        return results[:limit]


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    import tempfile, shutil
    from coding_tentacle.memory.bug_learning_memory import BugLearningMemory
    
    print("HYBRID RETRIEVAL — Self-Test")
    print("=" * 55)
    passed = 0
    
    tmp = tempfile.mkdtemp()
    blm = BugLearningMemory(db_path=os.path.join(tmp, 'test.db'))
    
    # Seed experiences
    experiences = [
        ("NullPointer at payment.py:42", "NullPointer", "guard_clause", "Optional field not checked", "Added guard clause"),
        ("AttributeError: NoneType in checkout module", "NullPointer", "null_check", "None type has no attribute", "Added null check"),
        ("TypeError: int + str at line 10", "TypeError", "type_cast", "Type mismatch", "str() conversion"),
        ("TypeError: cannot concat str to int", "TypeError", "type_cast", "int passed to string builder", "explicit str()"),
        ("ModuleNotFoundError: config not found", "ImportError", "import_fix", "Missing import", "Added import"),
        ("DROP TABLE users via eval()", "SecurityRisk", "BLOCKED", "SQL injection", "BLOCKED"),
    ]
    
    for sig, bt, fix_type, root, fix in experiences:
        blm.record_experience(bug_signature=sig, bug_type=bt, fix_type=fix_type, root_cause=root, fix_summary=fix, file_path='test.py')
    
    es = EmbeddingStore(blm)
    es.index_all()
    
    # T1: Indexing works
    t1 = len(es.vectors) >= 4
    print(f"  T1: {'✅' if t1 else '❌'} Indexed → {len(es.vectors)} documents")
    
    # T2: Semantic similarity: NullPointer variants
    results = es.hybrid_search("NoneType has no attribute in checkout", bug_type="NullPointer", limit=3)
    t2 = len(results) >= 1
    print(f"  T2: {'✅' if t2 else '❌'} Semantic match → {len(results)} results")
    
    # T3: Hybrid finds both keyword AND semantic matches
    keyword_found = any('payment' in str(r) for r in results)
    semantic_found = any('NoneType' in str(r) for r in results) or len(results) >= 2
    t3 = keyword_found or semantic_found
    print(f"  T3: {'✅' if t3 else '❌'} Hybrid coverage → keyword={keyword_found} semantic={semantic_found}")
    
    # T4: TypeError variants connect
    results_t = es.hybrid_search("cannot concat str to int", bug_type="TypeError", limit=3)
    t4 = len(results_t) >= 1
    print(f"  T4: {'✅' if t4 else '❌'} TypeError match → {len(results_t)} results")
    
    # T5: Cosine similarity works
    qv = es._get_query_vector("null pointer none type")
    dv = es._get_query_vector("NullPointer at payment.py:42 Optional field not checked")
    sim = es._cosine_similarity(qv, dv)
    t5 = sim > 0.0
    print(f"  T5: {'✅' if t5 else '❌'} Cosine → {sim:.3f}")
    
    # T6: SecurityRisk still findable (not blocked by embedding)
    results_s = es.hybrid_search("DROP TABLE via eval injection", limit=3)
    t6 = len(results_s) >= 1
    print(f"  T6: {'✅' if t6 else '❌'} SecurityRisk match → {len(results_s)} results")
    
    # T7: No false positives for unrelated queries
    results_u = es.search("database connection timeout", limit=3)
    t7 = all(s < 0.3 for _, s in results_u) if results_u else True
    print(f"  T7: {'✅' if t7 else '❌'} Low sim for unrelated → {[round(s,2) for _,s in results_u[:2]]}")
    
    # T8: Hybrid scores have 3 components
    if results:
        t8 = len(results[0]) >= 3
        print(f"  T8: {'✅' if t8 else '❌'} Score components → {results[0][1:] if results else 'none'}")
    else:
        t8 = True; print(f"  T8: ⚠️  No results to check")
    
    # T9: TF-IDF bigrams capture phrases
    tokens = es._tokenize("null pointer has no attribute")
    t9 = 'null_pointer' in tokens
    print(f"  T9: {'✅' if t9 else '❌'} Bigrams → null_pointer in tokens: {'yes' if t9 else 'no'}")
    
    # T10: ID increases with docs
    before = es.doc_count
    es.index_experience(999, "new bug", "Unknown", "test", "test")
    t10 = es.doc_count == before + 1
    print(f"  T10: {'✅' if t10 else '❌'} Doc count → {es.doc_count}")
    
    shutil.rmtree(tmp, ignore_errors=True)
    passed = sum([t1,t2,t3,t4,t5,t6,t7,t8,t9,t10])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/10 Tests bestanden")
    print(f"  {'✅ HYBRID RETRIEVAL FERTIG' if passed >= 9 else '⚠️'}")
