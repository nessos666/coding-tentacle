"""
RUBY DEMO READINESS — P2.3
Fourth language. Ruby 3.2 installed. Templates + Procedures + Safety.

Safety VETO: eval, system(), backticks, YAML.load ALWAYS blocked.

Autor: Hermes + David | Coding Tentacle 2026
"""
import re, time, os


# ═══════════ RUBY BUG PATTERNS ═══════════
RUBY_BUG_PATTERNS = {
    'Ruby_NoMethodNil': {
        'keywords': ['NoMethodError', 'nil', 'NilClass', 'undefined method'],
        'fix': 'value&.method  # safe navigation operator (Ruby 2.3+)',
        'description': 'NoMethodError on nil — use &. or check nil first',
    },
    'Ruby_LoadError': {
        'keywords': ['LoadError', 'require', 'cannot load', 'no such file'],
        'fix': "require 'gem_name' rescue nil\n# or: gem 'gem_name' in Gemfile",
        'description': 'LoadError — gem not installed or wrong path',
    },
    'Ruby_NameError': {
        'keywords': ['NameError', 'undefined local variable', 'undefined method'],
        'fix': '# Check variable scope or method definition',
        'description': 'NameError — undefined variable or method',
    },
    'Ruby_ArgumentError': {
        'keywords': ['ArgumentError', 'wrong number of arguments', 'given'],
        'fix': 'def method(arg1, arg2 = nil, **opts)  # flexible signature',
        'description': 'ArgumentError — wrong number or type of arguments',
    },
    'Ruby_TypeError': {
        'keywords': ['TypeError', 'no implicit conversion', "can't convert"],
        'fix': 'value.to_s  # explicit conversion',
        'description': 'TypeError — no implicit conversion between types',
    },
    'Ruby_SyntaxError': {
        'keywords': ['SyntaxError', 'syntax error', 'unexpected'],
        'fix': '# Check Ruby version compatibility and syntax',
        'description': 'SyntaxError — invalid Ruby syntax',
    },
    'Ruby_KeyError': {
        'keywords': ['KeyError', 'key not found', 'Hash'],
        'fix': "hash.fetch(:key, default)  # safe key access with default",
        'description': 'KeyError — use fetch with default instead of []',
    },
    'Ruby_FrozenError': {
        'keywords': ['FrozenError', "can't modify frozen", 'frozen'],
        'fix': 'value = value.dup  # create mutable copy',
        'description': 'FrozenError — trying to modify frozen object',
    },
    'Ruby_DangerousEval': {
        'keywords': ['eval(', 'system(', 'exec(', 'YAML.load', 'Marshal.load',
                     '%x{'],
        'fix': '# BLOCKED: dangerous method — requires human review',
        'description': 'Security Risk — eval/system/YAML.load detected',
        'block': True,
    },
}


# ═══════════ RUBY SAFETY BLOCKLIST ═══════════
RUBY_SAFETY_BLOCKLIST = [
    r'\beval\s*\(', r'\bsystem\s*\(', r'\bexec\s*\(', r'`[^`]*`',
    r'%x\{', r'YAML\.load', r'Marshal\.load', r'File\.delete\s*\(',
    r'FileUtils\.rm', r'Process\.spawn\s*\(', r'Kernel\.send\s*\(',
    r'\.constantize', r'\.classify', r'\.safe_constantize',
]


def classify_ruby_bug(error_message, code=""):
    """Classify a Ruby error into a bug type."""
    combined = (error_message + ' ' + code).lower()
    
    # Check dangerous first
    for bug_type, pattern in RUBY_BUG_PATTERNS.items():
        if pattern.get('block'):
            for kw in pattern['keywords']:
                if re.search(re.escape(kw).lower() if '\\' not in kw else kw.lower(), 
                           code or error_message, re.IGNORECASE):
                    return bug_type, pattern
    
    # Check error patterns
    for bug_type, pattern in RUBY_BUG_PATTERNS.items():
        if pattern.get('block'):
            continue
        for kw in pattern['keywords']:
            if re.search(re.escape(kw.lower()), combined):
                return bug_type, pattern
    
    return 'Ruby_Unknown', {'fix': '# Unknown Ruby error', 'description': 'Unknown'}


def is_dangerous_ruby(code):
    """Check if Ruby code contains dangerous methods. Returns (blocked, reason)."""
    for pattern in RUBY_SAFETY_BLOCKLIST:
        if re.search(pattern, code, re.IGNORECASE):
            return True, f"BLOCKED: {pattern}"
    return False, ""


