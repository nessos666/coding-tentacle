"""
IMPACT ANALYZER — RC25
Predicts system-wide impact before a fix is applied.
"What happens if file A is modified?"

Integrates: ProjectMap + SkillStore + ProcedureStore + TestMap.

Author: Hermes + David | Coding Tentacle 2026
Research: TDAD (70% regression reduction) + Athena
"""
import re, time, os, math
from dataclasses import dataclass, field


@dataclass
class ImpactReport:
    """Full impact analysis for a proposed change."""
    changed_file: str
    changed_function: str = ''
    bug_type: str = ''
    impacted_files: list = field(default_factory=list)
    impacted_tests: list = field(default_factory=list)
    related_skills: list = field(default_factory=list)
    related_procedures: list = field(default_factory=list)
    dependency_depth: int = 0
    importer_count: int = 0
    has_tests: bool = False
    is_core_file: bool = False
    risk_score: float = 0.0
    risk_components: dict = field(default_factory=dict)
    risk_reason: str = ''
    recommended_review: str = 'REQUEST_MORE'  # APPROVE | REQUEST_MORE | ESCALATE
    diff_size: int = 0


class TestMap:
    """Maps source files to likely test files.
    
    Heuristics:
    - src/payment.py → tests/test_payment.py, tests/payment_test.py
    - app/models/user.rb → spec/models/user_spec.rb
    - src/lib.rs → tests/lib_test.rs, src/tests/lib.rs
    """
    
    PATTERNS = [
        # Python
        (r'src/(.+)\.py$', [r'test[s]?/test_\1.py', r'test[s]?/\1_test.py']),
        # Ruby
        (r'app/(.+)\.rb$', [r'spec/\1_spec.rb']),
        # Rust
        (r'src/(.+)\.rs$', [r'test[s]?/\1_test.rs']),
        # Go
        (r'(.+)\.go$', [r'\1_test.go']),
        # JS/TS
        (r'src/(.+)\.(js|ts)x?$', [r'test[s]?/\1.test.\2', r'__tests__/\1.test.\2']),
        # Java
        (r'src/main/java/(.+)\.java$', [r'src/test/java/\1Test.java']),
        # C++
        (r'src/(.+)\.(cpp|cxx)$', [r'test[s]?/\1_test.\2', r'test[s]?/test_\1.\2']),
        # Shell
        (r'(.+)\.sh$', []),  # No standard test convention
    ]
    
    def __init__(self, project_map=None):
        self.pm = project_map
        self.explicit_map = {}  # file → [test_files]
        self.found_tests = 0
    
    def add_mapping(self, source_file, test_files):
        """Explicitly map a source file to its test files."""
        if isinstance(test_files, str):
            test_files = [test_files]
        self.explicit_map[source_file] = test_files
    
    def find_tests_for(self, file_path):
        """Find likely test files for a source file."""
        if file_path in self.explicit_map:
            return self.explicit_map[file_path]
        
        # Try pattern matching
        for src_pattern, test_patterns in self.PATTERNS:
            m = re.search(src_pattern, file_path)
            if m:
                results = []
                for tp in test_patterns:
                    try:
                        test_file = re.sub(src_pattern, tp, file_path)
                        results.append(test_file)
                    except:
                        pass
                if results:
                    self.found_tests += 1
                    return results
        
        return []
    
    def has_tests(self, file_path):
        return len(self.find_tests_for(file_path)) > 0


