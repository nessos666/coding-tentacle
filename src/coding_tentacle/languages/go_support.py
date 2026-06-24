"""
GO DEMO READINESS — P2.5
Sixth language. Go 1.22 installed. Templates + Safety.

Safety VETO: os/exec(user), unsafe, raw SQL ALWAYS blocked.

Autor: Hermes + David | Coding Tentacle 2026
"""
import re, time, os


# ═══════════ GO BUG PATTERNS ═══════════
GO_BUG_PATTERNS = {
    'Go_SliceBounds': {
        'keywords': ['slice bounds', 'index out of range', 'slice bounds out of range',
                     'panic.*index'],
        'fix': 'if idx < len(slice) { val := slice[idx] }',
        'description': 'Slice bounds — check len() before index access',
    },
    'Go_NilPointer': {
        'keywords': ['nil pointer', 'nil dereference', 'invalid memory address',
                     'nil pointer dereference', 'panic.*nil'],
        'fix': 'if ptr != nil {\n    ptr.Method()\n}',
        'description': 'Nil pointer dereference — add nil check before access',
    },
    'Go_MissingImport': {
        'keywords': ['undefined', 'imported and not used', 'could not import',
                     'no required module', 'package .* is not in'],
        'fix': 'import (\n    "package/path"\n)',
        'description': 'Missing import — add import statement or go get',
    },
    'Go_UnhandledError': {
        'keywords': ['err != nil', 'error', 'must be handled', 'unhandled error'],
        'fix': 'if err != nil {\n    return fmt.Errorf("op: %w", err)\n}',
        'description': 'Unhandled error — check err != nil and return or handle',
    },
    'Go_TypeMismatch': {
        'keywords': ['cannot use', 'type .* is not', 'cannot convert',
                     'mismatched types', 'incompatible'],
        'fix': 'value, ok := x.(ExpectedType)\n// or: strconv.Itoa / strconv.Atoi',
        'description': 'Type mismatch — use type assertion or conversion',
    },
    'Go_SliceBounds': {
        'keywords': ['slice bounds', 'index out of range', 'slice bounds out of range',
                     'panic.*index'],
        'fix': 'if idx < len(slice) {\n    val := slice[idx]\n}',
        'description': 'Slice bounds — check len() before index access',
    },
    'Go_UnhandledError': {
        'keywords': ['err != nil', 'error', 'must be handled', 'unhandled error'],
        'fix': 'if err != nil {\n    return fmt.Errorf("op: %w", err)\n}',
        'description': 'Unhandled error — check err != nil and return or handle',
    },
    'Go_ContextTimeout': {
        'keywords': ['context deadline exceeded', 'context', 'timeout', 'deadline'],
        'fix': 'ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)\ndefer cancel()',
        'description': 'Context timeout — use context.WithTimeout',
    },
    'Go_GoroutineLeak': {
        'keywords': ['goroutine leak', 'leak', 'WaitGroup', 'not closed',
                     'channel not closed'],
        'fix': 'var wg sync.WaitGroup\nwg.Add(1)\ngo func() { defer wg.Done(); ... }()\nwg.Wait()',
        'description': 'Goroutine leak — use sync.WaitGroup',
    },
    'Go_DataRace': {
        'keywords': ['data race', 'race', 'race condition', 'concurrent',
                     'go test -race', 'WARNING: DATA RACE'],
        'fix': 'var mu sync.Mutex\nmu.Lock()\ndefer mu.Unlock()\n// or: sync/atomic',
        'description': 'Data race — use sync.Mutex or atomic operations',
    },
    'Go_DangerousCall': {
        'keywords': ['os/exec', 'exec.Command', 'unsafe.', 'database/sql.*fmt.Sprintf',
                     'Sprintf.*SELECT', 'Sprintf.*DELETE'],
        'fix': '// BLOCKED: dangerous call — requires human review',
        'description': 'Security Risk — os/exec, unsafe, or raw SQL',
        'block': True,
    },
}


def classify_go_bug(error_message, code=""):
    """Classify a Go error into a bug type."""
    combined = (error_message + ' ' + code).lower()
    
    for bug_type, pattern in GO_BUG_PATTERNS.items():
        if pattern.get('block'):
            for kw in pattern['keywords']:
                if re.search(kw.lower(), code or error_message, re.IGNORECASE):
                    return bug_type, pattern
    
    for bug_type, pattern in GO_BUG_PATTERNS.items():
        if pattern.get('block'):
            continue
        for kw in pattern['keywords']:
            if re.search(kw.lower(), combined, re.IGNORECASE):
                return bug_type, pattern
    
    return 'Go_Unknown', {'fix': '// Unknown error', 'description': 'Unknown'}


def is_dangerous_go(code):
    """Check for dangerous Go patterns."""
    dangerous = [
        r'os/exec', r'exec\.Command\(', r'unsafe\.', 
        r'fmt\.Sprintf\(.*SELECT', r'fmt\.Sprintf\(.*DELETE',
        r'fmt\.Sprintf\(.*INSERT', r'fmt\.Sprintf\(.*DROP',
    ]
    for pattern in dangerous:
        if re.search(pattern, code, re.IGNORECASE):
            return True, f"BLOCKED: {pattern}"
    return False, ""


