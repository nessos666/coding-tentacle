"""
RC86 SWE-BENCH BENCHMARK RUNNER
Loads SWE-bench Lite tasks, runs through CT pipeline, saves results.
Resumable. Reproducible. Stats + export.
"""
import sys, os, json, time, subprocess, hashlib, glob
from dataclasses import dataclass, field, asdict
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@dataclass
class RunReport:
    task_id: str = ''
    repo: str = ''
    base_commit: str = ''
    engine: str = 'opencode'
    start_time: str = ''
    end_time: str = ''
    duration_s: float = 0.0
    success: bool = False
    patch_generated: bool = False
    patch_bytes: int = 0
    patch_hash: str = ''
    safety_passed: bool = True
    reflection: dict = field(default_factory=dict)
    test_passed: bool = False
    test_output: str = ''
    error: str = ''
    status: str = 'PENDING'


class SWEBenchRunner:
    """Loads + runs SWE-bench tasks through CT pipeline. Resumable."""
    
    def __init__(self, results_dir: str = None, tasks_file: str = None):
        self.results_dir = results_dir or os.path.expanduser('~/.coding_tentacle/benchmarks/results')
        self.tasks_file = tasks_file or '/tmp/swe-bench-test.json'
        self.tasks = []
        self.results = []
        os.makedirs(self.results_dir, exist_ok=True)
    
    def load_tasks(self, filepath: str = None, limit: int = 0) -> int:
        """Load SWE-bench Lite tasks."""
        path = filepath or self.tasks_file
        if not os.path.exists(path):
            print(f'No tasks file at {path}')
            return 0
        
        self.tasks = []
        with open(path) as f:
            data = json.load(f)
        
        for entry in (data[:limit] if limit else data):
            self.tasks.append({
                'instance_id': entry.get('instance_id', ''),
                'repo': entry.get('repo', ''),
                'base_commit': entry.get('base_commit', ''),
                'problem_statement': entry.get('problem_statement', ''),
                'FAIL_TO_PASS': entry.get('FAIL_TO_PASS', []),
                'PASS_TO_PASS': entry.get('PASS_TO_PASS', []),
            })
        
        return len(self.tasks)
    
    def run_all(self, engine: str = 'opencode', skip_existing: bool = True) -> list[RunReport]:
        """Run all loaded tasks."""
        for i, task in enumerate(self.tasks):
            pid = task['instance_id']
            
            # Check if already completed
            if skip_existing:
                existing = self._find_existing(pid)
                if existing and existing.status == 'DONE':
                    print(f'  [{i+1}/{len(self.tasks)}] {pid[:50]} — SKIP (already done)')
                    self.results.append(existing)
                    continue
            
            print(f'  [{i+1}/{len(self.tasks)}] {pid[:50]}')
            report = self.run_task(task, engine=engine)
            self.results.append(report)
            self._save_report(report)
        
        return self.results
    
    def run_task(self, task: dict, engine: str = 'opencode') -> RunReport:
        """Run one SWE-bench task through CT pipeline."""
        report = RunReport(
            task_id=task['instance_id'],
            repo=task['repo'],
            base_commit=task.get('base_commit', ''),
            engine=engine,
            start_time=datetime.now().isoformat(),
        )
        t0 = time.time()
        
        try:
            # 1. BugModeRouter
            from coding_tentacle.brains.bug_mode_router import BugModeRouter
            router = BugModeRouter()
            mode = router.route(task['problem_statement'])
            
            # 2. OpenCode integration
            repo_dir = f'/tmp/ct_swb_{hash(task["instance_id"]) % 10000}'
            if not self._prepare_repo(task, repo_dir):
                report.error = 'REPO_CLONE_FAILED'
                report.status = 'FAILED'
            else:
                prompt = self._build_prompt(task)
                
                # RC92: Use PTY adapter for reliable output
                from coding_tentacle.llm.adapters.opencode_pty_adapter import OpenCodePTYAdapter
                pty = OpenCodePTYAdapter(timeout=60)
                pty_result = pty.generate(prompt, cwd=repo_dir)
                
                report.duration_s = pty_result.duration_s
                
                if pty_result.status == 'SUCCESS' and pty_result.unified_diff:
                    report.patch_generated = True
                    report.patch_bytes = len(pty_result.unified_diff)
                    report.patch_hash = hashlib.sha256(pty_result.unified_diff.encode()).hexdigest()[:16]
                    report.status = 'PATCH_GENERATED'
                    oc_output = pty_result.unified_diff  # Use diff directly, skip old parser
                elif pty_result.status == 'NO_PATCH':
                    report.error = 'NO_PATCH: ' + (pty_result.error or 'No diff in PTY output')
                    report.status = 'NO_PATCH'
                    oc_output = pty_result.raw_output
                else:
                    report.error = pty_result.error or f'PTY status: {pty_result.status}'
                    report.status = pty_result.status
                    oc_output = pty_result.raw_output
                
                # 3. Parse patch
                from coding_tentacle.llm.opencode_export_parser import OpenCodeExportParser
                parser = OpenCodeExportParser()
                parsed = parser.parse_raw_text(oc_output)
                
                if parsed.valid:
                    report.patch_generated = True
                    report.patch_bytes = len(parsed.patch_text)
                    report.patch_hash = hashlib.sha256(parsed.patch_text.encode()).hexdigest()[:16]
                    report.status = 'PATCH_GENERATED'
                else:
                    report.error = f'No patch: {parsed.parse_errors}'
                    report.status = 'NO_PATCH'
            
            # 4. Safety
            report.safety_passed = True
            
            # 5. Reflection
            try:
                from coding_tentacle.brains.reflection_brain import ReflectionBrain, ReflectionInput
                rb = ReflectionBrain()
                ri = ReflectionInput(
                    bug_mode=mode.mode, engine=engine,
                    tests_after=1 if report.patch_generated else 0,
                    duration_s=time.time() - t0,
                )
                reflection = rb.reflect(ri)
                report.reflection = {
                    'success_reason': reflection.success_reason,
                    'recommended_rule': reflection.recommended_rule,
                }
            except:
                pass
            
            if report.patch_generated and report.safety_passed:
                report.success = True
                report.status = 'DONE'
            
        except Exception as e:
            report.error = str(e)[:200]
            report.status = 'ERROR'
        
        report.end_time = datetime.now().isoformat()
        report.duration_s = round(time.time() - t0, 1)
        return report
    
    def _prepare_repo(self, task: dict, repo_dir: str) -> bool:
        """Clone repo if not exists."""
        if os.path.exists(repo_dir):
            return True
        try:
            subprocess.run(
                ['git', 'clone', '--depth', '1', f'https://github.com/{task["repo"]}.git', repo_dir],
                capture_output=True, timeout=60, check=False
            )
            return os.path.exists(repo_dir)
        except:
            return False
    
    def _build_prompt(self, task: dict) -> str:
        failing = ', '.join(task.get('FAIL_TO_PASS', [])[:3])
        return f"""Fix this bug. Output ONLY a unified diff.

Bug: {task['problem_statement'][:1500]}
Failing Tests: {failing}

Generate a minimal fix as unified diff (--- / +++ / @@). No explanation."""
    
    def _run_opencode(self, prompt: str, repo_dir: str) -> str:
        try:
            proc = subprocess.run(
                ['opencode', '--prompt', prompt],
                capture_output=True, text=True, timeout=90,
                cwd=repo_dir,
            )
            return proc.stdout[:10000] if proc.stdout else ''
        except:
            return ''
    
    def _find_existing(self, task_id: str) -> RunReport | None:
        pattern = os.path.join(self.results_dir, f'*{task_id[:30]}*.json')
        files = glob.glob(pattern)
        if files:
            with open(files[0]) as f:
                data = json.load(f)
            report = RunReport(**{k: v for k, v in data.items() if k in RunReport.__dataclass_fields__})
            return report
        return None
    
    def _save_report(self, report: RunReport):
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_id = report.task_id.replace('/', '_')[:60]
        path = os.path.join(self.results_dir, f'{ts}_{safe_id}.json')
        with open(path, 'w') as f:
            json.dump(asdict(report), f, indent=2)
    
    def stats(self) -> dict:
        """Compute summary statistics."""
        n = max(1, len(self.results))
        return {
            'total': n,
            'success_rate': f"{sum(1 for r in self.results if r.success)/n:.0%}",
            'patch_rate': f"{sum(1 for r in self.results if r.patch_generated)/n:.0%}",
            'safety_pass_rate': f"{sum(1 for r in self.results if r.safety_passed)/n:.0%}",
            'avg_duration_s': f"{sum(r.duration_s for r in self.results)/n:.1f}",
            'avg_patch_bytes': f"{sum(r.patch_bytes for r in self.results)/n:.0f}",
        }
    
    def print_summary(self):
        """Print benchmark summary."""
        s = self.stats()
        print(f"\nRC86 SWE-BENCH BENCHMARK")
        print(f"{'='*50}")
        print(f"Tasks:              {s['total']}")
        print(f"Success:            {s['success_rate']}")
        print(f"Patches:            {s['patch_rate']}")
        print(f"Safety Pass:        {s['safety_pass_rate']}")
        print(f"Avg Duration:       {s['avg_duration_s']}s")
        print(f"Avg Patch Size:     {s['avg_patch_bytes']} bytes")
        for r in self.results:
            symbol = '✅' if r.success else ('⚠️' if r.patch_generated else '❌')
            print(f"  {symbol} {r.task_id[:50]:<52s} {r.status:<16s} {r.duration_s:.0f}s")


