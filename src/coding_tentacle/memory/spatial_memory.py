"""
SPATIAL MEMORY V1 — Riebschläger Proposal 3
Dateisystem als räumliches Gedächtnis. Ordner, Importe, Nähe, Zonen.
Read-only. Ergänzt ProjectMap + CausalChainGraph.
"""
import os, re, json
from dataclasses import dataclass, field


@dataclass
class FileNode:
    path: str
    name: str
    directory: str
    extension: str
    zone: str = 'unknown'
    related: list = field(default_factory=list)
    likely_tests: list = field(default_factory=list)


@dataclass
class SpatialMap:
    project_root: str = ''
    files: list = field(default_factory=list)
    directories: dict = field(default_factory=dict)
    zones: dict = field(default_factory=dict)
    import_graph: dict = field(default_factory=dict)


class SpatialMemory:
    """Reads project filesystem as a navigable spatial memory."""
    
    ZONE_PATTERNS = {
        'brain': ['brains/', 'brain', 'sg_brain', 'root_cause', 'causal_chain',
                  'prompt_injection', 'reflex_layer', 'skeptic', 'deutero', 'meta'],
        'memory': ['memory/', 'blm', 'rule_memory', 'procedural', 'skill',
                   'consolidation', 'working_memory', 'experience'],
        'learning': ['learning/', 'engine_learning', 'outcome_learning',
                     'backward_paths', 'consolidation_cycle'],
        'safety': ['safety/', 'inhibitory', 'approval_gate', 'escalation',
                   'security_store', 'veto', 'prompt_injection'],
        'audit': ['audit/', 'evidence_ledger', 'self_observation'],
        'orchestrator': ['orchestrator/', 'shadow_mode', 'engine_router', 
                         'metabrain', 'repair_loop'],
        'knowledge': ['knowledge/', 'project_map', 'impact_analyzer', 
                      'bug_pattern', 'library_store'],
        'classifier': ['classifier/', 'unified_classifier'],
        'patch': ['patch/', 'diff_generator', 'sandbox', 'test_runner'],
        'config': ['config.py', 'pyproject.toml', 'setup.py'],
        'test': ['tests/', 'test_', '_test.py', 'scripts/full_regression'],
    }
    
    def __init__(self, project_root: str = '.'):
        self.project_root = project_root
        self._cache = {}
    
    def build_map(self, project_root: str = None) -> SpatialMap:
        """Build spatial map of project structure."""
        root = project_root or self.project_root
        smap = SpatialMap(project_root=root)
        
        if not os.path.exists(root):
            return smap
        
        # Walk directory tree
        for dirpath, dirnames, filenames in os.walk(root):
            # Skip hidden + cache
            dirnames[:] = [d for d in dirnames if not d.startswith('.') 
                          and d not in ('__pycache__', 'node_modules', '.git', 'archive')]
            
            rel_dir = os.path.relpath(dirpath, root)
            if rel_dir == '.':
                rel_dir = ''
            
            for fname in filenames:
                if fname.startswith('.') or fname.endswith(('.pyc', '.pyo')):
                    continue
                
                fpath = os.path.join(rel_dir, fname) if rel_dir else fname
                full_path = os.path.join(dirpath, fname)
                
                node = FileNode(
                    path=fpath,
                    name=fname,
                    directory=rel_dir,
                    extension=os.path.splitext(fname)[1],
                    zone=self._classify_zone(fpath),
                )
                smap.files.append(node)
                
                # Directory index
                smap.directories.setdefault(rel_dir, []).append(fpath)
                smap.zones.setdefault(node.zone, []).append(fpath)
        
        # Build import graph (Python only)
        for node in smap.files:
            if node.extension == '.py':
                full_path = os.path.join(root, node.path)
                try:
                    node.related = self._extract_imports(full_path, smap)
                except:
                    pass
        
        # Find related files (same directory)
        for node in smap.files:
            siblings = smap.directories.get(node.directory, [])
            node.related = list(set(
                [s for s in siblings if s != node.path][:5] + node.related[:3]
            ))
            node.likely_tests = self._find_likely_tests(node.path, smap)
        
        return smap
    
    def find_related_files(self, file_path: str, smap: SpatialMap = None) -> list:
        """Find spatially related files."""
        if smap is None:
            smap = self.build_map()
        
        matches = []
        target_name = os.path.splitext(os.path.basename(file_path))[0]
        target_dir = os.path.dirname(file_path)
        
        # Same directory
        matches.extend(smap.directories.get(target_dir, [])[:3])
        
        # Similar name
        for node in smap.files:
            node_name = os.path.splitext(node.name)[0]
            if node_name != target_name and target_name in node_name:
                matches.append(node.path)
        
        return list(set(matches))[:8]
    
    def find_likely_tests(self, file_path: str, smap: SpatialMap = None) -> list:
        """Find test files likely related to a source file."""
        if smap is None:
            smap = self.build_map()
        return self._find_likely_tests(file_path, smap)
    
    def _find_likely_tests(self, file_path: str, smap: SpatialMap) -> list:
        """Internal: find test files for a source file."""
        base = os.path.splitext(os.path.basename(file_path))[0]
        candidates = []
        
        for node in smap.files:
            nbase = os.path.splitext(node.name)[0]
            # test_foo.py or foo_test.py
            if (nbase == f'test_{base}' or nbase == f'{base}_test' or
                f'test_{base}' in nbase):
                candidates.append(node.path)
            # In tests/ directory
            if 'tests/' in node.path or 'test/' in node.path:
                if base in nbase:
                    candidates.append(node.path)
        
        return candidates[:3]
    
    def _classify_zone(self, file_path: str) -> str:
        """Classify which architectural zone a file belongs to."""
        fpath_lower = file_path.lower()
        for zone, patterns in self.ZONE_PATTERNS.items():
            for pat in patterns:
                if pat in fpath_lower:
                    return zone
        return 'unknown'
    
    def _extract_imports(self, file_path: str, smap: SpatialMap) -> list:
        """Extract local imports from a Python file."""
        imports = []
        try:
            with open(file_path) as f:
                for line in f:
                    # Match: from coding_tentacle.X import Y
                    m = re.match(r'from\s+(coding_tentacle\.[\w.]+)\s+import', line)
                    if m:
                        mod_path = m.group(1).replace('.', '/') + '.py'
                        if any(n.path and mod_path in n.path for n in smap.files):
                            imports.append(mod_path)
        except:
            pass
        return imports


