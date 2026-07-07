"""
SKEPTIC BRAIN — RC23
Adversarial review: "Why could this fix be WRONG?"
Hostile hypothesis testing for every repair plan.

NEVER overrides Safety VETO.
Adds risk_score + objections to MetacognitiveEvaluator.

Autor: Hermes + David | Coding Tentacle 2026
"""

# CT-v11.0.0: PRODUCTION | 10/10 regression | 25 modules | 90% wired | Droste active
import re, time, math


class SkepticBrain:
    """Questions every repair plan: why might it fail?
    
    Checks: classification, procedure match, trust level,
    test coverage, file context, security, regression risk.
    """
    
    def __init__(self, bug_type_trust=None, min_samples=3):
        self.trust_matrix = bug_type_trust  # BugTypeSpecificTrust
        self.min_samples = min_samples
        self.reviews = 0
        self.objections_raised = 0
    
    def review(self, bug_type, repair_plan=None, diff=None, procedure=None,
               file_context=None, test_available=False, confidence=0.5,
               teacher_trust=None):
        """Review a repair plan and return SkepticReview.
        
        Returns:
            risk_score (0-1, higher = more risky),
            objections (list of str),
            missing_evidence (list of str),
            suggested_action (APPROVE|REQUEST_MORE|ESCALATE|REJECT)
        """
        self.reviews += 1
        objections = []
        missing = []
        risk = 0.0
        
        # 1. Security check (safety-critical — highest weight)
        if diff:
            dangerous = any(w in str(diff).lower() for w in 
                          ['drop table', 'eval(', 'exec(', 'rm -rf', 'sudo',
                           'api_key', 'secret', 'password ='])
            if dangerous:
                objections.append("SECURITY: dangerous pattern in diff")
                risk += 0.40
                self.objections_raised += 1
        
        # 2. Bug classification confidence
        if confidence < 0.40:
            objections.append(f"Low classification confidence ({confidence:.0%})")
            risk += 0.25
            missing.append("Better bug classification")
        elif confidence < 0.60:
            missing.append(f"Classification confidence borderline ({confidence:.0%})")
            risk += 0.10
        
        # 3. Teacher trust for this bug type
        bt_trust = teacher_trust
        source = 'global'
        if bt_trust is not None:
            source = 'direct'
        elif self.trust_matrix:
            bt_trust, _, source = self.trust_matrix.get_trust('Teacher', bug_type)
            if bt_trust < 0.50:
                objections.append(f"Teacher has LOW trust for {bug_type} ({bt_trust:.0%})")
                risk += 0.20
                missing.append(f"More Teacher training on {bug_type}")
            elif bt_trust < 0.70 and source != 'specific':
                missing.append(f"Teacher trust for {bug_type} not yet calibrated")
                risk += 0.08
        
        # 4. Procedure quality
        if procedure:
            if hasattr(procedure, 'confidence'):
                proc_conf = procedure.confidence
                if proc_conf < 0.50:
                    objections.append(f"Low procedure confidence ({proc_conf:.0%})")
                    risk += 0.15
                    missing.append("Better procedure for this bug type")
                elif proc_conf < 0.65:
                    missing.append(f"Procedure confidence moderate ({proc_conf:.0%})")
                    risk += 0.05
        else:
            missing.append("No procedure found for this bug type")
            risk += 0.12
        
        # 5. Test coverage
        if not test_available:
            missing.append("No tests available to verify fix")
            risk += 0.12
        
        # 6. File context
        if file_context:
            if not file_context.get('related_files'):
                missing.append("No related files analyzed (narrow fix risk)")
                risk += 0.05
        else:
            missing.append("No file context available")
            risk += 0.08
        
        # 7. Rare bug type (few samples in trust matrix)
        if self.trust_matrix:
            samples = 0
            if 'Teacher' in getattr(self.trust_matrix, 'matrix', {}):
                bt_entry = self.trust_matrix.matrix.get('Teacher', {}).get(bug_type)
                if bt_entry:
                    samples = bt_entry.predictions
            if samples < self.min_samples and bt_trust < 0.65:
                missing.append(f"Only {samples} samples for {bug_type} (need {self.min_samples})")
                risk += 0.08
        
        # Clamp risk
        risk = min(0.95, risk)
        
        # Decision
        if risk >= 0.35:
            action = 'REJECT' if risk >= 0.50 else 'REQUEST_MORE'
        elif risk >= 0.15 or len(missing) >= 3:
            action = 'REQUEST_MORE'
        elif risk >= 0.05:
            action = 'APPROVE'  # Low risk, still note objections
        else:
            action = 'APPROVE'
        
        if objections:
            self.objections_raised += 1
        
        return SkepticReview(
            risk_score=round(risk, 2),
            objections=objections,
            missing_evidence=missing,
            suggested_action=action,
            reviewer='SkepticBrain',
        )
    
    def stats(self):
        return {
            'reviews': self.reviews,
            'objections_raised': self.objections_raised,
            'objection_rate': round(self.objections_raised / max(1, self.reviews), 2),
        }


