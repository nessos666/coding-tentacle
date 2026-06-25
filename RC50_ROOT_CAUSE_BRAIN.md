# CODING TENTACLE — RC50 ROOT CAUSE BRAIN V1
### Working Copy: ~/Schreibtisch/CODING_TENTACLE_WORKING/coding_tentacle_v0.9.0_testlab

---

## PHASE 1 — RESEARCH SYNTHESIS

### How Professional Systems Determine Root Cause

**Spectrum-Based Fault Localization (SBFL):**
- Ranks code statements by likelihood of containing the bug
- Uses test pass/fail coverage data to compute suspiciousness scores
- Tarantula, Ochiai, DStar metrics

**Program Slicing:**
- Static backward slicing: "What statements could affect this line?"
- Dynamic forward slicing: "What statements are affected by this value?"
- Combined with SBFL for precision (OptRCA, 2026)

**Orthogonal Defect Classification (ODC):**
- IBM's taxonomy: 8 defect types classified by:
  1. Function (what the defect does)
  2. Insertion (when in lifecycle was it introduced)
  3. Trigger (what activates it)
  4. Impact (what it affects)
  5. Target (what artifact)

**CWE Root Cause Mapping (MITRE, 2026):**
- Maps CVEs to CWEs by root cause, not symptom
- "A single architectural flaw can produce 50 different bug reports"
- Pattern: vulnerability type → weakness category → root cause pattern

**Key Insight from Research:**
Bug TYPE (NullPointer) ≠ Root CAUSE.
Root CAUSE = WHY did this NullPointer exist?

12 different NullPointer bugs might share 1 root cause:
→ "No input validation layer exists"
→ "Singleton pattern used incorrectly"
→ "No null-annotations in codebase"

---

## PHASE 2 — ROOT CAUSE BRAIN DESIGN

### Architecture

```
RootCauseBrain
├── Inputs:
│   ├── bug_report (raw text)
│   ├── bug_type (from UnifiedClassifier)
│   ├── diff (from engine)
│   ├── impact_data (from ImpactAnalyzer)
│   ├── blm_history (similar past bugs)
│   ├── project_map (file dependencies)
│   ├── procedural_memory (known fix patterns)
│   └── engine_trust (from EngineLearning)
│
├── Analysis Layers:
│   ├── L1: Bug-Type → Root-Cause-Class mapping
│   ├── L2: Similarity → "Seen this pattern before?"
│   ├── L3: Impact → "What systems does this affect?"
│   ├── L4: History → "Same file/module had bugs before?"
│   └── L5: Pattern → "Architectural anti-pattern?"
│
└── Output: RootCauseReport
    ├── root_cause: str          ← "No input validation layer"
    ├── confidence: float        ← 0.72
    ├── affected_component: str  ← "UserService"
    ├── suspected_function: str  ← "get_profile()"
    ├── suspected_module: str    ← "views.py"
    ├── architectural_pattern: str ← "Missing Guard Clause"
    ├── repeat_count: int        ← 4 (same cause, different symptoms)
    ├── evidence: list           ← ["3 similar bugs in BLM", "No validate() call"]
    └── recommendation: str      ← "Add input validation layer"
```

### Root Cause Classes (18 categories)

| Root Cause Class | Typical Bug Types | Example |
|-----------------|-------------------|---------|
| MISSING_GUARD | NullPointer, KeyError | No null-check before access |
| TYPE_CONFUSION | TypeError, ValueError | int passed where str expected |
| IMPORT_BREAKAGE | ImportError | Dependency upgrade broke path |
| NO_VALIDATION | NullPointer, SecurityRisk | User input unsanitized |
| ASYNC_MISHANDLING | RaceCondition, Deadlock | Shared state without lock |
| API_MISUSE | ValueError, TypeError | Wrong parameter order |
| DEPRECATED_CALL | ImportError, SyntaxError | Removed function still called |
| STATE_LEAK | MemoryError, RaceCondition | Singleton mutated concurrently |
| CIRCULAR_DEPENDENCY | ImportError, RecursionError | A imports B imports A |
| MISSING_ERROR_HANDLER | Deadlock, Timeout | No try/except on I/O |
| CONFIG_DRIFT | FileNotFoundError, KeyError | Config key renamed, code not updated |
| VERSION_MISMATCH | ImportError, TypeError | Library v2 API used with v1 installed |
| PERMISSION_ERROR | PermissionError | Hardcoded path to protected dir |
| RESOURCE_EXHAUSTION | MemoryError, Timeout | Connection pool not released |
| ENCODING_MISMATCH | EncodingError | UTF-8 assumed, Latin-1 received |
| DATA_CORRUPTION | ValueError, KeyError | Cache returns stale data |
| CONCURRENCY_BUG | RaceCondition, Deadlock | No synchronization primitive |
| SECURITY_BYPASS | SecurityRisk | auth check missing in one path |

---

## PHASE 3 — ROOT CAUSE GRAPH

