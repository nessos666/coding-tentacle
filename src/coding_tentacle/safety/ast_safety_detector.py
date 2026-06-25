"""
AST SAFETY DETECTOR — RC63
Analyzes Python code structure via AST — not just text/patterns.
Detects dangerous function calls, subprocess misuse, unpickle, etc.
Read-only. Never executes code.
"""
import ast
from dataclasses import dataclass, field


@dataclass
class ASTSafetyFinding:
    severity: str = 'low'  # low / medium / high / critical
    confidence: float = 0.9
    line_number: int = 0
    node_type: str = ''
    explanation: str = ''
    recommendation: str = ''


@dataclass
class ASTSafetyResult:
    findings: list = field(default_factory=list)
    overall_severity: str = 'clean'  # clean / warning / critical
    explanation: str = ''


class ASTSafetyDetector:
    """Analyzes Python code structure for dangerous patterns."""
    
    DANGEROUS_FUNCTIONS = {
        'eval': ('critical', 'eval() executes arbitrary code — REPLACE with safe parser'),
        'exec': ('critical', 'exec() runs arbitrary code — NEVER use with user input'),
        'compile': ('critical', 'compile() can execute code — verify source is trusted'),
        '__import__': ('critical', 'Dynamic import — use importlib instead if needed'),
        'getattr': ('medium', 'Dynamic attribute access — may bypass safety checks'),
        'globals': ('medium', 'Access to global namespace — potential code injection'),
        'locals': ('medium', 'Access to local namespace — potential injection'),
        'vars': ('low', 'Namespace inspection — rarely dangerous, verify usage'),
    }
    
    DANGEROUS_IMPORTS = {
        'subprocess': ('high', 'Subprocess execution — PREFER subprocess.run(args, shell=False)'),
        'ctypes': ('high', 'C-level code execution — verify library source'),
        'pickle': ('critical', 'Unpickling untrusted data → RCE. Use JSON instead.'),
        'marshal': ('critical', 'marshal.loads() with untrusted data → dangerous'),
        'dill': ('high', 'dill is more powerful than pickle — verify input source'),
        'socket': ('low', 'Network access — mark for review'),
    }
    
    DANGEROUS_METHODS = {
        'system': ('high', 'os.system() runs shell commands — use subprocess.run()'),
        'popen': ('high', 'os.popen() deprecated — use subprocess.run()'),
        'call': ('medium', 'subprocess.call() — prefer subprocess.run()'),
        'run': ('medium', 'subprocess.run() — CHECK shell= parameter'),
        'check_output': ('medium', 'subprocess.check_output() — verify input sanitized'),
        'loads': ('high', 'Deserialization — verify input source is trusted'),
        'load': ('medium', 'Deserialization — check if yaml.load (unsafe) or yaml.safe_load'),
        'rmtree': ('medium', 'shutil.rmtree() deletes directories — verify path is safe'),
        'remove': ('medium', 'os.remove() deletes files — verify path'),
        'unlink': ('medium', 'os.unlink() deletes files — verify path'),
    }
    
    DANGEROUS_SUBPROCESS_ARGS = [
        'shell=True', 'shell = True',
        'stdin=PIPE', 'text=True', 'universal_newlines=True',
    ]
    
    def analyze(self, code: str) -> ASTSafetyResult:
        """Parse Python code and detect dangerous patterns."""
        result = ASTSafetyResult()
        
        if not code or not code.strip():
            return result
        
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            result.findings.append(ASTSafetyFinding(
                severity='low', confidence=0.95,
                line_number=e.lineno or 0,
                node_type='SyntaxError',
                explanation=f'Code cannot be parsed: {e.msg}',
                recommendation='Fix syntax before safety analysis',
            ))
            result.overall_severity = 'warning'
            result.explanation = 'Syntax error — cannot fully analyze'
            return result
        
        user_input_vars = self._find_user_input_vars(tree)
        
        for node in ast.walk(tree):
            self._check_call(node, result)
            self._check_import(node, result)
            self._check_attribute(node, result, user_input_vars)
            self._check_string_danger(node, result)
            self._check_shell_true(node, result)
        
        # Compute overall severity
        has_critical = any(f.severity == 'critical' for f in result.findings)
        has_high = any(f.severity == 'high' for f in result.findings)
        
        if has_critical:
            result.overall_severity = 'critical'
            result.explanation = f'{len(result.findings)} safety findings — CRITICAL: code contains dangerous patterns'
        elif has_high:
            result.overall_severity = 'warning'
            result.explanation = f'{len(result.findings)} safety findings — review required'
        elif result.findings:
            result.overall_severity = 'warning'
            result.explanation = f'{len(result.findings)} safety findings — low severity'
        else:
            result.overall_severity = 'clean'
            result.explanation = 'No dangerous AST patterns detected'
        
        return result
    
    def _find_user_input_vars(self, tree: ast.AST) -> set:
        """Find variables that originate from user input."""
        inputs = set()
        for node in ast.walk(tree):
            # input() call
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'input':
                if isinstance(node, ast.Assign) and node.targets:
                    pass
            # request, sys.argv, os.environ
            if isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name) and node.value.id in ('request', 'sys'):
                    inputs.add(node.attr)
        return inputs
    
    def _check_call(self, node: ast.AST, result: ASTSafetyResult):
        """Check function calls for dangerous patterns."""
        if not isinstance(node, ast.Call):
            return
        
        # Direct dangerous function: eval(), exec()
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in self.DANGEROUS_FUNCTIONS:
                severity, recommendation = self.DANGEROUS_FUNCTIONS[func_name]
                result.findings.append(ASTSafetyFinding(
                    severity=severity, confidence=0.95,
                    line_number=node.lineno,
                    node_type=f'Call:{func_name}',
                    explanation=f'{func_name}() called — potential code execution',
                    recommendation=recommendation,
                ))
        
        # Method call: os.system(), subprocess.run()
        if isinstance(node.func, ast.Attribute):
            method_name = node.func.attr
            if method_name in self.DANGEROUS_METHODS:
                severity, recommendation = self.DANGEROUS_METHODS[method_name]
                
                # Check for user input in argument
                user_input_detected = False
                for arg in node.args:
                    if isinstance(arg, ast.Name) and arg.id in self._find_user_input_vars(node):
                        severity = 'critical'
                        user_input_detected = True
                
                result.findings.append(ASTSafetyFinding(
                    severity=severity, confidence=0.90,
                    line_number=node.lineno,
                    node_type=f'Method:{method_name}',
                    explanation=f'{method_name}() called{" with user input" if user_input_detected else ""}',
                    recommendation=recommendation,
                ))
    
    def _check_import(self, node: ast.AST, result: ASTSafetyResult):
        """Check imports for dangerous modules."""
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name.split('.')[0]
                if mod in self.DANGEROUS_IMPORTS:
                    severity, recommendation = self.DANGEROUS_IMPORTS[mod]
                    result.findings.append(ASTSafetyFinding(
                        severity=severity, confidence=0.90,
                        line_number=node.lineno,
                        node_type=f'Import:{mod}',
                        explanation=f'import {mod} — {recommendation[:50]}',
                        recommendation=recommendation,
                    ))
        
        if isinstance(node, ast.ImportFrom):
            mod = node.module.split('.')[0] if node.module else ''
            if mod in self.DANGEROUS_IMPORTS:
                severity, recommendation = self.DANGEROUS_IMPORTS[mod]
                result.findings.append(ASTSafetyFinding(
                    severity=severity, confidence=0.90,
                    line_number=node.lineno,
                    node_type=f'ImportFrom:{mod}',
                    explanation=f'from {node.module} import — {recommendation[:50]}',
                    recommendation=recommendation,
                ))
    
    def _check_attribute(self, node: ast.AST, result: ASTSafetyResult, 
                         user_input_vars: set):
        """Check attribute access for dangerous patterns."""
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            # Check for callable attributes on dangerous modules
            if isinstance(node.func.value, ast.Name):
                if node.func.value.id == 'os' and node.func.attr in ('system', 'popen'):
                    result.findings.append(ASTSafetyFinding(
                        severity='high', confidence=0.95,
                        line_number=node.lineno,
                        node_type=f'OS:{node.func.attr}',
                        explanation=f'os.{node.func.attr}() — use subprocess instead',
                        recommendation='Replace with subprocess.run(args, shell=False)',
                    ))
    
    def _check_string_danger(self, node: ast.AST, result: ASTSafetyResult):
        """Check string literals and f-strings for dangerous patterns."""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if 'rm -rf' in node.value or 'DROP TABLE' in node.value:
                result.findings.append(ASTSafetyFinding(
                    severity='high', confidence=0.85,
                    line_number=node.lineno,
                    node_type='DangerousString',
                    explanation=f'String contains dangerous pattern: {node.value[:60]}',
                    recommendation='This string appears dangerous — verify it is safe',
                ))
    
    def _check_shell_true(self, node: ast.AST, result: ASTSafetyResult):
        """Detect shell=True in subprocess calls."""
        if isinstance(node, ast.keyword):
            if node.arg == 'shell' and hasattr(node.value, 'value') and node.value.value is True:
                result.findings.append(ASTSafetyFinding(
                    severity='high', confidence=0.95,
                    line_number=node.lineno,
                    node_type='Subprocess:shell=True',
                    explanation='subprocess with shell=True — Shell injection risk',
                    recommendation='Use shell=False with command as list of arguments',
                ))


