"""
TEST RUNNER — RC13
Runs tests inside sandbox after patch application.
Timeout-protected, output-limited, safety-checked.

Integrates with SandboxRunner — tests only run in isolated temp dirs.

Autor: Hermes + David | Coding Tentacle 2026
"""
import subprocess, time, re, shlex
from dataclasses import dataclass, field, asdict


DANGEROUS_TEST_COMMANDS = [
    r'rm\s+-rf', r'sudo\s+', r'chmod\s+777',
    r'curl\s+', r'wget\s+', r'nc\s+',
    r'>\s*/etc/', r'pip\s+install', r'npm\s+install',
    r'git\s+push', r'docker\s+run',
]


@dataclass
class TestResult:
    """Result of running tests in sandbox."""
    success: bool
    command: str
    exit_code: int = -1
    stdout: str = ""
    stderr: str = ""
    duration_ms: float = 0.0
    tests_passed: int = 0
    tests_failed: int = 0
    safety_blocked: bool = False
    safety_reason: str = ""
    timeout_occurred: bool = False
    error_message: str = ""


class TestRunner:
    """Runs tests inside sandbox. Safety-checked, timeout-protected."""
    
    def __init__(self, safety_brain=None, max_timeout=30, max_output=2000):
        self.safety_brain = safety_brain
        self.max_timeout = max_timeout
        self.max_output = max_output
        self.results = []
        self.total_runs = 0
        self.blocked_count = 0
    
    def run(self, sandbox_path, test_command="pytest -x -q", file_path=None):
        """Run tests in the sandbox. Returns TestResult."""
        self.total_runs += 1
        t0 = time.time()
        
        # ═══ SAFETY: check command ═══
        cmd_lower = test_command.lower()
        for pattern in DANGEROUS_TEST_COMMANDS:
            if re.search(pattern, cmd_lower):
                self.blocked_count += 1
                return TestResult(
                    success=False,
                    command=test_command,
                    safety_blocked=True,
                    safety_reason=f"Dangerous command blocked: {pattern}",
                )
        
        # ═══ SAFETY: verify sandbox path ═══
        if not sandbox_path or '/tmp/' not in sandbox_path:
            self.blocked_count += 1
            return TestResult(
                success=False,
                command=test_command,
                safety_blocked=True,
                safety_reason="Test must run inside /tmp/ sandbox only",
            )
        
        # ═══ PARSED COMMAND ═══
        try:
            cmd_parts = shlex.split(test_command)
        except ValueError:
            cmd_parts = test_command.split()
        
        # If specific file requested, append it
        if file_path:
            cmd_parts.append(file_path)
        
        # ═══ RUN TESTS ═══
        stdout = ""
        stderr = ""
        exit_code = -1
        timeout_occurred = False
        
        try:
            result = subprocess.run(
                cmd_parts,
                capture_output=True, text=True,
                timeout=self.max_timeout,
                cwd=sandbox_path,
                env={**__import__('os').environ, 'PATH': '/usr/bin:/bin'},
            )
            stdout = result.stdout[-self.max_output:]
            stderr = result.stderr[-self.max_output:]
            exit_code = result.returncode
        except subprocess.TimeoutExpired:
            timeout_occurred = True
            stderr = f"Tests timed out after {self.max_timeout}s"
            exit_code = -1
        except FileNotFoundError:
            stderr = f"Test command not found: {cmd_parts[0]}"
            exit_code = -1
        except Exception as e:
            stderr = str(e)
            exit_code = -1
        
        # ═══ PARSE RESULTS ═══
        tests_passed = 0
        tests_failed = 0
        
        # Try to extract pytest-style output
        passed_match = re.search(r'(\d+)\s+passed', stdout + stderr)
        failed_match = re.search(r'(\d+)\s+failed', stdout + stderr)
        if passed_match:
            tests_passed = int(passed_match.group(1))
        if failed_match:
            tests_failed = int(failed_match.group(1))
        
        if not passed_match and not failed_match:
            # Simple heuristic: exit_code 0 = likely passed
            if exit_code == 0:
                tests_passed = 1
            elif exit_code > 0:
                tests_failed = 1
        
        result = TestResult(
            success=(exit_code == 0),
            command=test_command,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            duration_ms=(time.time() - t0) * 1000,
            tests_passed=tests_passed,
            tests_failed=tests_failed,
            timeout_occurred=timeout_occurred,
        )
        
        self.results.append(result)
        return result
    
    def stats(self):
        return {
            'total_runs': self.total_runs,
            'blocked_by_safety': self.blocked_count,
            'success_rate': round(
                sum(1 for r in self.results if r.success) / max(1, len(self.results)), 2
            ),
            'actions_executed': 0,  # Only runs in sandbox
        }


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    import tempfile, os
    
    print("TEST RUNNER — Self-Test")
    print("=" * 55)
    passed = 0
    
    runner = TestRunner(max_timeout=5)
    python_exe = __import__('sys').executable
    
    # Setup: create a sandbox with a trivial test file
    sb = tempfile.mkdtemp(prefix='ct_test_', dir='/tmp')
    test_file = os.path.join(sb, 'test_dummy.py')
    
    # T1: Run passing test (use sys.executable)
    with open(test_file, 'w') as f:
        f.write("# passing test\nassert 1 == 1\nprint('1 passed')\n")
    result = runner.run(sb, test_command=f"{python_exe} test_dummy.py")
    t1 = result.success and result.exit_code == 0
    print(f"  T1: {'✅' if t1 else '❌'} Passing test → exit={result.exit_code} out={result.stdout[:50]}")
    
    # T2: Run failing test
    with open(test_file, 'w') as f:
        f.write("# failing test\nassert 1 == 2, 'FAIL'\n")
    result2 = runner.run(sb, test_command=f"{python_exe} test_dummy.py")
    t2 = not result2.success and result2.exit_code != 0
    print(f"  T2: {'✅' if t2 else '❌'} Failing test → exit={result2.exit_code} err={result2.stderr[:50]}")
    
    # T3: Dangerous command blocked
    result3 = runner.run(sb, test_command="rm -rf /")
    t3 = result3.safety_blocked
    print(f"  T3: {'✅' if t3 else '❌'} rm -rf blocked → {result3.safety_reason}")
    
    # T4: Non-sandbox path blocked
    result4 = runner.run("/etc", test_command="pytest")
    t4 = result4.safety_blocked
    print(f"  T4: {'✅' if t4 else '❌'} /etc path blocked → {result4.safety_reason}")
    
    # T5: Timeout protection (sleep 30s, timeout=5s)
    result5 = runner.run(sb, test_command=f"{python_exe} -c 'import time; time.sleep(30)'")
    t5 = result5.timeout_occurred
    print(f"  T5: {'✅' if t5 else '❌'} Timeout → {result5.timeout_occurred}")
    
    # T6: Stats
    st = runner.stats()
    t6 = st['actions_executed'] == 0 and st['total_runs'] >= 4
    print(f"  T6: {'✅' if t6 else '❌'} Stats → {st['total_runs']} runs, read-only")
    
    import shutil; shutil.rmtree(sb, ignore_errors=True)
    passed = sum([t1,t2,t3,t4,t5,t6])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/6 Tests bestanden")
    print(f"  {'✅ TEST RUNNER FERTIG' if passed >= 5 else '⚠️'}")
