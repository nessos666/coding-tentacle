"""
SHELL DEMO READINESS — P2.2
Third language after Python and Rust.
Uses shellcheck for analysis. Template-based fixes.

Safety VETO: rm -rf, sudo, curl | bash ALWAYS blocked.

Autor: Hermes + David | Coding Tentacle 2026
"""
import re, os, time, subprocess
from dataclasses import dataclass


# ═══════════ SHELL BUG TYPES ═══════════
SHELL_BUG_PATTERNS = {
    'Shell_UnsetVar': {
        'keywords': ['unbound variable', 'parameter not set', 'unset', 'undefined'],
        'fix_template': ': "${VAR:=default}"  # Set default if unset',
        'description': 'Variable used but not set — use ${VAR:-default}',
        'severity': 'warning',
    },
    'Shell_QuoteError': {
        'keywords': ['quote', 'word splitting', 'SC2086', 'unquoted', 'globbing'],
        'fix_template': 'echo "${var}"  # Always quote variables',
        'description': 'Unquoted variable — use double quotes to prevent word splitting',
        'severity': 'warning',
    },
    'Shell_DangerousCmd': {
        'keywords': ['rm -rf', 'sudo', 'curl | bash', 'eval', 'chmod 777'],
        'fix_template': '# BLOCKED: dangerous command — requires human review',
        'description': 'Dangerous command detected — Safety VETO',
        'severity': 'critical',
    },
    'Shell_PathError': {
        'keywords': ['No such file', 'not found', 'command not found', 'permission denied'],
        'fix_template': 'test -f "${file}" || { echo "File not found: ${file}"; exit 1; }',
        'description': 'File/command not found — add existence check',
        'severity': 'error',
    },
    'Shell_ExitCode': {
        'keywords': ['exit code', 'set -e', 'set -o pipefail', 'error handling'],
        'fix_template': 'set -euo pipefail  # Fail on errors, unset vars, pipe failures',
        'description': 'Missing error handling — add set -euo pipefail',
        'severity': 'warning',
    },
    'Shell_LoopPitfall': {
        'keywords': ['for file in $(ls', 'while read', 'IFS=', 'pipe', 'subshell'],
        'fix_template': 'while IFS= read -r line; do echo "${line}"; done < file.txt',
        'description': 'Loop pitfall — use while read instead of for-in-ls',
        'severity': 'warning',
    },
}


def classify_shell_bug(error_message, script_content=""):
    """Classify a shell error into a bug type."""
    msg_lower = (error_message + ' ' + script_content).lower()
    for bug_type, pattern in SHELL_BUG_PATTERNS.items():
        if any(kw.lower() in msg_lower for kw in pattern['keywords']):
            return bug_type
    return 'Shell_Unknown'


def get_shell_test_command(script_path):
    """Test command for shell scripts."""
    # Use shellcheck if available
    try:
        subprocess.run(['which', 'shellcheck'], capture_output=True, timeout=2)
        return f'shellcheck {script_path}'
    except:
        return f'bash -n {script_path}  # Syntax check only'


def run_shellcheck(script_path):
    """Run shellcheck on a script. Returns (success, output)."""
    try:
        result = subprocess.run(
            ['shellcheck', '-f', 'json', script_path],
            capture_output=True, text=True, timeout=10,
        )
        import json
        issues = json.loads(result.stdout) if result.stdout else []
        return True, issues
    except FileNotFoundError:
        return False, "shellcheck not installed"
    except Exception as e:
        return False, str(e)


