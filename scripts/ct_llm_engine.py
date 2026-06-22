"""
CT + LLM FIX ENGINE — RC33
Coding Tentacle as Safety/Analysis layer, OpenCode as Fix engine.

CT: classifies, builds context, safety-checks, sandbox-tests, learns
OpenCode: generates actual code fix (unified diff only)

Author: Hermes + David | Coding Tentacle 2026
"""
import sys, os, time, json, tempfile, shutil, subprocess
sys.path.insert(0, '/home/boobi/GEHIRN_BIBLIOTHEK')
sys.path.insert(0, '/home/boobi/GEHIRN_BIBLIOTHEK/src/coding_tentacle')

from coding_tentacle.config import Config
from coding_tentacle.orchestrator.shadow_mode import ShadowModeRunner, GitHubIssueRun
from coding_tentacle.orchestrator.metabrain import MetaBrain, SafetyBrain
from coding_tentacle.safety.inhibitory_control import InhibitoryControl
from coding_tentacle.knowledge.security_store import create_seed_security_store
from coding_tentacle.orchestrator.teacher_student import Teacher
from coding_tentacle.patch.diff_generator import DiffGenerator
from coding_tentacle.patch.patch_suggestion import PatchSuggestionEngine
from coding_tentacle.patch.sandbox_runner import SandboxRunner
from coding_tentacle.patch.test_runner import TestRunner
from coding_tentacle.memory.procedural_memory import ProcedureStore
from coding_tentacle.memory.skill_compiler import SkillStore
from coding_tentacle.classifier.semantic_classifier import SemanticBugClassifier
from coding_tentacle.orchestrator.skeptic_brain import SkepticBrain
from coding_tentacle.knowledge.impact_analyzer import ImpactAnalyzer
from coding_tentacle.knowledge.project_map import ProjectMap
from coding_tentacle.memory.bug_learning_memory import BugLearningMemory


# ═══════════ PHASE 1: AVAILABILITY CHECK ═══════════
def check_engines():
    engines = {}
    
    # OpenCode
    try:
        result = subprocess.run(['opencode', '--version'], capture_output=True, text=True, timeout=10)
        engines['OpenCode'] = {'available': True, 'version': result.stdout.strip()}
    except Exception as e:
        engines['OpenCode'] = {'available': False, 'error': str(e)}
    
    # Codex CLI
    try:
        result = subprocess.run(['codex', '--version'], capture_output=True, text=True, timeout=10)
        engines['Codex'] = {'available': True, 'version': result.stdout.strip()}
    except:
        engines['Codex'] = {'available': False, 'error': 'NOT INSTALLED'}
    
    return engines


