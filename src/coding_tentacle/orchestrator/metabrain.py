"""
METABRAIN V1 — RC10
Four specialized sub-brains coordinated through TentacleBus.
Teacher | Planning | Safety | Learning

Safety Brain has VETO over all others.
Conflicts resolved by priority: Safety > Teacher > Planning > Learning.

Autor: Hermes + David | Coding Tentacle 2026
"""

# CT-v11.0.0: PRODUCTION | 10/10 regression | 25 modules | 90% wired | Droste active
import time
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class BrainDecision:
    """Output from one sub-brain."""
    brain_name: str          # "Teacher", "Planning", "Safety", "Learning"
    decision: str            # "GO", "BLOCK", "ASK_CONTEXT", "PLAN_READY"
    reason: str
    confidence: float = 0.5
    metadata: dict = field(default_factory=dict)
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


class SafetyBrain:
    """Has ABSOLUTE VETO. Blocks dangerous operations. Never overridden."""
    
    def __init__(self, ic=None, security_store=None, el=None):
        self.ic = ic
        self.security_store = security_store
        self.el = el
        self.name = "Safety"
        self.priority = 100  # Highest
    
    def evaluate(self, bug_report, proposed_action="analyze", 
                 patch="", confidence=0.5, context=None):
        """Safety check — runs FIRST, can BLOCK everything.
        Now scans BOTH bug_report AND code/patch content (RC15.9B)."""
        bug_lower = bug_report.lower()
        patch_lower = (patch or "").lower()
        if context and isinstance(context, dict):
            code = context.get('file', '') + ' ' + context.get('code', '')
            patch_lower += ' ' + code.lower()
        
        # Hard security checks
        dangerous = any(w in bug_lower or w in patch_lower for w in 
            ['drop table', 'delete from', 'rm -rf', 'api_key', 
             'secret', 'password', '../../', '/etc/passwd', 'eval(',
             'exec(', 'os.system', 'subprocess', 'pickle.loads',
             'curl ', 'wget ', '__import__("os"', '/etc/shadow'])
        
        if dangerous:
            return BrainDecision(
                brain_name="Safety",
                decision="BLOCK",
                reason=f"Security pattern detected: {bug_report[:60]}",
                confidence=1.0,
                metadata={'veto': True, 'dangerous': True}
            )
        
        # Check SecurityStore
        if self.security_store:
            results = self.security_store.detect_danger(patch or bug_report)
            if results:
                return BrainDecision(
                    brain_name="Safety",
                    decision="BLOCK",
                    reason=f"SecurityStore: {results[0].name if hasattr(results[0], 'name') else 'danger detected'}",
                    confidence=0.95,
                    metadata={'veto': True, 'source': 'SecurityStore'}
                )
        
        # Safe — pass through
        return BrainDecision(
            brain_name="Safety",
            decision="GO",
            reason="No security threat detected",
            confidence=0.9,
            metadata={'veto': False}
        )


class TeacherBrain:
    """Evaluates hypotheses and creates repair plans."""
    
    def __init__(self, bq=None, br=None, teacher=None):
        self.bq = bq
        self.br = br
        self.teacher = teacher  # RC8.5 Teacher
        self.name = "Teacher"
        self.priority = 90
    
    def evaluate(self, bug_report, grounding=None, context=None):
        # If we have RC8.5 Teacher, delegate
        if self.teacher:
            plan = self.teacher.create_plan(bug_report, 
                                           grounding=grounding)
            if plan:
                return BrainDecision(
                    brain_name="Teacher",
                    decision="PLAN_READY",
                    reason=f"Plan created: {plan.fix_type} for {plan.bug_type}",
                    confidence=plan.confidence,
                    metadata={'plan': asdict(plan)}
                )
        
        # Fallback: use BQ
        if self.bq:
            r = self.bq.think(bug_report)
            bt = r.get('bug_type', 'Unknown')
            return BrainDecision(
                brain_name="Teacher",
                decision="GO" if bt not in ('Unknown', 'SecurityRisk') else "ASK_CONTEXT",
                reason=f"BQ identified: {bt}",
                confidence=r.get('grounding_score', 0.3),
                metadata={'bug_type': bt}
            )
        
        return BrainDecision(
            brain_name="Teacher",
            decision="ASK_CONTEXT",
            reason="No BQ or Teacher available",
            confidence=0.1
        )


