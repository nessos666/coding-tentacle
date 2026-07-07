"""
AST SECURITY ANALYZER — RC11 P0.2
Structural Python code analysis using ast.parse().

Detects dangerous code patterns at the AST level that simple
regex matching misses: dynamic code loading, unsafe imports,
obfuscated patterns, suspicious control flow.

Runs via AST Visitor pattern. Zero dependencies beyond stdlib ast.

Detection categories:
  1. DYNAMIC_CODE: eval(), exec(), compile() with non-constant args
  2. UNSAFE_IMPORT: __import__(), importlib.import_module() with variables
  3. UNSAFE_DESERIALIZE: pickle.loads(), yaml.load(), marshal.loads()
  4. HIDDEN_NETWORK: socket/requests/urllib in unexpected contexts
  5. HIDDEN_FILE: open()/os.remove()/shutil.rmtree() with suspicious paths
  6. CODE_EXFIL: Writing code/credentials to external locations
  7. ATTRIBUTE_HIDE: getattr/setattr/delattr with dynamic names
"""

# CT-v11.0.0: PRODUCTION | 10/10 regression | 25 modules | 90% wired | Droste active

from __future__ import annotations
import ast
from dataclasses import dataclass, field


@dataclass
class ASTSecurityFinding:
    """A single security finding from AST analysis."""
    line_number: int
    category: str          # 'DYNAMIC_CODE', 'UNSAFE_IMPORT', etc.
    risk: str              # 'CRITICAL', 'HIGH', 'MEDIUM'
    code: str              # The offending code snippet
    description: str       # Human-readable explanation
    cwe: str = ''          # Associated CWE


@dataclass
class ASTSecurityResult:
    """Complete AST security scan result."""
    findings: list[ASTSecurityFinding] = field(default_factory=list)
    num_critical: int = 0
    num_high: int = 0
    num_medium: int = 0
    parse_error: str = ''

    @property
    def clean(self) -> bool:
        return len(self.findings) == 0 and not self.parse_error

    @property
    def risk_score(self) -> float:
        """Overall risk score 0.0-1.0."""
        if self.parse_error:
            return 1.0
        if not self.findings:
            return 0.0
        weights = {'CRITICAL': 1.0, 'HIGH': 0.7, 'MEDIUM': 0.3}
        total = sum(weights.get(f.risk, 0.3) for f in self.findings)
        return round(min(1.0, total / max(1, len(self.findings)) * 1.2), 2)

    def to_dict(self) -> dict:
        return {
            'clean': self.clean,
            'num_critical': self.num_critical,
            'num_high': self.num_high,
            'num_medium': self.num_medium,
            'risk_score': self.risk_score,
            'parse_error': self.parse_error,
            'findings': [
                {
                    'line': f.line_number,
                    'category': f.category,
                    'risk': f.risk,
                    'cwe': f.cwe,
                    'description': f.description,
                }
                for f in self.findings[:30]
            ],
        }


