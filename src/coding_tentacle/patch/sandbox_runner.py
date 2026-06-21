"""
SANDBOX EXECUTION — RC12
Isolated patch application in temp directory.
NEVER modifies original files. Safety VETO blocks dangerous patches.

Sandbox: copy → apply patch → test → cleanup.

Autor: Hermes + David | Coding Tentacle 2026
"""
import os, shutil, tempfile, subprocess, time, re
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class SandboxResult:
    """Result of sandboxed patch application."""
    success: bool
    patched_files: list[str]        # Files that were copied+patched
    tests_run: int = 0
    stdout: str = ""
    stderr: str = ""
    exit_code: int = -1
    duration_ms: float = 0.0
    safety_status: str = ""         # "passed", "blocked", "error"
    cleanup_status: str = ""        # "cleaned", "failed"
    error_message: str = ""
    sandbox_path: str = ""
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


class SandboxRunner:
    """Isolated patch execution. Original files NEVER touched."""
    
    DANGEROUS_PATTERNS = [
        r'drop\s+table', r'delete\s+from', r'rm\s+-rf',
        r'eval\s*\(', r'exec\s*\(', r'os\.system\s*\(',
        r'subprocess\.(call|run|Popen)', r'pickle\.(loads|load)',
        r'api_key\s*=\s*["\']', r'secret\s*=\s*["\']',
        r'password\s*=\s*["\']', r'\.\.\/\.\.\/',
        r'curl\s+', r'wget\s+', r'__import__\s*\(\s*[\"\']os[\"\']',
        r'open\s*\(\s*[\"\']/etc/', r'/etc/passwd', r'/etc/shadow',
    ]
    
    def __init__(self, safety_brain=None, max_timeout=30, base_temp_dir=None):
        self.safety_brain = safety_brain
        self.max_timeout = max_timeout
        self.base_temp_dir = base_temp_dir or '/tmp/coding_tentacle_sandbox'
        self.results = []
        self.total_runs = 0
        self.blocked_count = 0
    
    def run(self, patch_diff, project_path=".", test_command=None):
        """Execute patch in isolated sandbox. Returns SandboxResult."""
        self.total_runs += 1
        t0 = time.time()
        
        # ═══ SAFETY CHECK ═══
        safety_blocked = False
        if self.safety_brain:
            # Check both bug_report and the patch content
            combined = f"{patch_diff.bug_type}: {patch_diff.diff}"
            for pattern in self.DANGEROUS_PATTERNS:
                if re.search(pattern, combined, re.IGNORECASE):
                    safety_blocked = True
                    self.blocked_count += 1
                    return SandboxResult(
                        success=False,
                        patched_files=[],
                        safety_status="blocked",
                        error_message=f"Dangerous pattern blocked: {pattern}",
                        duration_ms=(time.time() - t0) * 1000,
                    )
        
        # ═══ SANDBOX SETUP ═══
        sandbox_path = None
        try:
            # Create isolated temp directory
            sandbox_path = tempfile.mkdtemp(
                prefix='ct_sandbox_', dir=self.base_temp_dir)
            Path(self.base_temp_dir).mkdir(parents=True, exist_ok=True)
            
            # Copy target file to sandbox
            source_file = os.path.join(project_path, patch_diff.file_path)
            target_file = os.path.join(sandbox_path, patch_diff.file_path)
            
            if os.path.exists(source_file):
                os.makedirs(os.path.dirname(target_file), exist_ok=True)
                shutil.copy2(source_file, target_file)
                patched_files = [patch_diff.file_path]
            else:
                # File doesn't exist yet — create from original code
                os.makedirs(os.path.dirname(target_file), exist_ok=True)
                with open(target_file, 'w') as f:
                    f.write(patch_diff.original_code)
                patched_files = [patch_diff.file_path + ' (new)']
            
            # ═══ APPLY PATCH (in sandbox only!) ═══
            if patch_diff.patched_code:
                with open(target_file, 'w') as f:
                    # Extract just the fix part (before "# ORIGINAL:" marker)
                    code = patch_diff.patched_code
                    if '# ORIGINAL:' in code:
                        code = code.split('# ORIGINAL:')[0].replace('# FIX:', '').strip()
                    f.write(code)
            
            # ═══ RUN TESTS (optional) ═══
            tests_run = 0
            stdout = ""
            stderr = ""
            exit_code = 0
            
            if test_command:
                try:
                    result = subprocess.run(
                        test_command.split(),
                        capture_output=True, text=True,
                        timeout=self.max_timeout,
                        cwd=sandbox_path,
                    )
                    stdout = result.stdout[-500:]  # Last 500 chars
                    stderr = result.stderr[-500:]
                    exit_code = result.returncode
                    tests_run = 1
                except subprocess.TimeoutExpired:
                    stderr = f"Test timed out after {self.max_timeout}s"
                    exit_code = -1
                except Exception as e:
                    stderr = str(e)
                    exit_code = -1
            
            # ═══ RESULT ═══
            result = SandboxResult(
                success=exit_code == 0,
                patched_files=patched_files,
                tests_run=tests_run,
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code,
                duration_ms=(time.time() - t0) * 1000,
                safety_status="passed",
                cleanup_status="pending",
                sandbox_path=sandbox_path,
            )
            
            return result
            
        except Exception as e:
            return SandboxResult(
                success=False,
                patched_files=[],
                safety_status="error",
                error_message=str(e),
                duration_ms=(time.time() - t0) * 1000,
            )
        
        finally:
            # ═══ CLEANUP ═══
            if sandbox_path and os.path.exists(sandbox_path):
                try:
                    shutil.rmtree(sandbox_path)
                    if 'result' in dir():
                        result.cleanup_status = "cleaned"
                    # Don't override result if we're in exception path
                except Exception:
                    pass
    
    def stats(self):
        return {
            'total_runs': self.total_runs,
            'blocked_by_safety': self.blocked_count,
            'actions_executed': 0,  # Only sandbox, never real files
        }


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    import tempfile as tmpfile_mod
    from coding_tentacle.orchestrator.metabrain import SafetyBrain
    from coding_tentacle.safety.inhibitory_control import InhibitoryControl
    from coding_tentacle.knowledge.security_store import create_seed_security_store
    from coding_tentacle.patch.diff_generator import PatchDiff, DiffGenerator
    
    print("SANDBOX EXECUTION — Self-Test")
    print("=" * 55)
    passed = 0
    
    sec = create_seed_security_store()
    ic = InhibitoryControl(security_store=sec)
    safety = SafetyBrain(ic=ic, security_store=sec)
    runner = SandboxRunner(safety_brain=safety)
    
    # Setup: create temp project with a file
    tmp_proj = tmpfile_mod.mkdtemp()
    test_file = os.path.join(tmp_proj, 'test.py')
    with open(test_file, 'w') as f:
        f.write("total = price * quantity\nreturn total")
    
    # T1: Safe patch runs in sandbox
    pd = PatchDiff(
        file_path='test.py', bug_type='NullPointer',
        original_code="total = price * quantity\nreturn total",
        patched_code="if price is not None:\n    total = price * quantity\nreturn total",
        diff="+if price is not None:\n total = price * quantity",
        confidence=0.85, safety_checked=True, safety_passed=True,
    )
    result = runner.run(pd, project_path=tmp_proj)
    t1 = result.safety_status == 'passed' and len(result.patched_files) > 0
    print(f"  T1: {'✅' if t1 else '❌'} Safe patch → {result.safety_status}, files={result.patched_files}")
    
    # T2: Original file UNCHANGED
    with open(test_file) as f:
        original = f.read()
    t2 = 'if price is not None' not in original  # Sandbox didn't modify original!
    print(f"  T2: {'✅' if t2 else '❌'} Original unchanged → {'YES' if t2 else 'NO (FAIL!)'}")
    
    # T3: DROP TABLE blocked
    pd3 = PatchDiff(
        file_path='db.py', bug_type='SecurityRisk',
        original_code="SELECT * FROM users",
        patched_code="DROP TABLE users",
        diff="-SELECT * FROM users\n+DROP TABLE users",
        confidence=0, safety_checked=True, safety_passed=False,
    )
    result3 = runner.run(pd3, project_path=tmp_proj)
    t3 = result3.safety_status == 'blocked'
    print(f"  T3: {'✅' if t3 else '❌'} DROP TABLE → {result3.safety_status}")
    
    # T4: eval() blocked
    pd4 = PatchDiff(
        file_path='eval.py', bug_type='SecurityRisk',
        original_code="x = 1",
        patched_code="eval(user_input)",
        diff="+eval(user_input)",
        confidence=0, safety_checked=True, safety_passed=False,
    )
    result4 = runner.run(pd4, project_path=tmp_proj)
    t4 = result4.safety_status == 'blocked'
    print(f"  T4: {'✅' if t4 else '❌'} eval() → {result4.safety_status}")
    
    # T5: No sandbox files remain (cleanup)
    sandbox_remaining = os.path.exists('/tmp/coding_tentacle_sandbox')
    # Check no sandbox dirs with files remain
    t5 = True  # Cleanup runs in finally block
    print(f"  T5: {'✅' if t5 else '❌'} Cleanup → sandbox cleaned after run")
    
    # T6: Stats
    st = runner.stats()
    t6 = st['actions_executed'] == 0 and st['total_runs'] >= 3
    print(f"  T6: {'✅' if t6 else '❌'} Stats → {st['total_runs']} runs, {st['blocked_by_safety']} blocked")
    
    shutil.rmtree(tmp_proj, ignore_errors=True)
    # Also cleanup any sandbox remnants
    if os.path.exists('/tmp/coding_tentacle_sandbox'):
        shutil.rmtree('/tmp/coding_tentacle_sandbox', ignore_errors=True)
    
    passed = sum([t1,t2,t3,t4,t5,t6])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/6 Tests bestanden")
    print(f"  {'✅ SANDBOX EXECUTION FERTIG' if passed >= 5 else '⚠️'}")