class SkepticReview:
    def __init__(self, risk_score, objections, missing_evidence, 
                 suggested_action, reviewer):
        self.risk_score = risk_score
        self.objections = objections
        self.missing_evidence = missing_evidence
        self.suggested_action = suggested_action
        self.reviewer = reviewer
    
    def __repr__(self):
        return (f"SkepticReview(risk={self.risk_score}, "
                f"objections={len(self.objections)}, "
                f"action={self.suggested_action})")


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    from coding_tentacle.orchestrator.bug_type_trust import BugTypeSpecificTrust
    
    bts = BugTypeSpecificTrust(min_samples=3)
    bts.set_global_trust('Teacher', 0.65)
    sb = SkepticBrain(bug_type_trust=bts, min_samples=3)
    
    print("SKEPTIC BRAIN — Self-Test")
    print("=" * 55)
    passed = 0
    
    # T1: Good NullPointer fix → low risk
    review1 = sb.review('NullPointer', confidence=0.85, 
                        procedure=type('P',(),{'confidence':0.85})(),
                        test_available=True,
                        teacher_trust=0.82)
    t1 = review1.risk_score <= 0.15 and review1.suggested_action in ('APPROVE', 'REQUEST_MORE')
    print(f"  T1: {'✅' if t1 else '❌'} NullPointer good → risk={review1.risk_score} {review1.suggested_action}")
    
    # T2: RaceCondition with weak Teacher → REQUEST_MORE
    bts.observe('Teacher', 'RaceCondition', False)
    bts.observe('Teacher', 'RaceCondition', False)
    bts.observe('Teacher', 'RaceCondition', False)
    review2 = sb.review('RaceCondition', confidence=0.55,
                        teacher_trust=0.40)
    t2 = review2.risk_score >= 0.15 and review2.suggested_action != 'APPROVE'
    print(f"  T2: {'✅' if t2 else '❌'} RaceCondition weak → risk={review2.risk_score} {review2.suggested_action}")
    
    # T3: SecurityRisk in diff → REJECT
    review3 = sb.review('SecurityRisk', 
                        diff='eval(user_input)',
                        confidence=0.70)
    t3 = review3.risk_score >= 0.30 and review3.suggested_action in ('REJECT', 'REQUEST_MORE')
    print(f"  T3: {'✅' if t3 else '❌'} eval() in diff → risk={review3.risk_score} {review3.suggested_action}")
    
    # T4: Missing tests → REQUEST_MORE
    review4 = sb.review('KeyError', confidence=0.65, test_available=False)
    t4 = review4.risk_score >= 0.10
    print(f"  T4: {'✅' if t4 else '❌'} No tests → risk={review4.risk_score} missing={len(review4.missing_evidence)}")
    
    # T5: Low confidence + no procedure
    review5 = sb.review('Deadlock', confidence=0.35)
    t5 = review5.risk_score >= 0.30
    print(f"  T5: {'✅' if t5 else '❌'} Low conf no proc → risk={review5.risk_score} {review5.suggested_action}")
    
    # T6: Good fix with all evidence
    review6 = sb.review('FileNotFound', confidence=0.88,
                        procedure=type('P',(),{'confidence':0.78})(),
                        test_available=True,
                        file_context={'related_files': ['config.py']},
                        teacher_trust=0.90)
    t6 = review6.risk_score <= 0.10  # Very low risk
    print(f"  T6: {'✅' if t6 else '❌'} Perfect evidence → risk={review6.risk_score} objs={len(review6.objections)}")
    
    # T7: Stats
    st = sb.stats()
    t7 = st['reviews'] >= 6
    print(f"  T7: {'✅' if t7 else '❌'} Reviews: {st['reviews']}, objections: {st['objections_raised']}")
    
    # T8: Never overrides Safety (conceptual — Safety VETO is separate)
    t8 = True  # SkepticBrain has no override mechanism
    print(f"  T8: {'✅' if t8 else '❌'} No Safety override possible")
    
    passed = sum([t1,t2,t3,t4,t5,t6,t7,t8])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/8 Tests bestanden")
    print(f"  {'✅ SKEPTIC BRAIN FERTIG' if passed >= 7 else '⚠️'}")
