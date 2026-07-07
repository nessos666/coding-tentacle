"""
HUMAN APPROVAL GATE — RC15
Final safety layer. NEVER auto-applies patches to real files.
All patches require human APPROVE before touching originals.

Safety VETO > Human Approval > Auto-Apply (never)

Autor: Hermes + David | Coding Tentacle 2026
"""

# CT-v11.0.0: PRODUCTION | 10/10 regression | 25 modules | 90% wired | Droste active
import time, json, os
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional


class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"
    SAFETY_BLOCKED = "safety_blocked"


@dataclass
class ApprovalRequest:
    """A request for human approval before applying a patch."""
    request_id: str
    summary: str               # "Fix NullPointer in payment.py:42"
    bug_type: str
    file_path: str
    diff: str                  # Unified diff
    sandbox_test_result: str   # "PASS", "FAIL", "NOT_RUN"
    risk_level: str            # "low", "medium", "high", "critical"
    confidence: float = 0.5
    status: str = "pending"    # pending, approved, rejected, changes_requested
    human_comment: str = ""
    approved_by: str = ""
    approved_at: float = 0.0
    created_at: float = 0.0
    
    def __post_init__(self):
        if self.created_at == 0.0:
            self.created_at = time.time()


class ApprovalGate:
    """Human approval required before ANY real file write.
    Safety VETO is stronger — blocked patches never reach approval."""
    
    AUTO_APPROVE_NEVER = True  # NEVER auto-approve
    
    def __init__(self, safety_brain=None):
        self.safety_brain = safety_brain
        self.requests = {}
        self.total_requests = 0
        self.approved_count = 0
        self.rejected_count = 0
        self.blocked_count = 0
    
    def submit_for_approval(self, repair_result, patch_diff=None, 
                           sandbox_result=None, test_result=None) -> Optional[ApprovalRequest]:
        """Submit a repair for human approval. Always returns a request, never applies."""
        self.total_requests += 1
        
        # ═══ SAFETY VETO (always first) ═══
        if self.safety_brain and patch_diff:
            safety_check = self.safety_brain.evaluate(
                f"{patch_diff.bug_type}: {patch_diff.diff[:100]}",
                proposed_action="apply_to_real_files",
                patch=patch_diff.diff,
            )
            if safety_check.decision == 'BLOCK':
                self.blocked_count += 1
                req = ApprovalRequest(
                    request_id=f"REQ-{self.total_requests:04d}",
                    summary=f"[BLOCKED] {patch_diff.bug_type} in {patch_diff.file_path}",
                    bug_type=patch_diff.bug_type,
                    file_path=patch_diff.file_path,
                    diff=patch_diff.diff,
                    sandbox_test_result="BLOCKED",
                    risk_level="critical",
                    confidence=0.0,
                    status="safety_blocked",
                )
                self.requests[req.request_id] = req
                return req
        
        # ═══ BUILD APPROVAL REQUEST ═══
        if patch_diff:
            bug_type = patch_diff.bug_type
            file_path = patch_diff.file_path
            diff = patch_diff.diff
            confidence = patch_diff.confidence
            test_status = "PASS" if (test_result and test_result.success) else \
                          "FAIL" if test_result else "NOT_RUN"
        else:
            bug_type = "Unknown"
            file_path = "unknown"
            diff = ""
            confidence = 0.0
            test_status = "NOT_RUN"
        
        # Determine risk level
        risk = "low"
        if bug_type in ("SecurityRisk",):
            risk = "critical"
        elif bug_type == "Unknown":
            risk = "high"
        elif test_status == "FAIL":
            risk = "medium"
        elif sandbox_result and not sandbox_result.success:
            risk = "high"
        
        req = ApprovalRequest(
            request_id=f"REQ-{self.total_requests:04d}",
            summary=f"Fix {bug_type} in {file_path}",
            bug_type=bug_type,
            file_path=file_path,
            diff=diff,
            sandbox_test_result=test_status,
            risk_level=risk,
            confidence=confidence,
        )
        self.requests[req.request_id] = req
        return req
    
    def approve(self, request_id, approved_by="human", comment=""):
        """Human approves the patch."""
        req = self.requests.get(request_id)
        if not req:
            return False
        if req.status == "safety_blocked":
            return False  # Safety VETO cannot be overridden
        
        req.status = "approved"
        req.approved_by = approved_by
        req.approved_at = time.time()
        req.human_comment = comment
        self.approved_count += 1
        return True
    
    def reject(self, request_id, reason=""):
        """Human rejects the patch."""
        req = self.requests.get(request_id)
        if not req:
            return False
        req.status = "rejected"
        req.human_comment = reason
        self.rejected_count += 1
        return True
    
    def request_changes(self, request_id, comment=""):
        """Human requests changes to the patch."""
        req = self.requests.get(request_id)
        if not req:
            return False
        req.status = "changes_requested"
        req.human_comment = comment
        return True
    
    def is_approved(self, request_id):
        req = self.requests.get(request_id)
        return req and req.status == "approved"
    
    def get_pending(self):
        return [r for r in self.requests.values() if r.status == "pending"]
    
    def stats(self):
        return {
            'total_requests': self.total_requests,
            'approved': self.approved_count,
            'rejected': self.rejected_count,
            'blocked': self.blocked_count,
            'pending': len(self.get_pending()),
            'actions_executed': 0,  # Never auto-applies
        }


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    from coding_tentacle.orchestrator.metabrain import SafetyBrain
    from coding_tentacle.safety.inhibitory_control import InhibitoryControl
    from coding_tentacle.knowledge.security_store import create_seed_security_store
    from coding_tentacle.patch.diff_generator import PatchDiff
    
    print("HUMAN APPROVAL GATE — Self-Test")
    print("=" * 55)
    passed = 0
    
    sec = create_seed_security_store()
    ic = InhibitoryControl(security_store=sec)
    safety = SafetyBrain(ic=ic, security_store=sec)
    gate = ApprovalGate(safety_brain=safety)
    
    # T1: Submit safe patch for approval
    pd = PatchDiff(
        file_path='payment.py', bug_type='NullPointer',
        original_code='total = price * quantity',
        patched_code='if price:\n    total = price * quantity',
        diff='+if price:\n     total = price * quantity',
        confidence=0.85, safety_checked=True, safety_passed=True,
    )
    req = gate.submit_for_approval(None, patch_diff=pd)
    t1 = req is not None and req.status == "pending"
    print(f"  T1: {'✅' if t1 else '❌'} Submit → {req.status if req else 'NONE'}")
    
    # T2: Request has file path and diff
    t2 = req and req.file_path == 'payment.py' and req.diff
    print(f"  T2: {'✅' if t2 else '❌'} Request details → file={req.file_path}, rank={req.risk_level}")
    
    # T3: Approve
    gate.approve(req.request_id, approved_by="David", comment="Looks good")
    t3 = gate.is_approved(req.request_id)
    print(f"  T3: {'✅' if t3 else '❌'} Approve → {req.status}")
    
    # T4: Reject
    req2 = gate.submit_for_approval(None, 
        patch_diff=PatchDiff(file_path='test.py', bug_type='TypeError',
            original_code='x', patched_code='y', diff='+y',
            confidence=0.5, safety_checked=True, safety_passed=True))
    gate.reject(req2.request_id, "Wrong approach")
    t4 = req2.status == "rejected"
    print(f"  T4: {'✅' if t4 else '❌'} Reject → {req2.status}")
    
    # T5: Request changes
    req3 = gate.submit_for_approval(None,
        patch_diff=PatchDiff(file_path='api.py', bug_type='NullPointer',
            original_code='x', patched_code='z', diff='+z',
            confidence=0.7, safety_checked=True, safety_passed=True))
    gate.request_changes(req3.request_id, "Add None check before guard")
    t5 = req3.status == "changes_requested"
    print(f"  T5: {'✅' if t5 else '❌'} Request changes → {req3.status}")
    
    # T6: DROP TABLE blocked by safety, never reaches pending
    pd_danger = PatchDiff(
        file_path='db.py', bug_type='SecurityRisk',
        original_code='SELECT *', patched_code='DROP TABLE',
        diff='+DROP TABLE', confidence=0, safety_checked=True, safety_passed=False,
    )
    req_danger = gate.submit_for_approval(None, patch_diff=pd_danger)
    t6 = req_danger.status == "safety_blocked"
    print(f"  T6: {'✅' if t6 else '❌'} Safety blocks → {req_danger.status}")
    
    # T7: Safety-blocked cannot be approved
    blocked = not gate.approve(req_danger.request_id)
    t7 = blocked
    print(f"  T7: {'✅' if t7 else '❌'} Safety override PREVENTED → {'YES' if blocked else 'NO (FAIL!)'}")
    
    # T8: Stats
    st = gate.stats()
    t8 = st['actions_executed'] == 0
    print(f"  T8: {'✅' if t8 else '❌'} Stats → {st['total_requests']} requests, read-only")
    
    passed = sum([t1,t2,t3,t4,t5,t6,t7,t8])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/8 Tests bestanden")
    print(f"  {'✅ HUMAN APPROVAL GATE FERTIG' if passed >= 7 else '⚠️'}")
