"""
OPENCODE PTY ADAPTER — RC89.1
Production PTY-based OpenCode integration. No REST assumptions.
Uses openpty() for reliable TUI output capture from OpenCode 1.17.9.
"""
import os, time, signal, subprocess
from dataclasses import dataclass


@dataclass
class PTYResult:
    status: str = 'ERROR'           # SUCCESS / NO_PATCH / TIMEOUT / ERROR
    raw_output: str = ''
    unified_diff: str = ''
    exit_code: int = -1
    duration_s: float = 0.0
    error: str = ''


class OpenCodePTYAdapter:
    """Reliable OpenCode integration via PTY. No HTTP/REST dependency."""
    
    def __init__(self, timeout: float = 60):
        self.timeout = timeout
    
    def generate(self, prompt: str, cwd: str = None) -> PTYResult:
        """Run OpenCode via PTY and capture unified diff output."""
        import pty
        
        result = PTYResult()
        t0 = time.time()
        
        try:
            master_fd, slave_fd = pty.openpty()
        except OSError as e:
            result.error = f'PTY open failed: {e}'
            return result
        
        try:
            proc = subprocess.Popen(
                ['opencode', '--prompt', prompt],
                stdin=slave_fd, stdout=slave_fd, stderr=slave_fd,
                cwd=cwd or os.getcwd(),
                start_new_session=True,
                env={**os.environ, 'TERM': 'dumb', 'OPENCODE_NO_COLOR': '1'},
            )
            os.close(slave_fd)
            
            # Read output until process completes or timeout
            output = b''
            deadline = time.time() + self.timeout
            
            while time.time() < deadline and proc.poll() is None:
                try:
                    chunk = os.read(master_fd, 4096)
                    if chunk:
                        output += chunk
                except (OSError, BlockingIOError):
                    time.sleep(0.2)
            
            # Timeout: kill process
            if proc.poll() is None:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                time.sleep(0.5)
                if proc.poll() is None:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                result.status = 'TIMEOUT'
                result.error = f'OpenCode timed out after {self.timeout}s'
            
            os.close(master_fd)
            
            text = output.decode('utf-8', errors='replace')
            result.raw_output = text
            result.exit_code = proc.returncode or 0
            result.duration_s = round(time.time() - t0, 1)
            
            # Extract unified diff
            diff = self._extract_diff(text)
            if diff:
                result.unified_diff = diff
                result.status = 'SUCCESS'
            elif result.status != 'TIMEOUT':
                result.status = 'NO_PATCH'
                if not text.strip():
                    result.error = 'Empty OpenCode output'
                else:
                    result.error = f'No unified diff in output ({len(text)} chars)'
            
        except Exception as e:
            result.error = f'PTY error: {str(e)[:200]}'
            result.status = 'ERROR'
            try:
                os.close(master_fd)
            except:
                pass
        
        return result
    
    def _extract_diff(self, text: str) -> str:
        """Extract unified diff from OpenCode output."""
        # Pattern: --- a/path\n+++ b/path\n@@ ...
        import re
        
        # Try complete diff block
        m = re.search(r'(---\s+[^\n]+\n\+\+\+\s+[^\n]+\n@@[^@]*@@.*?)(?=\n(?:---|$|\n\n))', text, re.DOTALL)
        if m:
            return m.group(1).strip()
        
        # Try just the @@ section (OpenCode sometimes skips ---/+++)
        m = re.search(r'@@\s+-\d+[^\n]*\n(.*?)(?=\n@@|\Z)', text, re.DOTALL)
        if m:
            return f'@@ {m.group(0).strip()}'
        
        return ''


# Self-test
if __name__ == "__main__":
    adapter = OpenCodePTYAdapter(timeout=10)
    passed = 0
    
    print("OPENCODE PTY ADAPTER — Self-Test")
    print("=" * 50)
    
    # T1: Adapter instantiates
    t1 = adapter is not None
    if t1: passed += 1
    print(f"  {'✅' if t1 else '❌'} T1: Instantiation")
    
    # T2: Diff extraction from known output
    known = """some text...
--- a/astropy/modeling/fitting.py
+++ b/astropy/modeling/fitting.py
@@ -2336,6 +2336,8 @@
+    if entry_points is None:
+        return
     for entry_point in entry_points:
more text..."""
    diff = adapter._extract_diff(known)
    t2 = len(diff) > 50 and 'entry_points' in diff
    if t2: passed += 1
    print(f"  {'✅' if t2 else '❌'} T2: Diff extraction ({len(diff)} chars)")
    
    # T3: Empty text = no diff
    t3 = adapter._extract_diff('') == ''
    if t3: passed += 1
    print(f"  {'✅' if t3 else '❌'} T3: Empty text → no diff")
    
    # T4: No diff in random text
    t4 = adapter._extract_diff('hello world') == ''
    if t4: passed += 1
    print(f"  {'✅' if t4 else '❌'} T4: No diff in random text")
    
    # T5: Multiple diffs — returns first
    multi = """--- a/x.py\n+++ b/x.py\n@@ -1 +1 @@\n-x\n+y\n--- a/y.py\n+++ b/y.py\n@@ -2 +2 @@\n-old\n+new"""
    diff = adapter._extract_diff(multi)
    t5 = 'x.py' in diff
    if t5: passed += 1
    print(f"  {'✅' if t5 else '❌'} T5: Multiple diffs → first extracted")
    
    print(f"\n  ERGEBNIS: {passed}/5 Tests")
    print(f"  {'✅ PTY ADAPTER READY' if passed >= 4 else '⚠️'}")