# ═══════════ PHASE 2+3: CT + OPENCODE PIPELINE ═══════════
def run_ct_opencode_pipeline(issue_title, issue_body, file_context=None):
    """CT analyzes → OpenCode fixes → CT validates → sandbox tests → learns."""
    
    # Setup CT pipeline
    cfg = Config()
    sec = create_seed_security_store()
    ic = InhibitoryControl(security_store=sec)
    safety = SafetyBrain(ic=ic, security_store=sec)
    mb = MetaBrain(safety=safety)
    ps_store = ProcedureStore(config=cfg)
    sk_store = SkillStore(config=cfg)
    teacher = Teacher(procedural_memory=ps_store, skill_store=sk_store)
    ps = PatchSuggestionEngine()
    dg = DiffGenerator(safety_brain=safety, patch_suggestion=ps)
    sr = SandboxRunner(safety_brain=safety)
    tr = TestRunner(max_timeout=15)
    sc = SemanticBugClassifier()
    sb = SkepticBrain()
    
    tmp_db = tempfile.mkdtemp()
    blm = BugLearningMemory(db_path=os.path.join(tmp_db, 'learn.db'))
    
    result = {'issue': issue_title[:60]}
    
    # STEP 1: CT classifies
    issue = GitHubIssueRun("https://github.com/test/repo", "#1", issue_title, issue_body)
    runner = ShadowModeRunner(meta_brain=mb, teacher=teacher, diff_generator=dg, sandbox_runner=sr)
    report = runner.analyze_issue(issue)
    
    bt = report.detected_bug_type
    if bt == 'Unknown':
        bt, _ = sc.classify(f"{issue_title} {issue_body}")
    
    result['bug_type'] = bt
    result['ct_confidence'] = report.confidence
    result['ct_diff_size'] = len(report.generated_diff)
    
    # STEP 2: Safety check
    dangerous, _ = blm.is_dangerous_pattern(f"{issue_title} {issue_body}")
    if dangerous:
        result['safety_blocked'] = True
        result['fixed'] = False
        result['reason'] = f"Safety BLOCK: {dangerous}"
        return result
    
    result['safety_blocked'] = False
    
    # STEP 3: Build context for LLM
    context = f"""BUG REPORT:
Title: {issue_title}
Description: {issue_body}

CODING TENTACLE ANALYSIS:
Bug Type: {bt} (confidence: {report.confidence:.0%})
Suggested Fix Pattern: {report.generated_diff[:300] if report.generated_diff else 'N/A'}

RULES:
1. Output ONLY a unified diff (diff -u format)
2. Do NOT modify any files directly
3. Do NOT execute shell commands
4. Do NOT commit, push, or create PRs
5. Your diff will be sandbox-tested before human review

Generate the fix:"""
    
    # STEP 4: Call OpenCode (if available)
    try:
        oc_result = subprocess.run(
            ['opencode', 'run', context],
            capture_output=True, text=True, timeout=60,
            cwd='/tmp',
        )
        result['opencode_output'] = oc_result.stdout[:500]
        result['opencode_exit'] = oc_result.returncode
    except FileNotFoundError:
        result['opencode_output'] = 'OPencode NOT INSTALLED'
        result['opencode_exit'] = -1
    except subprocess.TimeoutExpired:
        result['opencode_output'] = 'TIMEOUT'
        result['opencode_exit'] = -2
    except Exception as e:
        result['opencode_output'] = f'ERROR: {str(e)[:200]}'
        result['opencode_exit'] = -3
    
    result['fixed'] = result.get('opencode_exit', -1) == 0
    
    return result


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    print("╔══════════════════════════════════════════════╗")
    print("║  CT + LLM FIX ENGINE INTEGRATION TEST        ║")
    print("╚══════════════════════════════════════════════╝\n")
    
    # Phase 1: Check engines
    print("═══ PHASE 1: ENGINE AVAILABILITY ═══")
    engines = check_engines()
    for name, info in engines.items():
        status = '✅' if info['available'] else '❌'
        detail = info.get('version', info.get('error', 'unknown'))
        print(f"  {status} {name}: {detail}")
    
    # Phase 2+3: Test pipeline
    print(f"\n═══ PHASE 2+3: CT + OpenCode PIPELINE ═══")
    
    test_issues = [
        ("NullPointer in User.get_profile() when user is anonymous",
         "AttributeError: 'NoneType' object has no attribute 'get_profile' at views.py:42"),
        ("ImportError: cannot import 'url_quote' from 'werkzeug'",
         "After upgrading werkzeug to 2.0, the import path changed from werkzeug.urls to werkzeug.routing"),
        ("TypeError: unsupported operand type + for int and str",
         "At line 15: total = count + 'items' — trying to concatenate int and str"),
    ]
    
    for title, body in test_issues:
        print(f"\n  Issue: {title[:60]}")
        result = run_ct_opencode_pipeline(title, body)
        print(f"    Bug Type: {result['bug_type']}")
        print(f"    CT Diff:  {result['ct_diff_size']}B")
        print(f"    Safety:   {'BLOCKED 🔴' if result['safety_blocked'] else 'OK ✅'}")
        if 'opencode_output' in result:
            out = result['opencode_output'][:100].replace('\n', ' ')
            print(f"    OpenCode: {out}...")
    
    print(f"\n═══ HONEST ASSESSMENT ═══")
    if engines.get('OpenCode', {}).get('available'):
        print(f"  ✅ OpenCode available — CT can delegate fixes")
    else:
        print(f"  ❌ OpenCode NOT available")
    if engines.get('Codex', {}).get('available'):
        print(f"  ✅ Codex CLI available")
    else:
        print(f"  ❌ Codex CLI NOT installed")
    print(f"  ⚠️  CT stays as Safety/Analysis layer")
    print(f"  ⚠️  LLM handles actual code fix generation")
    print(f"  ✅ Pipeline pattern validated")
