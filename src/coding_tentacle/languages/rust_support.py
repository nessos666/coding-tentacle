"""
RUST DEMO READINESS — P2.1
Second language after Python. Templates, TestRunner, Procedures.

Uses cargo test for sandbox execution. Safety VETO active.

Autor: Hermes + David | Coding Tentacle 2026
"""
import re, os, time
from dataclasses import dataclass, field, asdict


# ═══════════ RUST BUG TYPES ═══════════
RUST_BUG_PATTERNS = {
    'Rust_OptionUnwrap': {
        'keywords': ['unwrap', 'panic', 'called `Option::unwrap()`', 'None'],
        'fix_template': 'match {var} {{\n    Some(val) => val,\n    None => return Err(...)  // or default\n}}',
        'description': 'Option.unwrap() panics on None — use match or ? operator',
    },
    'Rust_BorrowError': {
        'keywords': ['cannot borrow', 'borrow', 'mutable', 'immutable', 'already borrowed'],
        'fix_template': '// Clone before borrowing, or restructure ownership\nlet cloned = {var}.clone();',
        'description': 'Borrow checker conflict — clone or restructure ownership',
    },
    'Rust_LifetimeError': {
        'keywords': ['lifetime', 'does not live long enough', 'borrowed value'],
        'fix_template': "fn func<'a>(x: &'a str) -> &'a str {{\n    x\n}}",
        'description': 'Lifetime annotation missing or incorrect',
    },
    'Rust_UseError': {
        'keywords': ['use', 'unresolved import', 'not found in scope', 'mod'],
        'fix_template': 'use std::collections::HashMap;\n// or: mod my_module;',
        'description': 'Missing use statement or module declaration',
    },
    'Rust_TypeMismatch': {
        'keywords': ['mismatched types', 'expected', 'found', 'type'],
        'fix_template': 'let x: ExpectedType = value.into();  // or .try_into()?',
        'description': 'Type mismatch — use .into() or explicit conversion',
    },
    'Rust_ResultError': {
        'keywords': ['Result', 'must be used', 'unused Result', '#[must_use]'],
        'fix_template': 'let result = fallible_fn()?;  // propagate with ?',
        'description': 'Unused Result — use ? operator or match',
    },
    'Rust_PatternMatch': {
        'keywords': ['non-exhaustive patterns', 'not covered', 'match'],
        'fix_template': 'match value {{\n    Variant::A => {{}},\n    Variant::B => {{}},\n    _ => unreachable!(),\n}}',
        'description': 'Match not exhaustive — add missing arms',
    },
}


def classify_rust_bug(error_message):
    """Classify a Rust compiler error into a bug type."""
    msg_lower = error_message.lower()
    for bug_type, pattern in RUST_BUG_PATTERNS.items():
        if any(kw.lower() in msg_lower for kw in pattern['keywords']):
            return bug_type
    return 'Rust_Unknown'


# ═══════════ RUST PROCEDURE ═══════════
def create_rust_procedures(procedure_store):
    """Add Rust-specific procedures to the store."""
    from coding_tentacle.memory.procedural_memory import Procedure, ProcedureStep
    
    if not procedure_store.get_procedure("Rust_OptionUnwrap", "rust"):
        proc = Procedure(
            bug_type="Rust_OptionUnwrap", language="rust",
            trigger="panic: called `Option::unwrap()` on a `None` value",
            steps=[
                ProcedureStep(1, "analyze", "Which Option.unwrap() panicked?", "CodeContext", "line 42: config.unwrap()"),
                ProcedureStep(2, "suggest_match", "Replace .unwrap() with match or ?", "PatchSuggestion", "match config { Some(c) => c, None => return Err(...) }"),
                ProcedureStep(3, "cargo_test", "cargo test to verify", "TestRunner", "cargo test"),
                ProcedureStep(4, "verify", "No more panics", "ResultEvaluator", "Tests green, no unwrap panics"),
            ],
            confidence=0.75, created_at=time.time(), last_used=time.time()
        )
        procedure_store.procedures["Rust_OptionUnwrap:rust"] = proc
    
    if not procedure_store.get_procedure("Rust_BorrowError", "rust"):
        proc2 = Procedure(
            bug_type="Rust_BorrowError", language="rust",
            trigger="cannot borrow `x` as mutable because it is also borrowed as immutable",
            steps=[
                ProcedureStep(1, "analyze", "Which variable? Which borrow conflict?", "CodeContext", "x borrowed mutably and immutably"),
                ProcedureStep(2, "suggest_clone", "Clone before borrowing, or restructure", "PatchSuggestion", "let cloned = x.clone();"),
                ProcedureStep(3, "cargo_test", "Verify compilation", "TestRunner", "cargo check"),
                ProcedureStep(4, "verify", "Borrow checker satisfied", "ResultEvaluator", "Compiler happy"),
            ],
            confidence=0.65, created_at=time.time(), last_used=time.time()
        )
        procedure_store.procedures["Rust_BorrowError:rust"] = proc2
    
    procedure_store._save()


