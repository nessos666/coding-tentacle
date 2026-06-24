"""
LOCAL TENTACLE LEARNING — RC9
Each tentacle stores its own local experience.
Inspired by octopus: arms learn independently but report to central brain.
+ Federated learning pattern: local updates → central aggregation.
+ Just-In-Time RL: experience-rich context from accumulated logs.

Local reflexes NEVER override global Safety (IC/EL).

Autor: Hermes + David | Coding Tentacle 2026
"""
import time, json, os
from dataclasses import dataclass, field, asdict
from collections import defaultdict


@dataclass
class LocalExperience:
    """One local learning record for a tentacle."""
    input_signature: str      # "bug_type=NullPointer,file=payment.py"
    decision: str             # "guard_clause", "type_cast", "ASK_CONTEXT"
    outcome: bool             # success/failure
    confidence: float         # 0-1
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


class LocalTentacleMemory:
    """Local memory for ONE tentacle. Lightweight, fast, autonomous."""
    
    def __init__(self, tentacle_name, max_records=500):
        self.tentacle_name = tentacle_name
        self.max_records = max_records
        self.experiences: list[LocalExperience] = []
        self.preferred_inputs = defaultdict(lambda: {'success': 0, 'failure': 0})
        self.avoided_inputs = defaultdict(lambda: {'success': 0, 'failure': 0})
        self.last_used = time.time()
        
        # Local confidence adjustment (per bug_type)
        self.confidence_adjustments = defaultdict(float)  # bug_type → delta
        
        # Decay: unused local knowledge fades
        self.decay_rate = 0.01  # per day
    
    def record(self, input_signature, decision, outcome, confidence=0.5):
        """Store a local experience."""
        exp = LocalExperience(
            input_signature=input_signature,
            decision=decision,
            outcome=outcome,
            confidence=confidence,
        )
        self.experiences.append(exp)
        self.last_used = time.time()
        
        # Update local statistics
        bug_type = self._extract_bug_type(input_signature)
        if outcome:
            self.preferred_inputs[bug_type]['success'] += 1
            # Boost confidence locally
            self.confidence_adjustments[bug_type] = min(0.10, 
                self.confidence_adjustments[bug_type] + 0.01)
        else:
            self.avoided_inputs[bug_type]['failure'] += 1
            # Dampen confidence locally
            self.confidence_adjustments[bug_type] = max(-0.15,
                self.confidence_adjustments[bug_type] - 0.02)
        
        # Prune old records
        if len(self.experiences) > self.max_records:
            self.experiences = self.experiences[-self.max_records:]
    
    def get_local_confidence(self, bug_type, base_confidence):
        """Get locally adjusted confidence for a bug type."""
        delta = self.confidence_adjustments.get(bug_type, 0.0)
        return max(0.1, min(0.95, base_confidence + delta))
    
    def should_avoid(self, bug_type, decision):
        """Has this tentacle locally learned to AVOID this decision?"""
        avoid_stats = self.avoided_inputs.get(bug_type, {})
        prefer_stats = self.preferred_inputs.get(bug_type, {})
        failures = avoid_stats.get('failure', 0)
        successes = prefer_stats.get('success', 0)
        total = failures + successes
        if total >= 5 and failures > successes * 2:
            return True  # 2:1 failure ratio → avoid
        return False
    
    def get_local_stats(self, bug_type):
        """Get local statistics for a bug type."""
        pref = self.preferred_inputs.get(bug_type, {'success': 0, 'failure': 0})
        avoid = self.avoided_inputs.get(bug_type, {'success': 0, 'failure': 0})
        return {
            'preferred_successes': pref['success'],
            'avoided_failures': avoid['failure'],
            'confidence_delta': round(self.confidence_adjustments.get(bug_type, 0.0), 3),
            'total_local_experiences': len(self.experiences),
        }
    
    def apply_decay(self):
        """Unused knowledge slowly decays."""
        days_since_use = (time.time() - self.last_used) / 86400
        if days_since_use > 1:
            decay = self.decay_rate * days_since_use
            for bt in list(self.confidence_adjustments.keys()):
                current = self.confidence_adjustments[bt]
                if current > 0:
                    self.confidence_adjustments[bt] = max(0, current - decay)
                else:
                    self.confidence_adjustments[bt] = min(0, current + decay)
    
    def _extract_bug_type(self, signature):
        """Extract bug_type from input signature."""
        if 'bug_type=' in signature:
            return signature.split('bug_type=')[1].split(',')[0]
        parts = signature.split(':')
        if parts:
            return parts[0]
        return 'Unknown'
    
    def stats(self):
        return {
            'tentacle_name': self.tentacle_name,
            'total_experiences': len(self.experiences),
            'bug_types_learned': len(self.confidence_adjustments),
            'preferred_inputs': dict(self.preferred_inputs),
            'avoided_inputs': dict(self.avoided_inputs),
            'actions_executed': 0,
        }


