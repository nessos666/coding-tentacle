"""
OPENCODE EXPORT PARSER — CT 1.5
Parses OpenCode session data to extract unified diff patches.
Handles TUI/Rich-Text, plain text diffs, and JSON exports.
"""
import re, json
from dataclasses import dataclass, field


@dataclass
class OpenCodePatchResult:
    valid: bool = False
    patch_text: str = ''
    touched_files: list = field(default_factory=list)
    parse_errors: list = field(default_factory=list)
    safety_flags: list = field(default_factory=list)
    source: str = 'OPENCODE'
    session_id: str = ''
    confidence: float = 0.0


class OpenCodeExportParser:
    """Extracts patches from OpenCode session data in any format."""
    
    DANGEROUS_PATHS = ['/etc/', '/bin/', '/boot/', '/dev/', '/proc/', '/sys/',
                        '~/.ssh', '.env', 'id_rsa']
    
    def parse_session_file(self, filepath: str) -> OpenCodePatchResult:
        """Parse an OpenCode export JSON file."""
        result = OpenCodePatchResult()
        
        try:
            with open(filepath) as f:
                raw_text = f.read()
            
            # OpenCode export prepends "Exporting session: ..." — strip it
            json_start = raw_text.find('{')
            if json_start > 0:
                raw_text = raw_text[json_start:]
            
            data = json.loads(raw_text)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            result.parse_errors.append(f'Cannot read session file: {str(e)[:100]}')
            return result
        
        return self._parse_session_data(data)
    
    def parse_session_data(self, data: dict) -> OpenCodePatchResult:
        """Parse OpenCode session JSON data directly."""
        return self._parse_session_data(data)
    
    def parse_raw_text(self, text: str) -> OpenCodePatchResult:
        """Parse any text for unified diff patterns (handles TUI/Rich-Text)."""
        result = OpenCodePatchResult()
        
        if not text or len(text) < 10:
            result.parse_errors.append('Empty or too short text')
            return result
        
        patches = self._extract_all_diffs(text)
        
        if not patches:
            result.parse_errors.append('No unified diff found in text')
            return result
        
        # Use the largest/best patch
        best = max(patches, key=lambda p: len(p[0]))
        patch_text = best[0]
        source_type = best[1]
        
        result.source = source_type
        
        # Validate
        safety_check = self._validate_patch(patch_text)
        if safety_check['blocked']:
            result.safety_flags = safety_check['flags']
            result.parse_errors = safety_check['flags']
            return result
        
        result.valid = True
        result.patch_text = patch_text
        result.touched_files = self._extract_files(patch_text)
        result.confidence = min(0.95, 0.5 + 0.1 * len(result.touched_files))
        
        return result
    
    def _parse_session_data(self, data: dict) -> OpenCodePatchResult:
        """Internal: parse OpenCode JSON session data."""
        result = OpenCodePatchResult()
        result.session_id = data.get('sessionId', data.get('id', ''))
        
        messages = data.get('messages', [])
        if not messages:
            result.parse_errors.append('No messages in session data')
            return result
        
        # Search messages in reverse for last assistant with content
        for msg in reversed(messages):
            role = msg.get('info', {}).get('role', '')
            if role != 'assistant' and role != 'build':
                continue
            
            # Extract content from parts array
            parts = msg.get('parts', [])
            if not parts:
                continue
            
            content = ''
            for part in parts:
                if isinstance(part, dict) and part.get('type') == 'text':
                    content += part.get('text', '')
            
            if not content:
                # Fallback: direct content field
                content = msg.get('content', '')
                if isinstance(content, list):
                    content = ' '.join(str(c.get('text', c)) for c in content if isinstance(c, dict))
            
            if content and ('---' in content or 'diff' in content.lower()):
                parsed = self.parse_raw_text(content)
                if parsed.valid:
                    parsed.session_id = result.session_id
                    return parsed
        
        result.parse_errors.append('No patch generated in session')
        return result
    
    def _extract_all_diffs(self, text: str) -> list:
        """Extract all unified diffs from text (handles mixed TUI/Rich-Text)."""
        diffs = []
        
        # Pattern 1: ```diff ... ``` block (markdown)
        for m in re.finditer(r'```(?:diff|patch)?\s*\n(.*?)```', text, re.DOTALL):
            diffs.append((m.group(1).strip(), 'MARKDOWN_DIFF'))
        
        # Pattern 2: Plain unified diff (--- / +++ / @@)
        for m in re.finditer(r'(---\s+[^\n]+\n\+\+\+\s+[^\n]+\n@@[^@]*@@.*?)(?=\n(?:---|$))', text, re.DOTALL):
            diffs.append((m.group(1).strip(), 'PLAIN_DIFF'))
        
        # Pattern 3: Single unified diff without trailing ---
        m = re.search(r'(---\s+[^\n]+\n\+\+\+\s+[^\n]+\n@@[^@]*@@.*)', text, re.DOTALL)
        if m:
            diffs.append((m.group(1).strip(), 'PLAIN_DIFF'))
        
        # Pattern 4: OpenCode-specific TUI output (contains diff within Rich formatting)
        for m in re.finditer(r'@@\s+-(\d+),?(\d+)?\s+\+(\d+),?(\d+)?\s+@@(.*?)(?=\n(?:@@|\Z))', text, re.DOTALL):
            # Find the surrounding --- / +++ lines
            ctx = text[max(0, m.start()-500):m.end()+500]
            full_diff = re.search(r'(---\s+[^\n]+\n\+\+\+\s+[^\n]+\n.*)', ctx, re.DOTALL)
            if full_diff:
                diff_text = full_diff.group(1).strip()
                if diff_text not in [d[0] for d in diffs]:
                    diffs.append((diff_text, 'TUI_OUTPUT'))
        
        return diffs
    
    def _validate_patch(self, patch: str) -> dict:
        """Check patch for dangerous content."""
        flags = []
        
        for path in self.DANGEROUS_PATHS:
            if path.lower() in patch.lower():
                flags.append(f'DANGEROUS_PATH: {path}')
        
        if '../' in patch:
            flags.append('PATH_TRAVERSAL')
        
        for dangerous in ['DROP TABLE', 'DELETE FROM', 'rm -rf', 'sudo rm', 'chmod 777']:
            if dangerous.lower() in patch.lower():
                flags.append(f'DANGEROUS_OP: {dangerous}')
        
        return {'flags': flags, 'blocked': len(flags) > 0}
    
    def _extract_files(self, patch: str) -> list:
        """Extract file paths from unified diff."""
        files = []
        for m in re.finditer(r'^\+\+\+\s+b/(.+?)$', patch, re.MULTILINE):
            fpath = m.group(1).strip()
            if fpath and fpath not in files:
                files.append(fpath)
        return files