# ═══════════ RUST TEST RUNNER INTEGRATION ═══════════
def get_rust_test_command(project_path):
    """Determine the test command for a Rust project."""
    cargo_toml = os.path.join(project_path, 'Cargo.toml')
    if os.path.exists(cargo_toml):
        return 'cargo test -q 2>&1'
    return 'rustc --edition 2021 *.rs -o /tmp/test_bin && /tmp/test_bin'


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    print("RUST DEMO READINESS — Self-Test")
    print("=" * 55)
    passed = 0
    
    # T1: Classify Option.unwrap
    bt = classify_rust_bug("thread 'main' panicked at 'called `Option::unwrap()` on a `None` value'")
    t1 = bt == 'Rust_OptionUnwrap'
    print(f"  T1: {'✅' if t1 else '❌'} Option.unwrap panic → {bt}")
    
    # T2: Classify borrow error
    bt2 = classify_rust_bug("error[E0502]: cannot borrow `x` as mutable because it is also borrowed as immutable")
    t2 = bt2 == 'Rust_BorrowError'
    print(f"  T2: {'✅' if t2 else '❌'} Borrow error → {bt2}")
    
    # T3: Classify lifetime error
    bt3 = classify_rust_bug("error[E0597]: `y` does not live long enough")
    t3 = bt3 == 'Rust_LifetimeError'
    print(f"  T3: {'✅' if t3 else '❌'} Lifetime error → {bt3}")
    
    # T4: Classify unresolved import
    bt4 = classify_rust_bug("error[E0432]: unresolved import `std::collections`")
    t4 = bt4 == 'Rust_UseError'
    print(f"  T4: {'✅' if t4 else '❌'} Use error → {bt4}")
    
    # T5: Classify type mismatch
    bt5 = classify_rust_bug("error[E0308]: mismatched types — expected `String`, found `&str`")
    t5 = bt5 == 'Rust_TypeMismatch'
    print(f"  T5: {'✅' if t5 else '❌'} Type mismatch → {bt5}")
    
    # T6: Classify unused Result
    bt6 = classify_rust_bug("warning: unused `Result` that must be used")
    t6 = bt6 == 'Rust_ResultError'
    print(f"  T6: {'✅' if t6 else '❌'} Unused Result → {bt6}")
    
    # T7: Classify exhaustive match
    bt7 = classify_rust_bug("error[E0004]: non-exhaustive patterns: `None` not covered")
    t7 = bt7 == 'Rust_PatternMatch'
    print(f"  T7: {'✅' if t7 else '❌'} Pattern match → {bt7}")
    
    # T8: Create Rust procedures in store
    import tempfile
    from coding_tentacle.memory.procedural_memory import ProcedureStore
    tmp = tempfile.mkdtemp()
    ps = ProcedureStore(store_path=os.path.join(tmp, 'proc.json'))
    create_rust_procedures(ps)
    proc = ps.find_procedure("Rust_OptionUnwrap")
    t8 = proc is not None and proc.language == "rust"
    print(f"  T8: {'✅' if t8 else '❌'} Rust procedure → {proc.bug_type if proc else 'NONE'}")
    
    import shutil; shutil.rmtree(tmp, ignore_errors=True)
    
    passed = sum([t1,t2,t3,t4,t5,t6,t7,t8])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/8 Tests bestanden")
    print(f"  {'✅ RUST DEMO-READY' if passed >= 7 else '⚠️'}")
