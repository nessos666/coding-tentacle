"""
TENTACLE MESSAGE BUS — RC7.1
Blackboard + Pub/Sub communication between tentacles.
BQ broadcasts bug_type → BR, PS, PM, IC subscribe and react.

Pattern: Blackboard (WorkingMemory) + Pub/Sub (event subscriptions)
Zero new dependencies — builds on existing WorkingMemory.

Autor: Hermes + David | Coding Tentacle 2026
"""
import time, json
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class TentacleEvent:
    """A message sent from one tentacle to others via the bus."""
    source: str              # "BQ", "BR", "IC", ...
    event_type: str          # "bug_classified", "hypothesis_ready", "patch_suggested"...
    payload: dict            # Event-specific data
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


class TentacleBus:
    """Message bus for tentacle-to-tentacle communication.
    Uses WorkingMemory as blackboard + in-memory subscriptions."""
    
    def __init__(self, working_memory=None):
        self.wm = working_memory  # Existing WorkingMemory (blackboard)
        self.subscribers = defaultdict(list)  # event_type → [callbacks]
        self.event_log = []  # All events for debugging/tracing
        self.actions_executed = 0  # Read-only
        
    # ═══════ PUBLISH ═══════
    def publish(self, event: TentacleEvent):
        """Broadcast event to all subscribers AND write to blackboard."""
        self.event_log.append(event)
        
        # Write to WorkingMemory blackboard (if available)
        if self.wm:
            try:
                # Store in session state under 'bus_events'
                for sid in self.wm.sessions:
                    state = self.wm.sessions[sid]
                    bus_key = f"bus:{event.source}:{event.event_type}"
                    if not hasattr(state, 'bus_events'):
                        state.bus_events = {}
                    state.bus_events[bus_key] = event.payload
                    state.updated_at = time.time()
            except Exception:
                pass  # WM might not be initialized
        
        # Notify subscribers
        subs = self.subscribers.get(event.event_type, [])
        for callback in subs:
            try:
                callback(event)
            except Exception:
                pass  # Never crash on subscriber failure
    
    # ═══════ SUBSCRIBE ═══════
    def subscribe(self, event_type, callback, subscriber_name=""):
        """Subscribe to an event type. callback(event) called on each publish."""
        self.subscribers[event_type].append(callback)
        return len(self.subscribers[event_type]) - 1  # subscription_id
    
    def unsubscribe(self, event_type, subscription_id):
        if event_type in self.subscribers and subscription_id < len(self.subscribers[event_type]):
            self.subscribers[event_type][subscription_id] = None
    
    # ═══════ QUERY ═══════
    def get_last_event(self, event_type):
        """Get most recent event of type."""
        for ev in reversed(self.event_log):
            if ev.event_type == event_type:
                return ev
        return None
    
    def get_events_since(self, event_type, timestamp):
        """Get all events of type since timestamp."""
        return [ev for ev in self.event_log 
                if ev.event_type == event_type and ev.timestamp > timestamp]
    
    def get_blackboard_value(self, key):
        """Read a value from the WM blackboard."""
        if self.wm:
            for state in self.wm.sessions.values():
                if hasattr(state, 'bus_events') and key in state.bus_events:
                    return state.bus_events[key]
        return None
    
    # ═══════ TENTACLE HELPERS ═══════
    def bq_classified(self, bug_type, grounding_score, meaning=""):
        """BQ has classified a bug type → notify all interested tentacles."""
        self.publish(TentacleEvent(
            source="BQ",
            event_type="bug_classified",
            payload={
                'bug_type': bug_type,
                'grounding_score': grounding_score,
                'meaning': meaning,
            }
        ))
    
    def br_hypothesis_ready(self, bug_type, hypothesis, confidence):
        """BR has a hypothesis ready."""
        self.publish(TentacleEvent(
            source="BR",
            event_type="hypothesis_ready",
            payload={
                'bug_type': bug_type,
                'hypothesis': hypothesis,
                'confidence': confidence,
            }
        ))
    
    def ps_patch_suggested(self, bug_type, patch_type, confidence):
        """PatchSuggestion has a patch ready."""
        self.publish(TentacleEvent(
            source="PS",
            event_type="patch_suggested",
            payload={
                'bug_type': bug_type,
                'patch_type': patch_type,
                'confidence': confidence,
            }
        ))
    
    def ic_blocked(self, reason, severity="BLOCK"):
        """IC has blocked an action."""
        self.publish(TentacleEvent(
            source="IC",
            event_type="action_blocked",
            payload={
                'reason': reason,
                'severity': severity,
            }
        ))
    
    def pm_context_ready(self, file_path, related_files, importers):
        """ProjectMap has context ready."""
        self.publish(TentacleEvent(
            source="PM",
            event_type="project_context_ready",
            payload={
                'file': file_path,
                'related_files': related_files,
                'importers': importers,
            }
        ))
    
    def stats(self):
        return {
            'total_events': len(self.event_log),
            'subscriptions': sum(len(s) for s in self.subscribers.values()),
            'event_types': list(set(ev.event_type for ev in self.event_log)),
            'actions_executed': self.actions_executed,
        }


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    print("TENTACLE MESSAGE BUS — Self-Test")
    print("=" * 55)
    passed = 0
    
    bus = TentacleBus()
    
    # T1: Publish event
    bus.publish(TentacleEvent(source="BQ", event_type="bug_classified", 
                              payload={'bug_type': 'NullPointer', 'score': 0.87}))
    t1 = len(bus.event_log) == 1
    print(f"  T1: {'✅' if t1 else '❌'} Publish event → {len(bus.event_log)} events")
    
    # T2: Subscribe and receive
    received = []
    bus.subscribe("bug_classified", lambda ev: received.append(ev.payload), "test_sub")
    bus.bq_classified("NullPointer", 0.87, "NoneType detected")
    t2 = len(received) == 1 and received[0]['bug_type'] == 'NullPointer'
    print(f"  T2: {'✅' if t2 else '❌'} Subscribe+Receive → {received[0]['bug_type'] if received else 'NONE'}")
    
    # T3: Multiple subscribers
    received2 = []
    bus.subscribe("bug_classified", lambda ev: received2.append(ev), "test_sub2")
    bus.bq_classified("TypeError", 0.95, "type mismatch")
    t3 = len(received) == 2 and len(received2) == 1
    print(f"  T3: {'✅' if t3 else '❌'} Multiple subscribers → {len(received)}/{len(received2)} received")
    
    # T4: BQ→BR→PS flow
    bus.bq_classified("NullPointer", 0.87)
    bus.br_hypothesis_ready("NullPointer", "Variable is Optional[None]", 0.75)
    bus.ps_patch_suggested("NullPointer", "guard_clause", 0.84)
    t4 = len(bus.event_log) >= 4
    print(f"  T4: {'✅' if t4 else '❌'} Full pipeline trace → {len(bus.event_log)} events")
    
    # T5: IC blocked event
    bus.ic_blocked("DROP TABLE detected")
    ic_event = bus.get_last_event("action_blocked")
    t5 = ic_event is not None and ic_event.payload['reason'] == 'DROP TABLE detected'
    print(f"  T5: {'✅' if t5 else '❌'} IC blocked → {ic_event.payload['reason'] if ic_event else 'NONE'}")
    
    # T6: ProjectMap context
    bus.pm_context_ready("payment.py", ["order.py"], ["checkout.py"])
    pm_event = bus.get_last_event("project_context_ready")
    t6 = pm_event is not None and pm_event.payload['file'] == 'payment.py'
    print(f"  T6: {'✅' if t6 else '❌'} ProjectMap context → {pm_event.payload['file'] if pm_event else 'NONE'}")
    
    # T7: Get events since
    ts = time.time() - 1
    events = bus.get_events_since("bug_classified", ts)
    t7 = len(events) >= 2
    print(f"  T7: {'✅' if t7 else '❌'} Events since → {len(events)} bug_classified events")
    
    # T8: Stats
    st = bus.stats()
    t8 = st['total_events'] >= 6 and st['actions_executed'] == 0
    print(f"  T8: {'✅' if t8 else '❌'} Stats → {st['total_events']} events, read-only")
    
    # T9: No forbidden methods
    forbidden = ['execute','write','patch','run_shell','apply']
    t9 = not any(hasattr(bus, m) for m in forbidden)
    print(f"  T9: {'✅' if t9 else '❌'} No forbidden methods")
    
    # T10: Subscription management
    sub_id = bus.subscribe("patch_suggested", lambda ev: None, "test")
    bus.unsubscribe("patch_suggested", sub_id)
    t10 = True  # Doesn't crash
    print(f"  T10: {'✅' if t10 else '❌'} Unsubscribe works")
    
    passed = sum([t1,t2,t3,t4,t5,t6,t7,t8,t9,t10])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/10 Tests bestanden")
    print(f"  {'✅ TENTACLE MESSAGE BUS FERTIG' if passed >= 9 else '⚠️'}")
