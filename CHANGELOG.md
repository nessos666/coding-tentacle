# Changelog

## CODING TENTACLE 10.0.V — Cybernetic Repair Agent (2026-06-28)

Architecture publication. Phase 1 complete.

### Cybernetic Architecture
- Reflection → DeuteroLearning loop closed (RC95)
- SelfObservation → Evidence wiring (RC96)
- Adaptive Homeostasis: 12 vital signs self-adjusting (RC96)
- Autonomous SelfHealing: triggered by system pathologies (RC98)
- FeedbackDampener prevents oscillation (RC95)

### Integration
- OpenCode PTY Adapter: production-ready (RC89.1)
- Benchmark Runner: resumable CLI with stats (RC86)
- Failure Taxonomy: 73% of failures = single cause (RC91)

### Kybernetik Score: 5.86 → 8.08 → ~9.0/10

### Benchmark Status
- SWE-bench Score: NOT YET FINAL (50-task run pending)
- This is an ARCHITECTURE publication. Performance data follows.

---

## v1.0.0 (2026-06-26)

### Safety
- **5-Layer VETO**: ReflexLayer → AST → Semgrep → Bandit → SafetyBrain
- **PromptInjectionBrain**: 28 patterns, multi-language, Base64/HTML/Unicode decode
- **ASTSafetyDetector**: eval, exec, subprocess, pickle detection via code structure
- **100% Safety Accuracy** on all benchmarks (internal + QuixBugs + SWE-bench Lite)
- **Zero False Allows** on security-critical patterns

### Learning
- **BLM (Bug Learning Memory)**: SQLite+FTS5 persistent fix experience store
- **EngineLearning**: Bayesian trust updates per engine per bug type
- **DeuteroLearningBrain**: Learning-to-learn (Bateson Level II)
- **ConsolidationCycle**: Wake-sleep experience compaction into rules & skills
- **Closed Learning Loops**: Outcome→Engine, BLM→Consolidation, Evidence→Learning

### LLM Agent Interface
- **RepairAgentInterface**: Unified adapter for local/cloud LLM engines
- **AlgorithmicTournament**: Multi-candidate repair with scoring & safety checks
- **BudgetGuard**: Token/time/attempt/scope limits for LLM calls
- **PatchOutputParser**: Safe parsing of LLM-generated diffs
- **MockLLMAdapter**: Test adapter generating safe, predictable patches

### Brain Architecture
- **BugModeRouter**: Classes bugs into EXCEPTION/SECURITY/ALGORITHMIC/REPO modes
- **IssueUnderstandingBrain**: Classes GitHub issues (BUG, FEATURE_REQUEST, SECURITY, etc.)
- **ContextAcquisitionBrain**: Determines precisely WHAT information is missing
- **HomeostasisBrain**: 12 vital signs with self-regulation
- **SelfHealingBrain**: MAPE-K loop + Circuit Breaker per engine
- **SelfObservationBrain**: Decision trace + bias detection + calibration audit
- **CausalChainGraph**: Bug→Function→Module→Dependency→Root trace
- **RootCauseBrain**: 18 root cause classes with historical memory

### Benchmarks
- **Internal 30-case suite**: 97% Classification, 100% Root Cause, 100% Safety
- **QuixBugs (12 tasks)**: 100% Tournament launch, 100% Safety, 0 Auto-Apply
- **SWE-bench Lite (20 tasks)**: 7 EXCEPTION, 1 ALGORITHMIC, 12 classifiable
- **Zero False Blocks, Zero False Allows** across all benchmarks

### Infrastructure
- **pytest**: 36 tests in 4 suites (safety, brains, AST, hygiene)
- **Docker**: Reproducible container with `docker build && docker run`
- **GitHub Actions CI**: Python 3.10/3.11/3.12 matrix
- **pyproject.toml**: PEP 517-compliant packaging
- **Code Hygiene**: No dead imports, no duplicate methods, verified

### Known Limitations
- LLM patches are REVIEW CANDIDATES only — never auto-applied
- Mock LLM generates template patches, not semantic fixes
- SWE-bench Patch Success Rate not yet measured
- Feature Requests, Documentation issues route to human triage
- Cloud LLM adapters are stubs (no API keys required)
- Algorithmic bugs without stacktraces need LLM for semantic understanding
- No production deployment without HumanApprovalGate

---

## v0.9.0 (2026-06-24)
- Initial public release
- ShadowMode pipeline
- SafetyBrain + SkepticBrain
- BLM + EngineLearning
- GitHub: 100% Community Health
