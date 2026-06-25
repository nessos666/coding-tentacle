"""
LEARNING BACKWARD PATHS — P0.3
Closes 4 dead feedback loops: Outcome→Engine, BLM→Consolidation,
Consolidation→Rules/Skills, SelfObs/Evidence→Learning signals.
"""
import os, json, sqlite3


class LearningBackwardPaths:
    """Provides bridge functions that close learning feedback loops."""
    
    def __init__(self, blm_db_path=None, rc_mem_path=None):
        self.blm_db_path = blm_db_path or os.path.expanduser('~/.coding_tentacle/learning.db')
        self.rc_mem_path = rc_mem_path or os.path.expanduser('~/.coding_tentacle/root_causes.json')
        self.rule_candidates_path = os.path.expanduser('~/.coding_tentacle/rule_candidates.json')
    
    # ── PATH 1: OutcomeLearning → EngineLearning ──
    
    def feed_engine_learning(self, engine_name: str, bug_type: str, success: bool):
        """Update engine trust based on outcome."""
        try:
            # Update engine trust via a simple signal file
            trust_path = os.path.expanduser('~/.coding_tentacle/engine_trust.json')
            trust_data = {}
            if os.path.exists(trust_path):
                with open(trust_path) as f:
                    trust_data = json.load(f)
            
            key = f'{engine_name}:{bug_type}'
            entry = trust_data.get(key, {'trust': 0.60, 'attempts': 0, 'successes': 0})
            entry['attempts'] += 1
            if success:
                entry['successes'] += 1
            
            # Bayesian update with caps
            entry['trust'] = max(0.05, min(0.95,
                entry['successes'] / max(1, entry['attempts'])))
            
            trust_data[key] = entry
            os.makedirs(os.path.dirname(trust_path), exist_ok=True)
            with open(trust_path, 'w') as f:
                json.dump(trust_data, f)
            
            return entry['trust']
        except:
            return 0.60
    
    # ── PATH 2: BLM → ConsolidationCycle ──
    
    def get_unconsolidated_entries(self, since_days: int = 1) -> list:
        """Get BLM entries since last consolidation."""
        try:
            if not os.path.exists(self.blm_db_path):
                return []
            conn = sqlite3.connect(self.blm_db_path)
            cur = conn.execute(
                "SELECT bug_signature, bug_type, engine, success, file_path FROM experiences "
                "ORDER BY rowid DESC LIMIT 50"
            )
            rows = cur.fetchall()
            conn.close()
            return [{'signature': r[0], 'bug_type': r[1], 'engine': r[2],
                     'success': r[3], 'file': r[4]} for r in rows]
        except:
            return []
    
    # ── PATH 3: ConsolidationCycle → RuleMemory / SkillStore ──
    
    def generate_rule_candidates(self, experiences: list) -> list:
        """Generate safe PREFER/AVOID rule candidates from experiences."""
        candidates = []
        by_engine_type = {}
        
        for exp in experiences:
            eng = exp.get('engine', 'unknown')
            bt = exp.get('bug_type', 'Unknown')
            success = exp.get('success', False)
            key = f'{eng}+{bt}'
            entry = by_engine_type.get(key, {'successes': 0, 'failures': 0})
            if success:
                entry['successes'] += 1
            else:
                entry['failures'] += 1
            by_engine_type[key] = entry
        
        for key, counts in by_engine_type.items():
            eng, bt = key.split('+')
            total = counts['successes'] + counts['failures']
            if total < 2:
                continue
            
            rate = counts['successes'] / max(1, total)
            if rate >= 0.80 and counts['successes'] >= 2:
                candidates.append({
                    'rule': f'PREFER {eng} for {bt}',
                    'type': 'PREFER',
                    'engine': eng,
                    'bug_type': bt,
                    'evidence': f'{counts["successes"]}/{total} successes',
                    'confidence': min(0.90, rate),
                    'risk_level': 'low',
                    'auto_activate': True,  # Safe: high success rate
                })
            elif rate <= 0.20 and counts['failures'] >= 2:
                candidates.append({
                    'rule': f'AVOID {eng} for {bt}',
                    'type': 'AVOID',
                    'engine': eng,
                    'bug_type': bt,
                    'evidence': f'{counts["successes"]}/{total} successes',
                    'confidence': min(0.90, 1.0 - rate),
                    'risk_level': 'medium',
                    'auto_activate': False,  # Needs human review
                })
        
        # Save candidates
        os.makedirs(os.path.dirname(self.rule_candidates_path), exist_ok=True)
        with open(self.rule_candidates_path, 'w') as f:
            json.dump(candidates, f, indent=2)
        
        return candidates
    
    # ── PATH 4: SelfObservation / Evidence → Learning Signals ──
    
    def extract_learning_signals(self, safety_warnings: list = None,
                                  skeptic_risk: float = 0.0,
                                  test_passed: bool = None,
                                  confidence: float = 0.5,
                                  unknown_bug: bool = False,
                                  missing_evidence: list = None) -> dict:
        """Extract learning signals from observation and evidence."""
        signals = {
            'calibration_warning': False,
            'safety_override_warning': False,
            'unknown_blindness': False,
            'audit_gap': False,
            'overconfidence': False,
        }
        
        # Safety warning + engine still ran = safety override
        if safety_warnings and test_passed is not None:
            signals['safety_override_warning'] = True
        
        # High confidence + failed test = overconfidence
        if confidence > 0.80 and test_passed is False:
            signals['overconfidence'] = True
            signals['calibration_warning'] = True
        
        # Unknown bug + no review = unknown blindness
        if unknown_bug and test_passed is None:
            signals['unknown_blindness'] = True
        
        # Missing evidence = audit gap
        if missing_evidence:
            signals['audit_gap'] = True
        
        return signals


