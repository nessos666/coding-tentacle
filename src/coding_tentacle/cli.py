"""
CT v11.0.0 CLI — coding-tentacle command-line interface

Usage:
    ct repair --issue "NullPointer in payment.py"
    ct benchmark --dataset ct_repair_010.jsonl
    ct version
"""

# CT-v11.0.0: PRODUCTION | 10/10 regression | 25 modules | 90% wired | Droste active

import sys
import argparse


def cmd_repair(args):
    """Run CT repair pipeline on a bug description."""
    from coding_tentacle.orchestrator.shadow_mode import ShadowModeRunner, GitHubIssueRun
    from coding_tentacle.orchestrator.metabrain import MetaBrain, SafetyBrain
    from coding_tentacle.safety.inhibitory_control import InhibitoryControl
    from coding_tentacle.knowledge.security_store import create_seed_security_store
    from coding_tentacle.orchestrator.teacher_student import Teacher
    from coding_tentacle.patch.diff_generator import DiffGenerator

    # Setup pipeline
    sec = create_seed_security_store()
    ic = InhibitoryControl(security_store=sec)
    safety = SafetyBrain(ic=ic, security_store=sec)
    mb = MetaBrain(safety=safety)
    
    runner = ShadowModeRunner(
        meta_brain=mb, teacher=Teacher(),
        diff_generator=DiffGenerator(), safety_brain=safety,
        droste_client='auto',
    )

    issue = GitHubIssueRun(
        repo_url=args.repo or 'https://github.com/user/repo',
        issue_url=args.issue_url or 'https://github.com/user/repo/issues/1',
        issue_title=args.issue or 'Bug report',
        issue_body=args.body or '',
    )

    report = runner.analyze_issue(issue)
    
    print(f"Bug Type:    {report.detected_bug_type}")
    print(f"Confidence:  {report.confidence:.0%}")
    print(f"Security:    {'🛡️ BLOCKED' if report.security_blocked else '✅ PASS'}")
    print(f"Engine:      {report.engine_used or 'none'}")
    print(f"Risk Score:  {report.security_risk_score:.2f}")
    print(f"Skeptic:     {report.skeptic_recommendation or 'N/A'}")
    print(f"BLM Written: {report.blm_written}")
    print(f"Rules:       {report.rules_updated}")
    print(f"Droste:      {report.droste_nodes} nodes, {report.droste_budget_used} chars")
    print(f"WM Session:  {report.wm_session_id}")
    print(f"Duration:    {report.duration_ms:.0f}ms")
    print(f"Recommend:   {report.recommendation}")


def cmd_benchmark(args):
    """Run benchmark suite."""
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))
    from rc12_benchmark.benchmark_runner import BenchmarkRunner
    
    runner = BenchmarkRunner()
    dataset = args.dataset or 'scripts/rc12_benchmark/datasets/ct_repair_010.jsonl'
    run = runner.run_benchmark(
        dataset_path=dataset,
        engine=args.engine or 'auto',
        limit=args.limit or 0,
        output_dir=args.output or 'benchmark_results',
    )
    
    ag = run.aggregate
    print(f"Cases:    {ag.get('total',0)}")
    print(f"Success:  {ag.get('success_rate',0):.0%}")
    print(f"Repair:   {ag.get('repair_rate',0):.0%}")
    print(f"Security: {ag.get('security_blocked',0)} blocks")


def cmd_scorecard(args):
    """Show CT Scorecard."""
    from scripts.rc12_benchmark.batch_runner import ScorecardEngine
    
    engine = ScorecardEngine()
    aggregates = {}
    sc = engine.compute(aggregates)
    print(sc.to_markdown())


def cmd_version(args):
    """Show version."""
    print("coding-tentacle v11.0.0")
    print("Secure Self-Learning Repair Agent")
    print("https://github.com/nessos666/coding-tentacle")


def main():
    parser = argparse.ArgumentParser(
        description='Coding Tentacle — Secure Self-Learning Bug Repair Agent',
        prog='ct'
    )
    sub = parser.add_subparsers(dest='command', help='Commands')
    
    # repair
    p_repair = sub.add_parser('repair', help='Run repair pipeline on a bug')
    p_repair.add_argument('--issue', help='Bug description (title)')
    p_repair.add_argument('--body', help='Bug details')
    p_repair.add_argument('--repo', help='Repository URL')
    p_repair.add_argument('--issue-url', help='Issue URL')
    p_repair.set_defaults(func=cmd_repair)
    
    # benchmark
    p_bench = sub.add_parser('benchmark', help='Run benchmark suite')
    p_bench.add_argument('--dataset', help='Path to JSONL dataset')
    p_bench.add_argument('--engine', help='Engine (auto/opencode/claude)')
    p_bench.add_argument('--limit', type=int, help='Max cases')
    p_bench.add_argument('--output', help='Output directory')
    p_bench.set_defaults(func=cmd_benchmark)
    
    # scorecard
    p_score = sub.add_parser('scorecard', help='Show CT Scorecard')
    p_score.set_defaults(func=cmd_scorecard)
    
    # version
    p_ver = sub.add_parser('version', help='Show version')
    p_ver.set_defaults(func=cmd_version)
    
    args = parser.parse_args()
    if args.command:
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