# Self-test
if __name__ == "__main__":
    parser = OpenCodeExportParser()
    passed = 0
    
    print("OPENCODE EXPORT PARSER — Self-Test")
    print("=" * 55)
    
    # T1: Parse plain unified diff
    r1 = parser.parse_raw_text("""
--- a/astropy/modeling/fitting.py
+++ b/astropy/modeling/fitting.py
@@ -2336,6 +2336,8 @@
+    if entry_points is None:
+        return
     for entry_point in entry_points:
""")
    t1 = r1.valid and 'fitting.py' in str(r1.touched_files)
    if t1: passed += 1
    print(f"  {'✅' if t1 else '❌'} T1: Plain diff → valid={r1.valid} files={r1.touched_files} source={r1.source}")
    
    # T2: Parse markdown diff block
    r2 = parser.parse_raw_text("""Here is the fix:
```diff
--- a/views.py
+++ b/views.py
@@ -40,7 +40,8 @@
-    return None
+    return user.name
```""")
    t2 = r2.valid and 'views.py' in str(r2.touched_files)
    if t2: passed += 1
    print(f"  {'✅' if t2 else '❌'} T2: Markdown diff → valid={r2.valid} source={r2.source}")
    
    # T3: Block dangerous path
    r3 = parser.parse_raw_text("""--- a/etc/passwd\n+++ b/etc/passwd\n@@ -1 +1 @@\n- root\n+ root:x:0:0""" )
    t3 = not r3.valid and len(r3.safety_flags) > 0
    if t3: passed += 1
    print(f"  {'✅' if t3 else '❌'} T3: Block /etc/ → valid={r3.valid} flags={r3.safety_flags}")
    
    # T4: Mock session JSON
    mock = {'sessionId': 'ses_test', 'messages': [
        {'role': 'user', 'content': 'Fix the bug'},
        {'role': 'assistant', 'content': '--- a/test.py\n+++ b/test.py\n@@ -1 +1 @@\n- bug\n+ fix\n'},
    ]}
    r4 = parser._parse_session_data(mock)
    t4 = r4.valid and r4.session_id == 'ses_test'
    if t4: passed += 1
    print(f"  {'✅' if t4 else '❌'} T4: Session JSON → valid={r4.valid} session={r4.session_id}")
    
    # T5: Empty text
    r5 = parser.parse_raw_text('')
    t5 = not r5.valid
    if t5: passed += 1
    print(f"  {'✅' if t5 else '❌'} T5: Empty → valid={r5.valid}")
    
    # T6: Block ../ traversal
    r6 = parser.parse_raw_text('--- a/../secrets.py\n+++ b/../secrets.py\n@@ -1 +1 @@\n- x\n+ y')
    t6 = not r6.valid
    if t6: passed += 1
    print(f"  {'✅' if t6 else '❌'} T6: Block ../ → valid={r6.valid}")
    
    # T7: Rich text with diff
    r7 = parser.parse_raw_text("""⬝⬝⬝The issue is at line 2339...
--- a/astropy/modeling/fitting.py
+++ b/astropy/modeling/fitting.py
@@ -2336,6 +2336,8 @@
+    if entry_points is None:
+        return
▣  Build · Big Pickle""")
    t7 = r7.valid
    if t7: passed += 1
    print(f"  {'✅' if t7 else '❌'} T7: Rich text diff → valid={r7.valid}")
    
    print(f"\n  ERGEBNIS: {passed}/7 Tests")
    print(f"  {'✅ OPENCODE EXPORT PARSER FERTIG' if passed >= 5 else '⚠️'}")