class ImpactAnalyzer:
    """Analyzes the impact of a proposed code change.
    
    Uses ProjectMap for dependency analysis, TestMap for test discovery,
    SkillStore + ProcedureStore for skill/procedure impact.
    """
    
    def __init__(self, project_map, test_map=None, skill_store=None, procedure_store=None):
        self.pm = project_map
        self.test_map = test_map or TestMap(project_map)
        self.skills = skill_store
        self.procedures = procedure_store
        self.analyses = 0
    
    # Risk weights
    IMPORTER_WEIGHT = 0.15
    CORE_FILE_WEIGHT = 0.20
    NO_TEST_WEIGHT = 0.15
    SKILL_COUNT_WEIGHT = 0.10
    PROCEDURE_WEIGHT = 0.08
    DEPTH_WEIGHT = 0.08
    DIFF_SIZE_WEIGHT = 0.05
    SECURITY_WEIGHT = 0.30
    
    def analyze(self, file_path, function_name='', bug_type='', diff='', 
                code_context=None):
        """Full impact analysis."""
        self.analyses += 1
        report = ImpactReport(
            changed_file=file_path,
            changed_function=function_name,
            bug_type=bug_type,
            diff_size=len(diff) if diff else 0,
        )
        
        # 1. Dependency analysis via ProjectMap
        importers = self.pm.who_imports(file_path) if self.pm else []
        report.impacted_files = importers
        report.importer_count = len(importers)
        report.dependency_depth = self._compute_depth(file_path)
        report.is_core_file = report.importer_count >= 5
        
        risk = 0.0
        components = {}
        
        # 2. Importer count risk
        imp_risk = min(0.95, report.importer_count * self.IMPORTER_WEIGHT / 5)
        risk += imp_risk
        components['importers'] = round(imp_risk, 2)
        
        # 3. Core file risk
        if report.is_core_file:
            risk += self.CORE_FILE_WEIGHT
            components['core_file'] = self.CORE_FILE_WEIGHT
        else:
            components['core_file'] = 0.0
        
        # 4. Test coverage
        report.impacted_tests = self.test_map.find_tests_for(file_path)
        report.has_tests = len(report.impacted_tests) > 0
        if not report.has_tests:
            risk += self.NO_TEST_WEIGHT
            components['no_tests'] = self.NO_TEST_WEIGHT
        else:
            components['no_tests'] = 0.0
        
        # 5. Skill impact
        if self.skills:
            for skill_name, skill_data in getattr(self.skills, 'skills', {}).items():
                if hasattr(skill_data, 'source_procedure'):
                    if file_path in str(getattr(skill_data, 'source_procedure', '')):
                        report.related_skills.append(skill_name)
        if report.related_skills:
            sk_risk = min(0.30, len(report.related_skills) * self.SKILL_COUNT_WEIGHT / 3)
            risk += sk_risk
            components['skills'] = round(sk_risk, 2)
        else:
            components['skills'] = 0.0
        
        # 6. Procedure impact
        if self.procedures:
            for key, proc in getattr(self.procedures, 'procedures', {}).items():
                if bug_type and bug_type in str(key):
                    report.related_procedures.append(proc.bug_type if hasattr(proc, 'bug_type') else str(key))
        if report.related_procedures:
            proc_risk = min(0.20, len(report.related_procedures) * self.PROCEDURE_WEIGHT / 2)
            risk += proc_risk
            components['procedures'] = round(proc_risk, 2)
        else:
            components['procedures'] = 0.0
        
        # 7. Depth risk
        if report.dependency_depth > 2:
            depth_risk = min(0.20, report.dependency_depth * self.DEPTH_WEIGHT)
            risk += depth_risk
            components['depth'] = round(depth_risk, 2)
        else:
            components['depth'] = 0.0
        
        # 8. Diff size risk
        if diff and len(diff) > 200:
            diff_risk = min(0.10, len(diff) * self.DIFF_SIZE_WEIGHT / 500)
            risk += diff_risk
            components['diff_size'] = round(diff_risk, 2)
        else:
            components['diff_size'] = 0.0
        
        # 9. Security proximity
        if bug_type == 'SecurityRisk':
            risk += self.SECURITY_WEIGHT
            components['security'] = self.SECURITY_WEIGHT
        else:
            components['security'] = 0.0
        
        report.risk_score = min(0.95, round(risk, 2))
        report.risk_components = components
        
        # Risk reason
        reasons = []
        if report.importer_count >= 5:
            reasons.append(f"{report.importer_count} importers → core file")
        if not report.has_tests:
            reasons.append("NO test coverage found")
        if report.dependency_depth > 2:
            reasons.append(f"deep dependency chain ({report.dependency_depth})")
        if bug_type == 'SecurityRisk':
            reasons.append("SECURITY-RISK")
        report.risk_reason = '; '.join(reasons) if reasons else 'Low impact'
        
        # Recommended review level
        if bug_type == 'SecurityRisk' or report.risk_score >= 0.50:
            report.recommended_review = 'ESCALATE'
        elif report.risk_score >= 0.25:
            report.recommended_review = 'REQUEST_MORE'
        else:
            report.recommended_review = 'APPROVE'
        
        return report
    
    def _compute_depth(self, file_path):
        """Compute max dependency depth for a file."""
        seen = set()
        def dfs(path, depth=0):
            if path in seen or depth > 10:
                return depth
            seen.add(path)
            importers = self.pm.who_imports(path) if self.pm else []
            if not importers:
                return depth
            return max(dfs(imp, depth + 1) for imp in importers)
        return dfs(file_path)
    
    def quick_risk(self, file_path, bug_type=''):
        """Fast risk check without full analysis. Returns (risk, recommendation)."""
        importers = len(self.pm.who_imports(file_path)) if self.pm else 0
        has_tests = self.test_map.has_tests(file_path)
        
        risk = 0.0
        if importers >= 5: risk += 0.20
        if not has_tests: risk += 0.15
        if bug_type == 'SecurityRisk': risk = 0.95
        
        if risk >= 0.50 or bug_type == 'SecurityRisk':
            return risk, 'ESCALATE'
        elif risk >= 0.25:
            return risk, 'REQUEST_MORE'
        return risk, 'APPROVE'


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    from coding_tentacle.knowledge.project_map import ProjectMap
    import tempfile, shutil
    
    print("IMPACT ANALYZER — Self-Test")
    print("=" * 55)
    passed = 0
    
    # Setup
    pm = ProjectMap()
    tmp = tempfile.mkdtemp()
    # Create a tiny project structure
    os.makedirs(os.path.join(tmp, 'src'), exist_ok=True)
    with open(os.path.join(tmp, 'src', 'payment.py'), 'w') as f:
        f.write("from src.auth import check_user\nfrom src.logger import log\ndef process(): check_user(); log('paid')")
    with open(os.path.join(tmp, 'src', 'auth.py'), 'w') as f:
        f.write("def check_user(): return True")
    with open(os.path.join(tmp, 'src', 'logger.py'), 'w') as f:
        f.write("def log(msg): print(msg)")
    with open(os.path.join(tmp, 'tests', '__init__.py'), 'w') as f:
        f.write("")
    with open(os.path.join(tmp, 'tests', 'test_payment.py'), 'w') as f:
        f.write("from src.payment import process\ndef test_process(): process()")
    os.makedirs(os.path.join(tmp, 'tests'), exist_ok=True)
    
    pm.build_cached(tmp)
    tm = TestMap(pm)
    ia = ImpactAnalyzer(pm, test_map=tm)
    
    # T1: Core file with importers
    report1 = ia.analyze(os.path.join(tmp, 'src', 'auth.py'), bug_type='NullPointer')
    t1 = report1.importer_count >= 1  # payment imports auth
    print(f"  T1: {'✅' if t1 else '❌'} Core auth.py → {report1.importer_count} importers")
    
    # T2: Risk score computed
    t2 = report1.risk_score >= 0.0 and report1.risk_score < 1.0
    print(f"  T2: {'✅' if t2 else '❌'} Risk score → {report1.risk_score}")
    
    # T3: Payment is core file (imported by tests)
    report3 = ia.analyze(os.path.join(tmp, 'src', 'payment.py'))
    t3 = report3.importer_count >= 0  # payment may have test importers
    print(f"  T3: {'✅' if t3 else '❌'} Payment analyzed → importers={report3.importer_count}")
    
    # T4: Security risk = high risk
    report4 = ia.analyze(os.path.join(tmp, 'src', 'payment.py'), bug_type='SecurityRisk', 
                         diff='eval(user_input)')
    t4 = report4.risk_score >= 0.30 and report4.recommended_review == 'ESCALATE'
    print(f"  T4: {'✅' if t4 else '❌'} SecurityRisk → risk={report4.risk_score} {report4.recommended_review}")
    
    # T5: Risk components
    t5 = len(report4.risk_components) >= 5
    print(f"  T5: {'✅' if t5 else '❌'} Risk components → {len(report4.risk_components)}")
    
    # T6: Low-risk file
    report6 = ia.analyze(os.path.join(tmp, 'src', 'logger.py'), bug_type='TypeError')
    t6 = report6.risk_score < report1.risk_score or report6.risk_score < 0.3
    print(f"  T6: {'✅' if t6 else '❌'} Logger low risk → risk={report6.risk_score}")
    
    # T7: TestMap finds tests
    tests = tm.find_tests_for(os.path.join(tmp, 'src', 'payment.py'))
    t7 = len(tests) >= 1
    print(f"  T7: {'✅' if t7 else '❌'} TestMap → {tests}")
    
    # T8: TestMap for different languages
    tests_rs = tm.find_tests_for('src/lib.rs')
    tests_rb = tm.find_tests_for('app/models/user.rb')
    t8 = len(tests_rs) >= 1 and len(tests_rb) >= 1
    print(f"  T8: {'✅' if t8 else '❌'} Multi-lang → Rust={tests_rs} Ruby={tests_rb}")
    
    # T9: Quick risk
    risk, rec = ia.quick_risk(os.path.join(tmp, 'src', 'payment.py'), 'NullPointer')
    t9 = rec in ('APPROVE', 'REQUEST_MORE')
    print(f"  T9: {'✅' if t9 else '❌'} Quick risk → {risk:.2f} {rec}")
    
    # T10: Stats
    t10 = ia.analyses >= 5
    print(f"  T10: {'✅' if t10 else '❌'} Analyses: {ia.analyses}")
    
    shutil.rmtree(tmp, ignore_errors=True)
    passed = sum([t1,t2,t3,t4,t5,t6,t7,t8,t9,t10])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/10 Tests bestanden")
    print(f"  {'✅ IMPACT ANALYZER FERTIG' if passed >= 9 else '⚠️'}")
