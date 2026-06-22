"""
SKILL COMPILATION — RC8.0
Transforms successful procedures into reusable skills.
Inspired by HERAKLES: hierarchical skill compilation.

A Skill is a Procedure that has been validated 3+ times successfully.
Skills are callable by ANY tentacle, not just ProceduralMemory.

Autor: Hermes + David | Coding Tentacle 2026
"""
import time, json, os, hashlib
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Skill:
    """A compiled, reusable bug-fixing skill."""
    name: str                     # "safe_guard_clause_for_optional_value"
    source_procedure: str         # Which procedure created this skill
    bug_type: str                 # "NullPointer", "TypeError", ...
    language: str                 # "python", "java", ...
    trigger: str                  # When to activate
    fix_pattern: str              # The fix template
    confidence: float = 0.5       # Based on procedure success rate
    times_compiled: int = 0       # Times this skill was compiled/refined
    times_called: int = 0         # Times other tentacles called this skill
    times_succeeded: int = 0      # Times the skill deployment succeeded
    verification_method: str = "" # How to verify the fix works
    dependent_skills: list = field(default_factory=list)  # Skills this depends on
    created_at: float = 0.0
    last_used: float = 0.0
    
    def __post_init__(self):
        if self.created_at == 0.0:
            self.created_at = time.time()
        if self.last_used == 0.0:
            self.last_used = time.time()
    
    def success_rate(self):
        return self.times_succeeded / max(1, self.times_called)
    
    def to_dict(self):
        return asdict(self)


