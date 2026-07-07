"""
RC12 METRIC COLLECTOR — Standardisierte Metriken pro Repair

17 Metriken in 4 Kategorien: Repair, Security, Performance, Learning.
Jede Auswertung eines Benchmarks produziert genau diese strukturierten Daten.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional
import time
import json


@dataclass
class RepairMetrics:
    """Repair-specific metrics."""
    success: bool = False
    diff_generated: bool = False
    diff_size_bytes: int = 0
    tests_passed: int = 0
    tests_total: int = 0
    test_success_rate: float = 0.0


@dataclass
class SecurityMetrics:
    """Security scan results."""
    blocked: bool = False
    risk_score: float = 0.0
    trojan_clean: bool = True
    ast_findings: int = 0
    ast_critical: int = 0
    ast_high: int = 0
    cwe_findings: int = 0
    dangerous_patterns: int = 0


@dataclass
class PerformanceMetrics:
    """Performance + cost metrics."""
    total_ms: float = 0.0
    engine_ms: float = 0.0
    scan_ms: float = 0.0
    token_usage_est: int = 0
    engine_used: str = ''
    engine_available: bool = False


@dataclass
class LearningMetrics:
    """Learning state metrics."""
    engine_trust: float = 0.0
    trust_source: str = ''       # global/blended/specific
    rules_applied: int = 0
    blm_entries_used: int = 0
    consolidator_rule: str = ''
    learning_active: bool = False


@dataclass
class BenchmarkResult:
    """Complete result for one benchmark case."""
    case_id: str
    bug_type: str = ''
    success: bool = False
    repair: RepairMetrics = field(default_factory=RepairMetrics)
    security: SecurityMetrics = field(default_factory=SecurityMetrics)
    performance: PerformanceMetrics = field(default_factory=PerformanceMetrics)
    learning: LearningMetrics = field(default_factory=LearningMetrics)
    decision_trace: dict = field(default_factory=dict)
    error: str = ''
    timestamp: float = 0.0

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()

    def to_dict(self) -> dict:
        return {
            'case_id': self.case_id,
            'bug_type': self.bug_type,
            'success': self.success,
            'repair': asdict(self.repair),
            'security': asdict(self.security),
            'performance': asdict(self.performance),
            'learning': asdict(self.learning),
            'decision_trace': self.decision_trace,
            'error': self.error,
            'timestamp': self.timestamp,
        }


class MetricCollector:
    """
    Collects and computes standardized metrics from a ShadowRunReport.
    
    Usage:
        collector = MetricCollector()
        result = collector.collect(case_id, shadow_report)
    """

    def collect(self, case_id: str, report, engine_name: str = '',
                duration_ms: float = 0.0) -> BenchmarkResult:
        """
        Extract 17 metrics from a ShadowRunReport into BenchmarkResult.
        
        Args:
            case_id: Unique benchmark case identifier
            report: ShadowRunReport from shadow_mode.ShadowModeRunner.analyze_issue()
            engine_name: Name of engine used (if available)
            duration_ms: Total pipeline duration in ms
        """
        result = BenchmarkResult(case_id=case_id)
        
        # --- Bug Type ---
        result.bug_type = getattr(report, 'detected_bug_type', 'Unknown')
        
        # --- Repair Metrics ---
        diff = getattr(report, 'generated_diff', '')
        result.repair.diff_generated = bool(diff)
        result.repair.diff_size_bytes = len(diff.encode()) if diff else 0
        
        test_result = getattr(report, 'test_result', {}) or {}
        result.repair.tests_passed = test_result.get('tests_passed', 0)
        result.repair.tests_total = test_result.get('tests_total', 0)
        if result.repair.tests_total > 0:
            result.repair.test_success_rate = result.repair.tests_passed / result.repair.tests_total
        
        # Success = diff generated AND (tests pass OR no tests needed)
        result.repair.success = bool(
            diff and (
                (result.repair.tests_total > 0 and result.repair.tests_passed == result.repair.tests_total)
                or (result.repair.tests_total == 0 and diff)
            )
        )
        
        # --- Security Metrics ---
        result.security.blocked = getattr(report, 'security_blocked', False)
        result.security.risk_score = getattr(report, 'security_risk_score', 0.0)
        result.security.trojan_clean = getattr(report, 'trojan_source_clean', True)
        result.security.ast_findings = 0  # Populated by SecurityBrain scan
        result.security.ast_critical = 0
        result.security.cwe_findings = len(getattr(report, 'safety_events', []))
        result.security.dangerous_patterns = 0
        
        # --- Performance Metrics ---
        result.performance.total_ms = duration_ms
        result.performance.engine_used = engine_name
        result.performance.token_usage_est = result.repair.diff_size_bytes * 3  # Rough estimate
        
        # --- Learning Metrics ---
        result.learning.engine_trust = getattr(report, 'skeptic_risk', 0.0)
        result.learning.trust_source = getattr(report, 'bug_type_trust_source', 'global')
        result.learning.rules_applied = 1 if getattr(report, 'consolidator_rule', '') else 0
        result.learning.consolidator_rule = getattr(report, 'consolidator_rule', '')
        result.learning.blm_entries_used = 0  # Populated by BLM
        result.learning.learning_active = getattr(report, 'blm_written', False)
        
        # --- Overall Success ---
        result.success = result.repair.success and not result.security.blocked
        
        return result

    def aggregate(self, results: list[BenchmarkResult]) -> dict:
        """Compute aggregate statistics from a list of results."""
        if not results:
            return {'total': 0}
        
        total = len(results)
        successes = sum(1 for r in results if r.success)
        blocked = sum(1 for r in results if r.security.blocked)
        diffs = sum(1 for r in results if r.repair.diff_generated)
        
        repair_successes = sum(1 for r in results if r.repair.success)
        
        return {
            'total': total,
            'successes': successes,
            'success_rate': round(successes / total, 3) if total else 0,
            'repair_successes': repair_successes,
            'repair_rate': round(repair_successes / total, 3) if total else 0,
            'security_blocked': blocked,
            'security_block_rate': round(blocked / total, 3) if total else 0,
            'diffs_generated': diffs,
            'diff_rate': round(diffs / total, 3) if total else 0,
            'avg_runtime_ms': round(sum(r.performance.total_ms for r in results) / total, 1),
            'avg_risk_score': round(sum(r.security.risk_score for r in results) / total, 3),
            'avg_trust': round(sum(r.learning.engine_trust for r in results) / total, 3),
            'avg_diff_bytes': round(sum(r.repair.diff_size_bytes for r in results) / max(1, diffs)),
            'rules_used': sum(1 for r in results if r.learning.rules_applied > 0),
            'learning_active': sum(1 for r in results if r.learning.learning_active),
        }


# ─── Self-Tests ─────────────────────────────────────────────────────────

if __name__ == '__main__':
    # Create a mock report-like object
    class MockReport:
        detected_bug_type = 'NullPointer'
        generated_diff = 'def fix(): pass'
        test_result = {'tests_passed': 3, 'tests_total': 3, 'success': True}
        security_blocked = False
        security_risk_score = 0.0
        trojan_source_clean = True
        safety_events = []
        skeptic_risk = 0.08
        bug_type_trust_source = 'specific'
        consolidator_rule = 'PREFER:opencode:87%'
        blm_written = True
        approval_status = 'pending'

    collector = MetricCollector()
    passed = 0

    # T1: Single collection
    print("T1: Single collect...", end=" ")
    r = collector.collect('test_001', MockReport(), engine_name='opencode', duration_ms=4200)
    assert r.case_id == 'test_001'
    assert r.repair.success
    assert r.security.trojan_clean
    assert r.learning.consolidator_rule
    passed += 1
    print("OK")

    # T2: to_dict
    print("T2: to_dict...", end=" ")
    d = r.to_dict()
    assert d['repair']['success']
    assert d['security']['trojan_clean']
    passed += 1
    print("OK")

    # T3: Aggregate
    print("T3: Aggregate...", end=" ")
    ag = collector.aggregate([r, r, r])
    assert ag['total'] == 3
    assert ag['success_rate'] == 1.0
    passed += 1
    print("OK")

    # T4: Failed repair
    print("T4: Failed repair...", end=" ")
    mr2 = MockReport()
    mr2.generated_diff = ''
    r2 = collector.collect('test_002', mr2)
    assert not r2.repair.success
    assert not r2.success
    passed += 1
    print("OK")

    # T5: Security blocked
    print("T5: Security blocked...", end=" ")
    mr3 = MockReport()
    mr3.security_blocked = True
    r3 = collector.collect('test_003', mr3)
    assert r3.security.blocked
    assert not r3.success  # blocked → not success
    passed += 1
    print("OK")

    # T6: Aggregate with mixed results
    print("T6: Mixed aggregate...", end=" ")
    ag2 = collector.aggregate([r, r2, r3])
    assert ag2['total'] == 3
    assert ag2['security_blocked'] == 1
    assert 0.0 < ag2['success_rate'] < 1.0
    passed += 1
    print("OK")

    print(f"\n{'='*50}")
    print(f"  {passed}/6 Tests bestanden")
    print(f"  {'✅ METRIC COLLECTOR FERTIG' if passed >= 6 else '❌'}")
