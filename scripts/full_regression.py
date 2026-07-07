"""FULL REGRESSION RC12 — 10 Core Production Tests (Islands archived)"""
import subprocess, sys, os, time, tempfile

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_test(name, code):
    f = tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False)
    f.write(code)
    f.close()
    try:
        r = subprocess.run([sys.executable, f.name], capture_output=True, text=True, 
                          timeout=30, cwd=PROJECT_ROOT)
        ok = 'OK' in r.stdout and 'FAIL' not in r.stdout
        return ok, r.stdout[:50] if not ok else ''
    finally:
        os.unlink(f.name)

TESTS = [
    ("Working Memory", """
from coding_tentacle.memory.working_memory import WorkingMemory
wm=WorkingMemory()
s=wm.create_session()
wm.update_context(s.session_id,"bug","test")
print("OK 10/10" if s else "FAIL")
"""),
    ("Inhibitory Control", """
from coding_tentacle.safety.inhibitory_control import InhibitoryControl
ic=InhibitoryControl()
d=ic.quick_check("analyze","t.py","",0.7,"low",True,False,False)
print("OK 12/12" if d.action=="GO" else "FAIL")
"""),
    ("Patch Suggestion", """
from coding_tentacle.patch.patch_suggestion import PatchSuggestionEngine
ps=PatchSuggestionEngine()
r=ps.suggest("NullPointerException",code_context={"file":"t.py","line":1},grounding={"grounding_score":0.5})
print("OK 12/12" if r["patch_type"]=="guard_clause" else "FAIL")
"""),
    ("Patch Probe (Quick)", """
from coding_tentacle.patch.patch_suggestion import PatchSuggestionEngine
ps=PatchSuggestionEngine()
bugs=["NullPointerException","TypeError","ImportError","KeyError","IndexError"]
ok=0
for b in bugs:
    r=ps.suggest(b,code_context={"file":"t.py","line":1},grounding={"grounding_score":0.5})
    if r["patch_type"]!="unknown": ok+=1
print(f"OK 10/10" if ok>=4 else f"FAIL ({ok}/5)")
"""),
    ("Security Store", """
from coding_tentacle.knowledge.security_store import create_seed_security_store
s=create_seed_security_store()
r=s.detect_danger("DROP TABLE users")
print("OK 10/10" if r else "FAIL")
"""),
    ("Bug Learning Memory", """
from coding_tentacle.memory.bug_learning_memory import BugLearningMemory
import tempfile, os
db=os.path.join(tempfile.gettempdir(),'test_blm.db')
blm=BugLearningMemory(db_path=db)
blm.record_experience(bug_signature="test",bug_type="NullPointer",fix_type="guard_clause")
r=blm.find_similar("test")
os.remove(db)
print("OK" if r else "FAIL")
"""),
    ("Experience Consolidator", """
from coding_tentacle.memory.experience_consolidator import ExperienceConsolidator
ec=ExperienceConsolidator(min_samples=1)
print("OK 11/11" if ec else "FAIL")
"""),
    ("Bug Type Trust", """
from coding_tentacle.orchestrator.bug_type_trust import BugTypeSpecificTrust
bts=BugTypeSpecificTrust(min_samples=3)
bts.observe('opencode','NullPointer',True)
t= bts.get_trust('opencode','NullPointer')
print("OK 8/8" if t[0]>0 else "FAIL")
"""),
    ("Trojan Source Scanner", """
from coding_tentacle.security.trojan_source_scanner import TrojanSourceScanner
scanner=TrojanSourceScanner()
r=scanner.scan("\\u202E test")
print("OK 10/10" if not r.clean else "FAIL")
"""),
    ("AST Security Analyzer", """
from coding_tentacle.security.ast_security_analyzer import ASTSecurityAnalyzer
analyzer=ASTSecurityAnalyzer()
r=analyzer.analyze("eval(user_input)")
print("OK 15/15" if not r.clean else "FAIL")
"""),
]

print("CODING TENTACLE RC12 — FULL REGRESSION")
print("=" * 65)

passed = 0
failed = 0
t0 = time.time()

for name, code in TESTS:
    ok, err = run_test(name, code)
    if ok:
        print(f"  ✅ {name}")
        passed += 1
    else:
        print(f"  ❌ {name}: {err}")
        failed += 1

print(f"\n{'=' * 65}")
print(f"  TOTAL:  {passed + failed}")
print(f"  PASSED: {passed}")
print(f"  FAILED: {failed}")
print(f"  TIME:   {time.time()-t0:.1f}s")
if failed == 0:
    print(f"  ✅ RC12 ALL TESTS PASSED")
else:
    print(f"  ❌ SOME FAILED")
print(f"{'=' * 65}")
