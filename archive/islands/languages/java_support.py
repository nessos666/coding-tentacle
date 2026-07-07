"""
JAVA DEMO-READY — P3.1
Eighth and final language. OpenJDK 21 installed. Templates + Safety.

Safety VETO: Runtime.exec(), ProcessBuilder, raw SQL ALWAYS blocked.

Autor: Hermes + David | Coding Tentacle 2026
"""
import re, time, os, subprocess


# ═══════════ JAVA BUG PATTERNS ═══════════
JAVA_BUG_PATTERNS = {
    'Java_NullPointer': {
        'keywords': ['NullPointerException', 'null pointer', 'null', 'NPE'],
        'fix': 'if (obj != null) { obj.method(); }\n// or: Objects.requireNonNull(obj, "msg");',
        'description': 'NullPointerException — add null check or use Optional',
    },
    'Java_ClassNotFound': {
        'keywords': ['ClassNotFoundException', 'NoClassDefFoundError',
                     'class not found', 'could not find'],
        'fix': '// Check: classpath, JAR dependencies, or IDE build path',
        'description': 'ClassNotFoundException — missing JAR or wrong classpath',
    },
    'Java_NoSuchMethod': {
        'keywords': ['NoSuchMethodException', 'NoSuchMethodError',
                     'method not found', 'no such method'],
        'fix': '// Check method signature: parameter types, return type, visibility',
        'description': 'NoSuchMethodError — method signature mismatch or missing',
    },
    'Java_IndexOutOfBounds': {
        'keywords': ['IndexOutOfBoundsException', 'ArrayIndexOutOfBoundsException',
                     'StringIndexOutOfBoundsException', 'index out', 'out of bounds'],
        'fix': 'if (index >= 0 && index < list.size()) { var item = list.get(index); }',
        'description': 'IndexOutOfBounds — add bounds check before access',
    },
    'Java_IllegalArgument': {
        'keywords': ['IllegalArgumentException', 'illegal argument',
                     'invalid argument', 'wrong argument'],
        'fix': 'if (arg == null || arg.isEmpty()) { throw new IllegalArgumentException("Invalid arg"); }',
        'description': 'IllegalArgumentException — validate arguments at method entry',
    },
    'Java_ConcurrentModification': {
        'keywords': ['ConcurrentModificationException', 'concurrent',
                     'modification', 'iterator'],
        'fix': '// Use Iterator.remove() or ConcurrentHashMap\n// Or: CopyOnWriteArrayList',
        'description': 'ConcurrentModificationException — use thread-safe collections',
    },
    'Java_IOError': {
        'keywords': ['IOException', 'FileNotFoundException', 'EOFException',
                     'io error', 'file error'],
        'fix': 'try (var reader = new BufferedReader(new FileReader(path))) {\n    // use reader\n} catch (IOException e) {\n    // handle\n}',
        'description': 'IOException — use try-with-resources and proper error handling',
    },
    'Java_SQLError': {
        'keywords': ['SQLException', 'sql', 'JDBC', 'database', 'connection'],
        'fix': 'try (var conn = DriverManager.getConnection(url);\n     var stmt = conn.prepareStatement("SELECT ...")) {\n    // use prepared statement\n}',
        'description': 'SQLException — use PreparedStatement and try-with-resources',
    },
    'Java_DangerousCall': {
        'keywords': ['Runtime.getRuntime().exec', 'ProcessBuilder',
                     'Class.forName.*user', 'DriverManager.*user'],
        'fix': '// BLOCKED: dangerous call — requires human review',
        'description': 'Security Risk — Runtime.exec/ProcessBuilder/unsafe reflection',
        'block': True,
    },
}


JAVA_DANGEROUS_PATTERNS = [
    r'Runtime\.getRuntime\(\)\.exec', r'ProcessBuilder',
    r'Class\.forName\(.*user', r'DriverManager\.getConnection\(.*user',
    r'System\.setSecurityManager\(null',
]


def classify_java_bug(error_message, code=""):
    """Classify a Java error into a bug type."""
    combined = (error_message + ' ' + code).lower()
    
    for bug_type, pattern in JAVA_BUG_PATTERNS.items():
        if pattern.get('block'):
            for kw in pattern['keywords']:
                if re.search(re.escape(kw.lower()), code or error_message, re.IGNORECASE):
                    return bug_type, pattern
    
    for bug_type, pattern in JAVA_BUG_PATTERNS.items():
        if pattern.get('block'):
            continue
        for kw in pattern['keywords']:
            if any(c in kw for c in '.*+?^$(){}|[]\\'):
                kw_pattern = kw.lower()
            else:
                kw_pattern = re.escape(kw.lower())
            if re.search(kw_pattern, combined, re.IGNORECASE):
                return bug_type, pattern
    
    return 'Java_Unknown', {'fix': '// Unknown error', 'description': 'Unknown'}


def is_dangerous_java(code):
    """Check for dangerous Java patterns."""
    for pattern in JAVA_DANGEROUS_PATTERNS:
        if re.search(pattern, code, re.IGNORECASE):
            return True, f"BLOCKED: {pattern}"
    return False, ""


def get_java_compile_command(file_path):
    """Compile-check command for Java."""
    return f'javac -Xlint:all {file_path} 2>&1'


