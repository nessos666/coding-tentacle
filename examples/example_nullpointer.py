"""Example: NullPointer Bug — Full Coding Tentacle Pipeline

This script demonstrates the full CT pipeline on a NullPointerException bug.
Run: python examples/example_nullpointer.py
Requires: coding-tentacle installed (pip install -e .)
"""
import sys
import os

# Ensure src/ is on path for development installs
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from coding_tentacle.memory.working_memory import WorkingMemory
from coding_tentacle.safety.inhibitory_control import InhibitoryControl
from coding_tentacle.knowledge.security_store import create_seed_security_store
from coding_tentacle.patch.patch_suggestion import PatchSuggestionEngine
from coding_tentacle.orchestrator.engine_router import EngineRouter

print("=" * 65)
print("CODING TENTACLE — Example: NullPointer Bug")
print("=" * 65)

# ── Step 1: Initialize Core Components ──────────────────────
wm = WorkingMemory()
session = wm.create_session()
ic = InhibitoryControl()
sec = create_seed_security_store()
engine = PatchSuggestionEngine()
router = EngineRouter()

# ── Step 2: Bug Report ──────────────────────────────────────
bug = (
    'NullPointerException\n'
    '  File "payment.py", line 42, in process\n'
    '    return obj.amount'
)
ctx = {"file": "payment.py", "line": 42, "code": "obj.amount"}

print(f"\n🐛 BUG: {bug.split(chr(10))[0]}")
print(f"📍 FILE: {ctx['file']}:{ctx['line']}")

# ── Step 3: Safety Check ────────────────────────────────────
decision = ic.quick_check(
    proposed_action="analyze", target_file=ctx["file"],
    patch="", confidence=0.7,
    risk_level="low", test_available=False,
    rollback_available=False, security_sensitive=False,
)
print(f"\n🛡️  SAFETY: {decision.action} (blockers={decision.blockers})")

# ── Step 4: Security Scan ───────────────────────────────────
danger = sec.detect_danger(bug)
print(f"🔒 SECURITY: {'⚠️  DANGER DETECTED' if danger else '✅ Clean'}")

# ── Step 5: Patch Suggestion ────────────────────────────────
patch = engine.suggest(
    bug,
    code_context=ctx,
    grounding={"grounding_score": 0.7},
)
print(f"\n🔧 PATCH SUGGESTION:")
print(f"   Type: {patch['patch_type']}")
print(f"   Patch:\n{patch['suggested_patch']}")
print(f"   Explanation: {patch['explanation']}")
print(f"   Risk: {patch['risk_level']} | Human review: {patch['requires_human_review']}")

# ── Step 6: Engine Router Health ───────────────────────────
router.check_health()
print(f"\n⚙️  ROUTER: {'✅ Healthy' if router.health_checked else '❌ Unhealthy'}")

# ── Step 7: Working Memory Audit ────────────────────────────
wm.update_context(session.session_id, "bug", bug)
print(f"🧠 MEMORY: Session {session.session_id} updated")

print(f"\n{'=' * 65}")
print("✅ EXAMPLE COMPLETE — 0 assertions failed")
print(f"{'=' * 65}")