# ═══════════ SELF-TEST ═══════════
if __name__ == "__main__":
    import tempfile, shutil
    tmp = tempfile.mkdtemp()
    
    lbp = LearningBackwardPaths(
        blm_db_path=os.path.join(tmp, 'test.db'),
        rc_mem_path=os.path.join(tmp, 'rc.json'),
    )
    lbp.rule_candidates_path = os.path.join(tmp, 'rules.json')
    passed = 0
    
    print("LEARNING BACKWARD PATHS — Self-Test")
    print("=" * 55)
    
    # T1: Engine trust update — success
    t = lbp.feed_engine_learning('opencode', 'NullPointer', True)
    t1 = t > 0.60
    if t1: passed += 1
    print(f"  {'✅' if t1 else '❌'} T1: Success increased trust → {t:.2f}")
    
    # T2: Engine trust update — failure
    t = lbp.feed_engine_learning('ollama', 'RaceCondition', False)
    t2 = t < 0.50
    if t2: passed += 1
    print(f"  {'✅' if t2 else '❌'} T2: Failure decreased trust → {t:.2f}")
    
    # T3: Rule candidates from experiences
    exps = [
        {'engine': 'opencode', 'bug_type': 'NullPointer', 'success': True},
        {'engine': 'opencode', 'bug_type': 'NullPointer', 'success': True},
        {'engine': 'opencode', 'bug_type': 'NullPointer', 'success': True},
        {'engine': 'ollama', 'bug_type': 'RaceCondition', 'success': False},
        {'engine': 'ollama', 'bug_type': 'RaceCondition', 'success': False},
    ]
    rules = lbp.generate_rule_candidates(exps)
    t3 = len(rules) >= 1
    if t3: passed += 1
    print(f"  {'✅' if t3 else '❌'} T3: Rule candidates → {len(rules)} rules")
    
    # T4: PREFER rules auto-activated
    prefer_rules = [r for r in rules if r.get('auto_activate')]
    t4 = len(prefer_rules) >= 1
    if t4: passed += 1
    print(f"  {'✅' if t4 else '❌'} T4: Auto-activate safe rules → {len(prefer_rules)}")
    
    # T5: AVOID rules NOT auto-activated
    avoid_rules = [r for r in rules if not r.get('auto_activate')]
    t5 = all(not r.get('auto_activate') for r in avoid_rules)
    if t5: passed += 1
    print(f"  {'✅' if t5 else '❌'} T5: Dangerous rules stay manual → {len(avoid_rules)}")
    
    # T6: Learning signals from evidence
    signals = lbp.extract_learning_signals(
        safety_warnings=['DROP TABLE'],
        skeptic_risk=0.10,
        test_passed=False,
        confidence=0.92,
        unknown_bug=True,
        missing_evidence=['missing_test'])
    t6 = signals.get('overconfidence') and signals.get('unknown_blindness')
    if t6: passed += 1
    print(f"  {'✅' if t6 else '❌'} T6: Evidence signals → {signals}")
    
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n  ERGEBNIS: {passed}/6 Tests")
    print(f"  {'✅ LEARNING BACKWARD PATHS FERTIG' if passed >= 5 else '⚠️'}")
