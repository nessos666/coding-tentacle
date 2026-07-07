"""
C++ DEMO READINESS — P2.4
Fifth language. GCC + CMake installed. Templates + Safety.

Safety VETO: system(), popen(), strcpy(), gets() ALWAYS blocked.

Autor: Hermes + David | Coding Tentacle 2026
"""
import re, time, os, subprocess


# ═══════════ C++ BUG PATTERNS ═══════════
CPP_BUG_PATTERNS = {
    'Cpp_NullPointer': {
        'keywords': ['null', 'nullptr', 'segfault', 'segmentation fault',
                     'dereference', 'null pointer'],
        'fix': 'if (ptr != nullptr) { ptr->method(); }  // guard before dereference',
        'description': 'Null pointer dereference — add guard or use std::optional',
    },
    'Cpp_MissingInclude': {
        'keywords': ['not declared', 'no member named', 'incomplete type',
                     'forward declaration', 'undefined reference', 'has not been'],
        'fix': '#include <header>  // missing header',
        'description': 'Missing include or forward declaration',
    },
    'Cpp_TypeMismatch': {
        'keywords': ['cannot convert', 'no matching function', 'type mismatch',
                     'invalid cast', 'reinterpret_cast'],
        'fix': 'auto value = static_cast<TargetType>(source);  // explicit cast',
        'description': 'Type mismatch — use explicit cast or fix signature',
    },
    'Cpp_BufferOverflow': {
        'keywords': ['buffer', 'overflow', 'out of bounds', 'stack overflow',
                     'heap overflow', 'address sanitizer'],
        'fix': 'std::vector<int> buf(size);  // safe container instead of raw array\n// or: std::array<int, N> buf;',
        'description': 'Buffer overflow — use std::vector or std::array',
    },
    'Cpp_UseAfterFree': {
        'keywords': ['use after free', 'dangling', 'freed', 'deleted',
                     'double free', 'use-after-free', 'heap-use-after'],
        'fix': 'ptr = nullptr;  // after delete\n// or: use std::unique_ptr / std::shared_ptr',
        'description': 'Use-after-free — use smart pointers (unique_ptr/shared_ptr)',
    },
    'Cpp_MemoryLeak': {
        'keywords': ['memory leak', 'leak', 'not freed', 'not deleted',
                     'valgrind'],
        'fix': 'std::unique_ptr<T> ptr = std::make_unique<T>();  // auto-cleanup',
        'description': 'Memory leak — use RAII and smart pointers',
    },
    'Cpp_LinkerError': {
        'keywords': ['linker', 'undefined reference', 'multiple definition',
                     'ld returned'],
        'fix': '# Check CMakeLists.txt: target_link_libraries(target lib)\n// or: add missing .cpp to build',
        'description': 'Linker error — missing library or object file',
    },
    'Cpp_RaceCondition': {
        'keywords': ['race', 'thread', 'data race', 'mutex', 'lock',
                     'concurrent', 'not thread-safe'],
        'fix': 'std::lock_guard<std::mutex> lock(mtx);  // thread-safe access',
        'description': 'Race condition — use std::mutex or std::atomic',
    },
    'Cpp_DangerousCall': {
        'keywords': ['system(', 'popen(', 'exec', 'strcpy', 'strcat',
                     'gets(', 'sprintf('],
        'fix': '// BLOCKED: dangerous function — requires human review',
        'description': 'Security Risk — system/strcpy/gets detected',
        'block': True,
    },
}


# ═══════════ C++ SAFETY BLOCKLIST ═══════════
CPP_SAFETY_BLOCKLIST = [
    r'\bsystem\s*\(', r'\bpopen\s*\(', r'\bexecl\w*\s*\(', r'\bexecv\w*\s*\(',
    r'\bstrcpy\s*\(', r'\bstrcat\s*\(', r'\bgets\s*\(', r'\bsprintf\s*\(',
    r'#include\s*<stdlib\.h>.*system', r'delete\[\].*\w+;.*delete\[\]',
    r'new\s+\w+.*;.*delete\s+\w+;.*\w+\s*\(',  # use-after-free pattern
]


def classify_cpp_bug(error_message, code=""):
    """Classify a C++ error into a bug type."""
    combined = (error_message + ' ' + code).lower()
    
    # Check dangerous first
    for bug_type, pattern in CPP_BUG_PATTERNS.items():
        if pattern.get('block'):
            for kw in pattern['keywords']:
                kw_clean = kw.replace('(', r'\(').replace(')', r'\)')
                if re.search(kw_clean, code or error_message, re.IGNORECASE):
                    return bug_type, pattern
    
    for bug_type, pattern in CPP_BUG_PATTERNS.items():
        if pattern.get('block'):
            continue
        for kw in pattern['keywords']:
            if kw.lower() in combined:
                return bug_type, pattern
    
    return 'Cpp_Unknown', {'fix': '// Unknown error', 'description': 'Unknown'}


def is_dangerous_cpp(code):
    """Check if C++ code contains dangerous functions."""
    for pattern in CPP_SAFETY_BLOCKLIST:
        if re.search(pattern, code, re.IGNORECASE):
            return True, f"BLOCKED: {pattern}"
    return False, ""


def get_cpp_syntax_check_command(file_path):
    """Compile-check command for C++."""
    return f'g++ -std=c++17 -fsyntax-only -Wall -Wextra {file_path} 2>&1'


