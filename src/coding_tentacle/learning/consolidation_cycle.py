"""
CONSOLIDATION CYCLE — RC55
Wake-Sleep: Day collects experiences → Night consolidates into skills & rules.
Oktopus: Vertikaler Lobus = LTP/LTD = Langzeitgedächtnis-Konsolidierung.
"""
import os, json, sqlite3
from dataclasses import dataclass, field


@dataclass
class ConsolidationReport:
    status: str = 'NO_DATA'  # COMPLETED / NO_DATA / WARNING / FAILED
    analyzed_entries: int = 0
    root_cause_clusters: list = field(default_factory=list)
    successful_patterns: list = field(default_factory=list)
    failed_patterns: list = field(default_factory=list)
    skill_candidates: list = field(default_factory=list)
    rule_candidates: list = field(default_factory=list)
    trust_adjustments: list = field(default_factory=list)
    recommendations: list = field(default_factory=list)


class ConsolidationCycle:
    """Nightly consolidation: compresses experiences into reusable knowledge."""
    
    def __init__(self, blm_db_path=None, rc_mem_path=None):
        self.blm_db_path = blm_db_path or os.path.expanduser('~/.coding_tentacle/learning.db')
        self.rc_mem_path = rc_mem_path or os.path.expanduser('~/.coding_tentacle/root_causes.json')
    
    def run(self, min_entries: int = 3, dry_run: bool = False) -> ConsolidationReport:
        """Execute consolidation cycle."""
        report = ConsolidationReport()
        
        # Phase 1: Load BLM experiences
        experiences = self._load_blm_experiences()
        if len(experiences) < min_entries:
            report.status = 'NO_DATA'
            report.analyzed_entries = len(experiences)
            report.recommendations.append(f'Need at least {min_entries} entries (have {len(experiences)})')
            return report
        
        report.analyzed_entries = len(experiences)
        
        # Phase 2: Cluster by root cause
        clusters = self._cluster_by_root_cause(experiences)
        for rc, bugs in clusters.items():
            if len(bugs) >= 3:
                report.root_cause_clusters.append({
                    'root_cause': rc,
                    'count': len(bugs),
                    'bug_types': list(set(b['bug_type'] for b in bugs)),
                    'files': list(set(b.get('file', 'unknown') for b in bugs)),
                })
        
        # Phase 3: Identify successful patterns
        successes = [e for e in experiences if e.get('success', False)]
        failures = [e for e in experiences if not e.get('success', False)]
        
        if successes:
            by_engine = {}
            for s in successes:
                eng = s.get('engine', 'unknown')
                bt = s.get('bug_type', 'Unknown')
                key = f'{eng}+{bt}'
                by_engine[key] = by_engine.get(key, 0) + 1
            
            for key, count in by_engine.items():
                if count >= 2:
                    report.successful_patterns.append(f'{key}: {count}× successful')
        
        if failures:
            by_pattern = {}
            for f in failures:
                eng = f.get('engine', 'unknown')
                bt = f.get('bug_type', 'Unknown')
                key = f'{eng}+{bt}'
                by_pattern[key] = by_pattern.get(key, 0) + 1
            
            for key, count in by_pattern.items():
                if count >= 2:
                    report.failed_patterns.append(f'{key}: {count}× failed')
        
        # Phase 4: Generate skill candidates
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
        
        for cluster in report.root_cause_clusters:
            rc = cluster['root_cause']
            if rc in skill_map and cluster['count'] >= 3:
                report.skill_candidates.append({
                    'skill': skill_map[rc],
                    'root_cause': rc,
                    'evidence_count': cluster['count'],
                    'files': cluster['files'][:3],
                })
        
        # Phase 5: Generate rule candidates
        for sp in report.successful_patterns:
            eng, bt = sp.split(':')[0].split('+')
            report.rule_candidates.append({
                'rule': f'PREFER {eng} for {bt}',
                'type': 'PREFER',
                'engine': eng,
                'bug_type': bt,
                'evidence': sp,
            })
        
        for fp in report.failed_patterns:
            eng, bt = fp.split(':')[0].split('+')
            report.rule_candidates.append({
                'rule': f'AVOID {eng} for {bt}',
                'type': 'AVOID',
                'engine': eng,
                'bug_type': bt,
                'evidence': fp,
            })
        
        # Phase 6: Trust adjustments
        for fp in report.failed_patterns:
            eng, bt = fp.split(':')[0].split('+')
            failures_for_pattern = sum(1 for f in failures 
                                      if f.get('engine') == eng and f.get('bug_type') == bt)
            if failures_for_pattern >= 3:
                report.trust_adjustments.append({
                    'engine': eng,
                    'bug_type': bt,
                    'adjustment': -0.08 * failures_for_pattern,
                    'reason': f'{failures_for_pattern}× failed',
                })
        
        report.status = 'COMPLETED'
        report.recommendations.append(
            f'Consolidated {report.analyzed_entries} entries → '
            f'{len(report.root_cause_clusters)} clusters, '
            f'{len(report.skill_candidates)} skill candidates, '
            f'{len(report.rule_candidates)} rule candidates'
        )
        
        return report
    
    def _load_blm_experiences(self):
        """Load experiences from BugLearningMemory."""
        try:
            if not os.path.exists(self.blm_db_path):
                return []
            conn = sqlite3.connect(self.blm_db_path)
            cur = conn.execute(
                "SELECT bug_signature, bug_type, engine, success, file_path, root_cause FROM experiences"
            )
            rows = cur.fetchall()
            conn.close()
            return [{'bug_signature': r[0], 'bug_type': r[1], 'engine': r[2],
                     'success': r[3], 'file': r[4], 'root_cause': r[5] if len(r) > 5 else ''}
                    for r in rows]
        except:
            return []
    
    def _cluster_by_root_cause(self, experiences):
        """Group experiences by root cause pattern."""
        clusters = {}
        rc_map = {
            'none': 'MISSING_GUARD',
            'null': 'MISSING_GUARD',
            'has no attribute': 'MISSING_GUARD',
            'cannot import': 'BAD_IMPORT_PATH',
            'eval(': 'UNSAFE_EVAL',
            'os.system': 'UNSAFE_SHELL',
            'race': 'RACE_CONDITION',
            'deadlock': 'DEADLOCK',
            'timeout': 'TIMEOUT',
            'typeerror': 'WRONG_TYPE_CONVERSION',
        }
        
        for exp in experiences:
            sig = (exp.get('bug_signature', '') + ' ' + exp.get('root_cause', '')).lower()
            rc = 'OTHER'
            for kw, name in rc_map.items():
                if kw in sig:
                    rc = name
                    break
            clusters.setdefault(rc, []).append(exp)
        
        return clusters


