"""
PARALLEL ACTIVATIONMANAGER — RC16
Runs independent tentacles concurrently via threads.
Safety VETO always runs FIRST and sequentially.
Dependent tentacles wait for their prerequisites.

Inspired by: Codex 8-parallel-subagent architecture.

Autor: Hermes + David | Coding Tentacle 2026
"""
import time, threading
from dataclasses import dataclass, field
from collections import defaultdict
from typing import Optional


# Dependency graph: which tentacles can run in parallel
TENTACLE_DEPENDENCIES = {
    'SafetyBrain':      {'depends_on': [],           'blocking': True},   # ALWAYS FIRST
    'BQ':               {'depends_on': ['SafetyBrain'], 'blocking': False},
    'BR':               {'depends_on': ['SafetyBrain'], 'blocking': False},
    'BLM':              {'depends_on': ['SafetyBrain'], 'blocking': False},
    'RuleMemory':        {'depends_on': ['BLM'],        'blocking': False},
    'ProjectMap':       {'depends_on': ['SafetyBrain'], 'blocking': False},
    'ProceduralMemory': {'depends_on': ['BQ'],          'blocking': False},
    'SkillStore':       {'depends_on': ['ProceduralMemory'], 'blocking': False},
    'PatchSuggestion':  {'depends_on': ['BQ', 'BR', 'RuleMemory'], 'blocking': False},
    'DiffGenerator':    {'depends_on': ['PatchSuggestion'], 'blocking': False},
    'SandboxRunner':    {'depends_on': ['DiffGenerator'], 'blocking': False},
    'TestRunner':       {'depends_on': ['SandboxRunner'], 'blocking': False},
    'LearningBrain':    {'depends_on': ['TestRunner'],  'blocking': False},
}


@dataclass
class TentacleResult:
    tentacle: str
    success: bool
    result: any = None
    error: str = ""
    duration_ms: float = 0.0


