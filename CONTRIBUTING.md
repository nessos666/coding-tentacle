# Contributing to Coding Tentacle

Thank you for your interest in contributing! Coding Tentacle is a safety-first code repair agent, and we welcome
contributions that improve its reliability, safety, or capabilities.

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork: `git clone https://github.com/YOUR_USERNAME/coding-tentacle.git`
3. **Install** in development mode: `pip install -e ".[dev]"`
4. **Create a branch**: `git checkout -b feature/your-feature-name`

## Development Setup

```bash
pip install -e ".[dev]"
pytest tests/ -v          # Run test suite (must be 14/14)
ct version                 # Verify CLI works
```

## Guidelines

### Code Style
- Follow **PEP 8** for Python code
- Use type hints where practical
- Keep functions small and focused — single responsibility
- Document public APIs with docstrings

### Safety First
- Never bypass the SecurityBrain VETO layer
- All generated code must pass through the safety scan pipeline
- If you add a new engine route, it must go through the same safety gates
- Test your changes against the security regression suite (10 tests)

### Testing
- **RED → GREEN → REFACTOR**: Write a failing test first, then implement
- All 14 pytest tests must pass before submitting a PR
- Add tests for new functionality
- Regression suite (10 tests) must remain green

### Pull Requests
1. Ensure tests pass: `pytest tests/ -v`
2. Update documentation if you change behavior
3. Keep PRs focused — one feature or fix per PR
4. Write a clear PR description explaining what and why
5. Reference any related issues

### Commit Messages
Write clear, concise commit messages:
```
type: Short description (max 72 chars)

Longer explanation if needed. What and why, not how.
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `security`

## Project Structure

```
src/coding_tentacle/   # Main package
tests/                 # Test suite (14 tests)
docs/                  # Documentation
examples/              # Usage examples
research/              # Research notes and papers
scripts/               # Utility scripts
```

## Need Help?

Open an [issue](https://github.com/nessos666/coding-tentacle/issues) or start a discussion. We're happy to help!

---

Thank you for making Coding Tentacle safer and better for everyone. 🐙
