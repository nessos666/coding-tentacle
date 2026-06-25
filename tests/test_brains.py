"""Brain and learning system tests."""
import sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from coding_tentacle.brains.homeostasis_brain import HomeostasisBrain
from coding_tentacle.brains.deutero_learning_brain import DeuteroLearningBrain
from coding_tentacle.brains.self_healing_brain import SelfHealingBrain
from coding_tentacle.learning.backward_paths import LearningBackwardPaths


def test_homeostasis_stable():
    brain = HomeostasisBrain()
    r = brain.check(engine_trust=0.80, error_rate=0.05, blm_entries=100,
                    response_time=12.0, safety_active=True, approval_active=True,
                    reflex_active=True, injection_active=True)
    assert r.status == 'STABLE'

def test_homeostasis_low_trust():
    brain = HomeostasisBrain()
    r = brain.check(engine_trust=0.08, error_rate=0.05, blm_entries=100,
                    response_time=12.0, safety_active=True, approval_active=True,
                    reflex_active=True, injection_active=True)
    assert r.status in ('WARNING', 'CRITICAL')

def test_homeostasis_high_error():
    brain = HomeostasisBrain()
    r = brain.check(engine_trust=0.75, error_rate=0.45, blm_entries=100,
                    response_time=12.0, safety_active=True, approval_active=True,
                    reflex_active=True, injection_active=True)
    assert r.status == 'CRITICAL'

def test_homeostasis_missing_safety():
    brain = HomeostasisBrain()
    r = brain.check(engine_trust=0.75, error_rate=0.05, blm_entries=100,
                    response_time=12.0, safety_active=False, approval_active=True,
                    reflex_active=True, injection_active=True)
    assert r.status == 'CRITICAL'

def test_deutero_healthy():
    brain = DeuteroLearningBrain()
    r = brain.evaluate(engine_trusts={'opencode': 0.75, 'ollama': 0.60})
    assert r.status == 'HEALTHY'

def test_deutero_trust_collapse():
    brain = DeuteroLearningBrain()
    r = brain.evaluate(engine_trusts={'ollama': 0.02})
    assert 'TRUST_COLLAPSE' in str(r.detected_pathologies)

def test_deutero_monoculture():
    brain = DeuteroLearningBrain()
    r = brain.evaluate(engine_usage={'opencode': 95, 'ollama': 2, 'claude': 3})
    assert 'ENGINE_MONOCULTURE' in str(r.detected_pathologies)

def test_circuit_breaker():
    shb = SelfHealingBrain()
    for _ in range(5):
        shb.record_engine_result('bad_engine', False)
    assert shb.circuit_breaker.is_blocked('bad_engine')
    
    shb.record_engine_result('bad_engine', True)
    assert not shb.circuit_breaker.is_blocked('bad_engine')

def test_backward_paths_trust_update():
    tmp = tempfile.mkdtemp()
    lbp = LearningBackwardPaths(blm_db_path=os.path.join(tmp, 'test.db'))
    t = lbp.feed_engine_learning('opencode', 'NullPointer', True)
    assert t > 0.60
    import shutil; shutil.rmtree(tmp, ignore_errors=True)

def test_backward_paths_signals():
    lbp = LearningBackwardPaths()
    sig = lbp.extract_learning_signals(
        confidence=0.92, test_passed=False, unknown_bug=True)
    assert sig['overconfidence']
    assert sig['unknown_blindness']
