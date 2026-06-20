"""
GEHIRN E — Kybernetisch Brain v2 (A+B+C+D + Regelkreise)
FIX: Graph-Related jetzt via Bug-Typ. Pattern-Candidates via Memories-Liste.
Autor: Hermes + David | Coding Tentacle Gehirn Bibliothek
"""

import time, math, random
import numpy as np
from collections import defaultdict

class KybernetischBrain:
    def __init__(self):
        self.patterns: dict = {}
        self.memories: list = []
        self.graph_edges: dict = {}
        self.q_table: dict = {}
        self.k = 1.0; self.decay_lambda = 0.01
        self.explore_threshold = 2.5
        self.epsilon = 0.15; self.alpha = 0.1; self.gamma = 0.9
        self.total_bugs = 0; self.total_learned = 0
        self.episodes_since_consolidation = 0
        self.consolidation_threshold = 50; self.meta_interval = 100
    
    def think(self, bug_signature, bug_embedding):
        self.total_bugs += 1
        emb = np.array(bug_embedding)
        bug_type = bug_signature.split(':')[0] if ':' in bug_signature else bug_signature
        
        surprisal = self._surprisal(emb)
        
        if surprisal > self.explore_threshold or not self.memories:
            action = self._rl_choose(bug_type)
            return {'action': 'EXPLORE', 'pattern': None, 'surprisal': surprisal,
                    'reasoning': f"Neu (Surprisal={surprisal:.1f}bits). RL: {action}"}
        
        related = self._graph_related(bug_signature)
        
        # Patterns aus verwandten Signatures via memories
        pattern_candidates = {}
        for mem_sig, mem_emb, mem_pat, mem_succ in self.memories:
            if mem_sig in related and mem_pat in self.patterns:
                f, c, uses, succ, last = self.patterns[mem_pat]
                decay = math.exp(-self.decay_lambda * max(0, (time.time()-last)/86400))
                eff = c * decay
                if eff > 0.2:
                    if mem_pat not in pattern_candidates or eff > pattern_candidates[mem_pat]:
                        pattern_candidates[mem_pat] = eff
        
        if pattern_candidates:
            best = max(pattern_candidates, key=pattern_candidates.get)
            best_eff = pattern_candidates[best]
            return {'action': 'APPLY_PATTERN', 'pattern': best, 'confidence': best_eff,
                    'surprisal': surprisal, 'related_count': len(related),
                    'reasoning': f"Bekannt (Surprisal={surprisal:.1f}). Pattern '{best}' Konfidenz={best_eff:.2f}"}
        
        return {'action': 'EXPLORE', 'pattern': None, 'surprisal': surprisal,
                'reasoning': f"Bekannt aber kein sicheres Pattern ({len(related)} verwandt)"}
    
    def learn(self, bug_signature, pattern, success, embedding=None):
        self.total_learned += 1
        bug_type = bug_signature.split(':')[0] if ':' in bug_signature else bug_signature
        
        if pattern not in self.patterns:
            self.patterns[pattern] = [0.5, 0.1, 0, 0, time.time()]
        f, c, uses, succ_cnt, _ = self.patterns[pattern]
        uses += 1
        if success: succ_cnt += 1
        f = succ_cnt / uses; c = uses / (uses + self.k)
        self.patterns[pattern] = [f, c, uses, succ_cnt, time.time()]
        
        emb_arr = np.array(embedding) if embedding else np.zeros(384)
        self.memories.append((bug_signature, emb_arr, pattern, success))
        
        # Graph edges: Verbinde ähnliche Bug-Typen
        if bug_signature not in self.graph_edges:
            self.graph_edges[bug_signature] = set()
        for existing_sig, existing_emb, _, _ in self.memories[:-1]:
            existing_bt = existing_sig.split(':')[0] if ':' in existing_sig else existing_sig
            if bug_type == existing_bt:
                self.graph_edges[bug_signature].add(existing_sig)
                if existing_sig not in self.graph_edges:
                    self.graph_edges[existing_sig] = set()
                self.graph_edges[existing_sig].add(bug_signature)
        
        reward = 1.0 if success else -0.5
        old_q = self.q_table.get((bug_type, 'APPLY_PATTERN'), 0.0)
        next_qs = [self.q_table.get((bug_type, a), 0.0) for a in ['STORE', 'APPLY_PATTERN', 'IGNORE']]
        self.q_table[(bug_type, 'APPLY_PATTERN')] = old_q + self.alpha * (reward + self.gamma * max(next_qs) - old_q)
        
        self.episodes_since_consolidation += 1
        if self.episodes_since_consolidation >= self.consolidation_threshold:
            self._consolidate()
            self.episodes_since_consolidation = 0
    
    def stats(self):
        n = len(self.memories)
        active_p = sum(1 for p in self.patterns.values() if p[1] > 0.3)
        return {'brain_type': 'Kybernetisch v2', 'total_bugs': self.total_bugs,
                'patterns_active': active_p, 'patterns_total': len(self.patterns),
                'memories': n, 'graph_nodes': len(self.graph_edges)}
    
    def _surprisal(self, emb):
        if not self.memories: return float('inf')
        sims = [self._cosine(emb, m[1]) for m in self.memories]
        p = max(sims)
        return -math.log2(max(p, 0.001))
    
    def _rl_choose(self, bug_type):
        actions = ['STORE', 'APPLY_PATTERN', 'IGNORE']
        if random.random() < self.epsilon: return random.choice(actions)
        qs = [self.q_table.get((bug_type, a), 0.0) for a in actions]
        return actions[np.argmax(qs)]
    
    def _graph_related(self, signature):
        bug_type = signature.split(':')[0] if ':' in signature else signature
        related = set()
        bt_lower = bug_type.lower()
        for node in self.graph_edges:
            if bt_lower in node.lower():
                related.add(node)
                for neighbor in self.graph_edges.get(node, set()):
                    related.add(neighbor)
        return related
    
    def _cosine(self, a, b):
        if len(a) == 0 or len(b) == 0: return 0.0
        norm = np.linalg.norm(a) * np.linalg.norm(b)
        return np.dot(a, b) / norm if norm > 0 else 0.0
    
    def _consolidate(self):
        if len(self.memories) < 10: return
        cutoff = len(self.memories) * 8 // 10
        self.memories = self.memories[-cutoff:]
    
    def __repr__(self):
        s = self.stats()
        return f"KybernetischBrain(patterns={s['patterns_active']}, memories={s['memories']})"

if __name__ == "__main__":
    print("GEHIRN E v2 — Kybernetisch")
    from sentence_transformers import SentenceTransformer
    m = SentenceTransformer('all-MiniLM-L6-v2')
    b = KybernetischBrain()
    for i in range(15):
        bt = ['NullPointer','OffByOne','TypeError'][i%3]
        emb = m.encode(f"{bt} error bug").tolist()
        sig = f"{bt}:f{i}.py:{i}"
        dec = b.think(sig, emb)
        b.learn(sig, f"fix_{bt}", i < 12, emb)
        if i % 3 == 0: print(f"  Bug{i+1}: {dec['action']:15s} | {dec['reasoning'][:55]}")
    print(b.stats()); print("✅ Gehirn E v2 läuft.")
