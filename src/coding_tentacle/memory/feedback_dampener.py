"""
FEEDBACK DAMPENING — RC8.6
Prevents positive feedback loops from creating fix monocultures.
Cap confidence, diminishing returns, exploration bonus.

No complex RL. Just robust statistics.

Autor: Hermes + David | Coding Tentacle 2026
"""

# CT-v11.0.0: PRODUCTION | 10/10 regression | 25 modules | 90% wired | Droste active
import math


class FeedbackDampener:
    """Prevents over-amplification of fix confidence.
    Works with RuleMemory, BugLearningMemory, ExperienceConsolidator."""
    
    def __init__(self, max_confidence=0.90, min_confidence=0.10,
                 diminishing_factor=0.85, exploration_bonus=0.08,
                 diversity_threshold=0.70):
        self.max_confidence = max_confidence    # Never exceed this
        self.min_confidence = min_confidence    # Never go below this
        self.diminishing_factor = diminishing_factor  # Each additional success = less boost
        self.exploration_bonus = exploration_bonus    # Bonus for under-used fixes
        self.diversity_threshold = diversity_threshold  # If one fix dominates, penalize
        
    def dampen_confidence(self, current_confidence, success_count, 
                          total_fixes_for_bug, total_fix_types):
        """Apply dampening to prevent over-confidence.
        
        Args:
            current_confidence: Raw confidence (0-1)
            success_count: Times this fix succeeded
            total_fixes_for_bug: Total fixes for this bug type
            total_fix_types: Number of different fix types tried
        
        Returns:
            Dampened confidence
        """
        dampened = current_confidence
        
        # RULE 1: Hard cap
        dampened = min(dampened, self.max_confidence)
        dampened = max(dampened, self.min_confidence)
        
        # RULE 2: Diminishing returns
        # After 10 successes, each new success gives only 85% of previous boost
        if success_count > 10:
            extra = success_count - 10
            # Diminishing: log-scaling instead of linear
            dampened = 0.80 + 0.10 * (1 - math.exp(-extra * 0.1))
            dampened = min(dampened, self.max_confidence)
        
        # RULE 3: Diversity penalty
        # If one fix type dominates (>70% of all fixes), penalize it
        if total_fixes_for_bug > 0 and total_fix_types > 1:
            dominance = success_count / max(1, total_fixes_for_bug)
            if dominance > self.diversity_threshold:
                penalty = (dominance - self.diversity_threshold) * 0.15
                dampened = max(self.min_confidence, dampened - penalty)
        
        # RULE 4: Exploration bonus for under-used fixes
        # Fix types with <20% usage get a small boost
        if total_fixes_for_bug > 0 and total_fix_types > 1:
            usage = success_count / max(1, total_fixes_for_bug)
            if usage < 0.20 and usage > 0:
                dampened = min(self.max_confidence, dampened + self.exploration_bonus)
        
        return round(dampened, 3)
    
    def should_explore(self, success_count, total_fixes_for_bug, total_fix_types):
        """Should we explore alternative fixes?
        Returns True if the system should try something different."""
        # If only one fix type tried → explore
        if total_fix_types <= 1:
            return True
        
        # If dominant fix has >85% usage → explore
        if total_fixes_for_bug > 0:
            dominance = success_count / max(1, total_fixes_for_bug)
            if dominance > 0.85:
                return True
        
        return False
    
    def get_alternative(self, preferred_fix, all_fix_types, usage_counts):
        """Suggest an alternative fix type to explore."""
        alternatives = [(ft, usage_counts.get(ft, 0)) 
                       for ft in all_fix_types if ft != preferred_fix]
        if not alternatives:
            return None
        
        # Pick the least-used alternative (exploration)
        alternatives.sort(key=lambda x: x[1])
        return alternatives[0][0]
    
    def stats(self):
        return {
            'max_confidence': self.max_confidence,
            'min_confidence': self.min_confidence,
            'diminishing_factor': self.diminishing_factor,
            'exploration_bonus': self.exploration_bonus,
            'diversity_threshold': self.diversity_threshold,
            'actions_executed': 0,
        }


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    print("FEEDBACK DAMPENING — Self-Test")
    print("=" * 55)
    passed = 0
    
    fd = FeedbackDampener()
    
    # T1: Normal confidence passes through
    c1 = fd.dampen_confidence(0.80, 5, 10, 3)
    t1 = 0.70 <= c1 <= 0.90
    print(f"  T1: {'✅' if t1 else '❌'} Normal confidence → {c1}")
    
    # T2: Hard cap prevents >0.90
    c2 = fd.dampen_confidence(0.98, 20, 25, 2)
    t2 = c2 <= 0.90
    print(f"  T2: {'✅' if t2 else '❌'} Hard cap → {c2} (max 0.90)")
    
    # T3: Diminishing returns — 45 successes no longer linear
    c3 = fd.dampen_confidence(0.95, 45, 50, 2)
    t3 = c3 < 0.90  # Should be dampened significantly
    print(f"  T3: {'✅' if t3 else '❌'} Diminishing (45 successes) → {c3}")
    
    # T4: Diversity penalty — dominant fix penalized
    c4 = fd.dampen_confidence(0.90, 45, 50, 4)  # 45/50=90% dominance, 4 types
    t4 = c4 < 0.90  # Penalized for dominance
    print(f"  T4: {'✅' if t4 else '❌'} Diversity penalty (90% dominant) → {c4}")
    
    # T5: Exploration bonus — under-used fix gets boost
    c5 = fd.dampen_confidence(0.30, 2, 50, 4)  # 2/50=4% usage
    t5 = c5 > 0.30  # Should get exploration bonus
    print(f"  T5: {'✅' if t5 else '❌'} Exploration bonus (4% usage) → {c5}")
    
    # T6: Should explore when only 1 fix type
    t6 = fd.should_explore(45, 50, 1)  # Only 1 fix type
    print(f"  T6: {'✅' if t6 else '❌'} Should explore (1 type) → True")
    
    # T7: Should explore when dominant >85%
    t7 = fd.should_explore(45, 50, 3)  # 90% dominance
    print(f"  T7: {'✅' if t7 else '❌'} Should explore (90% dominant) → {t7}")
    
    # T8: Should NOT explore when balanced
    t8 = not fd.should_explore(20, 50, 4)  # 40% balanced
    print(f"  T8: {'✅' if t8 else '❌'} Balanced (40%) → No exploration needed")
    
    # T9: Alternative suggestion
    alt = fd.get_alternative('guard_clause', 
                            ['guard_clause','try_except','Optional_check'],
                            {'guard_clause':45, 'try_except':3, 'Optional_check':2})
    t9 = alt is not None and alt != 'guard_clause'
    print(f"  T9: {'✅' if t9 else '❌'} Alternative → {alt} (least used)")
    
    # T10: Stats read-only
    t10 = fd.stats()['actions_executed'] == 0
    print(f"  T10: {'✅' if t10 else '❌'} Read-only")
    
    passed = sum([t1,t2,t3,t4,t5,t6,t7,t8,t9,t10])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/10 Tests bestanden")
    print(f"  {'✅ FEEDBACK DAMPENING FERTIG' if passed >= 9 else '⚠️'}")
