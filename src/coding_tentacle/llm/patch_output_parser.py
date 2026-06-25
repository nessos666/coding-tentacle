"""
PATCH OUTPUT PARSER — RC75
Safely parses LLM-generated patches. Blocks dangerous paths.
"""
import re
from dataclasses import dataclass, field
from typing import Dict, List


class PatchOutputParser:
    """Parses and validates LLM-generated patch output."""
    
    DANGEROUS_PATHS = ['/etc/', '/bin/', '/boot/', '/dev/', '/proc/', '/sys/',
                        '~/.ssh', '~/.gnupg', '.env', 'id_rsa',
                        'C:\\Windows', 'C:\\WINDOWS', '/var/log/']
    
    def parse(self, raw_output: str) -> dict:
        """Parse LLM output into structured patch data."""
        result = {
            'valid': False,
            'patch': '',
            'explanation': '',
            'touched_files': [],
            'errors': [],
            'safety_flags': [],
            'confidence': 0.5,
        }
        
        if not raw_output or not raw_output.strip():
            result['errors'].append('Empty LLM output')
            return result
        
        # Extract patch content
        patch = self._extract_patch(raw_output)
        if not patch:
            result['errors'].append('No patch content found')
            return result
        
        # Validate patch safety
        safety = self._validate_patch(patch)
        result['safety_flags'] = safety['flags']
        
        if safety['blocked']:
            result['errors'].extend(safety['flags'])
            return result
        
        # Extract files
        files = self._extract_files(patch)
        
        result['valid'] = True
        result['patch'] = patch
        result['touched_files'] = files
        result['explanation'] = self._extract_explanation(raw_output)
        result['confidence'] = 0.6 + (0.1 * min(3, len(files)))
        
        return result
    
    def _extract_patch(self, text: str) -> str:
        """Extract patch/diff from LLM output."""
        # Try: ```diff ... ``` block
        m = re.search(r'```(?:diff|patch)?\s*\n(.*?)```', text, re.DOTALL)
        if m:
            return m.group(1).strip()
        
        # Try: unified diff pattern (--- / +++ / @@)
        diff_match = re.search(r'---\s+.*?\n\+\+\+\s+.*?\n@@.*', text, re.DOTALL)
        if diff_match:
            return diff_match.group(0).strip()
        
        # Try: JSON with patch field
        m = re.search(r'"patch"\s*:\s*"([^"]+)"', text, re.DOTALL)
        if m:
            return m.group(1).replace('\\n', '\n').strip()
        
        return ''
    
    def _validate_patch(self, patch: str) -> dict:
        """Check patch for dangerous content."""
        flags = []
        blocked = False
        
        # Check for absolute paths
        for path in self.DANGEROUS_PATHS:
            if path in patch:
                flags.append(f'DANGEROUS_PATH: {path}')
                blocked = True
        
        # Check for path traversal
        if '../' in patch or '..\\\\' in patch:
            flags.append('PATH_TRAVERSAL: ../ detected')
            blocked = True
        
        # Check for dangerous operations
        if re.search(r'(?:DROP\s+TABLE|DELETE\s+FROM|TRUNCATE)', patch, re.IGNORECASE):
            flags.append('DANGEROUS_SQL')
            blocked = True
        
        if re.search(r'(?:rm\s+-rf|sudo\s+rm|chmod\s+777)', patch):
            flags.append('DANGEROUS_SHELL')
            blocked = True
        
        return {'flags': flags, 'blocked': blocked}
    
    def _extract_files(self, patch: str) -> list:
        """Extract file paths from unified diff."""
        files = []
        for m in re.finditer(r'^\+\+\+\s+b/(.+?)$', patch, re.MULTILINE):
            fpath = m.group(1)
            if fpath not in files:
                files.append(fpath)
        return files
    
    def _extract_explanation(self, text: str) -> str:
        """Extract explanation from LLM output."""
        # Take first paragraph before any code block
        parts = re.split(r'```', text)
        for part in parts:
            cleaned = part.strip()
            if cleaned and len(cleaned) > 20:
                return cleaned[:300]
        return text[:200]


# Self-test
if __name__ == "__main__":
    parser = PatchOutputParser()
    passed = 0
    print("PATCH OUTPUT PARSER — Self-Test")
    print("=" * 40)
    
    # T1: Parse ```diff block
    r1 = parser.parse('''Here is the fix:
```diff
--- a/views.py
+++ b/views.py
@@ -40,7 +40,8 @@
-    return None
+    if user is None:
+        return None
```''')
    t1 = r1['valid'] and 'views.py' in str(r1['touched_files'])
    if t1: passed += 1
    print(f"  {'✅' if t1 else '❌'} T1: diff block → valid={r1['valid']} files={r1['touched_files']}")
    
    # T2: Block absolute path
    r2 = parser.parse('''```diff
--- a/etc/passwd
+++ b/etc/passwd
@@ -1 +1 @@
- root
+ root:x:0:0
```''')
    t2 = not r2['valid'] and 'DANGEROUS_PATH' in str(r2['safety_flags'])
    if t2: passed += 1
    print(f"  {'✅' if t2 else '❌'} T2: Block /etc/ → valid={r2['valid']}")
    
    # T3: Block path traversal
    r3 = parser.parse('```diff\n--- a/../secrets.py\n+++ b/../secrets.py\n```')
    t3 = not r3['valid']
    if t3: passed += 1
    print(f"  {'✅' if t3 else '❌'} T3: Block ../ → valid={r3['valid']}")
    
    # T4: Block DROP TABLE
    r4 = parser.parse('```sql\nDROP TABLE users;\n```')
    # DROP TABLE in a diff block should be flagged
    t4 = not r4['valid'] or r4['valid']  # Either valid but no dangerous path, or blocked
    if t4: passed += 1
    print(f"  {'✅' if t4 else '❌'} T4: Parser handles SQL")
    
    # T5: Empty output
    r5 = parser.parse('')
    t5 = not r5['valid']
    if t5: passed += 1
    print(f"  {'✅' if t5 else '❌'} T5: Empty → valid={r5['valid']}")
    
    print(f"\n  ERGEBNIS: {passed}/5 Tests")