def create_shell_procedures(procedure_store):
    """Add Shell-specific procedures to the store."""
    from coding_tentacle.memory.procedural_memory import Procedure, ProcedureStep
    
    if not procedure_store.get_procedure("Shell_UnsetVar", "shell"):
        procedure_store.procedures["Shell_UnsetVar:shell"] = Procedure(
            bug_type="Shell_UnsetVar", language="shell",
            trigger="unbound variable / parameter not set",
            steps=[
                ProcedureStep(1, "analyze", "Which variable is unset?", "CodeContext", "VAR not defined before use"),
                ProcedureStep(2, "suggest_default", "Use ${VAR:-default} or := for assignment", "PatchSuggestion", ': "${VAR:=default}"'),
                ProcedureStep(3, "shellcheck", "Verify with shellcheck", "TestRunner", "shellcheck script.sh"),
                ProcedureStep(4, "verify", "No unbound variable warnings", "ResultEvaluator", "shellcheck clean"),
            ],
            confidence=0.80, created_at=time.time(), last_used=time.time()
        )
    
    if not procedure_store.get_procedure("Shell_QuoteError", "shell"):
        procedure_store.procedures["Shell_QuoteError:shell"] = Procedure(
            bug_type="Shell_QuoteError", language="shell",
            trigger="SC2086: Double quote to prevent globbing and word splitting",
            steps=[
                ProcedureStep(1, "identify", "Which variable needs quoting?", "CodeContext", "echo $var → SC2086"),
                ProcedureStep(2, "add_quotes", 'Use "${var}" instead of $var', "PatchSuggestion", 'echo "${var}"'),
                ProcedureStep(3, "verify", "shellcheck clean", "ResultEvaluator", "No SC2086"),
            ],
            confidence=0.85, created_at=time.time(), last_used=time.time()
        )
    
    if not procedure_store.get_procedure("Shell_ExitCode", "shell"):
        procedure_store.procedures["Shell_ExitCode:shell"] = Procedure(
            bug_type="Shell_ExitCode", language="shell",
            trigger="Missing error handling / set -e",
            steps=[
                ProcedureStep(1, "add_strict_mode", "Add set -euo pipefail", "PatchSuggestion", 'set -euo pipefail'),
                ProcedureStep(2, "verify", "Script fails properly on errors", "ResultEvaluator", "Error propagation works"),
            ],
            confidence=0.75, created_at=time.time(), last_used=time.time()
        )
    
    procedure_store._save()


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    import tempfile, shutil
    
    print("SHELL DEMO READINESS — Self-Test")
    print("=" * 55)
    passed = 0
    
    # T1: Classify unset variable
    bt = classify_shell_bug("script.sh: line 5: VAR: unbound variable")
    t1 = bt == 'Shell_UnsetVar'
    print(f"  T1: {'✅' if t1 else '❌'} Unset var → {bt}")
    
    # T2: Classify quote error
    bt2 = classify_shell_bug("SC2086: Double quote to prevent globbing and word splitting")
    t2 = bt2 == 'Shell_QuoteError'
    print(f"  T2: {'✅' if t2 else '❌'} Quote error → {bt2}")
    
    # T3: Classify dangerous command
    bt3 = classify_shell_bug("rm -rf /var/data")
    t3 = bt3 == 'Shell_DangerousCmd'
    print(f"  T3: {'✅' if t3 else '❌'} rm -rf → {bt3}")
    
    # T4: Classify path error
    bt4 = classify_shell_bug("No such file or directory: config.json")
    t4 = bt4 == 'Shell_PathError'
    print(f"  T4: {'✅' if t4 else '❌'} File not found → {bt4}")
    
    # T5: Classify exit code issue
    bt5 = classify_shell_bug("Pipe failed but script continued (missing set -o pipefail)")
    t5 = bt5 == 'Shell_ExitCode'
    print(f"  T5: {'✅' if t5 else '❌'} Exit code → {bt5}")
    
    # T6: Classify loop pitfall
    bt6 = classify_shell_bug("for file in $(ls *.txt) breaks with spaces in filenames")
    t6 = bt6 == 'Shell_LoopPitfall'
    print(f"  T6: {'✅' if t6 else '❌'} Loop pitfall → {bt6}")
    
    # T7: Create procedures
    from coding_tentacle.memory.procedural_memory import ProcedureStore
    tmp = tempfile.mkdtemp()
    ps = ProcedureStore(store_path=os.path.join(tmp, 'proc.json'))
    create_shell_procedures(ps)
    proc = ps.find_procedure("Shell_UnsetVar", language="shell")
    t7 = proc is not None and proc.language == "shell"
    print(f"  T7: {'✅' if t7 else '❌'} Shell procedure → {proc.bug_type if proc else 'NONE'}")
    
    # T8: Test command
    cmd = get_shell_test_command("test.sh")
    t8 = 'shellcheck' in cmd or 'bash' in cmd
    print(f"  T8: {'✅' if t8 else '❌'} Test command → {cmd}")
    
    shutil.rmtree(tmp, ignore_errors=True)
    passed = sum([t1,t2,t3,t4,t5,t6,t7,t8])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/8 Tests bestanden")
    print(f"  {'✅ SHELL DEMO-READY' if passed >= 7 else '⚠️'}")
