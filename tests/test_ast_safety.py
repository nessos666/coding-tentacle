"""AST Safety Detection — pytest suite for RC63."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from coding_tentacle.safety.ast_safety_detector import ASTSafetyDetector


def test_eval_critical():
    detector = ASTSafetyDetector()
    r = detector.analyze("user = input('>'); eval(user);")
    assert r.overall_severity == 'critical'
    assert any('eval' in f.explanation for f in r.findings)

def test_eval_literal():
    detector = ASTSafetyDetector()
    r = detector.analyze("eval('2+2');")
    assert r.overall_severity in ('critical', 'warning')

def test_exec_critical():
    detector = ASTSafetyDetector()
    r = detector.analyze("exec(user_code);")
    assert r.overall_severity == 'critical'

def test_subprocess_shell_true():
    detector = ASTSafetyDetector()
    r = detector.analyze("import subprocess; subprocess.run(cmd, shell=True);")
    assert r.overall_severity in ('warning', 'critical')

def test_subprocess_safe():
    detector = ASTSafetyDetector()
    r = detector.analyze("import subprocess; subprocess.run(['ls', '-la']);")
    assert r.overall_severity == 'clean'

def test_pickle_critical():
    detector = ASTSafetyDetector()
    r = detector.analyze("import pickle; data = pickle.loads(user_input);")
    assert any('pickle' in f.explanation.lower() for f in r.findings)

def test_clean_code():
    detector = ASTSafetyDetector()
    r = detector.analyze("def calculate(x, y): return x + y;")
    assert r.overall_severity == 'clean'

def test_syntax_error_graceful():
    detector = ASTSafetyDetector()
    r = detector.analyze("def broken(:")
    assert r.overall_severity == 'warning'

def test_empty_code():
    detector = ASTSafetyDetector()
    r = detector.analyze("")
    assert r.overall_severity == 'clean'

def test_import_socket():
    detector = ASTSafetyDetector()
    r = detector.analyze("import socket;")
    assert len(r.findings) >= 1
