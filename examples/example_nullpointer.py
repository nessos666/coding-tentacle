"""Example: NullPointer Bug — Full Pipeline"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '71_symbol_grounding'))
from mini_tentacle_system import MiniTentacleSystem
from patch_suggestion import PatchSuggestionEngine

print("=" * 65)
print("CODING TENTACLE — Example: NullPointer Bug")
print("=" * 65)

mts = MiniTentacleSystem()
engine = PatchSuggestionEngine()

# Step 1: Bug report
bug = 'NullPointerException\n  File "payment.py", line 42, in process\n    return obj.amount'
ctx = {'file': 'payment.py', 'line': 42, 'function': 'process', 'code': 'obj.amount'}
test = 'FAIL: test_payment_processing'

print(f"\n🐛 BUG: {bug.split(chr(10))[0]}")
print(f"📍 FILE: {ctx['file']}:{ctx['line']}")
print(f"🧪 TEST: {test}")

# Step 2: Mini-Tentacle Analysis
r = mts.process({
    'bug_report': bug, 'code_context': ctx,
    'test_output': test, 'requested_action': 'analyze', 'risk_level': 'low'
})

print(f"\n📊 ANALYSIS:")
print(f"   Grounding: {r['grounding']['score']:.2f} — {r['grounding']['meaning'][:60]}")
print(f"   Hypotheses: {r['reasoning']['hypotheses']}")
print(f"   Safety: {r['safety']['route']} (authorized={r['authorized']})")

# Step 3: Patch Suggestion
p = engine.suggest(bug, code_context=ctx, test_output=test,
                   grounding={'grounding_score': r['grounding']['score']})

print(f"\n🔧 PATCH SUGGESTION:")
print(f"   Type: {p['patch_type']}")
print(f"   Patch:\n{p['suggested_patch']}")
print(f"   Explanation: {p['explanation']}")
print(f"   Risk: {p['risk_level']} | Human review: {p['requires_human_review']}")
print(f"   Tests to run: {p['tests_to_run']}")
print(f"\n⚠️  NOTE: This is a SUGGESTION only. No code was changed.")