# ═══════════ SELF-TEST ═══════════
if __name__ == "__main__":
    import tempfile
    
    cc = ConsolidationCycle()
    passed = 0
    
    print("CONSOLIDATION CYCLE — Self-Test")
    print("=" * 55)
    
    # T1: No data
    r = cc.run(min_entries=1000)
    t1 = r.status == 'NO_DATA'
    if t1: passed += 1
    print(f"  {'✅' if t1 else '❌'} T1: No data → {r.status}")
    
    # T2–T7: Create fake BLM and test consolidation
    tmp = tempfile.mkdtemp()
    db = os.path.join(tmp, 'test.db')
    
    import sqlite3 as sq
    conn = sq.connect(db)
    conn.execute("CREATE TABLE IF NOT EXISTS experiences (bug_signature, bug_type, engine, success, file_path, root_cause)")
    # 3 MISSING_GUARD successes
    for i in range(3):
        conn.execute("INSERT INTO experiences VALUES (?,?,?,?,?,?)",
                     (f"NullPointer in views.py:{42+i}", "NullPointer", "opencode", True, "views.py", "MISSING_GUARD"))
    # 2 UNSAFE_EVAL failures
    for i in range(2):
        conn.execute("INSERT INTO experiences VALUES (?,?,?,?,?,?)",
                     (f"eval(user_input) in auth.py:{10+i}", "SecurityRisk", "ollama", False, "auth.py", "UNSAFE_EVAL"))
    # 1 random
    conn.execute("INSERT INTO experiences VALUES (?,?,?,?,?,?)",
                 ("import error", "ImportError", "opencode", True, "config.py", "BAD_IMPORT_PATH"))
    conn.commit()
    conn.close()
    
    cc2 = ConsolidationCycle(blm_db_path=db)
    r2 = cc2.run(min_entries=3)
    
    t2 = r2.status == 'COMPLETED'
    if t2: passed += 1
    print(f"  {'✅' if t2 else '❌'} T2: Consolidation completed → {r2.status}")
    
    t3 = len(r2.root_cause_clusters) >= 1
    if t3: passed += 1
    print(f"  {'✅' if t3 else '❌'} T3: Root cause clusters → {len(r2.root_cause_clusters)}")
    
    t4 = len(r2.successful_patterns) >= 1
    if t4: passed += 1
    print(f"  {'✅' if t4 else '❌'} T4: Successful patterns → {len(r2.successful_patterns)}")
    
    t5 = len(r2.skill_candidates) >= 1
    if t5: passed += 1
    print(f"  {'✅' if t5 else '❌'} T5: Skill candidates → {len(r2.skill_candidates)}")
    
    t6 = len(r2.rule_candidates) >= 1
    if t6: passed += 1
    print(f"  {'✅' if t6 else '❌'} T6: Rule candidates → {len(r2.rule_candidates)}")
    
    t7 = len(r2.recommendations) >= 1
    if t7: passed += 1
    print(f"  {'✅' if t7 else '❌'} T7: Recommendations → {len(r2.recommendations)}")
    
    t8 = r2.analyzed_entries == 6
    if t8: passed += 1
    print(f"  {'✅' if t8 else '❌'} T8: Analyzed entries → {r2.analyzed_entries}")
    
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    
    print(f"\n  ERGEBNIS: {passed}/8 Tests")
    print(f"  {'✅ CONSOLIDATION CYCLE FERTIG' if passed >= 6 else '⚠️'}")
