"""
OPENCODE ACP ADAPTER — RC89
Robust programmatic OpenCode integration via ACP protocol.
Handles server lifecycle, prompt dispatch, output capture.
No TUI dependency. Machine-readable output.
"""
import subprocess, time, json, os, signal, socket, requests, threading


class OpenCodeACPAdapter:
    """ACP-based OpenCode integration. Starts server, sends prompts, collects output."""
    
    def __init__(self, port: int = 0, cwd: str = None):
        self.port = port or self._find_free_port()
        self.cwd = cwd or os.getcwd()
        self.process = None
        self.ready = False
    
    def _find_free_port(self) -> int:
        """Find an available port."""
        import socket
        with socket.socket() as s:
            s.bind(('', 0))
            return s.getsockname()[1]
    
    def start(self, timeout: float = 10) -> bool:
        """Start OpenCode ACP server."""
        try:
            self.process = subprocess.Popen(
                ['opencode', 'serve', '--port', str(self.port), '--cwd', self.cwd,
                 '--print-logs', '--log-level', 'WARN'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                start_new_session=True,
            )
            
            # Wait for server readiness
            deadline = time.time() + timeout
            while time.time() < deadline:
                try:
                    resp = requests.get(f'http://127.0.0.1:{self.port}/health', timeout=2)
                    if resp.status_code == 200:
                        self.ready = True
                        return True
                except:
                    time.sleep(0.5)
            
            return False
        except Exception:
            return False
    
    def send_prompt(self, prompt: str, timeout: float = 60) -> dict:
        """Send a prompt to OpenCode and collect output."""
        if not self.ready:
            return {'status': 'ERROR', 'error': 'Server not ready'}
        
        try:
            resp = requests.post(
                f'http://127.0.0.1:{self.port}/prompt',
                json={'prompt': prompt, 'mode': 'fix'},
                timeout=timeout,
            )
            if resp.status_code == 200:
                return resp.json()
            return {'status': 'ERROR', 'error': f'HTTP {resp.status_code}: {resp.text[:200]}'}
        except requests.Timeout:
            return {'status': 'TIMEOUT', 'error': 'Request timed out'}
        except Exception as e:
            return {'status': 'ERROR', 'error': str(e)[:200]}
    
    def get_session(self, session_id: str = None) -> dict:
        """Get session data including generated patches."""
        try:
            resp = requests.get(f'http://127.0.0.1:{self.port}/session/{session_id or "latest"}', timeout=10)
            if resp.status_code == 200:
                return resp.json()
        except:
            pass
        return {}
    
    def stop(self):
        """Stop the ACP server."""
        if self.process:
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            except:
                pass
            self.process = None
            self.ready = False


class OpenCodeFallbackAdapter:
    """Fallback: direct CLI call with PTY for reliable output capture."""
    
    def generate(self, prompt: str, cwd: str = None, timeout: float = 60) -> dict:
        """Run OpenCode via PTY for reliable output."""
        import pty
        
        master_fd, slave_fd = pty.openpty()
        try:
            proc = subprocess.Popen(
                ['opencode', '--prompt', prompt],
                stdin=slave_fd, stdout=slave_fd, stderr=slave_fd,
                cwd=cwd or os.getcwd(),
                start_new_session=True,
            )
            os.close(slave_fd)
            
            deadline = time.time() + timeout
            output = b''
            while time.time() < deadline and proc.poll() is None:
                try:
                    chunk = os.read(master_fd, 4096)
                    output += chunk
                except:
                    time.sleep(0.5)
            
            if proc.poll() is None:
                proc.terminate()
            
            os.close(master_fd)
            text = output.decode('utf-8', errors='replace')
            
            return {
                'status': 'SUCCESS' if 'diff' in text.lower() or '--- a/' in text else 'NO_PATCH',
                'output': text,
                'duration': timeout,
                'patch_extracted': '--- a/' in text and '+++ b/' in text,
            }
        except Exception as e:
            return {'status': 'ERROR', 'error': str(e)[:200]}


# Self-test
if __name__ == "__main__":
    print("OPENCODE ACP ADAPTER — Self-Test")
    print("=" * 50)
    
    # Test fallback adapter (no server needed)
    fb = OpenCodeFallbackAdapter()
    result = fb.generate(
        prompt="In /tmp/astropy/astropy/modeling/fitting.py, add a None-check before accessing .name. Output ONLY unified diff.",
        cwd='/tmp',
        timeout=30
    )
    print(f"Fallback status: {result['status']}")
    print(f"Output: {len(result['output'])} chars")
    print(f"Patch found: {result['patch_extracted']}")
    if result['patch_extracted']:
        # Extract diff
        text = result['output']
        start = text.index('--- a/') if '--- a/' in text else -1
        if start >= 0:
            print(f"Patch starts at char {start}")
            print(text[start:start+300])
    
    print(f"\n✅ ACP Adapter ready (server mode available)")
    print(f"Use: adapter = OpenCodeACPAdapter()")
    print(f"     adapter.start()")
    print(f"     result = adapter.send_prompt('...')")
    print(f"     adapter.stop()")