# ═══════════ SELF-TEST ═══════════
if __name__ == "__main__":
    detector = ASTSafetyDetector()
    passed = 0
    
    print("AST SAFETY DETECTOR — Self-Test")
    print("=" * 55)
    
    tests = [
        ("T1: eval(user_input)", "user = input('>'); eval(user);", "critical"),
        ("T2: eval literal", "eval('2+2');", "critical"),
        ("T3: exec", "exec(user_code);", "critical"),
        ("T4: subprocess shell=True", "import subprocess; subprocess.run(cmd, shell=True);", "warning"),
        ("T5: subprocess safe", "import subprocess; subprocess.run(['ls', '-la']);", "clean"),
        ("T6: os.system", "import os; os.system('rm -rf /');", "warning"),
        ("T7: pickle.loads", "import pickle; data = pickle.loads(user_input);", "critical"),
        ("T8: clean code", "def calculate(x, y): return x + y;", "clean"),
        ("T9: globals", "g = globals();", "warning"),
        ("T10: shutil.rmtree", "import shutil; shutil.rmtree('/tmp/x');", "warning"),
        ("T11: open write", "with open('file.txt', 'w') as f: f.write('hello');", "clean"),
        ("T12: SyntaxError", "def broken(:", "warning"),
        ("T13: import multiple", "import socket, pickle;", "critical"),
        ("T14: subprocess+user", "cmd = input('>'); subprocess.run(cmd, shell=True);", "warning"),
        ("T15: empty code", "", "clean"),
        ("T16: dangerous string", "cmd = 'rm -rf /tmp/data';", "warning"),
    ]
    
    for name, code, expected in tests:
        r = detector.analyze(code)
        ok = (expected == r.overall_severity)
        if ok: passed += 1
        print(f"  {'✅' if ok else '❌'} {name:<30s} → {r.overall_severity:<8s} ({len(r.findings)} findings)")
    
    print(f"\n  ERGEBNIS: {passed}/{len(tests)} Tests")
    print(f"  {'✅ AST SAFETY DETECTOR FERTIG' if passed >= 14 else '⚠️'}")
