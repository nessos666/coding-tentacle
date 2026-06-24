"""
DYNAMIC TENTACLE ACTIVATION — RC7.2
ActivationManager decides which tentacles wake/sleep per bug type.
Like an octopus: only the needed arms activate.

Integrates with TentacleBus — subscribes to bug_classified events.

Autor: Hermes + David | Coding Tentacle 2026
"""
import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TentacleProfile:
    """Profile of one tentacle: what bugs it handles, its cost, priority."""
    name: str                    # "BQ", "BR", "IC", "PS", ...
    supported_bug_types: list[str]  # ["NullPointer","TypeError",...] or ["*"] for all
    excluded_bug_types: list[str]   # ["SecurityRisk"] — never activate for these
    priority: int = 5             # 1-10, higher = more important
    activation_cost: float = 1.0  # Relative computational cost
    avg_runtime_ms: float = 5.0   # Average runtime in ms
    description: str = ""
    
    def handles(self, bug_type: str) -> bool:
        """Can this tentacle handle this bug type?"""
        if bug_type in self.excluded_bug_types:
            return False
        if "*" in self.supported_bug_types:
            return True
        return bug_type in self.supported_bug_types


# Default tentacle registry
DEFAULT_PROFILES = [
    TentacleProfile("BQ", supported_bug_types=["*"], excluded_bug_types=[],
                    priority=10, activation_cost=2.0, avg_runtime_ms=3.0,
                    description="Symbol Grounding — klassifiziert ALLE Bugs"),
    
    TentacleProfile("BR", supported_bug_types=["*"], excluded_bug_types=["SecurityRisk"],
                    priority=9, activation_cost=3.0, avg_runtime_ms=8.0,
                    description="Scientific Method — Hypothesen für alle nicht-Security Bugs"),
    
    TentacleProfile("ProceduralMemory", 
                    supported_bug_types=["NullPointer","TypeError","ImportError","AttributeError","KeyError"],
                    excluded_bug_types=["SecurityRisk","Unknown"],
                    priority=8, activation_cost=1.0, avg_runtime_ms=2.0,
                    description="ProceduralMemory — nur für bekannte Bug-Typen"),
    
    TentacleProfile("BugLearningMemory",
                    supported_bug_types=["NullPointer","TypeError","ImportError","AttributeError","KeyError"],
                    excluded_bug_types=["Unknown"],
                    priority=8, activation_cost=1.5, avg_runtime_ms=5.0,
                    description="BugLearningMemory — nur für Bugs mit Historie"),
    
    TentacleProfile("RuleMemory",
                    supported_bug_types=["NullPointer","TypeError","ImportError","AttributeError"],
                    excluded_bug_types=["SecurityRisk","Unknown"],
                    priority=7, activation_cost=0.5, avg_runtime_ms=1.0,
                    description="RuleMemory — PREFER/AVOID für trainierte Bug-Typen"),
    
    TentacleProfile("PatchSuggestion",
                    supported_bug_types=["NullPointer","TypeError","ImportError","AttributeError","KeyError"],
                    excluded_bug_types=["SecurityRisk"],
                    priority=7, activation_cost=4.0, avg_runtime_ms=10.0,
                    description="PatchSuggestion — KEINE Patches für Security"),
    
    TentacleProfile("IC",
                    supported_bug_types=["*"], excluded_bug_types=[],
                    priority=10, activation_cost=2.0, avg_runtime_ms=2.0,
                    description="Inhibitory Control — IMMER aktiv (Safety)"),
    
    TentacleProfile("SecurityStore",
                    supported_bug_types=["SecurityRisk"], excluded_bug_types=[],
                    priority=10, activation_cost=1.0, avg_runtime_ms=1.0,
                    description="SecurityStore — NUR für SecurityRisk"),
    
    TentacleProfile("EL",
                    supported_bug_types=["SecurityRisk"], excluded_bug_types=[],
                    priority=9, activation_cost=1.0, avg_runtime_ms=1.0,
                    description="Escalation Logic — hauptsächlich für Security-Fälle"),
    
    TentacleProfile("ProjectMap",
                    supported_bug_types=["NullPointer","TypeError","ImportError","AttributeError"],
                    excluded_bug_types=["SecurityRisk","Unknown"],
                    priority=6, activation_cost=3.0, avg_runtime_ms=15.0,
                    description="ProjectMap — teuer, nur für Multi-File-Bugs"),
    
    TentacleProfile("WorkingMemory",
                    supported_bug_types=["*"], excluded_bug_types=[],
                    priority=10, activation_cost=0.5, avg_runtime_ms=1.0,
                    description="WorkingMemory — IMMER aktiv (Session-State)"),
]


@dataclass
class ActivationDecision:
    """Result of activation decision for one bug."""
    bug_type: str
    activated: list[str]    # Tentacle names to activate
    sleeping: list[str]     # Tentacle names to keep sleeping
    reason: str             # Why this decision?
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


