#!/usr/bin/env python3
"""
OPENCODE VS CODEX — Resumable Benchmark (RC34B)
Saves results incrementally. Supports --resume, --limit, --engine, --timeout.

Usage:
  python3 scripts/oc_vs_codex.py --limit 1 --engine opencode --resume
  python3 scripts/oc_vs_codex.py --limit 10 --engine both --timeout 90 --resume

Author: Hermes + David | Coding Tentacle 2026
"""
import sys, os, time, json, subprocess, argparse

sys.path.insert(0, '/home/boobi/GEHIRN_BIBLIOTHEK')
sys.path.insert(0, '/home/boobi/GEHIRN_BIBLIOTHEK/src/coding_tentacle')

from coding_tentacle.orchestrator.shadow_mode import ShadowModeRunner, GitHubIssueRun
from coding_tentacle.orchestrator.metabrain import MetaBrain, SafetyBrain
from coding_tentacle.safety.inhibitory_control import InhibitoryControl
from coding_tentacle.knowledge.security_store import create_seed_security_store
from coding_tentacle.patch.diff_generator import DiffGenerator
from coding_tentacle.patch.patch_suggestion import PatchSuggestionEngine
from coding_tentacle.classifier.semantic_classifier import SemanticBugClassifier
from coding_tentacle.memory.bug_learning_memory import BugLearningMemory

OPencode = '/usr/local/bin/opencode'
CODEX = '/home/boobi/.npm-global/bin/codex'
RESULTS_FILE = os.path.expanduser('~/Schreibtisch/CT_LLM_ENGINE_COMPARISON_REPORT.jsonl')

# 10 diverse test issues
ISSUES = [
    ("NullPointer in User.get_profile()", "NoneType has no attribute at views.py:42", "NullPointer"),
    ("ImportError: werkzeug.urls moved", "Cannot import url_quote from werkzeug.urls", "ImportError"),
    ("TypeError: int + str concatenation", "total = count + 'items' fails", "TypeError"),
    ("KeyError in config['database']", "Config dict missing database key", "KeyError"),
    ("IndexError in list access", "IndexError: list index out of bounds at line 15", "IndexError"),
    ("ValueError in int conversion", "ValueError: invalid literal for int()", "ValueError"),
    ("RaceCondition in counter++", "Concurrent requests cause data race", "RaceCondition"),
    ("FileNotFoundError config.yaml", "Missing config.yaml after deploy", "FileNotFoundError"),
    ("SQL Injection via raw query", "User input unsanitized in SQL query — DROP TABLE risk", "SecurityRisk"),
    ("RecursionError max depth", "Maximum recursion depth exceeded in tree walk", "RecursionError"),
]


def load_done():
    """Load already completed issue/engine pairs from JSONL."""
    done = set()
    if not os.path.exists(RESULTS_FILE):
        return done
    with open(RESULTS_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    r = json.loads(line)
                    done.add((r.get('issue_id'), r.get('engine')))
                except:
                    pass
    return done


def save_result(result):
    """Append a result line to JSONL."""
    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
    with open(RESULTS_FILE, 'a') as f:
        f.write(json.dumps(result, default=str) + '\n')


def call_engine(engine_path, engine_name, prompt, timeout=60):
    """Call an LLM engine. Returns (success, output, time_s)."""
    t0 = time.time()
    try:
        if 'opencode' in engine_name.lower():
            cmd = [engine_path, 'run', prompt]
        else:
            cmd = [engine_path, 'exec', '-m', prompt]  # -m for model-agnostic
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd='/tmp')
        dt = round(time.time() - t0, 1)
        return True, (result.stdout + result.stderr)[:600], dt
    except FileNotFoundError:
        return False, f"{engine_name} NOT FOUND", 0
    except subprocess.TimeoutExpired:
        return False, f"TIMEOUT after {timeout}s", timeout
    except Exception as e:
        return False, f"ERROR: {str(e)[:200]}", round(time.time() - t0, 1)


