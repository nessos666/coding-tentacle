"""RC2 DEEP BUG HUNT — 20-stage systematic probe"""
import sys, os, json, time, ast, subprocess, tempfile, traceback

PROJECT_ROOT = '/home/boobi/GEHIRN_BIBLIOTHEK'
os.chdir(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT)

BUGS_FOUND = []

def bug(level, stage, title, file_path, cause, fix, reproducible):
    BUGS_FOUND.append({'level': level, 'stage': stage, 'title': title,
                        'file': file_path, 'cause': cause, 'fix': fix, 'reproducible': reproducible})

def run_code(code, timeout=10):
    """Run code in subprocess, return stdout, stderr, exit_code"""
    f = tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False)
    f.write(code); f.close()
    try:
        r = subprocess.run([sys.executable, f.name], capture_output=True, text=True, timeout=timeout)
        return r.stdout, r.stderr, r.returncode
    except subprocess.TimeoutExpired:
        return '', 'TIMEOUT', -1
    finally:
        os.unlink(f.name)

# ═══════════ STAGE 1: SYNTAX CHECK ═══════════
print("STAGE 1: Syntax check — all .py files in src/")
for root, dirs, files in os.walk('src/coding_tentacle'):
    for f in files:
        if f.endswith('.py'):
            fp = os.path.join(root, f)
            try:
                ast.parse(open(fp).read())
            except SyntaxError as e:
                bug('P0', 1, f'Syntax error in {f}', fp, str(e), 'Fix syntax', True)

# ═══════════ STAGE 2: IMPORT MATRIX ═══════════
print("STAGE 2: Import matrix")
imports = [
    ("BQ", "from coding_tentacle.brains.sg_brain import SymbolGroundingBrain"),
    ("WM", "from coding_tentacle.memory.working_memory import WorkingMemory"),
    ("IC", "from coding_tentacle.safety.inhibitory_control import InhibitoryControl"),
    ("EL", "from coding_tentacle.safety.escalation_logic import EscalationLogic"),
    ("BR", "from coding_tentacle.reasoning.br_scientific_method import ScientificMethodBrain"),
    ("Patch", "from coding_tentacle.patch.patch_suggestion import PatchSuggestionEngine"),
    ("MTS", "from coding_tentacle.tentacles.mini_tentacle_system import MiniTentacleSystem"),
    ("Orch", "from coding_tentacle.orchestrator.minimal_orchestrator import MinimalOrchestrator"),
]
for name, imp in imports:
    out, err, rc = run_code(f"{imp}\nprint('OK')")
    if rc != 0 or 'OK' not in out:
        bug('P0', 2, f'Import failed: {name}', '', err, 'Check import path', True)

# ═══════════ STAGE 3: SELF-TESTS ═══════════
print("STAGE 3: Self-tests")
self_tests = [
    ("BQ", "src/coding_tentacle/brains/sg_brain.py"),
    ("WM", "src/coding_tentacle/memory/working_memory.py"),
    ("IC", "src/coding_tentacle/safety/inhibitory_control.py"),
    ("EL", "src/coding_tentacle/safety/escalation_logic.py"),
    ("BR", "src/coding_tentacle/reasoning/br_scientific_method.py"),
    ("Patch", "src/coding_tentacle/patch/patch_suggestion.py"),
    ("MTS", "src/coding_tentacle/tentacles/mini_tentacle_system.py"),
    ("Orch", "src/coding_tentacle/orchestrator/minimal_orchestrator.py"),
]
for name, fpath in self_tests:
    out, err, rc = run_code(open(fpath).read(), timeout=15)
    if 'PASS' in out or 'ERGEBNIS' in out:
        continue
    if rc != 0:
        bug('P1', 3, f'Self-test failed: {name}', fpath, err[:100], 'Debug self-test', True)

# ═══════════ STAGE 4: FULL REGRESSION ═══════════
print("STAGE 4: Full regression")
out, err, rc = run_code(open('scripts/full_regression.py').read(), timeout=30)
if 'ALL TESTS PASSED' not in out:
    bug('P0', 4, 'Full regression failed', 'scripts/full_regression.py', out[-200:], 'Fix failing test', True)

# ═══════════ STAGE 5: EXAMPLE ═══════════
print("STAGE 5: Example run")
if os.path.exists('examples/example_nullpointer.py'):
    out, err, rc = run_code(open('examples/example_nullpointer.py').read(), timeout=15)
    if 'BUG' not in out or 'PATCH' not in out:
        bug('P1', 5, 'Example broken', 'examples/example_nullpointer.py', err[:100], 'Fix example', True)
else:
    bug('P2', 5, 'Example file missing', 'examples/example_nullpointer.py', 'File not found', 'Create example', True)