```
Bug: NullPointer in get_profile()
  │
  ▼
Function: User.get_profile()
  │                   │
  │  confidence: 0.82  │  evidence: "No null-check at line 42"
  ▼
Class: User
  │                   │
  │  confidence: 0.65  │  evidence: "No @nullable annotation"
  ▼
Module: models/user.py
  │                   │
  │  confidence: 0.72  │  evidence: "3/5 recent bugs in this module"
  ▼
Dependency: auth.py → user.py
  │                   │
  │  confidence: 0.55  │  evidence: "auth module creates User without check"
  ▼
Library: /orm/models
  │                   │
  │  confidence: 0.30  │  evidence: "ORM allows null returns by default"
  ▼
Root Cause: MISSING_GUARD
  confidence: 0.78
  evidence: ["No null-check in function", "No validation class in module",
             "auth.py doesn't validate User before call", "3 similar NullPointer bugs"]
  recommendation: "Add @nullable annotations + InputValidator class"
```

---

## PHASE 4 — ROOT CAUSE MEMORY

Current BLM stores:
```
bug_signature: "NullPointer in payment.py:42"
bug_type: "NullPointer"
```

RC-Memory would store:
```
root_cause: "MISSING_GUARD"
source_module: "models/user.py"
source_component: "UserService"
bug_count: 12          ← 12 different bugs with same root cause
bug_types: ["NullPointer", "KeyError", "ValueError"]  ← different symptoms
fix_approach: "Add InputValidator class"
success_rate: 0.85      ← 85% of fixes worked
architectural_fix: "Add @nullable + validation layer"
```

When 13th bug arrives → RC-Brain says: "I've seen this 12 times. Root cause: MISSING_GUARD."

---

## PHASE 5 — INTEGRATION POINTS

```
TeacherBrain.enrich_prompt():
  BEFORE: "Fix this NullPointer bug"
  AFTER:  "Root cause: MISSING_GUARD (12 similar bugs).
           Affected: UserService.get_profile().
           Recommendation: Add input validation layer.
           Now fix THIS instance: NullPointer in views.py:42"

SkepticBrain.review():
  ADD: If root cause is REPEATING (>5 similar bugs):
       → risk += 0.15 ("Same class of bug keeps happening — something deeper broken")

BLM.record_experience():
  ADD: root_cause field to experiences table

OutcomeLearning:
  ADD: root_cause_patterns extraction
       "MISSING_GUARD → 85% successful when InputValidator added"
```

---

## PHASE 6 — IMPLEMENTATION

### File: `src/coding_tentacle/brains/root_cause_brain.py`

Core logic (pseudocode):

```python
class RootCauseBrain:
    ROOT_CAUSE_PATTERNS = {
        'NullPointer': {
            'primary': 'MISSING_GUARD',
            'alternatives': ['NO_VALIDATION', 'CONFIG_DRIFT', 'DATA_CORRUPTION'],
            'evidence_required': ['No null-check in function', 'No validation class'],
        },
        'RaceCondition': {
            'primary': 'CONCURRENCY_BUG',
            'alternatives': ['ASYNC_MISHANDLING', 'STATE_LEAK'],
            'evidence_required': ['Shared state without lock'],
        },
        'ImportError': {
            'primary': 'IMPORT_BREAKAGE',
            'alternatives': ['DEPRECATED_CALL', 'VERSION_MISMATCH', 'CIRCULAR_DEPENDENCY'],
            'evidence_required': ['Module path changed or removed'],
        },
        # ... 15 more patterns
    }
    
    def analyze(self, bug_type, diff, impact_data, blm_history) -> RootCauseReport:
        # L1: Bug-type → root-cause-class mapping
        candidates = self.ROOT_CAUSE_PATTERNS.get(bug_type, {})
        
        # L2: Similarity — have we seen this pattern?
        similar_bugs = blm_history.find_similar(diff, bug_type=bug_type)
        repeat_count = len(similar_bugs)
        
        # L3: Impact — what systems affected?
        affected = impact_data.get('impacted_files', [])
        
        # L4: History — same file had bugs before?
        file_history = [b for b in similar_bugs 
                       if b.get('file_path') == impact_data.get('file')]
        
        # L5: Pattern matching
        best_cause = self._match_pattern(candidates, diff, similar_bugs)
        
        return RootCauseReport(...)
    
    def _match_pattern(self, candidates, diff, similar_bugs):
        """Score each root cause candidate against evidence."""
        # Evidence scoring:
        # - No null-check in diff context: +0.30 for MISSING_GUARD
        # - No validation imports: +0.20 for NO_VALIDATION
        # - Same file had this bug before: +0.25 for repeat
        # - Multiple bug types with same root: +0.30
        # etc.
```

### Effort: 4h | ROI: 8 | Risk: Low

---

## PHASE 7 — RC51 RECOMMENDATION

```
Build RC50 RootCauseBrain V1 (4h):
  1. root_cause_brain.py — 150 LOC, 18 root cause classes
  2. RootCauseReport dataclass
  3. Wire to shadow_mode after ImpactAnalyzer
  4. Wire to TeacherBrain for prompt enrichment
  5. Wire to SkepticBrain for repeat-detection boost
  6. Add root_cause field to BLM.experiences table
  7. 10 tests (different bug types, same root cause)
  8. Regression green

Next: RC51 — 20-issue reality test with Root Cause detection
```

---

*RC50 Research & Design — Working Copy. 24. Juni 2026.*