def main():
    parser = argparse.ArgumentParser(description='OpenCode vs Codex Benchmark')
    parser.add_argument('--limit', type=int, default=10, help='Number of issues (default 10)')
    parser.add_argument('--engine', choices=['opencode', 'codex', 'both'], default='both')
    parser.add_argument('--timeout', type=int, default=60, help='Per-engine timeout in seconds')
    parser.add_argument('--resume', action='store_true', help='Skip already completed results')
    args = parser.parse_args()
    
    # Setup CT
    sec = create_seed_security_store()
    ic = InhibitoryControl(security_store=sec)
    safety = SafetyBrain(ic=ic, security_store=sec)
    mb = MetaBrain(safety=safety)
    ps = PatchSuggestionEngine()
    dg = DiffGenerator(safety_brain=safety, patch_suggestion=ps)
    sc = SemanticBugClassifier()
    blm = BugLearningMemory(db_path=os.path.join('/tmp', 'bench_oc_vs_cx.db'))
    runner = ShadowModeRunner(meta_brain=mb, teacher=None, diff_generator=dg, sandbox_runner=None)
    
    done = load_done() if args.resume else set()
    results = []
    engines_to_test = ['opencode', 'codex'] if args.engine == 'both' else [args.engine]
    
    print("╔══════════════════════════════════════════════╗")
    print("║  OPENCODE vs CODEX — Resumable Benchmark     ║")
    print(f"║  Issues: {min(args.limit, len(ISSUES))} | Engines: {args.engine} | Timeout: {args.timeout}s ║")
    print("╚══════════════════════════════════════════════╝\n")
    
    for i in range(min(args.limit, len(ISSUES))):
        title, body, expected_bt = ISSUES[i]
        print(f"═══ #{i+1} {title[:55]} ═══")
        
        # CT Analysis
        issue = GitHubIssueRun("https://github.com/test/repo", "#1", title, body)
        report = runner.analyze_issue(issue)
        bt = report.detected_bug_type
        if bt == 'Unknown':
            bt, _ = sc.classify(f"{title} {body}")
        
        print(f"  CT: {bt} (expected: {expected_bt}) match={bt==expected_bt}")
        
        # Safety check first
        dangerous, patterns = blm.is_dangerous_pattern(f"{title} {body}")
        if dangerous:
            print(f"  🔴 SAFETY BLOCK: {patterns} — skipping both engines")
            for eng in engines_to_test:
                result = {'issue_id': i, 'issue': title[:50], 'engine': eng,
                         'bug_type': bt, 'safety_blocked': True, 'diff': False}
                save_result(result); results.append(result)
            continue
        
        # Build prompt
        prompt = f"""Fix this bug. Output ONLY the corrected code or unified diff.

BUG: {title}
DESCRIPTION: {body}
BUG TYPE: {bt}

RULES: Output only the fix. Do NOT modify files. No commits. No PRs."""
        
        for eng in engines_to_test:
            key = (i, eng)
            if key in done:
                print(f"  {eng}: ⏭️  SKIPPED (already done)")
                continue
            
            engine_path = OPencode if eng == 'opencode' else CODEX
            ok, output, dt = call_engine(engine_path, eng, prompt, timeout=args.timeout)
            
            mark = '✅' if ok else '❌'
            print(f"  {eng} {mark} ({dt}s) → {output[:80].replace(chr(10), ' ')}...")
            
            result = {'issue_id': i, 'issue': title[:50], 'engine': eng,
                     'bug_type': bt, 'expected': expected_bt, 'ct_match': bt == expected_bt,
                     'engine_ok': ok, 'runtime_s': dt, 'output_preview': output[:200]}
            save_result(result)
            results.append(result)
    
    # Quick summary
    done_count = len([r for r in results if r.get('engine_ok')])
    total_count = len(results)
    print(f"\n═══ SUMMARY ═══")
    print(f"  Results: {total_count} | Engine OK: {done_count} | Failed: {total_count - done_count}")
    print(f"  File: {RESULTS_FILE}")
    
    return results


if __name__ == "__main__":
    main()
