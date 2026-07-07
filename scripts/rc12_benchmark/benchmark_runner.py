"""
RC12 BENCHMARK RUNNER — JSONL→Pipeline→Metrics→Report

Core benchmark execution engine. Loads JSONL datasets, runs each case
through CT pipeline, collects 17 metrics + decision trace, generates reports.

Usage:
    python -m scripts.rc12_benchmark.benchmark_runner \
        --dataset ct_repair_100.jsonl \
        --engine opencode \
        --limit 10 \
        --output results/

Produces:
    results/benchmark_results.jsonl   — Per-case metrics
    results/benchmark_report.md       — Aggregate report
    results/benchmark_traces/         — Decision traces per case
"""

import sys, os, time, json, argparse
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from coding_tentacle.orchestrator.shadow_mode import ShadowModeRunner, GitHubIssueRun
from coding_tentacle.orchestrator.metabrain import MetaBrain, SafetyBrain
from coding_tentacle.safety.inhibitory_control import InhibitoryControl
from coding_tentacle.knowledge.security_store import create_seed_security_store
from coding_tentacle.orchestrator.teacher_student import Teacher
from coding_tentacle.patch.diff_generator import DiffGenerator

# RC12 modules
from .metric_collector import MetricCollector, BenchmarkResult
from .explainability import ExplainabilityEngine, DecisionTrace
from .report_generator import ReportGenerator


@dataclass
class BenchmarkRun:
    """Complete benchmark run state."""
    dataset_path: str
    engine: str = 'auto'
    limit: int = 0
    results: list[BenchmarkResult] = field(default_factory=list)
    traces: list[DecisionTrace] = field(default_factory=list)
    aggregate: dict = field(default_factory=dict)
    total_duration_ms: float = 0.0
    errors: list[str] = field(default_factory=list)


