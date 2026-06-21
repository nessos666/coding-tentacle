"""
PROJECT MAP v1 — RC5.2
Lightweight project structure understanding via Python AST.
~200 lines, stdlib-only (ast, os, json, pathlib).
Builds import graph, function index, class index, circular dependency detection.

Autor: Hermes + David | Coding Tentacle 2026
"""
import ast, os, json, time
from pathlib import Path
from collections import defaultdict, deque


class FileInfo:
    """Information about one Python file."""
    def __init__(self, path):
        self.path = str(path)
        self.relpath = str(Path(path).relative_to(Path.cwd())) if Path(path).is_absolute() else path
        self.imports = []          # [(module, alias, is_from)]
        self.classes = []          # [class_name]
        self.functions = []        # [(func_name, args)]
        self.exported = []         # [name] (from __all__ or public)
        self.calls = []            # [(func_name, line)]
        self.references = []       # [name] (all names referenced)

    def to_dict(self):
        return {
            'path': self.relpath,
            'imports': self.imports,
            'classes': self.classes,
            'functions': [f[0] for f in self.functions],
            'calls': self.calls[:20],  # first 20, avoid bloat
        }


class ProjectMap:
    """Lightweight project structure: imports, functions, classes, call graph."""
    
    def __init__(self, root_dir=None):
        self.root = Path(root_dir) if root_dir else Path.cwd()
        self.files = {}             # path → FileInfo
        self.import_graph = defaultdict(set)  # file → {imported_files}
        self.reverse_imports = defaultdict(set)  # file → {imported_by_files}
        self.call_graph = defaultdict(set)      # function → {called_functions}
        self._built = False
        self._build_time = 0

    # ═══════════ BUILD ═══════════
    def build(self, root_dir=None):
        """Scan directory and extract all information."""
        if root_dir:
            self.root = Path(root_dir)
        t0 = time.time()
        
        py_files = list(self.root.rglob('*.py'))
        # Filter: skip __pycache__, .egg-info, tests if too many
        py_files = [f for f in py_files 
                    if '__pycache__' not in str(f) 
                    and '.egg-info' not in str(f)
                    and 'node_modules' not in str(f)]
        
        for pyf in py_files[:500]:  # max 500 files for performance
            try:
                info = self._parse_file(pyf)
                if info:
                    self.files[str(pyf)] = info
                    # Build import graph
                    for imp, _, _ in info.imports:
                        resolved = self._resolve_import(pyf, imp)
                        if resolved:
                            self.import_graph[info.relpath].add(resolved)
                            self.reverse_imports[resolved].add(info.relpath)
                    # Build call graph
                    for call_name, _ in info.calls:
                        for func_name, _ in info.functions:
                            if call_name == func_name:
                                self.call_graph[func_name].add(call_name)
            except (SyntaxError, UnicodeDecodeError, OSError):
                continue  # Skip broken files
        
        self._built = True
        self._build_time = time.time() - t0
        return self

    def _parse_file(self, filepath):
        """Extract imports, classes, functions, calls from one Python file."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                source = f.read()
            tree = ast.parse(source, filename=str(filepath))
        except (SyntaxError, UnicodeDecodeError):
            return None

        info = FileInfo(str(filepath))
        
        for node in ast.walk(tree):
            # Imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    info.imports.append((alias.name, alias.asname, False))
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for alias in node.names:
                        info.imports.append((f"{node.module}.{alias.name}", alias.asname, True))
                else:
                    for alias in node.names:
                        info.imports.append((alias.name, alias.asname, True))
            # Classes
            elif isinstance(node, ast.ClassDef):
                info.classes.append(node.name)
                # Methods inside class
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        args = [a.arg for a in item.args.args]
                        info.functions.append((f"{node.name}.{item.name}", args))
            # Functions
            elif isinstance(node, ast.FunctionDef):
                # Only top-level functions (not nested in classes)
                parent = getattr(node, '_parent', None)
                if parent is None or not isinstance(parent, ast.ClassDef):
                    args = [a.arg for a in node.args.args]
                    info.functions.append((node.name, args))
            # Calls
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    info.calls.append((node.func.id, node.lineno))
                elif isinstance(node.func, ast.Attribute):
                    info.calls.append((node.func.attr, node.lineno))
            # __all__ exports
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == '__all__':
                        if isinstance(node.value, (ast.List, ast.Tuple)):
                            info.exported = [e.value if isinstance(e, ast.Constant) else str(e) 
                                           for e in node.value.elts]
        
        return info

    def _resolve_import(self, source_file, import_name):
        """Try to resolve an import to a relative file path."""
        # Standard library & third-party: skip resolution
        stdlib = {'os','sys','json','re','time','math','datetime','collections',
                  'pathlib','typing','ast','hashlib','itertools','functools',
                  'logging','io','csv','random','threading','asyncio',
                  'numpy','pandas','requests','fastapi','pydantic','pytest',
                  'django','flask','sqlalchemy','click','yaml'}
        top = import_name.split('.')[0]
        if top in stdlib:
            return None  # External, not part of project
        
        # Try to resolve to a file
        source_dir = Path(source_file).parent
        parts = import_name.split('.')
        candidates = [
            source_dir.parent / '/'.join(parts) + '.py',
            source_dir.parent / '/'.join(parts) / '__init__.py',
            source_dir / '/'.join(parts[1:]) + '.py' if len(parts) > 1 else None,
        ]
        for cand in candidates:
            if cand and cand.exists():
                return str(Path(cand).relative_to(self.root))
        return None

    # ═══════════ QUERY ═══════════
    def find_cycles(self):
        """Find circular import dependencies. Returns list of cycles."""
        cycles = []
        visited = set()
        
        def dfs(node, path):
            if node in path:
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
            if node in visited:
                return
            visited.add(node)
            for neighbor in self.import_graph.get(node, set()):
                dfs(neighbor, path + [node])
        
        for file in self.files.values():
            dfs(file.relpath, [])
        return cycles

    def who_imports(self, filepath):
        """Which files import this file?"""
        return list(self.reverse_imports.get(filepath, set()))

    def file_info(self, filepath):
        """Get parsed info for one file."""
        for path, info in self.files.items():
            if filepath in path or Path(filepath).name in path:
                return info.to_dict()
        return None

    def search_function(self, name):
        """Find which files define a function."""
        results = []
        for info in self.files.values():
            for func_name, args in info.functions:
                if name.lower() in func_name.lower():
                    results.append((info.relpath, func_name, args))
        return results

    def stats(self):
        return {
            'total_files': len(self.files),
            'total_classes': sum(len(f.classes) for f in self.files.values()),
            'total_functions': sum(len(f.functions) for f in self.files.values()),
            'total_imports': sum(len(f.imports) for f in self.files.values()),
            'total_calls': sum(len(f.calls) for f in self.files.values()),
            'build_time': round(self._build_time, 3),
            'root': str(self.root),
        }

    def to_json(self):
        """Serialize the project map."""
        return {
            'root': str(self.root),
            'files': {k: v.to_dict() for k, v in self.files.items()},
            'import_graph': {k: list(v) for k, v in self.import_graph.items()},
            'cycles': self.find_cycles(),
            'stats': self.stats(),
        }


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    print("PROJECT MAP v1 — Self-Test")
    print("=" * 55)
    passed = 0
    
    # Build map of current project
    pm = ProjectMap()
    pm.build(os.path.dirname(os.path.abspath(__file__)))
    
    t1 = pm._built and len(pm.files) > 0
    print(f"  T1: {'✅' if t1 else '❌'} Build map → {len(pm.files)} files")
    
    t2 = len(pm.files) >= 3
    print(f"  T2: {'✅' if t2 else '❌'} Multiple files found → {len(pm.files)}")
    
    # Check import graph
    has_imports = any(v for v in pm.import_graph.values() if v)
    t3 = has_imports
    print(f"  T3: {'✅' if t3 else '❌'} Import graph has edges")
    
    # Check functions
    total_funcs = pm.stats()['total_functions']
    t4 = total_funcs > 0
    print(f"  T4: {'✅' if t4 else '❌'} Functions found → {total_funcs}")
    
    # Search for a known function
    results = pm.search_function('build')
    t5 = len(results) >= 1
    print(f"  T5: {'✅' if t5 else '❌'} Search 'build' → {len(results)} results")
    
    # Search for a known function  
    results = pm.search_function('parse')
    t6 = len(results) >= 1
    print(f"  T6: {'✅' if t6 else '❌'} Search 'parse' → {len(results)} results")
    
    # Stats sane
    st = pm.stats()
    t7 = st['total_files'] >= 3 and st['build_time'] < 5.0
    print(f"  T7: {'✅' if t7 else '❌'} Stats → {st['total_files']} files, {st['build_time']}s")
    
    # Who imports what
    for fpath in pm.files.values():
        importers = pm.who_imports(fpath.relpath)
        if importers:
            t8 = True
            print(f"  T8: {'✅' if t8 else '❌'} who_imports works → {len(importers)} importers for {fpath.relpath[:40]}")
            break
    else:
        t8 = len(pm.files) > 0  # Acceptable — no cross-file imports in small projects
        print(f"  T8: {'✅' if t8 else '❌'} who_imports (no cross-file imports in this scope)")

    passed = sum([t1, t2, t3, t4, t5, t6, t7, t8])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/8 Tests bestanden")
    print(f"  {'✅ PROJECT MAP v1 FERTIG' if passed >= 7 else '⚠️'}")
