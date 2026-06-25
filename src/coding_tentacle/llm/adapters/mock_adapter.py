"""
MOCK LLM ADAPTER — RC75
Generates safe, predictable patches for testing.
"""
from coding_tentacle.llm.repair_agent_interface import AgentInput


class MockLLMAdapter:
    """Mock LLM adapter for testing - generates safe diff patches."""
    
    def is_available(self) -> bool:
        return True
    
    def generate(self, agent_input: AgentInput) -> str:
        """Generate a mock patch response."""
        bug = agent_input.bug_report[:80]
        mode = agent_input.mode
        
        if mode == 'SECURITY':
            return ''
        
        file_name = 'views.py'
        if 'views.py' in bug:
            file_name = 'views.py'
        elif 'calc.py' in bug:
            file_name = 'calc.py'
        elif 'auth' in bug.lower():
            file_name = 'auth.py'
        
        explanation = f'Added None guard for {bug[:40]}'
        
        return f'''{explanation}

```diff
--- a/{file_name}
+++ b/{file_name}
@@ -40,7 +40,10 @@
 def get_profile(user):
-    return user.name.upper()
+    if user is None:
+        raise ValueError("User cannot be None")
+    return user.name.upper() if user.name else "Anonymous"
```
'''


class LocalLLMAdapter:
    """Adapter for local LLMs (Ollama, OpenCode). No API key required."""
    
    def __init__(self, command: list = None):
        self.command = command or ['ollama', 'run', 'granite3.2-vision']
        self._available = None
    
    def is_available(self) -> bool:
        if self._available is not None:
            return self._available
        import subprocess
        try:
            result = subprocess.run(self.command[:2], capture_output=True, timeout=10)
            self._available = result.returncode in (0, 1)  # 1 = help output = exists
        except:
            self._available = False
        return self._available
    
    def generate(self, agent_input: AgentInput) -> str:
        import subprocess
        prompt = self._build_prompt(agent_input)
        try:
            result = subprocess.run(
                self.command + [prompt],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                return result.stdout[:10000]
            return ''
        except subprocess.TimeoutExpired:
            raise TimeoutError('Local LLM timed out')
        except:
            return ''
    
    def _build_prompt(self, ai: AgentInput) -> str:
        return f"""Fix this bug. Output a unified diff patch.

Bug: {ai.bug_report}
Test Failure: {ai.failing_test}
Root Cause: {ai.root_cause}

Respond with explanation then ```diff patch."""