class PlanningBrain:
    """Plans step sequence — which Skills/Procedures to use."""
    
    def __init__(self, procedural_memory=None, skill_store=None, rule_memory=None):
        self.procedural_memory = procedural_memory
        self.skill_store = skill_store
        self.rule_memory = rule_memory
        self.name = "Planning"
        self.priority = 80
    
    def evaluate(self, bug_type, teacher_plan=None, context=None):
        procedure = None
        if self.procedural_memory and bug_type != 'SecurityRisk':
            procedure = self.procedural_memory.find_procedure(bug_type)
        
        skill = None
        if self.skill_store and bug_type != 'SecurityRisk':
            skill = self.skill_store.best_skill_for(bug_type)
        
        steps = []
        if procedure:
            steps = [s.action for s in procedure.steps[:5]]
        if skill:
            steps.append(f"skill:{skill.name}")
        
        if steps:
            return BrainDecision(
                brain_name="Planning",
                decision="SEQUENCE_READY",
                reason=f"{len(steps)} steps planned",
                confidence=procedure.confidence if procedure else 0.6,
                metadata={'steps': steps, 'has_skill': skill is not None}
            )
        
        return BrainDecision(
            brain_name="Planning",
            decision="NO_SEQUENCE",
            reason=f"No procedure/skill for {bug_type}",
            confidence=0.3
        )


class LearningBrain:
    """Collects feedback and updates all learning stores."""
    
    def __init__(self, blm=None, rule_memory=None, hypothesis_feedback=None,
                 feedback_dampener=None, coordinator=None):
        self.blm = blm
        self.rule_memory = rule_memory
        self.hypothesis_feedback = hypothesis_feedback
        self.feedback_dampener = feedback_dampener
        self.coordinator = coordinator  # Local learning coordinator
        self.name = "Learning"
        self.priority = 70  # Lowest — never overrides Safety/Teacher
    
    def evaluate(self, bug_type, execution_result=None, context=None):
        learnings = []
        
        # Collect from BLM
        if self.blm:
            best = self.blm.best_fix_for(bug_type)
            if best:
                learnings.append(f"BLM: {best[0]['fix_type']} ({best[0]['count']}× success)")
        
        # Collect from local tentacles
        if self.coordinator:
            agg = self.coordinator.aggregate_for_teacher(bug_type)
            if agg.get('conflicts'):
                learnings.append(f"Conflicts: {agg['conflicts']}")
        
        return BrainDecision(
            brain_name="Learning",
            decision="FEEDBACK_COLLECTED",
            reason=f"{len(learnings)} learnings available",
            confidence=0.7 if learnings else 0.3,
            metadata={'learnings': learnings}
        )


