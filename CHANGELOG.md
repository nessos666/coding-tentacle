# Coding Tentacle 11.0.1 — Technical Debt & Bugfix Release (2026-07-08)

## Summary

Stability release. No new features. No new brains. 31/31 tests pass.

## Changes

### Exception Handling (P0)

- **27 bare `except Exception` → proper logging** across 9 files
- 26 of 27 now use `logger.debug/warning/error/exception` with exception variable
- 1 intentional bare except retained: base64 decode (expected failure path)
- ShadowMode STEP 6B (Safety diff scan): `except→pass` → `logger.error() + report.safety_events.append()`
- Double-negative logic bugs fixed: `if not self._bug_type_trust is not None` → `if ... is None`

### Droste (P0)

- Database reindexed: 232 files, 1940 symbols, 2115 links (was v0.9.0-index)
- Renamed: `ct_v0.9.0.json` → `ct_v11.0.1.json`
- Auto-init path corrected: `~/coding-tentacle` → `~/GEHIRN_BIBLIOTHEK`

### Security (P1)

- SECURITY.md added: vulnerability reporting, architecture overview, limitations
- Safety bypass (STEP 6B) now properly logs and marks `SAFETY_SCAN_DEGRADED`

### Bug Fixes

- Self-test `t2 = report.recommendation` (string) → `bool()` (pre-existing bug)
- Version bump: 11.0.0 → 11.0.1

### Logging Standardization

All production modules now import `logging.getLogger(__name__)`:
- sandbox_runner.py, engine_learning.py, teacher_student.py
- engine_router.py, bug_learning_memory.py, experience_consolidator.py
- procedural_memory.py, impact_analyzer.py

## Regression

| Suite | Result |
|-------|--------|
| pytest (14) | ✅ 14/14 |
| Regression (10) | ✅ 10/10 |
| Shadow Mode Self-Test (7) | ✅ 7/7 |
| **Total** | **31/31** |

## Exception Statistics

| | Before | After |
|---|--------|-------|
| Bare `except Exception:` | 27 | 1 (intentional) |
| Silent `except: pass` | 12 | 0 |
| Files without logger | 8 | 0 |
