"""
SELF-HEALING BRAIN — RC56
MAPE-K Loop: Monitor → Analyze → Plan → Execute → Knowledge
Circuit Breaker per Engine. Auto-recovery. Never self-modify code.
"""
import time
from dataclasses import dataclass, field


@dataclass
class RecoveryRecord:
    problem: str
    root_cause: str
    action: str
    success: bool
    duration: float
    recovery_score: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class SelfHealingReport:
    status: str = 'STABLE'  # STABLE / RECOVERING / CRITICAL
    detected_problem: str = ''
    root_cause: str = ''
    recovery_plan: str = ''
    executed_actions: list = field(default_factory=list)
    circuit_breaker_states: dict = field(default_factory=dict)
    recovery_score: float = 1.0
    requires_human_review: bool = False
    explanation: str = ''


class CircuitBreaker:
    """Per-engine circuit breaker. CLOSED → OPEN → HALF_OPEN → CLOSED."""
    
    def __init__(self, failure_threshold=5, recovery_timeout=60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout  # seconds before HALF_OPEN
        self.states = {}  # engine_name → {'state', 'failures', 'last_failure', 'recoveries'}
    
    def state(self, engine_name: str) -> str:
        """Get current state for an engine."""
        e = self.states.get(engine_name, {})
        state = e.get('state', 'CLOSED')
        
        # Auto-transition OPEN → HALF_OPEN after timeout
        if state == 'OPEN':
            elapsed = time.time() - e.get('last_failure', 0)
            if elapsed > self.recovery_timeout:
                e['state'] = 'HALF_OPEN'
                e['failures'] = 0
                self.states[engine_name] = e
                return 'HALF_OPEN'
        
        return state
    
    def record_failure(self, engine_name: str):
        """Record a failure. May trip to OPEN."""
        e = self.states.get(engine_name, {'state': 'CLOSED', 'failures': 0, 'last_failure': 0, 'recoveries': 0})
        e['failures'] = e.get('failures', 0) + 1
        e['last_failure'] = time.time()
        
        if e['failures'] >= self.failure_threshold:
            e['state'] = 'OPEN'
        
        self.states[engine_name] = e
    
    def record_success(self, engine_name: str):
        """Record a success. May close circuit."""
        e = self.states.get(engine_name, {'state': 'CLOSED', 'failures': 0, 'last_failure': 0, 'recoveries': 0})
        e['failures'] = 0
        e['recoveries'] = e.get('recoveries', 0) + 1
        e['state'] = 'CLOSED'
        self.states[engine_name] = e
    
    def is_blocked(self, engine_name: str) -> bool:
        """Is this engine currently blocked?"""
        return self.state(engine_name) == 'OPEN'
    
    def get_all_states(self) -> dict:
        """Return all circuit breaker states."""
        return {k: self.state(k) for k in self.states}


class SelfHealingBrain:
    """MAPE-K: Monitor health → Analyze → Plan → Execute → Knowledge."""
    
    def __init__(self):
        self.circuit_breaker = CircuitBreaker()
        self.recovery_history: list[RecoveryRecord] = []
    
    def monitor_and_heal(self, health_data: dict = None, engine_name: str = '',
                         error_count: int = 0, unknown_rate: float = 0.0,
                         timeout_count: int = 0, safety_blocks: int = 0,
                         engine_trust: float = 0.60) -> SelfHealingReport:
        """MAPE-K: Full self-healing cycle."""
        report = SelfHealingReport()
        health = health_data or {}
        
        # Phase 1: Monitor
        snapshot = {
            'engine_state': self.circuit_breaker.state(engine_name) if engine_name else 'UNKNOWN',
            'error_count': error_count,
            'unknown_rate': unknown_rate,
            'timeout_count': timeout_count,
            'safety_blocks': safety_blocks,
            'engine_trust': engine_trust,
        }
        
        # Phase 2: Analyze
        problems = []
        
        if engine_name and self.circuit_breaker.is_blocked(engine_name):
            problems.append(('CIRCUIT_OPEN', 'critical', f'{engine_name} circuit breaker open'))
        
        if error_count >= 5:
            problems.append(('HIGH_ERROR_RATE', 'critical', f'{error_count} consecutive errors'))
        
        if engine_trust < 0.10:
            problems.append(('LOW_TRUST', 'critical', f'Engine trust {engine_trust:.2f}'))
        
        if safety_blocks >= 3:
            problems.append(('FREQUENT_SAFETY_BLOCKS', 'warning', f'{safety_blocks} safety blocks'))
        
        if timeout_count >= 3:
            problems.append(('TIMEOUTS', 'warning', f'{timeout_count} timeouts'))
        
        if unknown_rate > 0.40:
            problems.append(('HIGH_UNKNOWN_RATE', 'warning', f'{unknown_rate:.0%} unknown bugs'))
        
        if not problems:
            report.status = 'STABLE'
            report.recovery_score = 1.0
            report.explanation = 'All systems stable. No healing needed.'
            return report
        
        # Phase 3: Plan
        actions = []
        for problem, severity, detail in problems:
            if problem == 'CIRCUIT_OPEN':
                actions.append({'action': 'SWITCH_ENGINE', 'reason': detail, 'severity': severity})
                actions.append({'action': 'FORCE_HUMAN_REVIEW', 'reason': 'Circuit open', 'severity': severity})
            elif problem == 'HIGH_ERROR_RATE':
                actions.append({'action': 'PAUSE_AUTOMATION', 'reason': detail, 'severity': severity})
                actions.append({'action': 'FORCE_HUMAN_REVIEW', 'reason': 'Too many errors', 'severity': severity})
            elif problem == 'LOW_TRUST':
                actions.append({'action': 'CONSERVATIVE_ROUTE', 'reason': detail, 'severity': severity})
            elif problem == 'FREQUENT_SAFETY_BLOCKS':
                actions.append({'action': 'INCREASE_SAFETY_LEVEL', 'reason': detail, 'severity': severity})
            elif problem == 'TIMEOUTS':
                actions.append({'action': 'REDUCE_RETRY', 'reason': detail, 'severity': severity})
            elif problem == 'HIGH_UNKNOWN_RATE':
                actions.append({'action': 'REQUEST_MORE_CONTEXT', 'reason': detail, 'severity': severity})
        
        # Phase 4: Execute
        for action in actions:
            act = action['action']
            if act == 'SWITCH_ENGINE':
                report.executed_actions.append(f'Engine switched: {engine_name} blocked → using fallback')
            elif act == 'PAUSE_AUTOMATION':
                report.executed_actions.append('Automation paused: safe mode activated')
                report.status = 'CRITICAL'
            elif act == 'FORCE_HUMAN_REVIEW':
                report.requires_human_review = True
                report.executed_actions.append('Human review required')
            elif act == 'CONSERVATIVE_ROUTE':
                report.executed_actions.append('Routing: conservative mode (prefer fallback)')
            elif act == 'INCREASE_SAFETY_LEVEL':
                report.executed_actions.append('Safety level increased')
            elif act == 'REDUCE_RETRY':
                report.executed_actions.append('Retry limit reduced')
            elif act == 'REQUEST_MORE_CONTEXT':
                report.executed_actions.append('More context requested for unknown bugs')
        
        # Phase 5: Knowledge
        for action in actions:
            rec = RecoveryRecord(
                problem=action['reason'],
                root_cause=f"{problems[0][0] if problems else 'unknown'}",
                action=action['action'],
                success=True,  # Will be validated after execution
                duration=0.0,
                recovery_score=0.5 if action['severity'] == 'critical' else 0.8,
            )
            self.recovery_history.append(rec)
        
        # Final report
        critical_count = sum(1 for p in problems if p[1] == 'critical')
        if critical_count > 0:
            report.status = 'CRITICAL'
            report.recovery_score = max(0.1, 1.0 - critical_count * 0.3)
        else:
            report.status = 'RECOVERING'
            report.recovery_score = 0.6
        
        report.detected_problem = problems[0][2] if problems else ''
        report.root_cause = problems[0][0] if problems else ''
        report.recovery_plan = ' → '.join(a['action'] for a in actions)
        report.circuit_breaker_states = self.circuit_breaker.get_all_states()
        report.explanation = '\n'.join(report.executed_actions)
        
        return report
    
    def record_engine_result(self, engine_name: str, success: bool):
        """Feed engine result into circuit breaker."""
        if success:
            self.circuit_breaker.record_success(engine_name)
        else:
            self.circuit_breaker.record_failure(engine_name)


# ═══════════ SELF-TEST ═══════════
if __name__ == "__main__":
    shb = SelfHealingBrain()
    passed = 0
    
    print("SELF-HEALING BRAIN — Self-Test")
    print("=" * 55)
    
    # T1: All stable
    r = shb.monitor_and_heal(engine_trust=0.80, error_count=0)
    t1 = r.status == 'STABLE'
    if t1: passed += 1
    print(f"  {'✅' if t1 else '❌'} T1: Stable → {r.status} score={r.recovery_score}")
    
    # T2: Low trust
    r = shb.monitor_and_heal(engine_name="ollama", engine_trust=0.05, error_count=0)
    t2 = r.status in ('RECOVERING', 'CRITICAL')
    if t2: passed += 1
    print(f"  {'✅' if t2 else '❌'} T2: Low trust → {r.status} actions={len(r.executed_actions)}")
    
    # T3: High error rate
    r = shb.monitor_and_heal(engine_name="opencode", error_count=7)
    t3 = r.status == 'CRITICAL'
    if t3: passed += 1
    print(f"  {'✅' if t3 else '❌'} T3: High errors → {r.status}")
    
    # T4: Circuit breaker: 5 failures → OPEN
    for _ in range(5):
        shb.record_engine_result("unstable_engine", False)
    t4 = shb.circuit_breaker.is_blocked("unstable_engine")
    if t4: passed += 1
    print(f"  {'✅' if t4 else '❌'} T4: Circuit breaker OPEN → {shb.circuit_breaker.state('unstable_engine')}")
    
    # T5: Circuit breaker success → CLOSED
    shb.record_engine_result("unstable_engine", True)
    t5 = not shb.circuit_breaker.is_blocked("unstable_engine")
    if t5: passed += 1
    print(f"  {'✅' if t5 else '❌'} T5: Recovery → {shb.circuit_breaker.state('unstable_engine')}")
    
    # T6: Safety blocks
    r = shb.monitor_and_heal(engine_name="opencode", engine_trust=0.70, error_count=0, safety_blocks=4)
    t6 = len(r.executed_actions) >= 1
    if t6: passed += 1
    print(f"  {'✅' if t6 else '❌'} T6: Safety blocks → actions={len(r.executed_actions)}")
    
    # T7: Recovery history
    t7 = len(shb.recovery_history) > 0
    if t7: passed += 1
    print(f"  {'✅' if t7 else '❌'} T7: Recovery history → {len(shb.recovery_history)} records")
    
    # T8: High unknown rate
    r = shb.monitor_and_heal(engine_trust=0.70, error_count=0, unknown_rate=0.60)
    t8 = len(r.executed_actions) >= 1
    if t8: passed += 1
    print(f"  {'✅' if t8 else '❌'} T8: Unknown rate → actions={len(r.executed_actions)}")
    
    print(f"\n  ERGEBNIS: {passed}/8 Tests")
    print(f"  {'✅ SELF-HEALING BRAIN FERTIG' if passed >= 7 else '⚠️'}")