def create_cpp_procedures(procedure_store):
    """Create C++-specific procedures."""
    from coding_tentacle.memory.procedural_memory import Procedure, ProcedureStep
    
    procedures = {
        "Cpp_NullGuard:cpp": ("NullPointer", "Guard against nullptr",
            [("check", "Where is nullptr dereferenced?", "ptr->method()"),
             ("add_guard", "if (ptr != nullptr) { ptr->method(); }", "Guard clause"),
             ("smart_ptr", "Or: std::unique_ptr<T> ptr = ...", "Smart pointer"),
             ("compile", "g++ -fsyntax-only", "Compile check passes")]),
        "Cpp_IncludeFix:cpp": ("MissingInclude", "Add missing #include",
            [("identify", "Which header is missing?", "std::vector not found"),
             ("add_include", "#include <vector>", "Header added"),
             ("compile", "g++ -fsyntax-only", "Compile check passes")]),
        "Cpp_SafeBuffer:cpp": ("BufferOverflow", "Replace raw array with vector",
            [("identify", "Which raw array?", "int buf[100];"),
             ("replace", "std::vector<int> buf(100);", "Safe container"),
             ("at_method", "Or: buf.at(i) for bounds-checked access", "Bounds check")]),
        "Cpp_SmartPtr:cpp": ("MemoryLeak/UseAfterFree", "Use smart pointers",
            [("identify", "Raw pointer with new/delete?", "T* ptr = new T();"),
             ("replace", "auto ptr = std::make_unique<T>();", "RAII"),
             ("compile", "g++ -fsyntax-only", "Compile check passes")]),
        "Cpp_BlockDangerous:cpp": ("SecurityRisk", "BLOCK dangerous C functions",
            [("detect", "system/strcpy/gets found", "system(user_input)"),
             ("block", "SAFETY VETO", "NEVER auto-fix"),
             ("report", "Requires human review", "Report generated")]),
    }
    
    for key, (bt, desc, steps) in procedures.items():
        bp, lang = key.split(':')
        if not procedure_store.get_procedure(bp, lang):
            procedure_store.procedures[key] = Procedure(
                bug_type=bt, language=lang, trigger=desc,
                steps=[ProcedureStep(i+1, n, d, "CppSupport", exp, "")
                       for i, (n, d, exp) in enumerate(steps)],
                confidence=0.70, created_at=time.time(), last_used=time.time()
            )
    
    procedure_store._save()


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    import tempfile, shutil
    
    print("C++ DEMO READINESS — Self-Test")
    print("=" * 55)
    passed = 0
    
    # T1: NullPointer
    bt, _ = classify_cpp_bug("Segmentation fault (core dumped) at null.cpp:42")
    t1 = bt == 'Cpp_NullPointer'
    print(f"  T1: {'✅' if t1 else '❌'} NullPointer → {bt}")
    
    # T2: Missing include
    bt2, _ = classify_cpp_bug("error: 'std::vector' has not been declared")
    t2 = bt2 == 'Cpp_MissingInclude'
    print(f"  T2: {'✅' if t2 else '❌'} Missing include → {bt2}")
    
    # T3: TypeMismatch
    bt3, _ = classify_cpp_bug("error: cannot convert 'std::string' to 'int'")
    t3 = bt3 == 'Cpp_TypeMismatch'
    print(f"  T3: {'✅' if t3 else '❌'} Type mismatch → {bt3}")
    
    # T4: BufferOverflow
    bt4, _ = classify_cpp_bug("AddressSanitizer: heap-buffer-overflow on address")
    t4 = bt4 == 'Cpp_BufferOverflow'
    print(f"  T4: {'✅' if t4 else '❌'} Buffer overflow → {bt4}")
    
    # T5: UseAfterFree
    bt5, _ = classify_cpp_bug("AddressSanitizer: heap-use-after-free")
    t5 = bt5 == 'Cpp_UseAfterFree'
    print(f"  T5: {'✅' if t5 else '❌'} Use-after-free → {bt5}")
    
    # T6: system() BLOCKED
    blocked, _ = is_dangerous_cpp('system("rm -rf /");')
    t6 = blocked
    print(f"  T6: {'✅' if t6 else '❌'} system() → BLOCKED")
    
    # T7: strcpy BLOCKED
    blocked7, _ = is_dangerous_cpp('strcpy(dest, user_input);')
    t7 = blocked7
    print(f"  T7: {'✅' if t7 else '❌'} strcpy → BLOCKED")
    
    # T8: Safe code passes
    blocked8, _ = is_dangerous_cpp('std::cout << "hello";')
    t8 = not blocked8
    print(f"  T8: {'✅' if t8 else '❌'} Safe code → NOT blocked")
    
    # T9: Compile check command
    cmd = get_cpp_syntax_check_command('test.cpp')
    t9 = 'g++' in cmd and 'fsyntax-only' in cmd
    print(f"  T9: {'✅' if t9 else '❌'} Compile cmd → {cmd}")
    
    # T10: Procedures created
    from coding_tentacle.memory.procedural_memory import ProcedureStore
    tmp = tempfile.mkdtemp()
    ps = ProcedureStore(store_path=os.path.join(tmp, 'proc.json'))
    create_cpp_procedures(ps)
    count = sum(1 for k in ps.procedures if ':cpp' in k)
    t10 = count >= 4
    print(f"  T10: {'✅' if t10 else '❌'} {count} C++ procedures")
    
    shutil.rmtree(tmp, ignore_errors=True)
    passed = sum([t1,t2,t3,t4,t5,t6,t7,t8,t9,t10])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/10 Tests bestanden")
    print(f"  {'✅ C++ DEMO-READY' if passed >= 9 else '⚠️'}")