def create_ruby_procedures(procedure_store):
    """Create Ruby-specific procedures."""
    from coding_tentacle.memory.procedural_memory import Procedure, ProcedureStep
    
    procedures = {
        "Ruby_NilGuard:ruby": ("NoMethodNil", "Guard against nil",
            [("check", "Is variable nil?", "value = nil"),
             ("safe_nav", "Use &. operator", "value&.method"),
             ("or_guard", "Or: return if value.nil?", "return if value.nil?")]),
        "Ruby_RequireFix:ruby": ("LoadError", "Fix missing require",
            [("check_gemfile", "Gem installed?", "Gemfile or gemspec"),
             ("add_require", "Add require statement", "require 'gem_name'"),
             ("rescue_load", "Graceful fallback", "require 'gem' rescue nil")]),
        "Ruby_KeyAccess:ruby": ("KeyError", "Safe hash access",
            [("fetch_default", "Use fetch with default", "hash.fetch(:key, default)"),
             ("dig", "Or: hash.dig(:key)", "hash.dig(:nested, :key)")]),
        "Ruby_BlockDangerous:ruby": ("SecurityRisk", "BLOCK dangerous methods",
            [("detect", "Detect eval/system/backticks", "eval(user_input)"),
             ("block", "SAFETY VETO", "NEVER auto-fix"),
             ("report", "Requires human review", "Report generated")]),
    }
    
    for key, (bt, desc, steps) in procedures.items():
        bp, lang = key.split(':')
        if not procedure_store.get_procedure(bp, lang):
            procedure_store.procedures[key] = Procedure(
                bug_type=bt, language=lang, trigger=desc,
                steps=[ProcedureStep(i+1, n, d, "RubySupport", exp, "")
                       for i, (n, d, exp) in enumerate(steps)],
                confidence=0.72, created_at=time.time(), last_used=time.time()
            )
    
    procedure_store._save()


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    import tempfile, shutil
    
    print("RUBY DEMO READINESS — Self-Test")
    print("=" * 55)
    passed = 0
    
    # T1: NoMethodError on nil
    bt, _ = classify_ruby_bug("NoMethodError: undefined method `name' for nil:NilClass")
    t1 = bt == 'Ruby_NoMethodNil'
    print(f"  T1: {'✅' if t1 else '❌'} NoMethodNil → {bt}")
    
    # T2: LoadError
    bt2, _ = classify_ruby_bug("LoadError: cannot load such file -- some_gem")
    t2 = bt2 == 'Ruby_LoadError'
    print(f"  T2: {'✅' if t2 else '❌'} LoadError → {bt2}")
    
    # T3: ArgumentError
    bt3, _ = classify_ruby_bug("ArgumentError: wrong number of arguments (given 1, expected 2)")
    t3 = bt3 == 'Ruby_ArgumentError'
    print(f"  T3: {'✅' if t3 else '❌'} ArgumentError → {bt3}")
    
    # T4: KeyError
    bt4, _ = classify_ruby_bug("KeyError: key not found: :name")
    t4 = bt4 == 'Ruby_KeyError'
    print(f"  T4: {'✅' if t4 else '❌'} KeyError → {bt4}")
    
    # T5: eval() BLOCKED
    blocked, _ = is_dangerous_ruby('eval(user_input)')
    t5 = blocked
    print(f"  T5: {'✅' if t5 else '❌'} eval() → BLOCKED")
    
    # T6: system() BLOCKED
    blocked6, _ = is_dangerous_ruby('system("rm -rf /")')
    t6 = blocked6
    print(f"  T6: {'✅' if t6 else '❌'} system() → BLOCKED")
    
    # T7: YAML.load BLOCKED
    blocked7, _ = is_dangerous_ruby('YAML.load(untrusted_data)')
    t7 = blocked7
    print(f"  T7: {'✅' if t7 else '❌'} YAML.load → BLOCKED")
    
    # T8: Safe code passes
    blocked8, _ = is_dangerous_ruby('puts "hello world"')
    t8 = not blocked8
    print(f"  T8: {'✅' if t8 else '❌'} Safe code → NOT blocked")
    
    # T9: Procedures created
    from coding_tentacle.memory.procedural_memory import ProcedureStore
    tmp = tempfile.mkdtemp()
    ps = ProcedureStore(store_path=os.path.join(tmp, 'proc.json'))
    create_ruby_procedures(ps)
    count = sum(1 for k in ps.procedures if ':ruby' in k)
    t9 = count >= 3
    print(f"  T9: {'✅' if t9 else '❌'} {count} Ruby procedures")
    
    shutil.rmtree(tmp, ignore_errors=True)
    passed = sum([t1,t2,t3,t4,t5,t6,t7,t8,t9])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/9 Tests bestanden")
    print(f"  {'✅ RUBY DEMO-READY' if passed >= 8 else '⚠️'}")
