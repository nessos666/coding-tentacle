# Contributing to Coding Tentacle

Thanks for your interest! Coding Tentacle is a research/shadow-release project.

## How to contribute

1. **Open an issue** — Bug reports, feature ideas, questions
2. **Fork + PR** — Fork, branch, commit, PR
3. **Shadow Mode only** — Never commit/apply fixes to real repos

## Rules

- Safety VETO is absolute — never bypass
- All changes must pass `python3 scripts/full_regression.py`
- No auto-apply, no auto-PR, no auto-commit
- Keep modules independent and self-testable

## Development

```bash
git clone https://github.com/nessos666/coding-tentacle.git
cd coding-tentacle
python3 scripts/full_regression.py  # Should show ALL TESTS PASSED
```
