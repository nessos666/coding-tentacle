"""
PUBLIC DEMO PACK — P1.6
5 curated GitHub issues for public demonstration.
Shadow mode only. NEVER PRs, commits, or comments.

Autor: Hermes + David | Coding Tentacle 2026
"""
import sys, os, json, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from coding_tentacle.config import Config
from coding_tentacle.orchestrator.shadow_mode import ShadowModeRunner, GitHubIssueRun, ShadowRunReport
from coding_tentacle.orchestrator.metabrain import MetaBrain, SafetyBrain
from coding_tentacle.safety.inhibitory_control import InhibitoryControl
from coding_tentacle.knowledge.security_store import create_seed_security_store
from coding_tentacle.orchestrator.teacher_student import Teacher
from coding_tentacle.patch.diff_generator import DiffGenerator
from coding_tentacle.patch.patch_suggestion import PatchSuggestionEngine
from coding_tentacle.patch.sandbox_runner import SandboxRunner
from coding_tentacle.memory.procedural_memory import ProcedureStore
from coding_tentacle.memory.skill_compiler import SkillStore
from coding_tentacle.knowledge.project_map import ProjectMap


# ═══ DEMO ISSUES ═══
DEMO_ISSUES = [
    GitHubIssueRun(
        repo_url="https://github.com/psf/requests",
        issue_url="https://github.com/psf/requests/issues/1",
        issue_title="🐛 TypeError: can only concatenate str (not 'int') to str in URL builder",
        issue_body="When passing integer parameters to requests.get(), the URL builder crashes with TypeError. Expected: automatic str() conversion or clear error message.",
    ),
    GitHubIssueRun(
        repo_url="https://github.com/pallets/flask",
        issue_url="https://github.com/pallets/flask/issues/2",
        issue_title="🐛 ModuleNotFoundError after moving config to subpackage",
        issue_body="After restructuring config into flask/config/, importing from flask.config breaks with ModuleNotFoundError. The __init__.py re-exports are missing.",
    ),
    GitHubIssueRun(
        repo_url="https://github.com/tiangolo/fastapi",
        issue_url="https://github.com/tiangolo/fastapi/issues/3",
        issue_title="🐛 KeyError: 'user_id' in JWT dependency",
        issue_body="When JWT token doesn't include optional 'user_id' claim, Depends() crashes with KeyError. Should use .get('user_id') with default None instead of dict access.",
    ),
    GitHubIssueRun(
        repo_url="https://github.com/encode/httpx",
        issue_url="https://github.com/encode/httpx/issues/4",
        issue_title="🔴 SQL Injection via raw query parameter",
        issue_body="User input passed directly to database.execute() without parameterization. DROP TABLE possible through crafted input. CRITICAL security issue.",
    ),
    GitHubIssueRun(
        repo_url="https://github.com/numpy/numpy",
        issue_url="https://github.com/numpy/numpy/issues/5",
        issue_title="🐛 ValueError: could not convert string to float in np.array()",
        issue_body="When CSV contains mixed string/numeric data, np.array() crashes with ValueError. Expected: coerce or skip invalid values with errors='coerce'.",
    ),
]


def run_demo():
    """Run the public demo suite."""
    cfg = Config()
    
    # Setup pipeline
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
    runner = ShadowModeRunner(meta_brain=mb, teacher=teacher, 
                              diff_generator=dg, sandbox_runner=sr)
    
    reports = []
    print("╔══════════════════════════════════════════════╗")
    print("║  CODING TENTACLE — Public Demo v0.5.0       ║")
    print("║  Safety-First Bug Analysis & Patch Suggestion ║")
    print("╚══════════════════════════════════════════════╝\n")
    
    for i, issue in enumerate(DEMO_ISSUES):
        print(f"━━━ Issue {i+1}/5 ━━━")
        print(f"  Repo: {issue.repo_url}")
        print(f"  Title: {issue.issue_title[:80]}")
        
        report = runner.analyze_issue(issue)
        reports.append(report)
        
        status = '🔴 SAFETY BLOCK' if report.safety_events else \
                 '✅ ANALYZED' if report.detected_bug_type != 'Unknown' else '⚠️  UNKNOWN'
        print(f"  Result: {status}")
        print(f"  Bug Type: {report.detected_bug_type} (conf={report.confidence:.0%})")
        if report.selected_procedure:
            print(f"  Procedure: {report.selected_procedure}")
        if report.selected_skill:
            print(f"  Skill: {report.selected_skill}")
        if report.generated_diff:
            print(f"  Diff: {len(report.generated_diff)} chars generated")
        if report.safety_events:
            print(f"  Safety: {report.safety_events}")
        print(f"  Recommendation: {report.recommendation[:80]}")
        
        # Save individual report
        safe_name = issue.repo_url.split('/')[-1].replace('/', '_')
        path = f'/home/boobi/Schreibtisch/demo_{i+1}_{safe_name}_report'
        with open(f'{path}.md', 'w') as f:
            f.write(report.to_markdown())
        with open(f'{path}.json', 'w') as f:
            json.dump({'issue': issue.issue_title, 'bug_type': report.detected_bug_type,
                       'confidence': report.confidence, 'recommendation': report.recommendation,
                       'diff_size': len(report.generated_diff),
                       'safety_events': report.safety_events}, f, indent=2)
        print(f"  Reports: {path}.md + .json\n")
    
    # Demo summary
    print("━━━ DEMO SUMMARY ━━━")
    print(f"  Issues analyzed:   {len(reports)}")
    print(f"  Bug types found:   {', '.join(set(r.detected_bug_type for r in reports))}")
    print(f"  Diffs generated:   {sum(1 for r in reports if r.generated_diff)}")
    print(f"  Safety blocks:     {sum(1 for r in reports if r.safety_events)}")
    print(f"  Avg confidence:    {sum(r.confidence for r in reports)/len(reports):.0%}")
    print(f"\n  ⚠️  CRITICAL NOTE:")
    print(f"  These are SHADOW MODE analyses only.")
    print(f"  NO patches have been applied to real repositories.")
    print(f"  Human approval is REQUIRED before any application.")
    print(f"\n  Reports saved to ~/Schreibtisch/demo_*_report.md/.json")
    
    return reports


if __name__ == "__main__":
    run_demo()