def create_go_procedures(procedure_store):
    """Create Go-specific procedures."""
    from coding_tentacle.memory.procedural_memory import Procedure, ProcedureStep
    
    procedures = {
        "Go_NilGuard:go": ("NilPointer", "Guard against nil",
            [("check", "if ptr != nil { ptr.Method() }", "nil check"),
             ("err_check", "Check error before accessing result", "if err != nil"),
             ("test", "go test ./...", "Tests pass")]),
        "Go_ErrorCheck:go": ("UnhandledError", "Handle errors properly",
            [("check", "if err != nil { return err }", "Error check"),
             ("wrap", 'fmt.Errorf("op: %w", err)', "Error wrapping"),
             ("test", "go test ./...", "Tests pass")]),
        "Go_SliceGuard:go": ("SliceBounds", "Guard slice access",
            [("check", "if idx < len(s) { val := s[idx] }", "Bounds check"),
             ("range", "Or: for _, v := range s { }", "Range loop"),
             ("test", "go test ./...", "Tests pass")]),
        "Go_BlockDangerous:go": ("SecurityRisk", "BLOCK dangerous patterns",
            [("detect", "os/exec or unsafe or raw SQL", "Dangerous"),
             ("block", "SAFETY VETO", "NEVER auto-fix"),
             ("report", "Requires human review", "Report generated")]),
    }
    
    for key, (bt, desc, steps) in procedures.items():
        bp, lang = key.split(':')
        if not procedure_store.get_procedure(bp, lang):
            procedure_store.procedures[key] = Procedure(
                bug_type=bt, language=lang, trigger=desc,
                steps=[ProcedureStep(i+1, n, d, "GoSupport", exp, "")
                       for i, (n, d, exp) in enumerate(steps)],
                confidence=0.68, created_at=time.time(), last_used=time.time()
            )
    procedure_store._save()


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    import tempfile, shutil
    
    print("GO DEMO READINESS — Self-Test")
    print("=" * 55)
    passed = 0
    
    # T1: nil pointer
    bt, _ = classify_go_bug("panic: runtime error: invalid memory address or nil pointer dereference")
    t1 = bt == 'Go_NilPointer'
    print(f"  T1: {'✅' if t1 else '❌'} nil pointer → {bt}")
    
    # T2: missing import
    bt2, _ = classify_go_bug("undefined: fmt.Println")
    t2 = bt2 == 'Go_MissingImport'
    print(f"  T2: {'✅' if t2 else '❌'} undefined → {bt2}")
    
    # T3: unhandled error
    bt3, _ = classify_go_bug("result, err := fn()  // err must be handled")
    t3 = bt3 == 'Go_UnhandledError'
    print(f"  T3: {'✅' if t3 else '❌'} unhandled error → {bt3}")
    
    # T4: slice bounds
    bt4, _ = classify_go_bug("panic: runtime error: index out of range [5]")
    t4 = bt4 == 'Go_SliceBounds'
    print(f"  T4: {'✅' if t4 else '❌'} slice bounds → {bt4}")
    
    # T5: context deadline
    bt5, _ = classify_go_bug("context deadline exceeded")
    t5 = bt5 == 'Go_ContextTimeout'
    print(f"  T5: {'✅' if t5 else '❌'} context timeout → {bt5}")
    
    # T6: os/exec BLOCKED
    blocked, _ = is_dangerous_go('import "os/exec"; exec.Command("userInput")')
    t6 = blocked
    print(f"  T6: {'✅' if t6 else '❌'} os/exec → BLOCKED")
    
    # T7: safe code passes
    blocked7, _ = is_dangerous_go('fmt.Println("hello")')
    t7 = not blocked7
    print(f"  T7: {'✅' if t7 else '❌'} Safe code → NOT blocked")
    
    # T8: go compiler available
    import subprocess
    try:
        result = subprocess.run(['go', 'version'], capture_output=True, text=True, timeout=5)
        t8 = result.returncode == 0
        print(f"  T8: {'✅' if t8 else '❌'} go version → {result.stdout.strip()[:40]}")
    except:
        t8 = False
        print(f"  T8: ❌ go not found")
    
    # T9: Procedures created
    from coding_tentacle.memory.procedural_memory import ProcedureStore
    tmp = tempfile.mkdtemp()
    ps = ProcedureStore(store_path=os.path.join(tmp, 'proc.json'))
    create_go_procedures(ps)
    count = sum(1 for k in ps.procedures if ':go' in k)
    t9 = count >= 3
    print(f"  T9: {'✅' if t9 else '❌'} {count} Go procedures")
    
    shutil.rmtree(tmp, ignore_errors=True)
    passed = sum([t1,t2,t3,t4,t5,t6,t7,t8,t9])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/9 Tests bestanden")
    print(f"  {'✅ GO DEMO-READY' if passed >= 8 else '⚠️'}")