# ═══════════ STAGE 6: CLI ENTRYPOINTS ═══════════
print("STAGE 6: CLI entrypoints")
cli_tests = [
    ("pip install", "pip install --break-system-packages -e . 2>&1 | tail -1", False),
]
for name, cmd, _ in cli_tests:
    out, err, rc = run_code(f"import subprocess; r=subprocess.run('{cmd}',shell=True,capture_output=True,text=True); print(r.stdout); print(r.stderr)", timeout=30)
    if rc != 0 or 'Success' not in out:
        bug('P2', 6, f'CLI entrypoint: {name}', '', err[:100], 'Check CLI', True)

# ═══════════ STAGE 7-8: PATHS + JSON ═══════════
print("STAGE 7: Absolute path audit")
abs_paths = []
for root, dirs, files in os.walk('src'):
    for f in files:
        if f.endswith('.py'):
            content = open(os.path.join(root, f)).read()
            if '/home/boobi' in content and 'sys.path.insert' not in content:
                abs_paths.append(os.path.join(root, f))
if abs_paths:
    for p in abs_paths:
        bug('P2', 7, f'Absolute path: {p}', p, '/home/boobi', 'Replace with portable path', True)

print("STAGE 8: JSON/History files")
for root, dirs, files in os.walk('.'):
    for f in files:
        if f.endswith('.json') and ('Schreibtisch' in root or 'Desktop' in root):
            bug('P3', 8, f'Report on Desktop: {f}', os.path.join(root,f), 'Old report path', 'Move to data/reports/', False)

# ═══════════ STAGE 9-10: EXCEPTION + BLOCK ═══════════
print("STAGE 9: Exception paths")
exception_tests = [
    ("None input", "from coding_tentacle.tentacles.mini_tentacle_system import MiniTentacleSystem; m=MiniTentacleSystem(); r=m.process(None); print('HANDLED' if r else 'CRASH')"),
    ("Empty dict", "from coding_tentacle.tentacles.mini_tentacle_system import MiniTentacleSystem; m=MiniTentacleSystem(); r=m.process({}); print('HANDLED' if r else 'CRASH')"),
    ("Empty string bug", "from coding_tentacle.tentacles.mini_tentacle_system import MiniTentacleSystem; m=MiniTentacleSystem(); r=m.process({'bug_report':'','requested_action':'analyze','risk_level':'low'}); print('HANDLED' if r else 'CRASH')"),
]
for name, code in exception_tests:
    out, err, rc = run_code(code, timeout=10)
    if 'CRASH' in out or rc != 0:
        bug('P1', 9, f'Exception not handled: {name}', '', err[:100], 'Add try/except or None-check', True)

print("STAGE 10: BLOCK/HOLD/ESCALATE/GO")
safety_tests = [
    ("Credentials → BLOCK", "from coding_tentacle.safety.inhibitory_control import InhibitoryControl; ic=InhibitoryControl(); d=ic.evaluate({'proposed_action':'patch','target_file':'.env','patch':'API_KEY=x','confidence':0.5,'risk_level':'medium','test_available':False,'rollback_available':False,'security_sensitive':True}); print('OK' if d.action=='BLOCK' else f'FAIL:{d.action}')"),
    ("Critical+noRollback → BLOCK", "from coding_tentacle.safety.inhibitory_control import InhibitoryControl; ic=InhibitoryControl(); d=ic.evaluate({'proposed_action':'patch','target_file':'db.py','patch':'DROP TABLE','confidence':0.3,'risk_level':'critical','test_available':False,'rollback_available':False,'security_sensitive':False}); print('OK' if d.action=='BLOCK' else f'FAIL:{d.action}')"),
    ("Delete → BLOCK", "from coding_tentacle.safety.inhibitory_control import InhibitoryControl; ic=InhibitoryControl(); d=ic.evaluate({'proposed_action':'delete','target_file':'/tmp/x','patch':'os.remove','confidence':0.8,'risk_level':'medium','test_available':True,'rollback_available':True,'security_sensitive':False}); print('OK' if d.action=='BLOCK' else f'FAIL:{d.action}')"),
]
for name, code in safety_tests:
    out, err, rc = run_code(code, timeout=10)
    if 'OK' not in out:
        bug('P0', 10, f'Safety failure: {name}', 'inhibitory_control.py', out, 'Fix BLOCK logic', True)