class BenchmarkRunner:
    """
    Main benchmark execution engine.
    
    Loads cases → runs CT pipeline → collects metrics → generates report.
    """

    def __init__(self):
        self.collector = MetricCollector()
        self.explainer = ExplainabilityEngine()
        self.reporter = ReportGenerator()
        self._runner = None  # Lazy-init ShadowModeRunner
        self._droste = None

    def _get_runner(self):
        """Lazy-init CT pipeline components."""
        if self._runner is None:
            ic = InhibitoryControl()
            sec = create_seed_security_store()
            safety = SafetyBrain(ic, sec)
            mb = MetaBrain(safety=safety)
            self._runner = ShadowModeRunner(
                meta_brain=mb,
                teacher=Teacher(),
                diff_generator=DiffGenerator(),
                safety_brain=safety,
            )
        return self._runner

    def load_dataset(self, path: str, limit: int = 0) -> list[dict]:
        """
        Load benchmark cases from JSONL file.
        
        Expected format (one JSON object per line):
        {
            "case_id": "bug_001",
            "repo_url": "https://github.com/test/repo",
            "issue_title": "NullPointer in payment",
            "issue_body": "Error: NoneType has no attribute...",
            "expected_bug_type": "NullPointer",
            "expected_fix": "guard_clause",
            "category": "repair"
        }
        """
        cases = []
        if not os.path.exists(path):
            print(f"ERROR: Dataset not found: {path}")
            return cases

        with open(path) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                try:
                    case = json.loads(line)
                    # Ensure required fields
                    case.setdefault('case_id', f'case_{line_num}')
                    case.setdefault('repo_url', 'https://github.com/test/benchmark')
                    case.setdefault('issue_url',
                                    f'https://github.com/test/benchmark/issues/{line_num}')
                    case.setdefault('issue_body', '')
                    cases.append(case)
                except json.JSONDecodeError as e:
                    print(f"WARNING: Line {line_num}: JSON error: {e}")

                if limit and len(cases) >= limit:
                    break

        print(f"Loaded {len(cases)} cases from {path}")
        return cases

    def run_case(self, case: dict, engine: str = 'auto') -> tuple[BenchmarkResult, DecisionTrace]:
        """
        Run a single benchmark case through CT pipeline.
        
        Returns (metrics, decision_trace)
        """
        t0 = time.time()
        runner = self._get_runner()

        # Create GitHubIssueRun from case data
        issue = GitHubIssueRun(
            repo_url=case.get('repo_url', ''),
            issue_url=case.get('issue_url', ''),
            issue_title=case.get('issue_title', case.get('case_id', '')),
            issue_body=case.get('issue_body', ''),
        )

        # Run through CT pipeline
        try:
            report = runner.analyze_issue(issue)
        except Exception as e:
            # Create minimal result for failed runs
            result = BenchmarkResult(case_id=case['case_id'])
            result.error = str(e)
            trace = DecisionTrace(
                repair_id=case['case_id'],
                bug_type=case.get('expected_bug_type', 'Unknown'),
                final_outcome=f'ERROR: {str(e)[:100]}',
            )
            return result, trace

        duration_ms = (time.time() - t0) * 1000

        # Collect metrics
        engine_name = getattr(report, 'engine_used', '') or engine
        route_reason = getattr(report, 'approval_notes', '')

        result = self.collector.collect(
            case['case_id'], report,
            engine_name=engine_name,
            duration_ms=duration_ms,
        )

        # Generate decision trace
        trace = self.explainer.trace(
            report,
            case_id=case['case_id'],
            engine_name=engine_name,
            route_reason=route_reason,
            duration_ms=duration_ms,
        )

        # Attach trace to result
        result.decision_trace = trace.to_dict()

        return result, trace

    def run_benchmark(self, dataset_path: str, engine: str = 'auto',
                      limit: int = 0, output_dir: str = '') -> BenchmarkRun:
        """
        Run complete benchmark on a dataset.
        """
        run = BenchmarkRun(dataset_path=dataset_path, engine=engine, limit=limit)
        t0 = time.time()

        cases = self.load_dataset(dataset_path, limit)
        if not cases:
            return run

        # Set up output directory for traces
        if output_dir:
            traces_dir = os.path.join(output_dir, 'traces')
            os.makedirs(traces_dir, exist_ok=True)

        for i, case in enumerate(cases):
            case_id = case.get('case_id', f'case_{i+1}')
            print(f"  [{i+1}/{len(cases)}] {case_id}: "
                  f"{case.get('issue_title', '')[:60]}...", end=' ')

            result, trace = self.run_case(case, engine)
            run.results.append(result)
            run.traces.append(trace)

            # Quick status
            status = '✅' if result.success else ('🛡️' if result.security.blocked else '❌')
            print(f'{status} ({result.repair.diff_size_bytes}B, '
                  f'{result.performance.total_ms:.0f}ms)')

            # Save individual trace
            if output_dir:
                trace_path = os.path.join(traces_dir, f'{case_id}_trace.md')
                with open(trace_path, 'w') as f:
                    f.write(trace.to_markdown())

            # Save incremental results (crash-safe)
            if output_dir and i % 10 == 0:
                self._save_incremental(run, output_dir)

        run.total_duration_ms = (time.time() - t0) * 1000
        run.aggregate = self.collector.aggregate(run.results)

        # Generate final report
        if output_dir:
            self._save_final(run, output_dir)

        return run

    def _save_incremental(self, run: BenchmarkRun, output_dir: str):
        """Save incremental results (crash-safe)."""
        path = os.path.join(output_dir, 'benchmark_results.jsonl')
        with open(path, 'w') as f:
            for r in run.results:
                f.write(json.dumps(r.to_dict()) + '\n')

    def _save_final(self, run: BenchmarkRun, output_dir: str):
        """Generate final report files."""
        # JSONL results
        self._save_incremental(run, output_dir)

        # Summary JSON
        summary_path = os.path.join(output_dir, 'benchmark_summary.json')
        with open(summary_path, 'w') as f:
            json.dump({
                'dataset': run.dataset_path,
                'engine': run.engine,
                'total_cases': len(run.results),
                'total_duration_ms': run.total_duration_ms,
                'aggregate': run.aggregate,
            }, f, indent=2)

        # Markdown report
        report_md = run.aggregate
        report_md['dataset'] = run.dataset_path
        report_md['engine'] = run.engine
        report_md['duration_ms'] = run.total_duration_ms

        md = self.reporter.generate_markdown(report_md, run.results)
        report_path = os.path.join(output_dir, 'benchmark_report.md')
        with open(report_path, 'w') as f:
            f.write(md)

        print(f"\n📊 Report saved: {report_path}")
        print(f"📊 Results: {summary_path}")


# ─── CLI ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='CT RC12 Benchmark Runner')
    parser.add_argument('--dataset', required=True, help='Path to JSONL dataset')
    parser.add_argument('--engine', default='auto', help='Engine to use (auto/opencode/claude/ollama)')
    parser.add_argument('--limit', type=int, default=0, help='Max cases to run (0=all)')
    parser.add_argument('--output', default='benchmark_results', help='Output directory')
    args = parser.parse_args()

    runner = BenchmarkRunner()
    run = runner.run_benchmark(
        dataset_path=args.dataset,
        engine=args.engine,
        limit=args.limit,
        output_dir=args.output,
    )

    # Print summary
    ag = run.aggregate
    print(f"\n{'='*50}")
    print(f"BENCHMARK COMPLETE")
    print(f"  Cases: {ag.get('total', 0)}")
    print(f"  Success: {ag.get('successes', 0)} ({ag.get('success_rate', 0):.0%})")
    print(f"  Repair: {ag.get('repair_successes', 0)} ({ag.get('repair_rate', 0):.0%})")
    print(f"  Security Blocks: {ag.get('security_blocked', 0)}")
    print(f"  Duration: {run.total_duration_ms:.0f}ms")


if __name__ == '__main__':
    main()
