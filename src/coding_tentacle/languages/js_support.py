"""
JAVASCRIPT / TYPESCRIPT DEMO READINESS — P3.0
Seventh language family. Node 22 installed. Templates + Safety.

Safety VETO: eval(), Function(), child_process.exec ALWAYS blocked.

Autor: Hermes + David | Coding Tentacle 2026
"""
import re, time, os


# ═══════════ JS/TS BUG PATTERNS ═══════════
JS_BUG_PATTERNS = {
    'JS_UndefinedVar': {
        'keywords': ['undefined', 'is not defined', 'not defined', 'undefined var'],
        'fix': "const value = variable ?? defaultValue;  // nullish coalescing",
        'description': 'Undefined variable — use ?? or check typeof !== "undefined"',
    },
    'JS_NullUndefined': {
        'keywords': ['null', 'cannot read propert', 'of null', 'of undefined',
                     'TypeError.*null', 'TypeError.*undefined'],
        'fix': 'const result = obj?.property?.nested;  // optional chaining',
        'description': 'Null/undefined — use optional chaining (?.) or null check',
    },
    'JS_TypeError': {
        'keywords': ['TypeError', 'is not a function', 'not a function',
                     'cannot call', 'is not iterable'],
        'fix': "if (typeof value === 'function') value();  // type guard",
        'description': 'TypeError — add typeof check before usage',
    },
    'JS_ImportError': {
        'keywords': ['cannot find module', 'module not found', 'import error',
                     'cannot resolve', 'ERR_MODULE_NOT_FOUND'],
        'fix': "// Check: npm install package\n// Or: import { x } from './correct-path.js'",
        'description': 'Import error — check package installation or path',
    },
    'JS_AsyncAwait': {
        'keywords': ['unhandled promise', 'Promise', 'async', 'await',
                     '.then(', '.catch('],
        'fix': 'try {\n  const result = await asyncFn();\n} catch (err) {\n  console.error(err);\n}',
        'description': 'Unhandled promise — use try/catch with await or .catch()',
    },
    'JS_ReactHookError': {
        'keywords': ['hooks', 'useEffect', 'useState', 'useCallback',
                     'rules of hooks', 'rendered fewer hooks'],
        'fix': '// Hooks must be called at top level of component\n// Not inside conditions or loops',
        'description': 'React hook error — check rules of hooks',
    },
    'JS_StateMutation': {
        'keywords': ['mutate', 'mutation', 'state', 'setState',
                     'immutable', 'spread'],
        'fix': 'setState(prev => ({ ...prev, key: newValue }));  // immutable update',
        'description': 'State mutation — use immutable updates (spread/immer)',
    },
    'JS_TypeScriptError': {
        'keywords': ['type .* is not assignable', 'property .* does not exist',
                     'tsc', 'TypeScript.*error'],
        'fix': 'const value: ExpectedType = input as ExpectedType;',
        'description': 'TypeScript type error — fix annotation or assertion',
    },
    'JS_NetworkError': {
        'keywords': ['fetch', 'network', 'ECONNREFUSED', 'ENOTFOUND',
                     'timeout', 'AbortController'],
        'fix': 'const controller = new AbortController();\nfetch(url, { signal: controller.signal });',
        'description': 'Network error — add timeout via AbortController',
    },
    'JS_DangerousEval': {
        'keywords': ['eval(', 'Function(', 'new Function', 'child_process',
                     'exec(', 'execSync(', 'innerHTML', 'dangerouslySetInnerHTML',
                     'document.write('],
        'fix': '// BLOCKED: dangerous JS — requires human review',
        'description': 'Security Risk — eval/Function/child_process/innerHTML',
        'block': True,
    },
}


JS_DANGEROUS_PATTERNS = [
    r'\beval\s*\(', r'\bFunction\s*\(', r'new\s+Function\s*\(',
    r'child_process', r'child_process\.exec', r'child_process\)\.exec',
    r'\.innerHTML\s*=', r'dangerouslySetInnerHTML',
    r'document\.write\s*\(', r'fs\.writeFile.*user',
    r'shelljs\.exec', r'execSync\s*\(', r'exec\(\s*[\'\"].*user',
]


def classify_js_bug(error_message, code=""):
    """Classify a JS/TS error into a bug type."""
    combined = (error_message + ' ' + code).lower()
    
    for bug_type, pattern in JS_BUG_PATTERNS.items():
        if pattern.get('block'):
            for kw in pattern['keywords']:
                if re.search(re.escape(kw), code or error_message, re.IGNORECASE):
                    return bug_type, pattern
    
    for bug_type, pattern in JS_BUG_PATTERNS.items():
        if pattern.get('block'):
            continue
        for kw in pattern['keywords']:
            if re.search(re.escape(kw.lower()), combined, re.IGNORECASE):
                return bug_type, pattern
    
    return 'JS_Unknown', {'fix': '// Unknown error', 'description': 'Unknown'}


def is_dangerous_js(code):
    """Check for dangerous JS patterns."""
    for pattern in JS_DANGEROUS_PATTERNS:
        if re.search(pattern, code, re.IGNORECASE):
            return True, f"BLOCKED: {pattern}"
    return False, ""