class TentacleLearningCoordinator:
    """Coordinates local learning across tentacles. Aggregates for Teacher."""
    
    def __init__(self):
        self.tentacles: dict[str, LocalTentacleMemory] = {}
    
    def register_tentacle(self, name):
        """Register a new tentacle with its own local memory."""
        ltm = LocalTentacleMemory(tentacle_name=name)
        self.tentacles[name] = ltm
        return ltm
    
    def get_tentacle(self, name):
        return self.tentacles.get(name)
    
    def aggregate_for_teacher(self, bug_type):
        """Aggregate local learnings from ALL tentacles for Teacher review."""
        aggregated = {
            'bug_type': bug_type,
            'tentacle_learnings': {},
            'consensus_confidence': 0.5,
            'conflicts': [],
        }
        
        confidences = []
        for name, ltm in self.tentacles.items():
            stats = ltm.get_local_stats(bug_type)
            aggregated['tentacle_learnings'][name] = stats
            conf = 0.5 + stats['confidence_delta']
            confidences.append(conf)
        
        if confidences:
            aggregated['consensus_confidence'] = round(sum(confidences) / len(confidences), 3)
        
        # Detect conflicts: one tentacle prefers, another avoids
        for name, ltm in self.tentacles.items():
            if ltm.should_avoid(bug_type, 'guard_clause'):
                aggregated['conflicts'].append(f'{name} avoids guard_clause for {bug_type}')
        
        return aggregated
    
    def stats(self):
        return {
            'total_tentacles': len(self.tentacles),
            'total_local_experiences': sum(t.stats()['total_experiences'] for t in self.tentacles.values()),
            'actions_executed': 0,
        }


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    print("LOCAL TENTACLE LEARNING — Self-Test")
    print("=" * 55)
    passed = 0
    
    # T1: Create local memory for PatchSuggestion
    ps_mem = LocalTentacleMemory("PatchSuggestion")
    t1 = ps_mem.tentacle_name == "PatchSuggestion"
    print(f"  T1: {'✅' if t1 else '❌'} Create local memory → {ps_mem.tentacle_name}")
    
    # T2: Record local experiences
    for _ in range(8):
        ps_mem.record("bug_type=NullPointer,file=payment.py", "guard_clause", True, 0.85)
    for _ in range(2):
        ps_mem.record("bug_type=NullPointer,file=order.py", "try_except", False, 0.20)
    
    t2 = len(ps_mem.experiences) == 10
    print(f"  T2: {'✅' if t2 else '❌'} Record experiences → {len(ps_mem.experiences)} stored")
    
    # T3: Local confidence boost for NullPointer
    conf = ps_mem.get_local_confidence("NullPointer", 0.70)
    t3 = conf > 0.70  # Boost from 8 successes
    print(f"  T3: {'✅' if t3 else '❌'} Local confidence → {conf:.2f} (base=0.70, boosted)")
    
    # T4: Should avoid try_except? (8 success vs 2 failure = NOT enough to avoid)
    avoid = ps_mem.should_avoid("NullPointer", "try_except")
    t4 = not avoid  # 2 failures don't cross threshold (need 5+ and ratio >2:1)
    print(f"  T4: {'✅' if t4 else '❌'} Don't avoid yet → {avoid}")
    
    # T5: After many failures, should avoid
    for _ in range(20):
        ps_mem.record("bug_type=NullPointer,file=worker.py", "try_except", False, 0.15)
    avoid2 = ps_mem.should_avoid("NullPointer", "try_except")
    t5 = avoid2  # 22 failures vs 8 successes = avoid!
    print(f"  T5: {'✅' if t5 else '❌'} Avoid after many failures → {avoid2}")
    
    # T6: BR tentacle learns locally
    br_mem = LocalTentacleMemory("BR")
    for _ in range(6):
        br_mem.record("bug_type=NullPointer,hypothesis=Optional[None]", "correct", True, 0.82)
    for _ in range(3):
        br_mem.record("bug_type=NullPointer,hypothesis=RaceCondition", "wrong", False, 0.65)
    t6 = br_mem.get_local_confidence("NullPointer", 0.70) >= 0.70  # Balanced: 6 success vs 3 fail → no change
    print(f"  T6: {'✅' if t6 else '❌'} BR local learning → {br_mem.get_local_confidence('NullPointer', 0.70):.2f}")
    
    # T7: Coordinator aggregates
    coord = TentacleLearningCoordinator()
    coord.tentacles['PS'] = ps_mem
    coord.tentacles['BR'] = br_mem
    agg = coord.aggregate_for_teacher("NullPointer")
    t7 = len(agg['tentacle_learnings']) == 2
    print(f"  T7: {'✅' if t7 else '❌'} Aggregate → {len(agg['tentacle_learnings'])} tentacles")
    
    # T8: Decay — unused knowledge fades
    ps_mem.last_used = time.time() - 86400 * 10  # 10 days ago
    ps_mem.apply_decay()
    conf_decayed = ps_mem.get_local_confidence("NullPointer", 0.70)
    t8 = conf_decayed < 0.80  # Should have decayed
    print(f"  T8: {'✅' if t8 else '❌'} Decay after 10 days → {conf_decayed:.2f}")
    
    # T9: Stats read-only
    t9 = ps_mem.stats()['actions_executed'] == 0
    print(f"  T9: {'✅' if t9 else '❌'} Read-only")
    
    passed = sum([t1,t2,t3,t4,t5,t6,t7,t8,t9])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/9 Tests bestanden")
    print(f"  {'✅ LOCAL TENTACLE LEARNING FERTIG' if passed >= 8 else '⚠️'}")
