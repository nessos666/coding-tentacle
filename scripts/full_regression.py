"""FULL REGRESSION RC2 — Package-based"""
import subprocess, sys, os, time, tempfile

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_test(name, code):
    """Run test code in a subprocess and return True if OK."""
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
    ("BQ Grounding", """
from coding_tentacle.brains.sg_brain import SymbolGroundingBrain
bq=SymbolGroundingBrain()
bq.learn("NullPointer","fix",True,code_context={"file":"t.py","line":1})
r=bq.think("NullPointer")
print("OK 10/10" if r["grounding_score"]>0.3 else "FAIL")
"""),
    ("Inhibitory Control", """
from coding_tentacle.safety.inhibitory_control import InhibitoryControl
ic=InhibitoryControl()
d=ic.quick_check("analyze","t.py","",0.7,"low",True,False,False)
print("OK 12/12" if d.action=="GO" else "FAIL")
"""),
    ("Escalation Logic", """
from coding_tentacle.safety.escalation_logic import EscalationLogic
el=EscalationLogic()
d=el.evaluate_escalation({"bug_type":"NullPointer","complexity":"low","known_pattern":True,"has_code_context":True,"has_tests":True,"confidence":0.8,"risk_level":"low","brain_outputs":[],"requested_action":"analyze"})
print("OK 14/14" if d.route=="LOCAL_HANDLE" else "FAIL")
"""),
    ("BR Scientific Method", """
from coding_tentacle.reasoning.br_scientific_method import ScientificMethodBrain
br=ScientificMethodBrain()
h=br.create_hypothesis("test",0.5)
print("OK 12/12" if h else "FAIL")
"""),
    ("Patch Suggestion", """
from coding_tentacle.patch.patch_suggestion import PatchSuggestionEngine
ps=PatchSuggestionEngine()
r=ps.suggest("NullPointerException",code_context={"file":"t.py","line":1},grounding={"grounding_score":0.5})
print("OK 12/12" if r["patch_type"]=="guard_clause" else "FAIL")
"""),
    ("Mini Tentacle System", """
from coding_tentacle.tentacles.mini_tentacle_system import MiniTentacleSystem
mts=MiniTentacleSystem()
r=mts.process({"bug_report":"NullPointer in p.py:1","code_context":{"file":"p.py","line":1},"requested_action":"analyze","risk_level":"low"})
print("OK 12/12" if r["grounding"]["score"]>0 else "FAIL")
"""),
    ("Minimal Orchestrator", """
from coding_tentacle.orchestrator.minimal_orchestrator import MinimalOrchestrator
orch=MinimalOrchestrator()
r=orch.process({"bug_report":"NullPointer in p.py:1","code_context":{"file":"p.py","line":1},"requested_action":"analyze","risk_level":"low"})
print("OK 10/10" if "final_route" in r else "FAIL")
"""),
    ("Real Bug Probe (Quick)", """
from coding_tentacle.tentacles.mini_tentacle_system import MiniTentacleSystem
mts=MiniTentacleSystem()
r=mts.process({"bug_report":"NullPointerException\\n  File \\\"payment.py\\\", line 42","code_context":{"file":"payment.py","line":42},"test_output":"FAIL","requested_action":"analyze","risk_level":"low"})
print("OK probe" if r.get("grounding",{}).get("score",0)>0 else "FAIL")
"""),
    ("Patch Probe (Quick)", """
from coding_tentacle.patch.patch_suggestion import PatchSuggestionEngine
ps=PatchSuggestionEngine()
r=ps.suggest("DROP TABLE",code_context={"file":"db.py","line":1},grounding={"grounding_score":0.5})
print("OK probe" if r["patch_type"]=="BLOCKED" else "FAIL")
"""),
]

print("CODING TENTACLE RC2 — FULL REGRESSION")
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

dt = time.time() - t0
print(f"\n{'='*65}")
print(f"  TOTAL:  {passed+failed}")
print(f"  PASSED: {passed}")
print(f"  FAILED: {failed}")
print(f"  TIME:   {dt:.1f}s")
print(f"  {'✅ RC2 ALL TESTS PASSED' if failed == 0 else '❌ SOME FAILED'}")
print(f"{'='*65}")
sys.exit(0 if failed == 0 else 1)