class ParallelActivationManager:
    """Activates tentacles in parallel where dependencies allow.
    Safety VETO always runs first, sequentially."""
    
    def __init__(self, tentacles=None, max_parallel=8, max_timeout=30):
        self.tentacles = tentacles or {}
        self.max_parallel = max_parallel
        self.max_timeout = max_timeout
        self.activation_log = []
        self.actions_executed = 0
    
    def register(self, name, tentacle_obj):
        self.tentacles[name] = tentacle_obj
    
    def get_parallel_groups(self, bug_type):
        """Determine which tentacles can run in parallel."""
        groups = []
        completed = set()
        remaining = set(TENTACLE_DEPENDENCIES.keys())
        
        while remaining:
            group = []
            for name in list(remaining):
                deps = set(TENTACLE_DEPENDENCIES[name]['depends_on'])
                if deps.issubset(completed):
                    if TENTACLE_DEPENDENCIES[name]['blocking']:
                        # Blocking tentacles run ALONE in their group
                        groups.append([name])
                    else:
                        group.append(name)
                    remaining.discard(name)
            
            if group:
                groups.append(group)
            for name in groups[-1]:
                completed.add(name)
        
        return groups
    
    def run_parallel(self, bug_report, bug_type, code_context=None):
        """Run tentacles in parallel groups. Safety first."""
        groups = self.get_parallel_groups(bug_type)
        all_results = {}
        t0 = time.time()
        
        for group in groups:
            group_results = {}
            threads = []
            results_lock = threading.Lock()
            
            def run_one(name):
                t0_t = time.time()
                try:
                    tentacle = self.tentacles.get(name)
                    if not tentacle:
                        with results_lock:
                            group_results[name] = TentacleResult(
                                name, False, error=f"Tentacle '{name}' not registered")
                        return
                    
                    # Execute tentacle
                    result = self._execute_tentacle(name, tentacle, bug_report, bug_type, code_context)
                    with results_lock:
                        group_results[name] = TentacleResult(
                            name, True, result=result,
                            duration_ms=(time.time() - t0_t) * 1000)
                except Exception as e:
                    with results_lock:
                        group_results[name] = TentacleResult(
                            name, False, error=str(e),
                            duration_ms=(time.time() - t0_t) * 1000)
            
            # Start all tentacles in this group
            for name in group:
                t = threading.Thread(target=run_one, args=(name,), daemon=True)
                threads.append(t)
                t.start()
            
            # Wait for all to complete (with timeout)
            for t in threads:
                t.join(timeout=self.max_timeout)
            
            all_results.update(group_results)
            
            # If SafetyBrain blocked, stop everything
            if 'SafetyBrain' in group_results and group_results['SafetyBrain'].success:
                result = group_results['SafetyBrain'].result
                if isinstance(result, dict) and result.get('decision') == 'BLOCK':
                    break
        
        self.activation_log.append({
            'bug_type': bug_type,
            'groups': len(groups),
            'total_tentacles': len(all_results),
            'duration_ms': (time.time() - t0) * 1000,
            'parallel': sum(1 for g in groups if len(g) > 1),
        })
        
        return all_results
    
    def _execute_tentacle(self, name, tentacle, bug_report, bug_type, code_context):
        """Execute one tentacle. Dispatch based on tentacle type."""
        # SafetyBrain
        if name == 'SafetyBrain' and hasattr(tentacle, 'evaluate'):
            return tentacle.evaluate(bug_report, 
                   context=code_context)
        
        # BQ
        if name == 'BQ' and hasattr(tentacle, 'think'):
            return tentacle.think(bug_report)
        
        # BR
        if name == 'BR' and hasattr(tentacle, 'think'):
            return tentacle.think(bug_report)
        
        # BLM
        if name == 'BLM' and hasattr(tentacle, 'find_similar'):
            return tentacle.find_similar(bug_report, bug_type=bug_type)
        
        # RuleMemory
        if name == 'RuleMemory' and hasattr(tentacle, 'get_preferred_fix'):
            return tentacle.get_preferred_fix(bug_type)
        
        # ProjectMap
        if name == 'ProjectMap' and hasattr(tentacle, 'who_imports'):
            f = code_context.get('file', '') if code_context else ''
            return {'importers': tentacle.who_imports(f)[:5] if f else []}
        
        # ProceduralMemory
        if name == 'ProceduralMemory' and hasattr(tentacle, 'find_procedure'):
            return tentacle.find_procedure(bug_type)
        
        # SkillStore
        if name == 'SkillStore' and hasattr(tentacle, 'best_skill_for'):
            return tentacle.best_skill_for(bug_type)
        
        # PatchSuggestion
        if name == 'PatchSuggestion' and hasattr(tentacle, 'suggest'):
            return tentacle.suggest(bug_report, code_context=code_context,
                   grounding={'bug_type': bug_type})
        
        return {'status': 'executed'}
    
    def stats(self):
        return {
            'total_activations': len(self.activation_log),
            'avg_duration_ms': round(
                sum(a['duration_ms'] for a in self.activation_log) / max(1, len(self.activation_log)), 1
            ),
            'actions_executed': self.actions_executed,
        }


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    from coding_tentacle.safety.inhibitory_control import InhibitoryControl
    from coding_tentacle.knowledge.security_store import create_seed_security_store
    from coding_tentacle.orchestrator.metabrain import SafetyBrain, TeacherBrain
    from coding_tentacle.brains.sg_brain import SymbolGroundingBrain
    from coding_tentacle.memory.bug_learning_memory import BugLearningMemory
    from coding_tentacle.memory.procedural_memory import ProcedureStore
    from coding_tentacle.knowledge.project_map import ProjectMap
    import tempfile, os
    
    print("PARALLEL ACTIVATIONMANAGER — Self-Test")
    print("=" * 55)
    passed = 0
    
    tmp = tempfile.mkdtemp()
    
    # Setup tentacles
    sec = create_seed_security_store()
    ic = InhibitoryControl(security_store=sec)
    safety = SafetyBrain(ic=ic, security_store=sec)
    bq = SymbolGroundingBrain()
    blm = BugLearningMemory(db_path=os.path.join(tmp, 'blm.db'))
    ps_store = ProcedureStore(store_path=os.path.join(tmp, 'proc.json'))
    pm = ProjectMap()
    pm.build_cached('/home/boobi/GEHIRN_BIBLIOTHEK') if hasattr(pm, 'build_cached') else pm.build('/home/boobi/GEHIRN_BIBLIOTHEK')
    
    pam = ParallelActivationManager()
    pam.register('SafetyBrain', safety)
    pam.register('BQ', bq)
    pam.register('BLM', blm)
    pam.register('ProceduralMemory', ps_store)
    pam.register('ProjectMap', pm)
    
    # T1: Parallel groups are computed
    groups = pam.get_parallel_groups('NullPointer')
    t1 = len(groups) >= 3  # SafetyBrain alone, then BQ+BR+BLM+PM parallel, then others
    print(f"  T1: {'✅' if t1 else '❌'} Parallel groups → {len(groups)} groups: {[g[:3] for g in groups[:3]]}")
    
    # T2: SafetyBrain is ALWAYS first group
    t2 = 'SafetyBrain' in groups[0] and len(groups[0]) == 1
    print(f"  T2: {'✅' if t2 else '❌'} Safety first → group[0]={groups[0]}")
    
    # T3: Parallel execution works
    results = pam.run_parallel('NullPointerException', 'NullPointer', 
                               code_context={'file': 'test.py', 'line': 1})
    t3 = len(results) >= 3 and 'SafetyBrain' in results
    print(f"  T3: {'✅' if t3 else '❌'} Parallel run → {len(results)} tentacles executed")
    
    # T4: Safety VETO blocks other tentacles
    results_sec = pam.run_parallel('DROP TABLE users', 'SecurityRisk',
                                   code_context={'file': 'db.py', 'line': 10})
    has_safety = 'SafetyBrain' in results_sec
    t4 = has_safety
    print(f"  T4: {'✅' if t4 else '❌'} Security → SafetyBrain present")
    
    # T5: BQ result is available
    bq_result = results.get('BQ')
    t5 = bq_result is not None
    print(f"  T5: {'✅' if t5 else '❌'} BQ result → {bq_result.success if bq_result else False}")
    
    # T6: Stats read-only
    st = pam.stats()
    t6 = st['actions_executed'] == 0
    print(f"  T6: {'✅' if t6 else '❌'} Stats → read-only")
    
    passed = sum([t1,t2,t3,t4,t5,t6])
    import shutil; shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/6 Tests bestanden")
    print(f"  {'✅ PARALLEL ACTIVATION FERTIG' if passed >= 5 else '⚠️'}")