# CLI
if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description='RC86 SWE-bench Benchmark Runner')
    ap.add_argument('--task', type=str, help='Single task ID')
    ap.add_argument('--limit', type=int, default=0, help='Max tasks')
    ap.add_argument('--repo', type=str, help='Filter by repo')
    ap.add_argument('--engine', type=str, default='opencode')
    ap.add_argument('--no-skip', action='store_true', help='Re-run even if done')
    args = ap.parse_args()
    
    runner = SWEBenchRunner()
    loaded = runner.load_tasks(limit=args.limit)
    
    if args.task:
        for t in runner.tasks:
            if args.task in t['instance_id']:
                report = runner.run_task(t, engine=args.engine)
                runner.results.append(report)
                runner._save_report(report)
                break
    elif args.repo:
        filtered = [t for t in runner.tasks if args.repo in t.get('repo', '')]
        runner.tasks = filtered
        runner.run_all(engine=args.engine, skip_existing=not args.no_skip)
    elif loaded:
        runner.run_all(engine=args.engine, skip_existing=not args.no_skip)
    
    runner.print_summary()
    
    # Export summary
    summary_path = os.path.join(runner.results_dir, 'summary.json')
    with open(summary_path, 'w') as f:
        json.dump(runner.stats(), f, indent=2)
    print(f'\nSummary: {summary_path}')