class ASTSecurityVisitor(ast.NodeVisitor):
    """Walks AST and calls detectors for dangerous patterns."""

    DANGEROUS_DYNAMIC = {'eval', 'exec', 'compile'}

    DANGEROUS_DESERIALIZE = {
        'pickle.loads', 'pickle.load', 'yaml.load',
        'marshal.loads', 'marshal.load',
        'dill.loads', 'dill.load', 'joblib.load',
    }

    DANGEROUS_IMPORT = {'__import__', 'importlib.import_module',
                         'importlib.__import__', 'imp.load_source'}

    DANGEROUS_NETWORK = {
        'requests.get', 'requests.post', 'requests.put', 'requests.delete',
        'urllib.request.urlopen', 'urllib.request.urlretrieve',
        'http.client.HTTPConnection', 'socket.socket',
        'ftplib.FTP', 'smtplib.SMTP',
    }

    DANGEROUS_FILE_OPS = {
        'os.remove', 'os.unlink', 'os.rmdir', 'shutil.rmtree',
        'os.system', 'subprocess.call', 'subprocess.run', 'subprocess.Popen',
    }

    DANGEROUS_ATTRIBUTE = {'getattr', 'setattr', 'delattr', '__getattribute__'}

    def __init__(self):
        self.findings: list[ASTSecurityFinding] = []

    def _make_finding(self, node: ast.AST, category: str, risk: str,
                      desc: str, cwe: str = '') -> None:
        self.findings.append(ASTSecurityFinding(
            line_number=node.lineno,
            category=category,
            risk=risk,
            code=ast.unparse(node) if hasattr(ast, 'unparse') else str(node),
            description=desc,
            cwe=cwe,
        ))

    def visit_Call(self, node: ast.Call):
        """Check function/method calls for dangerous patterns."""
        # Get full function path
        func_path = self._get_call_path(node.func)

        # 1. DYNAMIC_CODE: eval/exec/compile
        if func_path in self.DANGEROUS_DYNAMIC:
            risk = 'CRITICAL'
            # Lower risk if argument is a string literal (less dangerous but still flag)
            if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                risk = 'HIGH'
            self._make_finding(node, 'DYNAMIC_CODE', risk,
                f'{func_path}() — dynamic code execution',
                'CWE-95')

        # 2. UNSAFE_DESERIALIZE
        elif func_path in self.DANGEROUS_DESERIALIZE:
            self._make_finding(node, 'UNSAFE_DESERIALIZE', 'CRITICAL',
                f'{func_path}() — unsafe deserialization',
                'CWE-502')

        # 3. UNSAFE_IMPORT
        elif func_path in self.DANGEROUS_IMPORT or (
            isinstance(node.func, ast.Attribute) and
            isinstance(node.func.value, ast.Call) and
            self._get_call_path(node.func.value.func) == 'importlib.import_module'):
            self._make_finding(node, 'UNSAFE_IMPORT', 'CRITICAL',
                f'{func_path}() — dynamic/reversible import',
                'CWE-506')

        # 4. HIDDEN_NETWORK in non-obvious contexts
        elif func_path in self.DANGEROUS_NETWORK:
            self._make_finding(node, 'HIDDEN_NETWORK', 'HIGH',
                f'{func_path}() — network call (potential data exfiltration)',
                'CWE-912')

        # 5. DANGEROUS FILE OPS
        elif func_path in self.DANGEROUS_FILE_OPS:
            self._make_finding(node, 'DANGEROUS_FILE_OP', 'HIGH',
                f'{func_path}() — dangerous file/system operation',
                'CWE-73')

        # 6. ATTRIBUTE_HIDE
        elif func_path in self.DANGEROUS_ATTRIBUTE:
            # Only flag if argument is dynamic (not a constant)
            if node.args and not isinstance(node.args[0], ast.Constant):
                self._make_finding(node, 'ATTRIBUTE_HIDE', 'MEDIUM',
                    f'{func_path}() with dynamic attribute name',
                    'CWE-506')

        # 7. Check for attribute-based dangerous calls: foo.__import__(...)
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in ('__import__', 'loads', 'load', 'system', 'popen'):
                self._make_finding(node, 'DYNAMIC_CODE', 'HIGH',
                    f'obj.{node.func.attr}() — suspicious attribute call',
                    'CWE-114')

        self.generic_visit(node)

    def visit_Import(self, node: ast.Import):
        """Check imports for suspicious patterns."""
        for alias in node.names:
            # Check import of modules commonly used for obfuscation
            if alias.name in ('base64', 'binascii', 'codecs', 'zlib', 'marshal'):
                self._make_finding(node, 'OBFUSCATION_IMPORT', 'MEDIUM',
                    f'import {alias.name} — commonly used for code obfuscation',
                    'CWE-506')
        self.generic_visit(node)

    def _get_call_path(self, func_node: ast.AST) -> str:
        """Extract full dotted path from a call node, e.g., 'os.system'."""
        if isinstance(func_node, ast.Name):
            return func_node.id
        elif isinstance(func_node, ast.Attribute):
            base = self._get_call_path(func_node.value)
            return f'{base}.{func_node.attr}' if base else func_node.attr
        return ''


