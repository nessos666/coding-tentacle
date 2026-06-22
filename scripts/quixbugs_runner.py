"""
QUIXBUGS BENCHMARK RUNNER — RC31
Runs Coding Tentacle against the QuixBugs benchmark.
40 Python bugs, 14 defect classes. Shadow mode only.

Author: Hermes + David | Coding Tentacle 2026
"""
import sys, os, time, json, tempfile, shutil, subprocess
sys.path.insert(0, '/home/boobi/GEHIRN_BIBLIOTHEK')
sys.path.insert(0, '/home/boobi/GEHIRN_BIBLIOTHEK/src/coding_tentacle')

from coding_tentacle.config import Config
from coding_tentacle.orchestrator.shadow_mode import ShadowModeRunner, GitHubIssueRun
from coding_tentacle.orchestrator.metabrain import MetaBrain, SafetyBrain
from coding_tentacle.safety.inhibitory_control import InhibitoryControl
from coding_tentacle.knowledge.security_store import create_seed_security_store
from coding_tentacle.orchestrator.teacher_student import Teacher
from coding_tentacle.patch.diff_generator import DiffGenerator
from coding_tentacle.patch.patch_suggestion import PatchSuggestionEngine
from coding_tentacle.patch.sandbox_runner import SandboxRunner
from coding_tentacle.patch.test_runner import TestRunner
from coding_tentacle.memory.procedural_memory import ProcedureStore
from coding_tentacle.memory.skill_compiler import SkillStore
from coding_tentacle.classifier.semantic_classifier import SemanticBugClassifier
from coding_tentacle.orchestrator.skeptic_brain import SkepticBrain

QB_PATH = '/tmp/QuixBugs'
BUGGY_DIR = os.path.join(QB_PATH, 'python_programs')
CORRECT_DIR = os.path.join(QB_PATH, 'correct_python_programs')

# Bug type mapping from QuixBugs defect classes
DEFECT_CLASSES = {
    'bitcount': 'Performance', 'breadth_first_search': 'Performance',
    'bucketsort': 'IndexError', 'depth_first_search': 'Performance',
    'detect_cycle': 'LogicError', 'find_first_in_sorted': 'IndexError',
    'find_in_sorted': 'IndexError', 'flatten': 'TypeError',
    'gcd': 'ValueError', 'get_factors': 'Performance',
    'hanoi': 'RecursionError', 'is_valid_parenthesization': 'LogicError',
    'kheapsort': 'IndexError', 'knapsack': 'Performance',
    'kth': 'IndexError', 'levenshtein': 'Performance',
    'lis': 'Performance', 'longest_common_subsequence': 'Performance',
    'max_sublist_sum': 'Performance', 'mergesort': 'IndexError',
    'minimum_spanning_tree': 'Performance', 'next_palindrome': 'LogicError',
    'next_permutation': 'LogicError', 'pascal': 'IndexError',
    'possible_change': 'Performance', 'powerset': 'Performance',
    'quicksort': 'IndexError', 'reverse_linked_list': 'NullPointer',
    'rpn_eval': 'ValueError', 'shortest_path_length': 'Performance',
    'shortest_path_lengths': 'Performance', 'shortest_paths': 'Performance',
    'shunting_yard': 'LogicError', 'sieve': 'Performance',
    'sqrt': 'ValueError', 'subsequences': 'Performance',
    'to_base': 'ValueError', 'topological_ordering': 'LogicError',
    'wrap': 'IndexError',
}