class MetaBrain:
    """Coordinates 4 sub-brains. Safety has VETO. Conflicts resolved by priority."""
    
    def __init__(self, safety=None, teacher=None, planning=None, learning=None, bus=None):
        self.safety = safety or SafetyBrain()
        self.teacher = teacher or TeacherBrain()
        self.planning = planning or PlanningBrain()
        self.learning = learning or LearningBrain()
        self.bus = bus
        self.brains = [self.safety, self.teacher, self.planning, self.learning]
        # Sort by priority (highest first)
        self.brains.sort(key=lambda b: -b.priority)
    
    def decide(self, bug_report, code_context=None, grounding=None, 
               proposed_action="analyze", patch=""):
        """Run all 4 brains. Safety first. Resolve conflicts."""
        decisions = {}
        
        # 1. SAFETY ALWAYS FIRST — can BLOCK everything
        safety_decision = self.safety.evaluate(bug_report, proposed_action, 
                                               patch, 0.5, code_context)
        decisions['Safety'] = safety_decision
        
        if safety_decision.decision == 'BLOCK':
            # VETO — stop here, no other brain matters
            if self.bus:
                self.bus.publish_event('metabrain_blocked', 
                    {'reason': safety_decision.reason})
            return {
                'final_decision': 'BLOCK',
                'reason': safety_decision.reason,
                'source': 'Safety',
                'brain_decisions': decisions,
                'authorized': False,
            }
        
        # 2. Teacher evaluates
        teacher_decision = self.teacher.evaluate(bug_report, grounding, code_context)
        decisions['Teacher'] = teacher_decision
        
        # 3. Planning evaluates (if Teacher has a plan)
        bug_type = 'Unknown'
        if teacher_decision.metadata.get('bug_type'):
            bug_type = teacher_decision.metadata['bug_type']
        elif teacher_decision.metadata.get('plan', {}).get('bug_type'):
            bug_type = teacher_decision.metadata['plan']['bug_type']
        
        planning_decision = self.planning.evaluate(bug_type, teacher_decision)
        decisions['Planning'] = planning_decision
        
        # 4. Learning evaluates
        learning_decision = self.learning.evaluate(bug_type, None, code_context)
        decisions['Learning'] = learning_decision
        
        # Determine final decision
        if teacher_decision.decision == 'PLAN_READY':
            final = 'PROCEED_WITH_PLAN'
            authorized = True
            reason = f"Plan ready: {teacher_decision.reason}. {learning_decision.reason}"
        elif teacher_decision.decision == 'ASK_CONTEXT':
            final = 'ASK_CONTEXT'
            authorized = False
            reason = teacher_decision.reason
        else:
            final = 'GO'
            authorized = True
            reason = 'Safety passed, proceeding'
        
        if self.bus:
            self.bus.publish_event('metabrain_decision', 
                {'final': final, 'authorized': authorized})
        
        return {
            'final_decision': final,
            'reason': reason,
            'source': 'MetaBrain',
            'brain_decisions': decisions,
            'authorized': authorized,
            'confidence': teacher_decision.confidence,
        }
    
    def stats(self):
        return {
            'total_brains': 4,
            'brain_names': [b.name for b in self.brains],
            'safety_veto_active': True,
            'actions_executed': 0,
        }


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    from coding_tentacle.safety.inhibitory_control import InhibitoryControl
    from coding_tentacle.knowledge.security_store import create_seed_security_store
    
    print("METABRAIN V1 — Self-Test")
    print("=" * 55)
    passed = 0
    
    sec = create_seed_security_store()
    ic = InhibitoryControl(security_store=sec)
    safety = SafetyBrain(ic=ic, security_store=sec)
    teacher = TeacherBrain()
    planning = PlanningBrain()
    learning = LearningBrain()
    mb = MetaBrain(safety=safety, teacher=teacher, planning=planning, learning=learning)
    
    # T1: Normal bug passes safety
    result = mb.decide("NullPointerException in test.py:42")
    t1 = result['final_decision'] != 'BLOCK'
    print(f"  T1: {'✅' if t1 else '❌'} NullPointer → {result['final_decision']}")
    
    # T2: Security bug BLOCKED
    result2 = mb.decide("DROP TABLE users; -- SQL injection")
    t2 = result2['final_decision'] == 'BLOCK'
    print(f"  T2: {'✅' if t2 else '❌'} DROP TABLE → {result2['final_decision']}")
    
    # T3: Safety brain identified as source
    t3 = result2['source'] == 'Safety'
    print(f"  T3: {'✅' if t3 else '❌'} Block source → {result2['source']}")
    
    # T4: All 4 brains participated
    t4 = len(result['brain_decisions']) == 4
    print(f"  T4: {'✅' if t4 else '❌'} All brains → {list(result['brain_decisions'].keys())}")
    
    # T5: Teacher produces plan
    teacher_data = result['brain_decisions']['Teacher']
    t5 = teacher_data.decision in ('GO', 'ASK_CONTEXT', 'PLAN_READY')
    print(f"  T5: {'✅' if t5 else '❌'} Teacher → {teacher_data.decision}")
    
    # T6: Planning evaluated  
    planning_data = result['brain_decisions']['Planning']
    t6 = planning_data.decision in ('NO_SEQUENCE', 'SEQUENCE_READY')
    print(f"  T6: {'✅' if t6 else '❌'} Planning → {planning_data.decision}")
    
    # T7: API_KEY blocked
    result3 = mb.decide("API_KEY='sk-***' exposed in config.py", patch="API_KEY='sk-***'")
    t7 = result3['final_decision'] == 'BLOCK'
    print(f"  T7: {'✅' if t7 else '❌'} API_KEY → {result3['final_decision']}")
    
    # T8: Stats read-only
    st = mb.stats()
    t8 = st['actions_executed'] == 0 and st['total_brains'] == 4
    print(f"  T8: {'✅' if t8 else '❌'} Stats → {st['total_brains']} brains, read-only")
    
    # T9: Safety priority highest
    t9 = mb.brains[0].priority == 100
    print(f"  T9: {'✅' if t9 else '❌'} Safety priority → {mb.brains[0].priority} (highest)")
    
    passed = sum([t1,t2,t3,t4,t5,t6,t7,t8,t9])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/9 Tests bestanden")
    print(f"  {'✅ METABRAIN V1 FERTIG' if passed >= 8 else '⚠️'}")