def create_js_procedures(procedure_store):
    """Create JS/TS-specific procedures."""
    from coding_tentacle.memory.procedural_memory import Procedure, ProcedureStep
    
    procedures = {
        "JS_NullGuard:javascript": ("NullUndefined", "Guard against null/undefined",
            [("optional_chaining", "Use ?. operator", "obj?.prop?.nested"),
             ("nullish_coalescing", "Use ?? for defaults", "const v = val ?? 'default'"),
             ("typeof_check", "Check before access", "if (x != null) { x.method() }")]),
        "JS_AsyncFix:javascript": ("AsyncAwait", "Fix unhandled promises",
            [("try_catch", "Wrap await in try/catch", "try { await fn() } catch(e) {}"),
             ("catch_chain", "Or use .catch()", ".catch(err => handle(err))"),
             ("test", "npm test", "Tests pass")]),
        "JS_ImportFix:javascript": ("ImportError", "Fix missing imports",
            [("check_package", "npm install package", "package.json check"),
             ("fix_path", "Correct import path", "./relative/path.js"),
             ("test", "npm test", "Tests pass")]),
        "JS_BlockDangerous:javascript": ("SecurityRisk", "BLOCK dangerous JS",
            [("detect", "eval/Function/child_process found", "Dangerous"),
             ("block", "SAFETY VETO", "NEVER auto-fix"),
             ("report", "Requires human review", "Report generated")]),
    }
    
    for key, (bt, desc, steps) in procedures.items():
        bp, lang = key.split(':')
        if not procedure_store.get_procedure(bp, lang):
            procedure_store.procedures[key] = Procedure(
                bug_type=bt, language=lang, trigger=desc,
                steps=[ProcedureStep(i+1, n, d, "JSSupport", exp, "")
                       for i, (n, d, exp) in enumerate(steps)],
                confidence=0.70, created_at=time.time(), last_used=time.time()
            )
    procedure_store._save()


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    import tempfile, shutil
    
    print("JS/TS DEMO READINESS — Self-Test")
    print("=" * 55)
    passed = 0
    
    # T1: undefined variable
    bt, _ = classify_js_bug("ReferenceError: x is not defined")
    t1 = bt == 'JS_UndefinedVar'
    print(f"  T1: {'✅' if t1 else '❌'} undefined → {bt}")
    
    # T2: null property access
    bt2, _ = classify_js_bug("TypeError: Cannot read properties of null (reading 'name')")
    t2 = bt2 == 'JS_NullUndefined'
    print(f"  T2: {'✅' if t2 else '❌'} null access → {bt2}")
    
    # T3: import error
    bt3, _ = classify_js_bug("Error: Cannot find module 'nonexistent-package'")
    t3 = bt3 == 'JS_ImportError'
    print(f"  T3: {'✅' if t3 else '❌'} import → {bt3}")
    
    # T4: unhandled promise
    bt4, _ = classify_js_bug("UnhandledPromiseRejectionWarning: Error: something went wrong")
    t4 = bt4 == 'JS_AsyncAwait'
    print(f"  T4: {'✅' if t4 else '❌'} promise → {bt4}")
    
    # T5: TypeScript error
    bt5, _ = classify_js_bug("TS2322: Type 'string' is not assignable to type 'number'")
    t5 = bt5 == 'JS_TypeScriptError'
    print(f"  T5: {'✅' if t5 else '❌'} TS error → {bt5}")
    
    # T6: eval() BLOCKED
    blocked, _ = is_dangerous_js('eval(userInput);')
    t6 = blocked
    print(f"  T6: {'✅' if t6 else '❌'} eval → BLOCKED")
    
    # T7: child_process BLOCKED
    blocked7, _ = is_dangerous_js('require("child_process").exec(userInput);')
    t7 = blocked7
    print(f"  T7: {'✅' if t7 else '❌'} child_process → BLOCKED")
    
    # T8: safe code passes
    blocked8, _ = is_dangerous_js('console.log("hello");')
    t8 = not blocked8
    print(f"  T8: {'✅' if t8 else '❌'} Safe code → NOT blocked")
    
    # T9: node available
    import subprocess
    try:
        r = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
        t9 = r.returncode == 0
        print(f"  T9: {'✅' if t9 else '❌'} node → {r.stdout.strip()}")
    except:
        t9 = False
    
    # T10: Procedures created
    from coding_tentacle.memory.procedural_memory import ProcedureStore
    tmp = tempfile.mkdtemp()
    ps = ProcedureStore(store_path=os.path.join(tmp, 'proc.json'))
    create_js_procedures(ps)
    count = sum(1 for k in ps.procedures if ':javascript' in k)
    t10 = count >= 3
    print(f"  T10: {'✅' if t10 else '❌'} {count} JS procedures")
    
    shutil.rmtree(tmp, ignore_errors=True)
    passed = sum([t1,t2,t3,t4,t5,t6,t7,t8,t9,t10])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/10 Tests bestanden")
    print(f"  {'✅ JS/TS DEMO-READY' if passed >= 9 else '⚠️'}")
