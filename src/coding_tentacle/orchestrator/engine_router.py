"""
ENGINE ROUTER — RC36
CT decides which fix engine to use per bug type.
OpenCode primary, Ollama fallback, Codex disabled.

Author: Hermes + David | Coding Tentacle 2026
"""
import subprocess, time, os


class EngineRouter:
    """Routes bugs to the best available fix engine. Respects Circuit Breaker."""
    
    def __init__(self, circuit_breaker=None):
        self.circuit_breaker = circuit_breaker  # P0.4: SelfHealingBrain's CircuitBreaker
        self.ENGINES = {
        'opencode': {
            'path': '/usr/local/bin/opencode',
            'check_cmd': ['opencode', '--version'],
            'fix_cmd': ['opencode', 'run', '{prompt}'],
            'status': 'unknown',
            'priority': 1,
            'bug_types': ['NullPointer', 'TypeError', 'ImportError', 'KeyError', 
                         'IndexError', 'ValueError', 'FileNotFoundError', 'SyntaxError'],
        },
        'ollama': {
            'path': '/usr/bin/ollama',
            'check_cmd': ['ollama', 'list'],
            'fix_cmd': ['ollama', 'run', 'granite3.2-vision', '{prompt}'],
            'status': 'unknown',
            'priority': 2,
            'bug_types': ['*'],  # All bug types
        },
        'claude': {
            'path': '/home/boobi/.local/bin/claude',
            'check_cmd': ['claude', '--version'],
            'fix_cmd': ['claude', '-p', '{prompt}'],
            'status': 'unknown',
            'priority': 1,  # Same as OpenCode — both are top-tier
            'bug_types': ['NullPointer', 'TypeError', 'ImportError', 'KeyError',
                         'IndexError', 'ValueError', 'SecurityRisk', 'RaceCondition',
                         'Deadlock', 'RecursionError', 'MemoryError', 'Performance'],
        },
        'codex': {
            'path': '/home/boobi/.npm-global/bin/codex',
            'check_cmd': ['codex', '--version'],
            'fix_cmd': ['codex', 'exec', '--skip-git-repo-check', '{prompt}'],
            'status': 'disabled',  # Needs API key
            'priority': 3,
            'bug_types': [],
            'disabled_reason': 'ChatGPT auth — no model access without API key',
        },
    }
    
    def __init__(self):
        self.health_checked = False
        self.route_stats = {}  # engine → {success, failure, timeout}
    
    def check_health(self):
        """Check which engines are available."""
        for name, cfg in self.ENGINES.items():
            if cfg['status'] == 'disabled':
                continue
            try:
                result = subprocess.run(cfg['check_cmd'], capture_output=True, 
                                       text=True, timeout=10)
                cfg['status'] = 'healthy' if result.returncode == 0 else 'unhealthy'
                cfg['last_check'] = time.time()
            except Exception:
                cfg['status'] = 'unavailable'
        self.health_checked = True
    
    def route(self, bug_type, priority='auto'):
        """Return the best engine for a bug type. Respects Circuit Breaker.
        
        Returns: (engine_name, engine_config, reason)
        """
        if not self.health_checked:
            self.check_health()
        
        candidates = []
        circuit_blocked = []
        
        for name, cfg in self.ENGINES.items():
            if cfg['status'] not in ('healthy', 'unknown'):
                continue
            
            # P0.4: Circuit Breaker check
            cb_state = 'CLOSED'  # Default: no breaker = closed
            if self.circuit_breaker:
                cb_state = self.circuit_breaker.state(name)
            
            if cb_state == 'OPEN':
                circuit_blocked.append(f'{name}(OPEN)')
                continue  # Skip completely
            
            if '*' in cfg['bug_types'] or bug_type in cfg['bug_types']:
                candidates.append((cfg['priority'], name, cfg, cb_state))
        
        if not candidates:
            if circuit_blocked:
                return None, None, f'ALL ENGINES BLOCKED: {", ".join(circuit_blocked)}'
            return None, None, "No engines available"
        
        candidates.sort()
        
        for _, name, cfg, cb_state in candidates:
            state_info = ''
            if cb_state == 'HALF_OPEN':
                state_info = ' (HALF_OPEN — test run)'
            return name, cfg, f'Routed to {name} (CB: {cb_state}){state_info}'
        
        return None, None, "Routing failed"
    
    def get_engine_status(self, engine_name: str) -> dict:
        """P0.4: Get full engine status including circuit breaker state."""
        cfg = self.ENGINES.get(engine_name, {})
        cb_state = 'CLOSED'
        if self.circuit_breaker:
            cb_state = self.circuit_breaker.state(engine_name)
        return {
            'health': cfg.get('status', 'unknown'),
            'circuit_breaker': cb_state,
            'path': cfg.get('path', ''),
            'priority': cfg.get('priority', 99),
        }
    
    def get_available_engines(self):
        """List all available engines."""
        if not self.health_checked:
            self.check_health()
        
        available = []
        for name, cfg in self.ENGINES.items():
            available.append({
                'name': name,
                'status': cfg['status'],
                'priority': cfg['priority'],
                'bug_types': cfg['bug_types'],
            })
        return available
    
    def record_result(self, engine_name, bug_type, success, duration_s):
        """Record engine performance for learning."""
        if engine_name not in self.route_stats:
            self.route_stats[engine_name] = {'success': 0, 'failure': 0, 'timeout': 0, 'total_s': 0}
        stats = self.route_stats[engine_name]
        if success:
            stats['success'] += 1
        elif duration_s >= 45:
            stats['timeout'] += 1
        else:
            stats['failure'] += 1
        stats['total_s'] += duration_s
    
    def stats(self):
        return {name: dict(s) for name, s in self.route_stats.items()}


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    print("ENGINE ROUTER — Self-Test")
    print("=" * 55)
    passed = 0
    
    router = EngineRouter()
    router.check_health()
    
    # T1: OpenCode available
    oc = router.ENGINES.get('opencode', {})
    t1 = oc.get('status') == 'healthy'
    print(f"  T1: {'✅' if t1 else '❌'} OpenCode → {oc.get('status')}")
    
    # T2: Ollama available
    ol = router.ENGINES.get('ollama', {})
    t2 = ol.get('status') == 'healthy'
    print(f"  T2: {'✅' if t2 else '❌'} Ollama → {ol.get('status')}")
    
    # T3: Codex disabled
    cx = router.ENGINES.get('codex', {})
    t3 = cx.get('status') == 'disabled'
    print(f"  T3: {'✅' if t3 else '❌'} Codex → {cx.get('status')}")
    
    # T4: Route NullPointer → OpenCode
    name, cfg, reason = router.route('NullPointer')
    t4 = name == 'opencode'
    print(f"  T4: {'✅' if t4 else '❌'} NullPointer → {name} ({reason})")
    
    # T5: Route RaceCondition → Ollama (not in opencode's bug_types)
    name5, _, _ = router.route('RaceCondition')
    t5 = name5 == 'ollama'
    print(f"  T5: {'✅' if t5 else '❌'} RaceCondition → {name5}")
    
    # T6: Route with priority=auto
    name6, _, _ = router.route('TypeError', 'auto')
    t6 = name6 == 'opencode'
    print(f"  T6: {'✅' if t6 else '❌'} TypeError auto → {name6}")
    
    # T7: Unknown bug type → Ollama (catch-all)
    name7, _, _ = router.route('UnknownXYZ')
    t7 = name7 == 'ollama'
    print(f"  T7: {'✅' if t7 else '❌'} Unknown → {name7}")
    
    # T8: Engine stats tracking
    router.record_result('opencode', 'NullPointer', True, 12.0)
    router.record_result('opencode', 'TypeError', True, 5.0)
    router.record_result('ollama', 'RaceCondition', False, 30.0)
    st = router.stats()
    t8 = st.get('opencode', {}).get('success') == 2
    print(f"  T8: {'✅' if t8 else '❌'} Stats → {st}")
    
    # T9: Available engines list
    avail = router.get_available_engines()
    t9 = len(avail) >= 2
    print(f"  T9: {'✅' if t9 else '❌'} Available → {len(avail)} engines")
    
    # T10: Routing table complete
    table = {name: cfg.get('bug_types', [])[:4] for name, cfg in router.ENGINES.items()}
    t10 = len(table) == 3
    print(f"  T10: {'✅' if t10 else '❌'} Routing table → {len(table)} engines")
    
    passed = sum([t1,t2,t3,t4,t5,t6,t7,t8,t9,t10])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/10 Tests bestanden")
    print(f"  {'✅ ENGINE ROUTER FERTIG' if passed >= 9 else '⚠️'}")
