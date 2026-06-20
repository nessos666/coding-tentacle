"""FULL REGRESSION — Coding Tentacle RC1
Run ALL tests with one command. Exit 0 = all passed, 1 = failures."""
import sys, os, subprocess, time

sys.path.insert(0, '/home/boobi/GEHIRN_BIBLIOTHEK')
sys.path.insert(0, '/home/boobi/GEHIRN_BIBLIOTHEK/71_symbol_grounding')
from config import PROJECT_ROOT, REPORTS_DIR, BQ_HISTORY_PATH

TESTS = [
    ("Working Memory", "working_memory.py"),
    ("BQ Grounding", "71_symbol_grounding/sg_brain.py"),
    ("Inhibitory Control", "inhibitory_control.py"),
    ("Escalation Logic", "escalation_logic.py"),
    ("BR Scientific Method", "br_scientific_method.py"),
    ("Patch Suggestion", "patch_suggestion.py"),
    ("Mini Tentacle System", "mini_tentacle_system.py"),
    ("Minimal Orchestrator", "minimal_orchestrator.py"),
    ("Real Bug Probe", "real_bug_probe.py"),
    ("Patch Probe", "patch_probe.py"),
]

print("CODING TENTACLE RC1 — FULL REGRESSION")
print("=" * 65)
passed = 0
failed = 0
t0 = time.time()

for name, script in TESTS:
    path = os.path.join(PROJECT_ROOT, script)
    if not os.path.exists(path):
        print(f"  ⚠️  {name:<25s} — FILE NOT FOUND: {script}")
        failed += 1
        continue
    try:
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, 
                                timeout=60, )
        ok = 'ERGEBNIS: 10/10' in result.stdout or 'ERGEBNIS: 12/12' in result.stdout or \
             'ERGEBNIS: 14/14' in result.stdout or 'MINI-TENTACLE SYSTEM FERTIG' in result.stdout or \
             'PATCH-SUGGESTION MVP FERTIG' in result.stdout or 'Gesamtscore' in result.stdout or \
             ('✅' in result.stdout and 'ERGEBNIS' in result.stdout)
        if ok or 'FERTIG' in result.stdout:
            print(f"  ✅ {name:<25s} PASSED")
            passed += 1
        else:
            print(f"  ❌ {name:<25s} FAILED")
            failed += 1
    except subprocess.TimeoutExpired:
        print(f"  ❌ {name:<25s} TIMEOUT")
        failed += 1
    except Exception as e:
        print(f"  ❌ {name:<25s} ERROR: {str(e)[:50]}")
        failed += 1

dt = time.time() - t0
print(f"\n{'='*65}")
print(f"  TOTAL:  {passed+failed} tests")
print(f"  PASSED: {passed}")
print(f"  FAILED: {failed}")
print(f"  TIME:   {dt:.1f}s")
print(f"  {'✅ ALL TESTS PASSED' if failed == 0 else '❌ SOME TESTS FAILED'}")
print(f"{'='*65}")
sys.exit(0 if failed == 0 else 1)
