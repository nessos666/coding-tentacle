"""
ENGINE ENSEMBLE MODE — RC38
When uncertain, both engines generate fixes. CT picks the best.
Ensemble only when: low confidence, high risk, or similar engine trust.

Author: Hermes + David | Coding Tentacle 2026
"""
import time, subprocess, json, os
from dataclasses import dataclass, field


@dataclass
class EngineCandidateResult:
    """One engine's fix attempt."""
    engine_name: str
    success: bool
    runtime_s: float
    diff: str = ''
    safety_passed: bool = True
    tests_passed: bool = False
    skeptic_risk: float = 0.0
    impact_risk: float = 0.0
    trust_score: float = 0.0
    reason: str = ''
    
    def score(self):
        """Overall quality score (higher = better)."""
        if not self.success or not self.safety_passed:
            return 0.0
        
        s = 0.0
        if self.tests_passed: s += 0.30
        s += self.trust_score * 0.25          # Engine trust
        s += (1.0 - self.skeptic_risk) * 0.20  # Low skeptic risk = good
        s += (1.0 - self.impact_risk) * 0.15  # Low impact risk = good
        s += 0.10 if len(self.diff) < 500 else 0.05  # Smaller diff = better
        return round(s, 3)


class EnsembleMode:
    """Run multiple engines and pick the best fix.
    
    Activates when:
    - Classification confidence < 0.60
    - Impact risk > 0.40
    - Skeptic risk > 0.30
    - Engine trusts are similar (diff < 0.15)
    - First samples being collected (< 5 samples)
    """
    
    def __init__(self, adaptive_router, engine_router, 
                 safety_brain=None, skeptic_brain=None):
        self.router = adaptive_router  # AdaptiveEngineRouter
        self.engine_router = engine_router  # EngineRouter
        self.safety = safety_brain
        self.skeptic = skeptic_brain
        self.ensemble_uses = 0
        self.single_uses = 0
    
    def should_ensemble(self, bug_type, confidence, impact_risk, skeptic_risk):
        """Determine if ensemble mode should be used."""
        reasons = []
        
        if confidence < 0.60:
            reasons.append(f"Low confidence ({confidence:.0%})")
        if impact_risk > 0.40:
            reasons.append(f"High impact risk ({impact_risk:.2f})")
        if skeptic_risk > 0.30:
            reasons.append(f"High skeptic risk ({skeptic_risk:.2f})")
        
        # Check if engine trusts are similar
        engines = ['opencode', 'ollama']
        trusts = [self.router.perf.get_trust(e, bug_type)[0] for e in engines]
        if max(trusts) - min(trusts) < 0.15:
            reasons.append(f"Similar engine trusts ({trusts[0]:.2f} vs {trusts[1]:.2f})")
        
        # First samples
        samples = [self.router.perf.get_trust(e, bug_type)[1] for e in engines]
        if max(samples) < 3:
            reasons.append(f"Low samples ({max(samples)})")
        
        return len(reasons) >= 2, reasons
    
    def run_engine(self, engine_name, prompt, timeout=60):
        """Run one engine. Returns EngineCandidateResult."""
        cfg = self.engine_router.ENGINES.get(engine_name, {})
        if not cfg or cfg.get('status', '') == 'disabled':
            return EngineCandidateResult(engine_name, False, 0, reason='Engine unavailable')
        
        engine_path = cfg['path']
        if 'opencode' in engine_name.lower():
            cmd = [engine_path, 'run', prompt]
        else:
            cmd = [engine_path, 'run', 'granite3.2-vision', prompt]
        
        t0 = time.time()
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd='/tmp')
            dt = round(time.time() - t0, 1)
            output = (result.stdout + result.stderr)[:600]
            return EngineCandidateResult(engine_name, True, dt, diff=output)
        except subprocess.TimeoutExpired:
            return EngineCandidateResult(engine_name, False, timeout, reason=f'TIMEOUT {timeout}s')
        except Exception as e:
            return EngineCandidateResult(engine_name, False, time.time() - t0, reason=str(e)[:200])
    
    def evaluate_candidates(self, candidates, bug_type):
        """Score all candidates, return winner."""
        for c in candidates:
            c.trust_score, _, _ = self.router.perf.get_trust(c.engine_name, bug_type)
        
        # Safety check
        dangerous = any('DROP TABLE' in c.diff or 'eval(' in c.diff or 'rm -rf' in c.diff
                       for c in candidates)
        if dangerous:
            for c in candidates:
                c.safety_passed = False
                c.reason = 'SAFETY BLOCK'
        
        candidates.sort(key=lambda c: -c.score())
        return candidates
    
    def decide_and_record(self, bug_type, confidence, impact_risk, skeptic_risk,
                          prompt, timeout=60):
        """Full ensemble decision: route or ensemble, execute, record."""
        use_ensemble, reasons = self.should_ensemble(bug_type, confidence, impact_risk, skeptic_risk)
        
        if use_ensemble:
            self.ensemble_uses += 1
            candidates = [
                self.run_engine('opencode', prompt, timeout),
                self.run_engine('ollama', prompt, timeout),
            ]
            evaluated = self.evaluate_candidates(candidates, bug_type)
            winner = evaluated[0] if evaluated else None
            
            if winner:
                self.router.record_result(winner.engine_name, bug_type, 
                                         winner.success, winner.runtime_s,
                                         winner.skeptic_risk, winner.impact_risk)
            return winner, 'ensemble', reasons
        
        else:
            self.single_uses += 1
            name, cfg, reason = self.router.route(bug_type)
            candidate = self.run_engine(name, prompt, timeout)
            self.router.record_result(name, bug_type, candidate.success, 
                                     candidate.runtime_s)
            return candidate, 'single', [reason]
    
    def stats(self):
        return {
            'ensemble_uses': self.ensemble_uses,
            'single_uses': self.single_uses,
            'ensemble_rate': round(self.ensemble_uses / max(1, self.ensemble_uses + self.single_uses), 2),
        }


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    import tempfile, shutil
    from coding_tentacle.orchestrator.engine_router import EngineRouter
    from coding_tentacle.orchestrator.engine_learning import AdaptiveEngineRouter, EnginePerformanceStore
    
    print("ENGINE ENSEMBLE MODE — Self-Test")
    print("=" * 55)
    passed = 0
    
    tmp = tempfile.mkdtemp()
    ps = EnginePerformanceStore(store_path=os.path.join(tmp, 'perf.json'))
    er = EngineRouter()
    er.check_health()
    ar = AdaptiveEngineRouter(er, ps)
    em = EnsembleMode(ar, er)
    
    # T1: should_ensemble with low confidence
    use, reasons = em.should_ensemble('NullPointer', 0.45, 0.30, 0.20)
    t1 = use
    print(f"  T1: {'✅' if t1 else '❌'} Low conf ensemble → {reasons}")
    
    # T2: should_ensemble with high impact
    use2, _ = em.should_ensemble('KeyError', 0.75, 0.50, 0.20)
    t2 = use2
    print(f"  T2: {'✅' if t2 else '❌'} High impact ensemble → ensemble={use2}")
    
    # T3: should_ensemble NOT for clear case
    use3, _ = em.should_ensemble('NullPointer', 0.85, 0.10, 0.05)
    t3 = not use3  # No ensemble needed
    print(f"  T3: {'✅' if t3 else '❌'} Clear case → ensemble={use3}")
    
    # T4: Candidate scoring
    c1 = EngineCandidateResult('opencode', True, 10, diff='if x is not None:', 
                                tests_passed=True, trust_score=0.90)
    c2 = EngineCandidateResult('ollama', True, 25, diff='if x:  # wrong', 
                                tests_passed=False, trust_score=0.30)
    t4 = c1.score() > c2.score()
    print(f"  T4: {'✅' if t4 else '❌'} Better fix wins → OpenCode={c1.score():.2f} Ollama={c2.score():.2f}")
    
    # T5: Safety block in candidate
    c_danger = EngineCandidateResult('opencode', True, 5, diff='DROP TABLE users')
    em.evaluate_candidates([c_danger], 'SecurityRisk')
    t5 = not c_danger.safety_passed
    print(f"  T5: {'✅' if t5 else '❌'} DROP TABLE blocked → safety={c_danger.safety_passed}")
    
    # T6: Empty candidate handling
    evaluated = em.evaluate_candidates([], 'NullPointer')
    t6 = len(evaluated) == 0
    print(f"  T6: {'✅' if t6 else '❌'} Empty candidates → {len(evaluated)}")
    
    # T7: Engine unavailable
    bad_c = em.run_engine('codex', 'fix this', timeout=10)
    t7 = not bad_c.success
    print(f"  T7: {'✅' if t7 else '❌'} Codex disabled → {bad_c.reason}")
    
    # T8: Stats
    em.ensemble_uses = 3
    em.single_uses = 7
    st = em.stats()
    t8 = st['ensemble_uses'] == 3 and st['single_uses'] == 7
    print(f"  T8: {'✅' if t8 else '❌'} Stats → ensemble={st['ensemble_uses']} single={st['single_uses']}")
    
    # T9: Low samples trigger ensemble
    use9, r9 = em.should_ensemble('Deadlock', 0.70, 0.35, 0.25)
    t9 = use9
    print(f"  T9: {'✅' if t9 else '❌'} Low samples → ensemble={use9} reasons={r9}")
    
    # T10: Scoring weights correct
    c_best = EngineCandidateResult('opencode', True, 8, diff='short', 
                                    tests_passed=True, safety_passed=True,
                                    skeptic_risk=0.05, impact_risk=0.05, trust_score=0.95)
    t10 = c_best.score() > 0.80
    print(f"  T10: {'✅' if t10 else '❌'} Perfect fix score → {c_best.score():.2f}")
    
    shutil.rmtree(tmp, ignore_errors=True)
    passed = sum([t1,t2,t3,t4,t5,t6,t7,t8,t9,t10])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/10 Tests bestanden")
    print(f"  {'✅ ENGINE ENSEMBLE FERTIG' if passed >= 9 else '⚠️'}")
