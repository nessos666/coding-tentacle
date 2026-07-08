"""
CT 11.x — PROMPT LEARNER (P0 Learning V2)

Speichert erfolgreiche Engine-Prompts und ruft sie für ähnliche Bugs ab.
Kein LLM-Magic. Nur datenbasiert: Welcher Prompt-Typ funktioniert am besten
für BugType X mit Engine Y?

CT-v11.0.0: PRODUCTION | Learning V2 P0 | Prompt Learning
"""

from __future__ import annotations
import json, os, time
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class PromptRecord:
    """Gespeicherter Prompt mit Metadaten."""
    bug_type: str
    engine: str
    prompt_template: str          # Die Prompt-Struktur (nicht der volle Prompt)
    success: bool
    droste_used: bool = False
    droste_nodes: int = 0
    reflection_quality: float = 0.5  # 0-1, kommt von ReflectionEngine
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()
    
    def age_days(self) -> float:
        return (time.time() - self.timestamp) / 86400
    
    def score(self) -> float:
        """Prompt-Score: Erfolg + Aktualität + Droste-Hilfe."""
        success_score = 1.0 if self.success else 0.1
        age_decay = max(0.1, 1.0 - self.age_days() / 7.0)  # 7-Tage-Halbwertszeit
        droste_bonus = 0.2 if (self.droste_used and self.droste_nodes > 3) else 0.0
        return (success_score * 0.5 + self.reflection_quality * 0.3 + droste_bonus) * age_decay


class PromptLearner:
    """
    Prompt-Template-Datenbank.
    
    Speichert: BugType × Engine × Prompt-Struktur × Ergebnis
    Ruft ab:    Bester Prompt für BugType + Engine
    
    Usage:
        learner = PromptLearner()
        
        # Vor Engine-Call:
        best = learner.get_best_prompt('NullPointer', 'opencode')
        if best:
            prompt = best.prompt_template.format(bug_report=bug)
        
        # Nach Repair:
        learner.record('NullPointer', 'opencode', template, success=True, droste_used=True)
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.path.expanduser(
            '~/.coding_tentacle/prompt_learner.json')
        self._records: list[PromptRecord] = []
        self._load()
    
    def _load(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path) as f:
                    data = json.load(f)
                self._records = [PromptRecord(**r) for r in data]
            except (json.JSONDecodeError, TypeError):
                self._records = []
    
    def _save(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, 'w') as f:
            json.dump([asdict(r) for r in self._records[-100:]], f, indent=2)
    
    def record(self, bug_type: str, engine: str, prompt_template: str,
               success: bool, droste_used: bool = False, droste_nodes: int = 0,
               reflection_quality: float = 0.5):
        """Speichere einen Prompt und sein Ergebnis."""
        rec = PromptRecord(
            bug_type=bug_type, engine=engine,
            prompt_template=prompt_template[:500],
            success=success, droste_used=droste_used,
            droste_nodes=droste_nodes,
            reflection_quality=reflection_quality)
        self._records.append(rec)
        # Keep only last 100 records
        if len(self._records) > 100:
            self._records = self._records[-100:]
        self._save()
    
    def get_best_prompt(self, bug_type: str, engine: str = None,
                         min_score: float = 0.3) -> Optional[PromptRecord]:
        """Finde den besten Prompt für bug_type (+ optional engine)."""
        candidates = []
        for r in self._records:
            if r.bug_type != bug_type:
                continue
            if engine and r.engine != engine:
                continue
            if not r.success:
                continue
            score = r.score()
            if score >= min_score:
                candidates.append((score, r))
        
        if not candidates:
            return None
        
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]
    
    def get_prompt_stats(self, bug_type: str) -> dict:
        """Statistik: Welche Prompt-Typen funktionieren am besten?"""
        matching = [r for r in self._records if r.bug_type == bug_type]
        if not matching:
            return {'bug_type': bug_type, 'records': 0}
        
        engines = {}
        for r in matching:
            if r.engine not in engines:
                engines[r.engine] = {'total': 0, 'success': 0}
            engines[r.engine]['total'] += 1
            if r.success:
                engines[r.engine]['success'] += 1
        
        best_engine = max(engines, key=lambda e: engines[e]['success'] / max(1, engines[e]['total']))
        return {
            'bug_type': bug_type,
            'records': len(matching),
            'best_engine': best_engine,
            'engine_stats': engines,
        }
    
    def __len__(self):
        return len(self._records)


# ─── Self-Tests ─────────────────────────────────────────────────────────

if __name__ == '__main__':
    import tempfile
    
    learner = PromptLearner(db_path=tempfile.mktemp())
    passed = 0
    
    # T1: Empty DB returns None
    print("T1: Empty DB → None...", end=" ")
    assert learner.get_best_prompt('NullPointer') is None
    passed += 1; print("OK")
    
    # T2: Record + retrieve
    print("T2: Record + retrieve...", end=" ")
    learner.record('NullPointer', 'opencode', 
                   "Fix {bug_type} in {file}. Add guard clause.", 
                   success=True, droste_used=True, droste_nodes=6)
    best = learner.get_best_prompt('NullPointer')
    assert best is not None
    assert best.engine == 'opencode'
    assert 'guard' in best.prompt_template
    passed += 1; print("OK")
    
    # T3: Failed prompts don't return
    print("T3: Failed prompts filtered...", end=" ")
    learner.record('NullPointer', 'ollama', "Fix bug.", success=False)
    best2 = learner.get_best_prompt('NullPointer', engine='ollama')
    assert best2 is None  # Only failed records for ollama
    passed += 1; print("OK")
    
    # T4: Bug-type filtering
    print("T4: Bug-type filtering...", end=" ")
    assert learner.get_best_prompt('TypeError') is None
    passed += 1; print("OK")
    
    # T5: Engine filtering
    print("T5: Engine filtering...", end=" ")
    best = learner.get_best_prompt('NullPointer', engine='opencode')
    assert best is not None
    passed += 1; print("OK")
    
    # T6: Scoring prefers recent successes
    print("T6: Score prefers Droste...", end=" ")
    learner.record('NullPointer', 'opencode',
                   "Best prompt with Droste context.",
                   success=True, droste_used=True, droste_nodes=8, reflection_quality=0.9)
    best = learner.get_best_prompt('NullPointer', engine='opencode')
    assert 'Droste' in best.prompt_template  # Higher score wins
    passed += 1; print("OK")
    
    # T7: Stats
    print("T7: Stats...", end=" ")
    stats = learner.get_prompt_stats('NullPointer')
    assert stats['records'] >= 3
    assert stats['best_engine'] == 'opencode'
    passed += 1; print("OK")
    
    # T8: DB persistence
    print("T8: Persistence...", end=" ")
    learner2 = PromptLearner(db_path=learner.db_path)
    assert len(learner2) == len(learner)
    passed += 1; print("OK")
    
    print(f"\n{'='*50}")
    print(f"  {passed}/8 Tests bestanden")
    print(f"  {'✅ PROMPT LEARNER FERTIG' if passed == 8 else '❌'}")
    
    os.unlink(learner.db_path)