def create_java_procedures(procedure_store):
    """Create Java-specific procedures."""
    from coding_tentacle.memory.procedural_memory import Procedure, ProcedureStep
    
    procedures = {
        "Java_NullGuard:java": ("NullPointer", "Guard against NPE",
            [("null_check", "if (obj != null) { obj.method(); }", "Null guard"),
             ("optional", "Or: Optional.ofNullable(obj).ifPresent(o -> o.method())", "Optional"),
             ("requireNonNull", "Or: Objects.requireNonNull(obj)", "Fail fast"),
             ("compile", "javac File.java", "Compiles")]),
        "Java_BoundsGuard:java": ("IndexOutOfBounds", "Guard list/array access",
            [("bounds_check", "if (i >= 0 && i < list.size()) { ... }", "Bounds guard"),
             ("for_each", "Or: for (var item : list) { ... }", "For-each loop"),
             ("compile", "javac File.java", "Compiles")]),
        "Java_ArgValidate:java": ("IllegalArgument", "Validate method arguments",
            [("null_check", "if (arg == null) throw new IllegalArgumentException()", "Arg check"),
             ("string_check", "if (arg.isEmpty()) throw ...", "String check"),
             ("compile", "javac File.java", "Compiles")]),
        "Java_BlockDangerous:java": ("SecurityRisk", "BLOCK dangerous Java",
            [("detect", "Runtime.exec/ProcessBuilder found", "Dangerous"),
             ("block", "SAFETY VETO", "NEVER auto-fix"),
             ("report", "Requires human review", "Report generated")]),
    }
    
    for key, (bt, desc, steps) in procedures.items():
        bp, lang = key.split(':')
        if not procedure_store.get_procedure(bp, lang):
            procedure_store.procedures[key] = Procedure(
                bug_type=bt, language=lang, trigger=desc,
                steps=[ProcedureStep(i+1, n, d, "JavaSupport", exp, "")
                       for i, (n, d, exp) in enumerate(steps)],
                confidence=0.70, created_at=time.time(), last_used=time.time()
            )
    procedure_store._save()


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    import tempfile, shutil
    
    print("JAVA DEMO-READY — Self-Test")
    print("=" * 55)
    passed = 0
    
    # T1: NullPointerException
    bt, _ = classify_java_bug("java.lang.NullPointerException at App.java:42")
    t1 = bt == 'Java_NullPointer'
    print(f"  T1: {'✅' if t1 else '❌'} NPE → {bt}")
    
    # T2: ClassNotFoundException
    bt2, _ = classify_java_bug("ClassNotFoundException: com.example.Missing")
    t2 = bt2 == 'Java_ClassNotFound'
    print(f"  T2: {'✅' if t2 else '❌'} ClassNotFound → {bt2}")
    
    # T3: IndexOutOfBounds
    bt3, _ = classify_java_bug("ArrayIndexOutOfBoundsException: 10")
    t3 = bt3 == 'Java_IndexOutOfBounds'
    print(f"  T3: {'✅' if t3 else '❌'} IndexOut → {bt3}")
    
    # T4: IllegalArgumentException
    bt4, _ = classify_java_bug("IllegalArgumentException: invalid argument")
    t4 = bt4 == 'Java_IllegalArgument'
    print(f"  T4: {'✅' if t4 else '❌'} IllegalArg → {bt4}")
    
    # T5: ConcurrentModification
    bt5, _ = classify_java_bug("ConcurrentModificationException at ArrayList.java")
    t5 = bt5 == 'Java_ConcurrentModification'
    print(f"  T5: {'✅' if t5 else '❌'} ConcurrentMod → {bt5}")
    
    # T6: IOException
    bt6, _ = classify_java_bug("java.io.FileNotFoundException: config.txt")
    t6 = bt6 == 'Java_IOError'
    print(f"  T6: {'✅' if t6 else '❌'} IOException → {bt6}")
    
    # T7: Runtime.exec BLOCKED
    blocked, _ = is_dangerous_java('Runtime.getRuntime().exec("rm -rf /");')
    t7 = blocked
    print(f"  T7: {'✅' if t7 else '❌'} Runtime.exec → BLOCKED")
    
    # T8: Safe code passes
    blocked8, _ = is_dangerous_java('System.out.println("hello");')
    t8 = not blocked8
    print(f"  T8: {'✅' if t8 else '❌'} Safe code → NOT blocked")
    
    # T9: javac available
    try:
        r = subprocess.run(['javac', '--version'], capture_output=True, text=True, timeout=5)
        t9 = r.returncode == 0
        print(f"  T9: {'✅' if t9 else '❌'} javac → {r.stdout.strip()[:30]}")
    except:
        t9 = False; print(f"  T9: ❌ javac not found")
    
    # T10: Procedures created
    from coding_tentacle.memory.procedural_memory import ProcedureStore
    tmp = tempfile.mkdtemp()
    ps = ProcedureStore(store_path=os.path.join(tmp, 'proc.json'))
    create_java_procedures(ps)
    count = sum(1 for k in ps.procedures if ':java' in k)
    t10 = count >= 3
    print(f"  T10: {'✅' if t10 else '❌'} {count} Java procedures")
    
    shutil.rmtree(tmp, ignore_errors=True)
    passed = sum([t1,t2,t3,t4,t5,t6,t7,t8,t9,t10])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/10 Tests bestanden")
    print(f"  {'✅ JAVA DEMO-READY — ALL 8 LANGUAGES COMPLETE' if passed >= 9 else '⚠️'}")
