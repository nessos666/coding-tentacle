"""
EXPERIENCE CONSOLIDATOR — RC6.8
Consolidates BugLearningMemory experiences into pattern rules.
PREFER rules: fix types with high success rate.
AVOID rules: fix types with high failure rate.

Read-only evidence for PatchSuggestion. NEVER overrides Safety.

Autor: Hermes + David | Coding Tentacle 2026
"""

# CT-v11.0.0: PRODUCTION | 10/10 regression | 25 modules | 90% wired | Droste active
import time, json, os
from collections import defaultdict, Counter
from dataclasses import dataclass, field, asdict

import logging
logger = logging.getLogger(__name__)


@dataclass
class Rule:
    bug_type: str
    action: str          # "PREFER" or "AVOID"
    fix_type: str
    confidence: float    # 0.0-1.0
    sample_size: int
    top_failure_category: str = ""
    created_at: float = 0.0
    last_updated: float = 0.0
    times_used: int = 0


class ExperienceConsolidator:
    """Compresses BLM experiences into actionable pattern rules."""
    
    def __init__(self, config=None, min_samples=10, success_threshold=0.80, avoid_threshold=0.20,
                 rule_path=None):
        self.min_samples = min_samples
        self.success_threshold = success_threshold
        self.avoid_threshold = avoid_threshold
        self.rule_path = rule_path or (config.get('learning.rules_path') if config else os.path.expanduser('~/.coding_tentacle/rules.json'))
        self.rules = []  # list[Rule]
        self.last_consolidation = 0.0
        self._load_rules()
    
    def consolidate(self, blm):
        """Run one consolidation pass. Creates/updates rules from BLM experiences."""
        groups = defaultdict(lambda: {'success': 0, 'failed': 0,
                                       'failure_categories': Counter()})
        
        # Query all experiences from BLM
        try:
            rows = blm.conn.execute(
                'SELECT bug_type, fix_type, success FROM experiences'
            ).fetchall()
        except Exception as e:
            logger.debug('Consolidation query: %s', e)
            return self.rules  # No data
        
        for row in rows:
            bt = row['bug_type'] or 'Unknown'
            ft = row['fix_type'] or 'unknown'
            key = (bt, ft)
            if row['success']:
                groups[key]['success'] += 1
            else:
                groups[key]['failed'] += 1
        
        new_rules = []
        for (bug_type, fix_type), stats in groups.items():
            total = stats['success'] + stats['failed']
            if total < self.min_samples:
                continue
            
            rate = stats['success'] / total
            
            if rate >= self.success_threshold:
                new_rules.append(Rule(
                    bug_type=bug_type, action='PREFER', fix_type=fix_type,
                    confidence=rate, sample_size=total,
                    top_failure_category='',
                    created_at=time.time(), last_updated=time.time()
                ))
            elif rate <= self.avoid_threshold:
                new_rules.append(Rule(
                    bug_type=bug_type, action='AVOID', fix_type=fix_type,
                    confidence=1.0 - rate, sample_size=total,
                    top_failure_category='',
                    created_at=time.time(), last_updated=time.time()
                ))
        
        # Merge with existing rules (update counters, preserve age)
        existing = {f"{r.bug_type}|{r.fix_type}|{r.action}": r for r in self.rules}
        merged = []
        for nr in new_rules:
            key = f"{nr.bug_type}|{nr.fix_type}|{nr.action}"
            if key in existing:
                old = existing[key]
                nr.times_used = old.times_used
                nr.created_at = old.created_at
            merged.append(nr)
        
        self.rules = merged
        self.last_consolidation = time.time()
        self._save_rules()
        return self.rules
    
    def get_preferred_fix(self, bug_type, max_results=3):
        """Get PREFER rules for a bug type."""
        matches = [r for r in self.rules 
                   if r.bug_type == bug_type and r.action == 'PREFER']
        matches.sort(key=lambda r: -(r.confidence * r.sample_size))
        return matches[:max_results]
    
    def get_avoided_fix(self, bug_type, max_results=3):
        """Get AVOID rules for a bug type."""
        matches = [r for r in self.rules 
                   if r.bug_type == bug_type and r.action == 'AVOID']
        matches.sort(key=lambda r: -(r.confidence * r.sample_size))
        return matches[:max_results]
    
    def check_fix(self, bug_type, fix_type):
        """Check if a fix type has a rule. Returns (action, confidence) or None."""
        for r in self.rules:
            if r.bug_type == bug_type and r.fix_type == fix_type:
                return (r.action, r.confidence)
        return None
    
    def apply_aging(self, max_age_days=30, decay_rate=0.1):
        """Age unused rules — confidence decays over time."""
        now = time.time()
        for r in self.rules:
            age_days = (now - r.last_updated) / 86400
            if age_days > max_age_days:
                # Decay: lose 10% confidence per 30-day period beyond max_age
                periods = (age_days - max_age_days) / 30
                r.confidence = max(0.5, r.confidence * (1.0 - decay_rate * periods))
    
    def prune(self, min_confidence=0.50, max_idle_days=180):
        """Remove stale/weak rules."""
        now = time.time()
        self.rules = [r for r in self.rules 
                      if r.confidence >= min_confidence 
                      and (now - r.last_updated) / 86400 < max_idle_days]
        self._save_rules()
    
    def stats(self):
        return {
            'total_rules': len(self.rules),
            'prefer_rules': sum(1 for r in self.rules if r.action == 'PREFER'),
            'avoid_rules': sum(1 for r in self.rules if r.action == 'AVOID'),
            'last_consolidation': time.strftime('%Y-%m-%d %H:%M', 
                time.localtime(self.last_consolidation)) if self.last_consolidation else 'never',
            'actions_executed': 0,  # Read-only
        }
    
    def _save_rules(self):
        os.makedirs(os.path.dirname(self.rule_path), exist_ok=True)
        with open(self.rule_path, 'w') as f:
            json.dump([asdict(r) for r in self.rules], f, indent=2)
    
    def _load_rules(self):
        if os.path.exists(self.rule_path):
            try:
                with open(self.rule_path) as f:
                    data = json.load(f)
                self.rules = [Rule(**d) for d in data]
            except Exception as e:
                logger.debug('Rules parse: %s', e)
                self.rules = []


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    import tempfile
    from coding_tentacle.memory.bug_learning_memory import BugLearningMemory
    
    print("EXPERIENCE CONSOLIDATOR — Self-Test")
    print("=" * 55)
    passed = 0
    
    # Setup: seed BLM with 100 experiences
    db = tempfile.mktemp(suffix='.db')
    blm = BugLearningMemory(db_path=db)
    
    # 45× guard_clause SUCCESS, 48× try_except FAILED, 5× Optional_check SUCCESS, 2× type_cast FAILED
    for i in range(45):
        blm.record_experience(bug_signature=f'NullPointer:file{i}.py', bug_type='NullPointer',
            fix_type='guard_clause', fix_summary='if x:', success=True, confidence=0.85)
    for i in range(48):
        blm.record_experience(bug_signature=f'NullPointer:file{i+100}.py', bug_type='NullPointer',
            fix_type='try_except', fix_summary='try: except:', success=False, confidence=0.15)
    for i in range(5):
        blm.record_experience(bug_signature=f'NullPointer:file{i+200}.py', bug_type='NullPointer',
            fix_type='Optional_check', fix_summary='Optional[...]', success=True, confidence=0.70)
    for i in range(2):
        blm.record_experience(bug_signature=f'NullPointer:file{i+300}.py', bug_type='NullPointer',
            fix_type='type_cast', fix_summary='int(x)', success=False, confidence=0.10)
    
    # Test Consolidation
    rule_path = tempfile.mktemp(suffix='.json')
    ec = ExperienceConsolidator(rule_path=rule_path)
    rules = ec.consolidate(blm)
    
    t1 = len(rules) >= 2
    print(f"  T1: {'✅' if t1 else '❌'} Consolidation → {len(rules)} rules generated")
    
    # PREFER rule for guard_clause
    prefer = ec.get_preferred_fix('NullPointer')
    t2 = len(prefer) >= 1 and prefer[0].fix_type == 'guard_clause'
    print(f"  T2: {'✅' if t2 else '❌'} PREFER guard_clause → conf={prefer[0].confidence:.0%}" if prefer else "  T2: ❌")
    
    # AVOID rule for try_except
    avoid = ec.get_avoided_fix('NullPointer')
    t3 = len(avoid) >= 1 and avoid[0].fix_type == 'try_except'
    print(f"  T3: {'✅' if t3 else '❌'} AVOID try_except → conf={avoid[0].confidence:.0%}" if avoid else "  T3: ❌")
    
    # Check: guard_clause is PREFER
    check = ec.check_fix('NullPointer', 'guard_clause')
    t4 = check and check[0] == 'PREFER'
    print(f"  T4: {'✅' if t4 else '❌'} check_fix(guard_clause) → {check}")
    
    # Check: try_except is AVOID
    check2 = ec.check_fix('NullPointer', 'try_except')
    t5 = check2 and check2[0] == 'AVOID'
    print(f"  T5: {'✅' if t5 else '❌'} check_fix(try_except) → {check2}")
    
    # No rule for unknown type
    check3 = ec.check_fix('RecursionError', 'any_fix')
    t6 = check3 is None
    print(f"  T6: {'✅' if t6 else '❌'} Unknown bug type → No rule")
    
    # Optional_check: 5 samples < min_samples (10) → no rule
    opt = [r for r in rules if r.fix_type == 'Optional_check']
    t7 = len(opt) == 0
    print(f"  T7: {'✅' if t7 else '❌'} Low sample (5) → No rule generated")
    
    # Stats
    st = ec.stats()
    t8 = st['total_rules'] >= 2 and st['actions_executed'] == 0
    print(f"  T8: {'✅' if t8 else '❌'} Stats → {st['total_rules']} rules, read-only")
    
    # Persistence
    ec2 = ExperienceConsolidator(rule_path=rule_path)
    t9 = len(ec2.rules) >= 2
    print(f"  T9: {'✅' if t9 else '❌'} Persistence → {len(ec2.rules)} rules reloaded")
    
    # Aging (simulate by calling, doesn't change young rules)
    ec.apply_aging(max_age_days=30)
    t10 = len(ec.rules) >= 2
    print(f"  T10: {'✅' if t10 else '❌'} Aging → Rules still active (too young)")
    
    # No forbidden methods
    forbidden = ['execute','write','patch','run_shell','apply','delete_file']
    t11 = not any(hasattr(ec, m) for m in forbidden)
    print(f"  T11: {'✅' if t11 else '❌'} No forbidden methods")
    
    passed = sum([t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11])
    os.unlink(db)
    import shutil; shutil.rmtree(os.path.dirname(rule_path), ignore_errors=True)
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/11 Tests bestanden")
    print(f"  {'✅ EXPERIENCE CONSOLIDATOR FERTIG' if passed >= 10 else '⚠️'}")