# ═══════════ SELF-TEST ═══════════
if __name__ == "__main__":
    import tempfile, shutil
    
    # Create fake project structure
    tmp = tempfile.mkdtemp()
    os.makedirs(f'{tmp}/brains')
    os.makedirs(f'{tmp}/memory')
    os.makedirs(f'{tmp}/safety')
    os.makedirs(f'{tmp}/orchestrator')
    os.makedirs(f'{tmp}/tests')
    
    # Create fake files
    for path, content in [
        ('brains/root_cause_brain.py', 'from coding_tentacle.memory import BugLearningMemory\nclass RootCauseBrain: pass'),
        ('brains/homeostasis_brain.py', 'class HomeostasisBrain: pass'),
        ('memory/spatial_memory.py', 'class SpatialMemory: pass'),
        ('safety/inhibitory_control.py', 'class InhibitoryControl: pass'),
        ('orchestrator/shadow_mode.py', 'from coding_tentacle.brains import RootCauseBrain\nclass ShadowMode: pass'),
        ('tests/test_root_cause.py', 'def test_root_cause(): pass'),
        ('tests/test_homeostasis.py', 'def test_homeostasis(): pass'),
        ('config.py', '# config'),
    ]:
        with open(f'{tmp}/{path}', 'w') as f:
            f.write(content)
    
    sm = SpatialMemory(project_root=tmp)
    smap = sm.build_map()
    passed = 0
    
    print("SPATIAL MEMORY — Self-Test")
    print("=" * 55)
    
    # T1: Map built
    t1 = len(smap.files) >= 5
    if t1: passed += 1
    print(f"  {'✅' if t1 else '❌'} T1: Map built → {len(smap.files)} files, {len(smap.directories)} dirs")
    
    # T2: Architectural zones
    zones_found = set(n.zone for n in smap.files)
    t2 = 'brain' in zones_found and 'safety' in zones_found and 'test' in zones_found
    if t2: passed += 1
    print(f"  {'✅' if t2 else '❌'} T2: Zones → {zones_found}")
    
    # T3: Related files (same directory)
    related = sm.find_related_files('brains/root_cause_brain.py', smap)
    t3 = 'brains/homeostasis_brain.py' in related
    if t3: passed += 1
    print(f"  {'✅' if t3 else '❌'} T3: Related files → {related}")
    
    # T4: Likely tests
    tests = sm.find_likely_tests('brains/root_cause_brain.py', smap)
    t4 = len(tests) >= 1 and 'tests/test_root_cause.py' in tests
    if t4: passed += 1
    print(f"  {'✅' if t4 else '❌'} T4: Likely tests → {tests}")
    
    # T5: Import graph
    for n in smap.files:
        if 'shadow_mode.py' in n.path:
            t5 = len(n.related) >= 1
            if t5: passed += 1
            print(f"  {'✅' if t5 else '❌'} T5: Import graph → {n.related}")
            break
    
    # T6: Missing path doesn't crash
    r = sm.find_related_files('nonexistent.py', smap)
    t6 = isinstance(r, list)
    if t6: passed += 1
    print(f"  {'✅' if t6 else '❌'} T6: Graceful missing → {len(r)} results")
    
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n  ERGEBNIS: {passed}/6 Tests")
    print(f"  {'✅ SPATIAL MEMORY FERTIG' if passed >= 5 else '⚠️'}")
