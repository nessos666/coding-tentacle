"""CT v1.0.0 — Core Regression Tests (pytest)"""
import sys, os, tempfile, subprocess
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src'))


class TestCoreModules:
    """Essential module imports and basic functionality."""

    def test_working_memory_import(self):
        from coding_tentacle.memory.working_memory import WorkingMemory
        wm = WorkingMemory()
        s = wm.create_session()
        assert s.session_id

    def test_inhibitory_control_import(self):
        from coding_tentacle.safety.inhibitory_control import InhibitoryControl
        ic = InhibitoryControl()
        d = ic.quick_check("analyze", "t.py", "", 0.7, "low", True, False, False)
        assert d.action == "GO"

    def test_patch_suggestion_import(self):
        from coding_tentacle.patch.patch_suggestion import PatchSuggestionEngine
        ps = PatchSuggestionEngine()
        r = ps.suggest("NullPointerException",
                       code_context={"file": "t.py", "line": 1},
                       grounding={"grounding_score": 0.5})
        assert r["patch_type"] == "guard_clause"

    def test_security_store_import(self):
        from coding_tentacle.knowledge.security_store import create_seed_security_store
        s = create_seed_security_store()
        r = s.detect_danger("DROP TABLE users")
        assert r

    def test_bug_learning_memory_import(self):
        from coding_tentacle.memory.bug_learning_memory import BugLearningMemory
        db = os.path.join(tempfile.gettempdir(), 'test_blm.db')
        blm = BugLearningMemory(db_path=db)
        blm.record_experience(bug_signature="test", bug_type="NullPointer",
                              fix_type="guard_clause", success=True)
        r = blm.find_similar("test")
        os.remove(db)
        assert r

    def test_experience_consolidator_import(self):
        from coding_tentacle.memory.experience_consolidator import ExperienceConsolidator
        ec = ExperienceConsolidator(min_samples=1)
        assert ec

    def test_bug_type_trust_import(self):
        from coding_tentacle.orchestrator.bug_type_trust import BugTypeSpecificTrust
        bts = BugTypeSpecificTrust(min_samples=3)
        bts.observe('opencode', 'NullPointer', True)
        t = bts.get_trust('opencode', 'NullPointer')
        assert t[0] > 0

    def test_trojan_source_scanner(self):
        from coding_tentacle.security.trojan_source_scanner import TrojanSourceScanner
        scanner = TrojanSourceScanner()
        r = scanner.scan("\u202E test")
        assert not r.clean

    def test_ast_security_analyzer(self):
        from coding_tentacle.security.ast_security_analyzer import ASTSecurityAnalyzer
        analyzer = ASTSecurityAnalyzer()
        r = analyzer.analyze("eval(user_input)")
        assert not r.clean

    def test_engine_router_import(self):
        from coding_tentacle.orchestrator.engine_router import EngineRouter
        router = EngineRouter()
        router.check_health()
        assert router.health_checked


class TestPipeline:
    """End-to-end pipeline tests."""

    def test_shadow_mode_import(self):
        from coding_tentacle.orchestrator.shadow_mode import (
            ShadowModeRunner, GitHubIssueRun, ShadowRunReport
        )
        assert ShadowModeRunner
        assert GitHubIssueRun
        assert ShadowRunReport

    def test_full_pipeline_clean_bug(self):
        """CT pipeline runs on a clean bug without crashing."""
        from coding_tentacle.orchestrator.shadow_mode import ShadowModeRunner, GitHubIssueRun
        from coding_tentacle.orchestrator.metabrain import MetaBrain, SafetyBrain
        from coding_tentacle.safety.inhibitory_control import InhibitoryControl
        from coding_tentacle.knowledge.security_store import create_seed_security_store
        from coding_tentacle.orchestrator.teacher_student import Teacher
        from coding_tentacle.patch.diff_generator import DiffGenerator

        sec = create_seed_security_store()
        ic = InhibitoryControl(security_store=sec)
        safety = SafetyBrain(ic=ic, security_store=sec)
        mb = MetaBrain(safety=safety)

        runner = ShadowModeRunner(
            meta_brain=mb, teacher=Teacher(),
            diff_generator=DiffGenerator(), safety_brain=safety,
        )

        issue = GitHubIssueRun(
            repo_url="https://github.com/test/repo",
            issue_url="https://github.com/test/repo/issues/1",
            issue_title="NullPointer in payment processing",
            issue_body="AttributeError: NoneType has no attribute process",
        )

        report = runner.analyze_issue(issue)
        assert report.detected_bug_type != ''
        assert report.recommendation != ''

    def test_pipeline_security_block(self):
        """CT blocks Trojan Source attack."""
        from coding_tentacle.orchestrator.shadow_mode import ShadowModeRunner, GitHubIssueRun
        from coding_tentacle.orchestrator.metabrain import MetaBrain, SafetyBrain
        from coding_tentacle.safety.inhibitory_control import InhibitoryControl
        from coding_tentacle.knowledge.security_store import create_seed_security_store
        from coding_tentacle.orchestrator.teacher_student import Teacher
        from coding_tentacle.patch.diff_generator import DiffGenerator

        sec = create_seed_security_store()
        ic = InhibitoryControl(security_store=sec)
        safety = SafetyBrain(ic=ic, security_store=sec)
        mb = MetaBrain(safety=safety)

        runner = ShadowModeRunner(
            meta_brain=mb, teacher=Teacher(),
            diff_generator=DiffGenerator(), safety_brain=safety,
        )

        issue = GitHubIssueRun(
            repo_url="https://github.com/test/repo",
            issue_url="https://github.com/test/repo/issues/1",
            issue_title="Fix payment\u202E",  # RLO character
            issue_body="Normal looking text",
        )

        report = runner.analyze_issue(issue)
        assert report.security_blocked


class TestCheckpoints:
    """Verify all v1.0.0 checkpoints are in place."""

    def test_checkpoints_present(self):
        import subprocess
        r = subprocess.run(
            ['grep', '-rl', 'CT-v11.0.0', 'src/'],
            capture_output=True, text=True, cwd=PROJECT_ROOT
        )
        count = len(r.stdout.strip().split('\n')) if r.stdout.strip() else 0
        assert count >= 20, f"Expected >=20 checkpoints, found {count}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