# ═══════════ STAGE 11-13: ROUTING + PATCH + EDGE ═══════════
print("STAGE 11: Routing cases")
routing_tests = [
    ("Known → LOCAL_HANDLE", "from coding_tentacle.safety.escalation_logic import EscalationLogic; el=EscalationLogic(); d=el.evaluate_escalation({'bug_type':'NullPointer','complexity':'low','known_pattern':True,'has_code_context':True,'has_tests':True,'confidence':0.8,'risk_level':'low','brain_outputs':[],'requested_action':'analyze'}); print('OK' if d.route=='LOCAL_HANDLE' else f'FAIL:{d.route}')"),
    ("Destructive → HUMAN_REVIEW", "from coding_tentacle.safety.escalation_logic import EscalationLogic; el=EscalationLogic(); d=el.evaluate_escalation({'bug_type':'bug','complexity':'high','known_pattern':False,'has_code_context':True,'has_tests':False,'confidence':0.3,'risk_level':'high','brain_outputs':[],'requested_action':'delete'}); print('OK' if d.route=='HUMAN_REVIEW' else f'FAIL:{d.route}')"),
]
for name, code in routing_tests:
    out, err, rc = run_code(code, timeout=10)
    if 'OK' not in out:
        bug('P1', 11, f'Routing failure: {name}', 'escalation_logic.py', out, 'Fix routing', True)

print("STAGE 12: Patch suggestion types")
patch_types = ['NullPointerException', 'AttributeError', 'TypeError', 'ImportError', 'IndexError', 'KeyError', 'MemoryLeak', 'RaceCondition', 'AssertionError', 'TimeoutError']
for bt in patch_types:
    code = f"from coding_tentacle.patch.patch_suggestion import PatchSuggestionEngine; ps=PatchSuggestionEngine(); r=ps.suggest('{bt}',code_context={{'file':'t.py','line':1}},grounding={{'grounding_score':0.5}}); print('OK' if r['patch_type']!='generic_fix' else 'FAIL:generic')"
    out, err, rc = run_code(code, timeout=10)
    if 'FAIL' in out:
        bug('P2', 12, f'Patch generic for {bt}', 'patch_suggestion.py', '', 'Add template', False)

print("STAGE 13: Known edge cases from real bug probe")
edges = [
    ("Unknown crash → generic", "from coding_tentacle.patch.patch_suggestion import PatchSuggestionEngine; ps=PatchSuggestionEngine(); r=ps.suggest('Segfault in native',code_context=None,grounding={{'grounding_score':0.0}}); print('OK' if r['patch_type']=='generic_fix' else f'FAIL:{r[\"patch_type\"]}')"),
    ("Empty bug → ASK_CONTEXT", "from coding_tentacle.brains.sg_brain import SymbolGroundingBrain; bq=SymbolGroundingBrain(); r=bq.think('UnknownError:x.py:1'); print('OK' if r['action']=='ASK_CONTEXT' else f'FAIL:{r[\"action\"]}')"),
]
for name, code in edges:
    out, err, rc = run_code(code, timeout=10)
    if 'OK' not in out:
        bug('P2', 13, f'Edge case: {name}', '', out, 'Handle edge case', False)

# ═══════════ STAGE 14-16: MISSING + BROKEN + EMPTY ═══════════
print("STAGE 14: Missing test data")
missing_tests = [
    ("No code_context", "from coding_tentacle.tentacles.mini_tentacle_system import MiniTentacleSystem; m=MiniTentacleSystem(); r=m.process({'bug_report':'NullPointer','code_context':None,'requested_action':'analyze','risk_level':'low'}); print('OK' if r['code_context']['has_context']==False else 'FAIL')"),
    ("No test_output", "from coding_tentacle.tentacles.mini_tentacle_system import MiniTentacleSystem; m=MiniTentacleSystem(); r=m.process({'bug_report':'NullPointer in p.py:1','code_context':{'file':'p.py','line':1},'test_output':None,'requested_action':'analyze','risk_level':'medium'}); print('OK' if r['final_route'] in ('CENTRAL_REVIEW','ROUTE_TO_TENTACLE') else f'FAIL:{r[\"final_route\"]}')"),
]
for name, code in missing_tests:
    out, err, rc = run_code(code, timeout=10)
    if 'OK' not in out:
        bug('P2', 14, f'Missing data: {name}', '', out, 'Improve handling', False)

print("STAGE 15: Broken test output")
broken_test_code = "from coding_tentacle.tentacles.mini_tentacle_system import MiniTentacleSystem; m=MiniTentacleSystem(); r=m.process({'bug_report':'NullPointer in p.py:1','code_context':{'file':'p.py','line':1},'test_output':'TRACEBACK:segfault_crash!!!','requested_action':'analyze','risk_level':'medium'}); print('HANDLED' if r else 'CRASH')"
out, err, rc = run_code(broken_test_code, timeout=10)
if rc != 0 or 'CRASH' in out:
    bug('P2', 15, 'Broken test output crashes', '', err[:100], 'Sanitize input', False)