class SkillStore:
    """Persistent store of compiled skills. Loadable by any tentacle."""
    
    def __init__(self, config=None, store_path=None):
        self.store_path = store_path or (config.get('learning.skills_path') if config else os.path.expanduser('~/.coding_tentacle/skills.json'))
        self.skills: dict[str, Skill] = {}  # name → Skill
        self.by_bug_type: dict[str, list[str]] = {}  # bug_type → [skill_names]
        self.actions_executed = 0
        self._load()
    
    # ═══════ COMPILE ═══════
    def compile_from_procedure(self, procedure, min_successes=3):
        """Compile a procedure into a skill (if enough successes)."""
        if not procedure:
            return None
        
        # Only compile procedures with enough success
        if procedure.times_succeeded < min_successes:
            return None
        
        # Generate skill name from procedure
        name = self._generate_skill_name(procedure)
        
        # Check if skill already exists — update it
        if name in self.skills:
            existing = self.skills[name]
            existing.confidence = procedure.confidence
            existing.times_compiled += 1
            existing.last_used = time.time()
            return existing
        
        # Determine fix pattern from the procedure's patch step
        fix_pattern = ""
        for step in procedure.steps:
            if step.action in ('patch_suggest', 'generate_patch'):
                fix_pattern = step.expected_output
                break
            elif step.action in ('blm_best_fix', 'rule_check'):
                fix_pattern = step.expected_output
        
        # Create new skill
        skill = Skill(
            name=name,
            source_procedure=f"{procedure.bug_type}:{procedure.language}",
            bug_type=procedure.bug_type,
            language=procedure.language,
            trigger=procedure.trigger,
            fix_pattern=fix_pattern,
            confidence=procedure.confidence,
            times_compiled=1,
            times_succeeded=0,  # Start fresh — skill deployment counts separately
            verification_method="pytest",
            dependent_skills=[],
        )
        self.skills[name] = skill
        
        # Index by bug_type
        if procedure.bug_type not in self.by_bug_type:
            self.by_bug_type[procedure.bug_type] = []
        self.by_bug_type[procedure.bug_type].append(name)
        
        self._save()
        return skill
    
    def _generate_skill_name(self, procedure):
        """Generate a clean skill name from procedure data."""
        prefix_map = {
            'NullPointer': 'safe_guard_for_optional',
            'TypeError': 'safe_type_cast',
            'ImportError': 'safe_import_resolve',
            'AttributeError': 'safe_attr_check',
            'KeyError': 'safe_key_access',
        }
        prefix = prefix_map.get(procedure.bug_type, f'safe_{procedure.bug_type.lower()}')
        return f"{prefix}_{hashlib.md5(procedure.trigger.encode()).hexdigest()[:6]}"
    
    # ═══════ QUERY ═══════
    def find_skills(self, bug_type, language="python", min_confidence=0.5):
        """Find skills for a bug type."""
        names = self.by_bug_type.get(bug_type, [])
        skills = [self.skills[n] for n in names 
                  if n in self.skills and self.skills[n].language == language
                  and self.skills[n].confidence >= min_confidence]
        skills.sort(key=lambda s: -(s.confidence * (1 + s.times_succeeded)))
        return skills
    
    def get_skill(self, name):
        return self.skills.get(name)
    
    def call_skill(self, name, success=True):
        """Record a skill being called (by any tentacle)."""
        skill = self.skills.get(name)
        if skill:
            skill.times_called += 1
            skill.last_used = time.time()
            if success:
                skill.times_succeeded += 1
                skill.confidence = min(0.99, skill.confidence + 0.02)
            else:
                skill.confidence = max(0.3, skill.confidence - 0.05)
            self._save()
    
    def best_skill_for(self, bug_type, language="python"):
        """Highest-confidence skill for a bug type."""
        skills = self.find_skills(bug_type, language)
        return skills[0] if skills else None
    
    def stats(self):
        return {
            'total_skills': len(self.skills),
            'bug_types': list(self.by_bug_type.keys()),
            'high_confidence': sum(1 for s in self.skills.values() if s.confidence >= 0.8),
            'actions_executed': self.actions_executed,
        }
    
    def _save(self):
        os.makedirs(os.path.dirname(self.store_path), exist_ok=True)
        data = {
            'skills': {k: v.to_dict() for k, v in self.skills.items()},
            'by_bug_type': self.by_bug_type,
        }
        with open(self.store_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load(self):
        if os.path.exists(self.store_path):
            try:
                with open(self.store_path) as f:
                    data = json.load(f)
                self.skills = {k: Skill(**v) for k, v in data.get('skills', {}).items()}
                self.by_bug_type = data.get('by_bug_type', {})
            except Exception:
                pass


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    import tempfile, shutil
    from coding_tentacle.memory.procedural_memory import ProcedureStore, Procedure, ProcedureStep
    
    print("SKILL COMPILATION — Self-Test")
    print("=" * 55)
    passed = 0
    
    tmp = tempfile.mkdtemp()
    ss = SkillStore(store_path=os.path.join(tmp, 'skills.json'))
    
    # Create a mock procedure with enough successes
    proc = Procedure(
        bug_type="NullPointer", language="python",
        trigger="NoneType has no attribute",
        steps=[
            ProcedureStep(1, "analyze_stacktrace", "Extract file+line", "CC", "file=t.py,line=42"),
            ProcedureStep(6, "patch_suggest", "Generate patch", "PS", "if self.value is not None:"),
        ],
        confidence=0.90, times_succeeded=5, times_used=6,
        created_at=time.time(), last_used=time.time()
    )
    
    # T1: Compile from procedure with enough successes
    skill = ss.compile_from_procedure(proc, min_successes=3)
    t1 = skill is not None and skill.bug_type == "NullPointer"
    print(f"  T1: {'✅' if t1 else '❌'} Compile Procedure→Skill → {skill.name if skill else 'NONE'}")
    
    # T2: Skill has fix pattern
    t2 = skill and "not None" in skill.fix_pattern
    print(f"  T2: {'✅' if t2 else '❌'} Fix pattern extracted → {skill.fix_pattern if skill else ''}")
    
    # T3: Find skills for NullPointer
    skills = ss.find_skills("NullPointer")
    t3 = len(skills) >= 1
    print(f"  T3: {'✅' if t3 else '❌'} Find skills → {len(skills)} for NullPointer")
    
    # T4: Best skill
    best = ss.best_skill_for("NullPointer")
    t4 = best is not None and best.confidence >= 0.8
    print(f"  T4: {'✅' if t4 else '❌'} Best skill → conf={best.confidence:.2f}" if best else "  T4: ❌")
    
    # T5: Call skill (success)
    if skill:
        ss.call_skill(skill.name, success=True)
        s2 = ss.get_skill(skill.name)
        t5 = s2.times_called == 1 and s2.times_succeeded == 1
        print(f"  T5: {'✅' if t5 else '❌'} Call+Success → called={s2.times_called} success={s2.times_succeeded}")
    
    # T6: No skill for unknown bug types
    skills_unk = ss.find_skills("RecursionError")
    t6 = len(skills_unk) == 0
    print(f"  T6: {'✅' if t6 else '❌'} Unknown bug → {len(skills_unk)} skills (should be 0)")
    
    # T7: No skill for SecurityRisk
    skills_sec = ss.find_skills("SecurityRisk")
    t7 = len(skills_sec) == 0
    print(f"  T7: {'✅' if t7 else '❌'} SecurityRisk → {len(skills_sec)} skills (should be 0)")
    
    # T8: Below-min-successes procedure does NOT compile
    proc_low = Procedure(
        bug_type="TypeError", language="python",
        trigger="can't multiply sequence",
        steps=[ProcedureStep(1, "analyze", "Parse", "CC", "file=t.py")],
        confidence=0.70, times_succeeded=1, times_used=5,
        created_at=time.time(), last_used=time.time()
    )
    skill_low = ss.compile_from_procedure(proc_low, min_successes=3)
    t8 = skill_low is None
    print(f"  T8: {'✅' if t8 else '❌'} Low-success not compiled → {skill_low}")
    
    # T9: Stats
    st = ss.stats()
    t9 = st['total_skills'] >= 1 and st['actions_executed'] == 0
    print(f"  T9: {'✅' if t9 else '❌'} Stats → {st['total_skills']} skills, read-only")
    
    # T10: Persistence
    ss2 = SkillStore(store_path=os.path.join(tmp, 'skills.json'))
    t10 = len(ss2.skills) >= 1
    print(f"  T10: {'✅' if t10 else '❌'} Persistence → {len(ss2.skills)} skills reloaded")
    
    passed = sum([t1,t2,t3,t4,t5,t6,t7,t8,t9,t10])
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/10 Tests bestanden")
    print(f"  {'✅ SKILL COMPILATION FERTIG' if passed >= 9 else '⚠️'}")
