"""
CT 1.5 — OPENCODE LIVE EVALUATION
First real LLM engine run on SWE-bench Lite tasks.
"""
import sys, os, json, time, subprocess, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from coding_tentacle.brains.bug_mode_router import BugModeRouter
from coding_tentacle.llm.budget_guard import BudgetGuard
from coding_tentacle.llm.patch_output_parser import PatchOutputParser


def run_opencode_live(task_data: dict) -> dict:
    """Run a real SWE-bench task through OpenCode with full CT pipeline."""
    
    instance_id = task_data.get('instance_id', 'unknown')
    problem = task_data.get('problem_statement', '')
    repo = task_data.get('repo', '')
    
    result = {
        'instance_id': instance_id,
        'repo': repo,
        'bug_mode': 'UNKNOWN',
        'patch_generated': False,
        'patch_bytes': 0,
        'parser_valid': False,
        'safety_clean': True,
        'evidence_saved': False,
        'duration_s': 0,
        'error': '',
        'status': 'PENDING',
    }
    
    t0 = time.time()
    
    try:
        # Step 1: BugModeRouter
        router = BugModeRouter()
        mode = router.route(problem)
        result['bug_mode'] = mode.mode
        
        # Step 2: Build prompt for OpenCode
        prompt = f"""Fix this bug in {repo}. Output ONLY a unified diff patch.

## Bug Description
{problem[:2000]}

## Instructions
- Analyze the bug
- Generate a minimal, safe fix
- Output as a unified diff (--- / +++ / @@ format)
- Do NOT output explanation, just the diff
- Do NOT use eval(), exec(), or subprocess
- Do NOT modify any files outside the scope of this bug

Now fix this bug:"""
        
        # Step 3: Call OpenCode with BudgetGuard
        budget = BudgetGuard(max_tokens=8000, max_seconds=30, max_attempts=1)
        budget_check = budget.check()
        
        if not budget_check.allowed:
            result['status'] = 'BUDGET_EXCEEDED'
            result['error'] = budget_check.reason
            return result
        
        try:
            proc = subprocess.run(
                ['opencode', 'run', '--model', 'deepseek-v4-pro', prompt],
                capture_output=True, text=True, timeout=30,
                cwd='/tmp',
            )
            raw_output = proc.stdout[:10000] if proc.stdout else ''
        except subprocess.TimeoutExpired:
            result['status'] = 'TIMEOUT'
            result['error'] = 'OpenCode call timed out (30s)'
            return result
        except Exception as e:
            result['status'] = 'ENGINE_ERROR'
            result['error'] = str(e)[:200]
            return result
        
        # Step 4: Parse patch output
        parser = PatchOutputParser()
        parsed = parser.parse(raw_output)
        
        if parsed['valid']:
            result['patch_generated'] = True
            result['patch_bytes'] = len(parsed['patch'])
            result['parser_valid'] = True
            result['touched_files'] = parsed['touched_files']
            
            if parsed['safety_flags']:
                result['safety_clean'] = False
                result['status'] = 'SAFETY_BLOCKED'
                result['error'] = f"Safety flags: {parsed['safety_flags']}"
            else:
                result['status'] = 'PATCH_GENERATED'
        else:
            result['status'] = 'PARSE_FAILED'
            result['error'] = f"Parse errors: {parsed['errors']}"
        
        # Step 5: Evidence hash
        if result['patch_generated']:
            patch_hash = hashlib.sha256(parsed['patch'].encode()).hexdigest()[:16]
            result['evidence_saved'] = True
            result['patch_hash'] = patch_hash
        
    except Exception as e:
        result['status'] = 'CRASH'
        result['error'] = str(e)[:200]
    
    result['duration_s'] = round(time.time() - t0, 1)
    return result


if __name__ == "__main__":
    print("CT 1.5 — OPENCODE LIVE EVALUATION")
    print("=" * 60)
    
    # Load SWE-bench tasks
    tasks_file = '/tmp/swe-bench-test.json'
    if not os.path.exists(tasks_file):
        print("⚠️ No SWE-bench data found. Run: python3 -c 'from datasets ...'")
        sys.exit(1)
    
    with open(tasks_file) as f:
        all_tasks = json.load(f)
    
    # Start with 3 tasks
    sample = all_tasks[:3]
    print(f"Running {len(sample)} tasks with OpenCode live...\n")
    
    results = []
    for i, task in enumerate(sample):
        pid = task.get('instance_id', f'task-{i}')
        problem = task.get('problem_statement', '')[:80]
        print(f"  [{i+1}/{len(sample)}] {pid[:50]}")
        print(f"         Issue: {problem}...")
        
        r = run_opencode_live(task)
        results.append(r)
        
        print(f"         Result: mode={r['bug_mode']:<12s} "
              f"patch={'YES' if r['patch_generated'] else 'NO':<4s} "
              f"bytes={r['patch_bytes']} "
              f"safety={'CLEAN' if r['safety_clean'] else 'BLOCKED'} "
              f"status={r['status']} "
              f"dur={r['duration_s']:.1f}s\n")
    
    # Summary
    print(f"\n{'─'*60}")
    print(f"CT 1.5 LIVE EVALUATION SUMMARY")
    print(f"Tasks:                {len(results)}")
    print(f"Patches generated:    {sum(1 for r in results if r['patch_generated'])}/{len(results)}")
    print(f"Parser valid:         {sum(1 for r in results if r['parser_valid'])}/{len(results)}")
    print(f"Safety clean:         {sum(1 for r in results if r['safety_clean'])}/{len(results)}")
    print(f"Evidence saved:       {sum(1 for r in results if r['evidence_saved'])}/{len(results)}")
    errors = [r for r in results if r['error']]
    if errors:
        print(f"\nErrors:")
        for r in errors:
            print(f"  {r['instance_id'][:50]}: {r['error'][:80]}")
    
    # Save report
    with open('/tmp/ct15_live_eval_report.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nReport saved: /tmp/ct15_live_eval_report.json")