print("STAGE 16: Empty inputs")
empty_tests = [
    ("Empty bug_report", "from coding_tentacle.brains.sg_brain import SymbolGroundingBrain; bq=SymbolGroundingBrain(); r=bq.think(''); print('OK' if r['action']=='ASK_CONTEXT' else f'FAIL:{r[\"action\"]}')"),
]
for name, code in empty_tests:
    out, err, rc = run_code(code, timeout=10)
    if 'OK' not in out:
        bug('P1', 16, f'Empty input: {name}', '', out, 'Add empty check', True)

# ═══════════ STAGE 17: CONTRADICTORY INPUTS ═══════════
print("STAGE 17: Contradictory inputs")
contra_code = "from coding_tentacle.tentacles.mini_tentacle_system import MiniTentacleSystem; m=MiniTentacleSystem(); sid=None; for i in range(5): r=m.process({'session_id':sid,'bug_report':f'Bug{i} in file{i}.py:{i}','code_context':{'file':f'file{i}.py','line':i},'requested_action':'analyze','risk_level':'low'}); sid=r['session_id']; r2=m.process({'session_id':sid,'bug_report':'DifferentBug in other.py:99','code_context':{'file':'other.py','line':99},'requested_action':'analyze','risk_level':'low'}); print('HANDLED' if r2 else 'CRASH')"
out, err, rc = run_code(contra_code, timeout=15)
if rc != 0 or 'CRASH' in out:
    bug('P2', 17, 'Contradictory session data', '', err[:100], 'Handle conflicts', False)

# ═══════════ STAGE 18: RISKY PATCHES ═══════════
print("STAGE 18: Risky patch simulation")
risky = [
    ("SQL injection", "DROP TABLE users; --"),
    ("Shell injection", "os.system('rm -rf /')"),
    ("Eval injection", "eval(user_input)"),
    ("Path traversal", "../../etc/passwd"),
]
for name, patch in risky:
    code = f'from coding_tentacle.patch.patch_suggestion import PatchSuggestionEngine; ps=PatchSuggestionEngine(); r=ps.suggest("{patch}",code_context={{"file":"t.py","line":1}},grounding={{"grounding_score":0.5}}); print("SAFE" if r["patch_type"]=="BLOCKED" else "UNSAFE: "+r["patch_type"])'
    out, err, rc = run_code(code, timeout=10)
    if 'UNSAFE' in out:
        bug('P0', 18, f'Unsafe patch not blocked: {name}', 'patch_suggestion.py', out, 'Add to DANGEROUS_PATTERNS', True)

# ═══════════ STAGE 19: HERMES RED-LINE RECONSTRUCTION ═══════════
print("STAGE 19: Hermes red-line reconstruction")
hermes_tests = [
    ("Duplicate if-blocks", "Check for 'if __name__' appearing twice in any file"),
    ("Indentation corruption", "Check all files compile with ast.parse"),
    ("Import loops", "Check for circular imports"),
]
for root, dirs, files in os.walk('src'):
    for f in files:
        if f.endswith('.py'):
            fp = os.path.join(root, f)
            content = open(fp).read()
            if content.count('if __name__ == "__main__":') > 1:
                bug('P1', 19, f'Duplicate if-block: {fp}', fp, '2x if __name__', 'Remove duplicate', True)
            try:
                ast.parse(content)
            except SyntaxError as e:
                bug('P1', 19, f'Indentation error: {fp}', fp, str(e), 'Fix indentation', True)

# ═══════════ STAGE 20: ERROR SUMMARY ═══════════
print("STAGE 20: Error summary")

P0 = [b for b in BUGS_FOUND if b['level'] == 'P0']
P1 = [b for b in BUGS_FOUND if b['level'] == 'P1']
P2 = [b for b in BUGS_FOUND if b['level'] == 'P2']
P3 = [b for b in BUGS_FOUND if b['level'] == 'P3']

print(f"\n{'='*65}")
print(f"  DEEP BUG HUNT — COMPLETE")
print(f"  {'='*65}")
print(f"  P0 (Critical):  {len(P0)}")
print(f"  P1 (High):      {len(P1)}") 
print(f"  P2 (Medium):    {len(P2)}")
print(f"  P3 (Low):       {len(P3)}")
print(f"  TOTAL BUGS:     {len(BUGS_FOUND)}")

if P0:
    print(f"\n  🔴 P0 CRITICAL:")
    for b in P0:
        print(f"     Stage {b['stage']}: {b['title']}")

if BUGS_FOUND:
    print(f"\n  📁 Report: RC2_DEEP_BUG_HUNT_REPORT.json")
    with open('RC2_DEEP_BUG_HUNT_REPORT.json', 'w') as f:
        json.dump({'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'), 
                   'total_bugs': len(BUGS_FOUND),
                   'P0': len(P0), 'P1': len(P1), 'P2': len(P2), 'P3': len(P3),
                   'bugs': BUGS_FOUND}, f, indent=2, default=str)
else:
    print(f"\n  ✅ NO BUGS FOUND — RC2 is clean")
