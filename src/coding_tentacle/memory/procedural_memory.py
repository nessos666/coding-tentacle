"""
PROCEDURAL MEMORY v1 — RC7.0
Stores step-by-step fix procedures per bug type.
Loads, runs, and improves procedures based on success/failure feedback.

NEVER executes actions. Read-only guidance for the repair pipeline.
SecurityRisk bugs → NO procedure, direct BLOCK.

Autor: Hermes + David | Coding Tentacle 2026
"""
import json, time, os
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class ProcedureStep:
    """One step in a fix procedure."""
    order: int                  # 1, 2, 3...
    action: str                 # "analyze_stacktrace", "bq_ground", "blm_lookup"...
    description: str            # What does this step do?
    tool: str                   # Which module/tool?
    expected_output: str        # What should result?
    fallback: str = ""          # What if step fails?
    success_count: int = 0      # Times this step succeeded
    failure_count: int = 0      # Times this step failed


@dataclass
class Procedure:
    """A complete fix procedure for one bug type."""
    bug_type: str               # "NullPointer", "TypeError", ...
    language: str               # "python", "java", ...
    trigger: str                # When to activate this procedure
    steps: list[ProcedureStep]
    confidence: float = 0.5     # Overall procedure confidence
    times_used: int = 0
    times_succeeded: int = 0
    created_at: float = 0.0
    last_used: float = 0.0

    def success_rate(self):
        return self.times_succeeded / max(1, self.times_used)

    def to_dict(self):
        return {
            'bug_type': self.bug_type, 'language': self.language,
            'trigger': self.trigger,
            'steps': [asdict(s) for s in self.steps],
            'confidence': self.confidence, 'times_used': self.times_used,
            'times_succeeded': self.times_succeeded,
            'created_at': self.created_at, 'last_used': self.last_used,
            'success_rate': round(self.success_rate(), 2)
        }