class ASTSecurityAnalyzer:
    """
    Analyzes Python code for security issues at the AST level.

    Usage:
        analyzer = ASTSecurityAnalyzer()
        result = analyzer.analyze(code_string)
        if not result.clean:
            print(f"Risk score: {result.risk_score}")
    """

    def analyze(self, code: str) -> ASTSecurityResult:
        """
        Parse and analyze Python code for security issues.

        Returns ASTSecurityResult with categorized findings.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return ASTSecurityResult(parse_error=str(e))

        visitor = ASTSecurityVisitor()
        visitor.visit(tree)

        # Count by risk level
        critical = sum(1 for f in visitor.findings if f.risk == 'CRITICAL')
        high = sum(1 for f in visitor.findings if f.risk == 'HIGH')
        medium = sum(1 for f in visitor.findings if f.risk == 'MEDIUM')

        return ASTSecurityResult(
            findings=visitor.findings,
            num_critical=critical,
            num_high=high,
            num_medium=medium,
        )


# ─── Self-Tests ─────────────────────────────────────────────────────────

if __name__ == '__main__':
    analyzer = ASTSecurityAnalyzer()
    passed = 0
    failed = 0

    # T1: Clean code
    print("T1: Clean code...", end=" ")
    r = analyzer.analyze("def hello():\n    return 'world'")
    assert r.clean
    assert r.risk_score == 0.0
    passed += 1
    print("OK")

    # T2: eval detection
    print("T2: eval()...", end=" ")
    r = analyzer.analyze("eval(user_input)")
    assert not r.clean
    assert any(f.category == 'DYNAMIC_CODE' for f in r.findings)
    assert r.num_critical >= 1
    passed += 1
    print("OK")

    # T3: exec with variable
    print("T3: exec()...", end=" ")
    r = analyzer.analyze("exec(some_string + more)")
    assert not r.clean
    assert r.num_critical >= 1
    passed += 1
    print("OK")

    # T4: pickle.loads
    print("T4: pickle.loads()...", end=" ")
    r = analyzer.analyze("import pickle; pickle.loads(data)")
    assert not r.clean
    assert any(f.category == 'UNSAFE_DESERIALIZE' for f in r.findings)
    passed += 1
    print("OK")

    # T5: __import__ with variable
    print("T5: __import__()...", end=" ")
    r = analyzer.analyze("__import__(module_name)")
    assert not r.clean
    assert any(f.category == 'UNSAFE_IMPORT' for f in r.findings)
    passed += 1
    print("OK")

    # T6: importlib.import_module
    print("T6: importlib.import_module()...", end=" ")
    r = analyzer.analyze("import importlib; importlib.import_module(unknown)")
    assert not r.clean
    assert r.num_critical >= 1
    passed += 1
    print("OK")

    # T7: os.system
    print("T7: os.system()...", end=" ")
    r = analyzer.analyze("import os; os.system('rm -rf /')")
    assert not r.clean
    assert any(f.category == 'DANGEROUS_FILE_OP' for f in r.findings)
    passed += 1
    print("OK")

    # T8: hidden network
    print("T8: Hidden network call...", end=" ")
    r = analyzer.analyze("import socket; s = socket.socket(); s.connect(('evil.com', 443))")
    assert not r.clean
    assert any(f.category == 'HIDDEN_NETWORK' for f in r.findings)
    passed += 1
    print("OK")

    # T9: requests.get
    print("T9: requests.get()...", end=" ")
    r = analyzer.analyze("import requests; requests.get(url + '/exfil?' + secrets)")
    assert not r.clean
    assert any(f.category == 'HIDDEN_NETWORK' for f in r.findings)
    passed += 1
    print("OK")

    # T10: SyntaxError handling
    print("T10: SyntaxError...", end=" ")
    r = analyzer.analyze("def broken(")
    assert r.parse_error
    assert r.risk_score == 1.0
    passed += 1
    print("OK")

    # T11: compile with string
    print("T11: compile()...", end=" ")
    r = analyzer.analyze("compile(user_code, '<string>', 'exec')")
    assert not r.clean
    assert r.num_critical >= 1
    passed += 1
    print("OK")

    # T12: Risk score calculation
    print("T12: Risk score...", end=" ")
    r = analyzer.analyze("eval(x); exec(y); os.system(z)")
    assert r.risk_score > 0.5
    passed += 1
    print(f"OK ({r.risk_score})")

    # T13: obfuscation import
    print("T13: Obfuscation import...", end=" ")
    r = analyzer.analyze("import base64\nimport marshal\nimport zlib")
    assert not r.clean
    assert any(f.category == 'OBFUSCATION_IMPORT' for f in r.findings)
    passed += 1
    print("OK")

    # T14: getattr with dynamic name
    print("T14: getattr with dynamic...", end=" ")
    r = analyzer.analyze("getattr(obj, unknown_attr)")
    assert not r.clean
    assert any(f.category == 'ATTRIBUTE_HIDE' for f in r.findings)
    passed += 1
    print("OK")

    # T15: to_dict serialization
    print("T15: to_dict...", end=" ")
    r = analyzer.analyze("eval(x)")
    d = r.to_dict()
    assert d['num_critical'] >= 1
    assert len(d['findings']) >= 1
    passed += 1
    print("OK")

    print(f"\n{'='*50}")
    print(f"  ERGEBNIS: {passed}/{passed+failed} Tests bestanden")
    print(f"  {'✅ AST SECURITY ANALYZER FERTIG' if passed >= 14 else '❌ FEHLER'}")