def run_quixbugs_benchmark():
    """Run CT against all 40 QuixBugs Python programs."""
    print("╔══════════════════════════════════════════════╗")
    print("║  CODING TENTACLE — QuixBugs Benchmark        ║")
    print("║  40 Python bugs | 14 defect classes          ║")
    print("╚══════════════════════════════════════════════╝\n")
    
    # Setup pipeline
    cfg = Config()
    sec = create_seed_security_store()
    ic = InhibitoryControl(security_store=sec)
    safety = SafetyBrain(ic=ic, security_store=sec)
    mb = MetaBrain(safety=safety)
    ps_store = ProcedureStore(config=cfg)
    sk_store = SkillStore(config=cfg)
    teacher = Teacher(procedural_memory=ps_store, skill_store=sk_store)
    ps = PatchSuggestionEngine()
    dg = DiffGenerator(safety_brain=safety, patch_suggestion=ps)
    sr = SandboxRunner(safety_brain=safety)
    tr = TestRunner(max_timeout=10)
    sc = SemanticBugClassifier()
    sb = SkepticBrain()
    
    runner = ShadowModeRunner(meta_brain=mb, teacher=teacher, 
                              diff_generator=dg, sandbox_runner=sr)
    
    # Get all buggy Python files
    bug_files = sorted([f for f in os.listdir(BUGGY_DIR) if f.endswith('.py') 
                        and not f.endswith('_test.py')])
    
    results = []
    t0_all = time.time()
    
    for bug_file in bug_files:
        bug_name = bug_file.replace('.py', '')
        bug_type = DEFECT_CLASSES.get(bug_name, 'Unknown')
        buggy_path = os.path.join(BUGGY_DIR, bug_file)
        correct_path = os.path.join(CORRECT_DIR, bug_file)
        test_file = os.path.join(BUGGY_DIR, f"{bug_name}_test.py")
        
        t0 = time.time()
        result = {'bug': bug_name, 'language': 'python', 'expected_type': bug_type}
        
        try:
            # Read buggy code
            with open(buggy_path) as f:
                buggy_code = f.read()
            
            # Run through CT pipeline
            issue = GitHubIssueRun(
                repo_url=f"https://github.com/jkoppel/QuixBugs",
                issue_url=f"https://github.com/jkoppel/QuixBugs/blob/master/python_programs/{bug_file}",
                issue_title=f"Bug in {bug_name}",
                issue_body=buggy_code[:500],
            )
            report = runner.analyze_issue(issue)
            
            bt = report.detected_bug_type
            if bt == 'Unknown':
                bt, _ = sc.classify(buggy_code[:200])
            result['detected_type'] = bt
            result['type_match'] = (bt == bug_type or bug_type == 'Unknown')
            result['confidence'] = report.confidence
            result['diff_size'] = len(report.generated_diff)
            result['safety_events'] = len(report.safety_events)
            
            if report.generated_diff:
                # Sandbox test
                sandbox_result = sr.run(patch_diff=report.generated_diff)
                result['sandbox_success'] = sandbox_result.success
                
                # Test runner
                if os.path.exists(test_file):
                    test_cmd = f"python -m pytest {test_file} -x -q 2>&1"
                    test_result = tr.run(sandbox_result.sandbox_path, test_command=test_cmd)
                    result['tests_run'] = True
                    result['tests_passed'] = test_result.tests_passed if hasattr(test_result, 'tests_passed') else 0
                    result['fixed'] = test_result.success
                else:
                    result['tests_run'] = False
                    result['fixed'] = False
            
            # Skeptic review
            review = sb.review(bt, confidence=report.confidence, test_available=result.get('tests_run', False))
            result['skeptic_decision'] = review.suggested_action
            result['risk_score'] = review.risk_score
            
        except Exception as e:
            result['error'] = str(e)[:100]
            result['fixed'] = False
        
        result['time_ms'] = round((time.time() - t0) * 1000)
        results.append(result)
        
        status = '✅' if result.get('fixed') else ('🔴' if result.get('safety_events', 0) > 0 else '❌')
        print(f"  {status} {bug_name:<30s} bt={result.get('detected_type','?'):<15s} "
              f"diff={result.get('diff_size',0):>4d}B "
              f"fixed={result.get('fixed', False)} "
              f"{result.get('time_ms',0)}ms")
    
    total_time = time.time() - t0_all
    
    # Summary
    fixed = sum(1 for r in results if r.get('fixed'))
    blocked = sum(1 for r in results if r.get('safety_events', 0) > 0)
    diffed = sum(1 for r in results if r.get('diff_size', 0) > 0)
    tried = len(results)
    type_match = sum(1 for r in results if r.get('type_match'))
    
    print(f"\n═══ QUIXBUGS RESULTS ═══")
    print(f"  Total:    {tried}")
    print(f"  Fixed:    {fixed} ({fixed/tried*100:.0f}%)")
    print(f"  Diffed:   {diffed} ({diffed/tried*100:.0f}%)")
    print(f"  Blocked:  {blocked}")
    print(f"  Type OK:  {type_match}/{tried}")
    print(f"  Time:     {total_time:.1f}s")
    
    # By defect class
    by_class = {}
    for r in results:
        dc = DEFECT_CLASSES.get(r['bug'], 'Unknown')
        if dc not in by_class: by_class[dc] = {'total':0,'fixed':0}
        by_class[dc]['total'] += 1
        if r.get('fixed'): by_class[dc]['fixed'] += 1
    
    print(f"\n═══ BY DEFECT CLASS ═══")
    for dc in sorted(by_class.keys()):
        d = by_class[dc]
        rate = d['fixed']/d['total']*100 if d['total'] > 0 else 0
        bar = '█'*int(rate/5) + '░'*(20-int(rate/5))
        print(f"  {dc:<20s} {d['fixed']:2d}/{d['total']:2d}  {bar} {rate:.0f}%")
    
    # Save
    report_data = {
        'benchmark': 'QuixBugs', 'total': tried, 'fixed': fixed,
        'diffed': diffed, 'blocked': blocked, 'type_match': type_match,
        'time_s': total_time, 'by_class': by_class, 'results': results,
    }
    path = '/home/boobi/Schreibtisch/RC31_QUIXBUGS_RESULTS.json'
    with open(path, 'w') as f:
        json.dump(report_data, f, indent=2)
    print(f"\nReport: {path}")
    
    return results


if __name__ == "__main__":
    run_quixbugs_benchmark()