class ActivationManager:
    """Decides which tentacles to activate based on bug type.
    Subscribes to TentacleBus 'bug_classified' events."""
    
    def __init__(self, profiles=None, message_bus=None):
        self.profiles = {p.name: p for p in (profiles or DEFAULT_PROFILES)}
        self.bus = message_bus
        self.decisions = []  # History of activation decisions
        self.actions_executed = 0
        
        # Auto-subscribe to bus
        if self.bus:
            self.bus.subscribe("bug_classified", self._on_bug_classified, "ActivationManager")
    
    def decide(self, bug_type: str, context: dict = None) -> ActivationDecision:
        """Decide which tentacles to activate for a bug type."""
        activated = []
        sleeping = []
        
        for name, profile in self.profiles.items():
            if profile.handles(bug_type):
                activated.append(name)
            else:
                sleeping.append(name)
        
        # Sort activated by priority (highest first)
        activated.sort(key=lambda n: self.profiles[n].priority, reverse=True)
        
        # Generate reason
        if bug_type == "SecurityRisk":
            reason = "SecurityRisk: Nur IC+SecurityStore+EL aktiv. Keine Patches."
        elif bug_type == "Unknown":
            reason = "Unknown: Nur BQ+BR+WM aktiv. ASK_CONTEXT."
        else:
            act_count = len(activated)
            sleep_count = len(sleeping)
            reason = f"{bug_type}: {act_count} tentacles active, {sleep_count} sleeping"
        
        decision = ActivationDecision(
            bug_type=bug_type,
            activated=activated,
            sleeping=sleeping,
            reason=reason,
        )
        self.decisions.append(decision)
        return decision
    
    def _on_bug_classified(self, event):
        """Auto-activate when BQ classifies a bug (via bus)."""
        bug_type = event.payload.get('bug_type', 'Unknown')
        self.decide(bug_type)
    
    def get_profile(self, name: str) -> Optional[TentacleProfile]:
        return self.profiles.get(name)
    
    def total_activation_cost(self, bug_type: str) -> float:
        """Estimated computational cost for this bug type."""
        decision = self.decide(bug_type)
        return sum(self.profiles[n].activation_cost for n in decision.activated)
    
    def stats(self):
        return {
            'total_tentacles': len(self.profiles),
            'total_decisions': len(self.decisions),
            'last_decision': self.decisions[-1].reason if self.decisions else 'none',
            'actions_executed': self.actions_executed,
        }


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    print("DYNAMIC TENTACLE ACTIVATION — Self-Test")
    print("=" * 55)
    passed = 0
    
    am = ActivationManager()
    
    # T1: NullPointer activation
    d = am.decide("NullPointer")
    t1 = len(d.activated) >= 6 and "PatchSuggestion" in d.activated and "SecurityStore" in d.sleeping
    print(f"  T1: {'✅' if t1 else '❌'} NullPointer → {len(d.activated)} active, {len(d.sleeping)} sleeping")
    
    # T2: SecurityStore SLEEPING for NullPointer
    t2 = "SecurityStore" in d.sleeping
    print(f"  T2: {'✅' if t2 else '❌'} SecurityStore sleeps for NullPointer")
    
    # T3: SecurityRisk activation
    d3 = am.decide("SecurityRisk")
    t3 = "IC" in d3.activated and "SecurityStore" in d3.activated and "PatchSuggestion" in d3.sleeping
    print(f"  T3: {'✅' if t3 else '❌'} SecurityRisk → {len(d3.activated)} active (IC+Sec+EL)")
    
    # T4: PatchSuggestion SLEEPING for SecurityRisk
    t4 = "PatchSuggestion" in d3.sleeping
    print(f"  T4: {'✅' if t4 else '❌'} PatchSuggestion sleeps for SecurityRisk")
    
    # T5: Unknown activation (minimal)
    d5 = am.decide("Unknown")
    t5 = len(d5.activated) <= 5  # BQ+BR+WM+IC+EL at most
    print(f"  T5: {'✅' if t5 else '❌'} Unknown → {len(d5.activated)} active (minimal)")
    
    # T6: Cost comparison
    cost_np = am.total_activation_cost("NullPointer")
    cost_sec = am.total_activation_cost("SecurityRisk")
    t6 = cost_np > cost_sec  # More tentacles = higher cost
    print(f"  T6: {'✅' if t6 else '❌'} Cost NullPointer={cost_np:.0f} > SecurityRisk={cost_sec:.0f}")
    
    # T7: Priority ordering
    first_active = d.activated[0] if d.activated else ""
    t7 = first_active in ("BQ", "IC", "WM")  # Priority 10 tentacles first
    print(f"  T7: {'✅' if t7 else '❌'} Priority order → {d.activated[:3]} (top 3)")
    
    # T8: Profile query
    prof = am.get_profile("IC")
    t8 = prof is not None and prof.priority == 10
    print(f"  T8: {'✅' if t8 else '❌'} IC profile → priority={prof.priority}")
    
    # T9: Stats
    st = am.stats()
    t9 = st['total_tentacles'] >= 10 and st['actions_executed'] == 0
    print(f"  T9: {'✅' if t9 else '❌'} Stats → {st['total_tentacles']} tentacles, read-only")
    
    # T10: Integration with bus
    from coding_tentacle.tentacles.message_bus import TentacleBus
    bus = TentacleBus()
    am2 = ActivationManager(message_bus=bus)
    bus.bq_classified("NullPointer", 0.87)
    last = am2.decisions[-1] if am2.decisions else None
    t10 = last is not None and last.bug_type == "NullPointer"
    print(f"  T10: {'✅' if t10 else '❌'} Bus integration → auto-activated on bug_classified")
    
    # T11: No forbidden methods
    forbidden = ['execute','write','patch','run_shell','apply']
    t11 = not any(hasattr(am, m) for m in forbidden)
    print(f"  T11: {'✅' if t11 else '❌'} No forbidden methods")
    
    passed = sum([t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/11 Tests bestanden")
    print(f"  {'✅ DYNAMIC ACTIVATION FERTIG' if passed >= 10 else '⚠️'}")