class ProcedureStore:
    """Persistent store of fix procedures. Read-only guidance."""
    
    def __init__(self, config=None, store_path=None):
        self.store_path = store_path or (config.get('learning.procedures_path') if config else os.path.expanduser('~/.coding_tentacle/procedures.json'))
        self.procedures: dict[str, Procedure] = {}  # key = "bug_type:language"
        self.actions_executed = 0
        self._load()
        if not self.procedures:
            self._create_defaults()
    
    # ═══════ QUERY ═══════
    def find_procedure(self, bug_type, language="python"):
        """Find the best procedure for a bug type."""
        key = f"{bug_type}:{language}"
        proc = self.procedures.get(key)
        if proc:
            proc.last_used = time.time()
            proc.times_used += 1
        return proc
    
    def get_procedure(self, bug_type, language="python"):
        return self.procedures.get(f"{bug_type}:{language}")
    
    def list_procedures(self):
        return {k: p.to_dict() for k, p in self.procedures.items()}
    
    # ═══════ FEEDBACK ═══════
    def record_success(self, bug_type, language="python"):
        """Mark procedure as successful."""
        key = f"{bug_type}:{language}"
        proc = self.procedures.get(key)
        if proc:
            proc.times_succeeded += 1
            proc.confidence = min(0.98, proc.confidence + 0.05)
            proc.times_used += 1
            self._save()
    
    def record_failure(self, bug_type, language="python", failed_step=None, reason=""):
        """Mark procedure as failed (overall or specific step)."""
        key = f"{bug_type}:{language}"
        proc = self.procedures.get(key)
        if proc:
            proc.times_used += 1
            proc.confidence = max(0.2, proc.confidence - 0.05)
            if failed_step and failed_step < len(proc.steps):
                proc.steps[failed_step].failure_count += 1
            self._save()
    
    # ═══════ STATS ═══════
    def stats(self):
        return {
            'total_procedures': len(self.procedures),
            'bug_types': list(set(p.bug_type for p in self.procedures.values())),
            'highest_confidence': max((p.confidence for p in self.procedures.values()), default=0),
            'actions_executed': self.actions_executed,
        }
    
    # ═══════ PERSISTENCE ═══════
    def _create_defaults(self):
        """Create default procedures for known bug types."""
        self.procedures["NullPointer:python"] = Procedure(
            bug_type="NullPointer", language="python",
            trigger="Stacktrace: NoneType, has no attribute, None, null pointer",
            steps=[
                ProcedureStep(1, "analyze_stacktrace",
                    "Extrahiere Datei + Zeile + Variable aus Stacktrace",
                    "CodeContext", "file=app.py, line=42, var=value"),
                ProcedureStep(2, "bq_ground",
                    "Bestätige Bug-Typ: NullPointer mit BQ Grounding",
                    "BQ", "NullPointer (grounding_score >= 0.35)"),
                ProcedureStep(3, "find_source",
                    "Finde wo die Variable herkommt (Return/Parameter/Optional)",
                    "ProjectMap.search_function()", "def get_value() -> Optional[str]",
                    fallback="Manuelle Code-Inspektion"),
                ProcedureStep(4, "blm_best_fix",
                    "Frage BugLearningMemory nach bestem Fix",
                    "BLM.best_fix_for()", "guard_clause (45× success)"),
                ProcedureStep(5, "rule_check",
                    "Prüfe PREFER/AVOID Regeln aus RuleMemory",
                    "RuleMemory.check_fix()", "PREFER guard_clause"),
                ProcedureStep(6, "patch_suggest",
                    "Erzeuge Patch-Vorschlag",
                    "PatchSuggestion", "if self.value is not None: ..."),
                ProcedureStep(7, "test_selection",
                    "Wähle relevante Tests aus",
                    "TestSelector", "pytest test_app.py -k test_null"),
                ProcedureStep(8, "verify",
                    "Verifiziere Fix (später: Sandbox-Lauf)",
                    "ResultEvaluator", "Tests grün → Fix gespeichert"),
            ],
            confidence=0.85, created_at=time.time(), last_used=time.time()
        )
        
        self.procedures["TypeError:python"] = Procedure(
            bug_type="TypeError", language="python",
            trigger="Stacktrace: TypeError, cannot concatenate, unsupported operand",
            steps=[
                ProcedureStep(1, "analyze_stacktrace",
                    "Extrahiere Datei + Zeile + Operanden aus Fehler",
                    "CodeContext", "file=worker.py, line=22, int + str"),
                ProcedureStep(2, "bq_ground",
                    "Bestätige Bug-Typ: TypeError",
                    "BQ", "TypeError (grounding_score >= 0.35)"),
                ProcedureStep(3, "blm_best_fix",
                    "Frage BLM nach bestem Fix für TypeError",
                    "BLM.best_fix_for()", "type_cast (38× success)"),
                ProcedureStep(4, "rule_check",
                    "Prüfe Regeln", "RuleMemory", "PREFER type_cast"),
                ProcedureStep(5, "patch_suggest",
                    "Erzeuge Patch", "PatchSuggestion", "str(value) oder int(value)"),
                ProcedureStep(6, "verify",
                    "Verifiziere", "ResultEvaluator", "Tests grün"),
            ],
            confidence=0.80, created_at=time.time(), last_used=time.time()
        )
        
        self.procedures["ImportError:python"] = Procedure(
            bug_type="ImportError", language="python",
            trigger="Stacktrace: ModuleNotFoundError, No module named, cannot import",
            steps=[
                ProcedureStep(1, "analyze_stacktrace",
                    "Welches Modul fehlt?", "CodeContext", "module=utils"),
                ProcedureStep(2, "check_installation",
                    "Ist das Package installiert?", "pip list", "utils==1.2.3"),
                ProcedureStep(3, "blm_best_fix",
                    "Bester Fix", "BLM", "pip install oder import fix"),
                ProcedureStep(4, "patch_suggest",
                    "Patch", "PatchSuggestion", "from utils import helper"),
                ProcedureStep(5, "verify", "Verifiziere", "ResultEvaluator", "Import OK"),
            ],
            confidence=0.70, created_at=time.time(), last_used=time.time()
        )
        
        # RC15.9: 7 NEW procedures for extended bug types
        self.procedures["IndexError:python"] = Procedure(
            bug_type="IndexError", language="python",
            trigger="Stacktrace: IndexError, list index out of range, off-by-one",
            steps=[
                ProcedureStep(1, "analyze_index", "Welcher Index? Welche Collection?",
                    "CodeContext", "list[5] on len=3 → out of range"),
                ProcedureStep(2, "check_bounds", "Prüfe len() vor Zugriff oder try/except",
                    "BQ", "IndexError — bounds check needed"),
                ProcedureStep(3, "suggest_guard", "Guard: if idx < len(collection): oder enumerate()",
                    "PatchSuggestion", "if idx < len(items):\n    return items[idx]"),
                ProcedureStep(4, "test", "Teste mit Edge-Cases (leer, erstes, letztes)",
                    "TestSelector", "pytest -k test_index"),
                ProcedureStep(5, "verify", "Verifiziere kein IndexError mehr",
                    "ResultEvaluator", "Tests grün"),
            ],
            confidence=0.65, created_at=time.time(), last_used=time.time()
        )
        
        self.procedures["ValueError:python"] = Procedure(
            bug_type="ValueError", language="python",
            trigger="Stacktrace: ValueError, invalid literal, invalid value",
            steps=[
                ProcedureStep(1, "analyze_value", "Welcher Wert? Welche Konvertierung?",
                    "CodeContext", "int('abc') → ValueError"),
                ProcedureStep(2, "validate_input", "Input vor Konvertierung validieren",
                    "BQ", "ValueError — input validation needed"),
                ProcedureStep(3, "suggest_try_parse", "try: int(x) except ValueError: ...",
                    "PatchSuggestion", "try:\n    value = int(x)\nexcept ValueError:\n    value = 0"),
                ProcedureStep(4, "test", "Teste mit validen und invaliden Inputs",
                    "TestSelector", "pytest -k test_value"),
                ProcedureStep(5, "verify", "Verifiziere kein ValueError mehr",
                    "ResultEvaluator", "Tests grün"),
            ],
            confidence=0.65, created_at=time.time(), last_used=time.time()
        )
        
        self.procedures["MemoryError:python"] = Procedure(
            bug_type="MemoryError", language="python",
            trigger="Stacktrace: MemoryError, out of memory, OOM",
            steps=[
                ProcedureStep(1, "analyze_allocation", "Wo wird zu viel Speicher allokiert?",
                    "CodeContext", "list(10**9) → MemoryError"),
                ProcedureStep(2, "suggest_streaming", "Generator/Iterator statt Liste, Chunking",
                    "PatchSuggestion", "for chunk in iter(lambda: f.read(8192), b''):"),
                ProcedureStep(3, "suggest_limit", "Batch-Größe begrenzen, Lazy Evaluation",
                    "PatchSuggestion", "MAX_BATCH = 10000"),
                ProcedureStep(4, "verify", "Verifiziere konstante Memory-Nutzung",
                    "ResultEvaluator", "Memory-Profil grün"),
            ],
            confidence=0.60, created_at=time.time(), last_used=time.time()
        )
        
        self.procedures["SyntaxError:python"] = Procedure(
            bug_type="SyntaxError", language="python",
            trigger="Stacktrace: SyntaxError, invalid syntax, version mismatch",
            steps=[
                ProcedureStep(1, "parse_error", "Welche Zeile? Welcher Syntax-Fehler?",
                    "CodeContext", "line 42: x = (1 + 2  → SyntaxError"),
                ProcedureStep(2, "locate_line", "Zeige defekte Zeile und Kontext",
                    "BQ", "SyntaxError — manual fix likely needed"),
                ProcedureStep(3, "suggest_fix", "Fehlende Klammer/Doppelpunkt/Einrückung?",
                    "PatchSuggestion", "x = (1 + 2)  # missing closing paren"),
                ProcedureStep(4, "verify", "python -m py_compile testet Syntax",
                    "ResultEvaluator", "Syntax OK"),
            ],
            confidence=0.70, created_at=time.time(), last_used=time.time()
        )
        
        self.procedures["ConnectionError:python"] = Procedure(
            bug_type="ConnectionError", language="python",
            trigger="Stacktrace: ConnectionError, ConnectionRefused, timeout, network",
            steps=[
                ProcedureStep(1, "analyze_endpoint", "Welcher Host:Port? HTTP/DB/API?",
                    "CodeContext", "localhost:5432 → ConnectionRefused"),
                ProcedureStep(2, "check_timeout", "Timeout setzen, Retry-Logik",
                    "PatchSuggestion", "requests.get(url, timeout=10)"),
                ProcedureStep(3, "add_retry", "Exponential Backoff oder Circuit Breaker",
                    "PatchSuggestion", "for attempt in range(3):\n    try: ...\n    except: time.sleep(2**attempt)"),
                ProcedureStep(4, "verify", "Verifiziere Graceful Degradation",
                    "ResultEvaluator", "Connection-Error-Handling getestet"),
            ],
            confidence=0.60, created_at=time.time(), last_used=time.time()
        )
        
        self.procedures["RaceCondition:python"] = Procedure(
            bug_type="RaceCondition", language="python",
            trigger="Stacktrace: race condition, deadlock, concurrency, thread safety",
            steps=[
                ProcedureStep(1, "analyze_shared_state", "Welche Variable? Welche Threads?",
                    "CodeContext", "counter += 1 in Thread-1 und Thread-2"),
                ProcedureStep(2, "suggest_lock", "threading.Lock oder asyncio.Lock",
                    "PatchSuggestion", "with self.lock:\n    self.counter += 1"),
                ProcedureStep(3, "suggest_ordering", "Queue oder Event für Reihenfolge",
                    "PatchSuggestion", "queue.put(item)  # thread-safe"),
                ProcedureStep(4, "test_concurrency", "Thread-sichere Tests mit pytest-timeout",
                    "TestSelector", "pytest -k test_concurrent"),
                ProcedureStep(5, "verify", "Verifiziere deterministisches Verhalten",
                    "ResultEvaluator", "Race-Condition-Test wiederholbar grün"),
            ],
            confidence=0.55, created_at=time.time(), last_used=time.time()
        )
        
        self.procedures["Performance:python"] = Procedure(
            bug_type="Performance", language="python",
            trigger="Stacktrace: performance, slow, N+1, loading, page load, optimize",
            steps=[
                ProcedureStep(1, "profile_hotspot", "cProfile/py-spy: Wo ist der Bottleneck?",
                    "CodeContext", "for item in items: db.query() → N+1"),
                ProcedureStep(2, "suggest_optimization", "Caching, Batch-Query, Lazy-Load?",
                    "PatchSuggestion", "items = db.query_all(ids)  # 1 query statt N"),
                ProcedureStep(3, "benchmark", "Vorher/Nachher Zeit messen",
                    "TestSelector", "python -m timeit ..."),
                ProcedureStep(4, "verify", "Verifiziere Verbesserung ohne Regression",
                    "ResultEvaluator", "Performance +20%, Tests grün"),
            ],
            confidence=0.50, created_at=time.time(), last_used=time.time()
        )
        
        self._save()
    
    def _save(self):
        os.makedirs(os.path.dirname(self.store_path), exist_ok=True)
        with open(self.store_path, 'w') as f:
            json.dump({k: p.to_dict() for k, p in self.procedures.items()}, f, indent=2)
    
    def _load(self):
        if os.path.exists(self.store_path):
            try:
                with open(self.store_path) as f:
                    data = json.load(f)
                for key, pd in data.items():
                    steps = [ProcedureStep(**s) for s in pd.get('steps', [])]
                    self.procedures[key] = Procedure(
                        bug_type=pd['bug_type'], language=pd['language'],
                        trigger=pd['trigger'], steps=steps,
                        confidence=pd.get('confidence', 0.5),
                        times_used=pd.get('times_used', 0),
                        times_succeeded=pd.get('times_succeeded', 0),
                        created_at=pd.get('created_at', 0),
                        last_used=pd.get('last_used', 0),
                    )
            except Exception:
                pass


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    import tempfile, shutil
    
    print("PROCEDURAL MEMORY v1 — Self-Test")
    print("=" * 55)
    passed = 0
    
    tmp = tempfile.mkdtemp()
    store_path = os.path.join(tmp, 'procedures.json')
    ps = ProcedureStore(store_path=store_path)
    
    # T1: Default procedures created
    t1 = len(ps.procedures) >= 3
    print(f"  T1: {'✅' if t1 else '❌'} Default procedures → {len(ps.procedures)} created")
    
    # T2: Find NullPointer procedure
    proc = ps.find_procedure("NullPointer")
    t2 = proc is not None and proc.bug_type == "NullPointer"
    print(f"  T2: {'✅' if t2 else '❌'} Find NullPointer → {len(proc.steps)} steps")
    
    # T3: Find TypeError procedure
    proc3 = ps.find_procedure("TypeError")
    t3 = proc3 is not None and len(proc3.steps) == 6
    print(f"  T3: {'✅' if t3 else '❌'} Find TypeError → {len(proc3.steps)} steps")
    
    # T4: Find ImportError procedure
    proc4 = ps.find_procedure("ImportError")
    t4 = proc4 is not None
    print(f"  T4: {'✅' if t4 else '❌'} Find ImportError → {len(proc4.steps)} steps")
    
    # T5: Unknown bug type → None
    t5 = ps.find_procedure("RecursionError") is None
    print(f"  T5: {'✅' if t5 else '❌'} Unknown bug → None")
    
    # T6: Record success
    ps.record_success("NullPointer")
    proc = ps.get_procedure("NullPointer")
    t6 = proc.times_succeeded == 1 and proc.confidence > 0.80
    print(f"  T6: {'✅' if t6 else '❌'} Success feedback → {proc.times_succeeded} success, conf={proc.confidence:.2f}")
    
    # T7: Record failure
    ps.record_failure("NullPointer", failed_step=3, reason="BLM returned wrong fix")
    proc = ps.get_procedure("NullPointer")
    t7 = proc.steps[3].failure_count == 1
    print(f"  T7: {'✅' if t7 else '❌'} Step failure feedback → step 3 failed={proc.steps[3].failure_count}")
    
    # T8: Persistence
    ps2 = ProcedureStore(store_path=store_path)
    proc2 = ps2.get_procedure("NullPointer")
    t8 = proc2 is not None and proc2.times_succeeded == 1
    print(f"  T8: {'✅' if t8 else '❌'} Persistence → reloaded with {proc2.times_succeeded} success")
    
    # T9: List procedures
    listing = ps.list_procedures()
    t9 = len(listing) >= 3
    print(f"  T9: {'✅' if t9 else '❌'} List → {len(listing)} procedures")
    
    # T10: Stats
    st = ps.stats()
    t10 = st['total_procedures'] >= 3 and st['actions_executed'] == 0
    print(f"  T10: {'✅' if t10 else '❌'} Stats → {st['total_procedures']} procedures, read-only")
    
    # T11: SecurityRisk — NO procedure
    t11 = ps.find_procedure("SecurityRisk") is None
    print(f"  T11: {'✅' if t11 else '❌'} SecurityRisk → No procedure (correct)")
    
    # T12: No forbidden methods
    forbidden = ['execute', 'write', 'patch', 'run_shell', 'apply', 'delete_file']
    t12 = not any(hasattr(ps, m) for m in forbidden)
    print(f"  T12: {'✅' if t12 else '❌'} No forbidden methods")
    
    passed = sum([t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12])
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/12 Tests bestanden")
    print(f"  {'✅ PROCEDURAL MEMORY v1 FERTIG' if passed >= 11 else '⚠️'}")
