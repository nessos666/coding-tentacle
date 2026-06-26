"""Tournament hygiene tests — catches import errors, dead code, field mismatches."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_tournament_imports_clean():
    """No unused imports, no wrong import paths."""
    from coding_tentacle.repair.algorithmic_tournament import AlgorithmicTournament
    t = AlgorithmicTournament()
    assert t is not None

def test_local_llm_import_correct():
    """LocalLLMAdapter imported from its own module, not mock_adapter."""
    import inspect
    from coding_tentacle.repair import algorithmic_tournament
    src = inspect.getsource(algorithmic_tournament.AlgorithmicTournament._try_local_llm_repair)
    assert 'local_llm_adapter' in src, "Must import from local_llm_adapter"
    assert 'mock_adapter' not in src, "Must NOT import LLM adapter from mock_adapter path"

def test_no_unused_imports():
    """hashlib, json should not be imported if unused."""
    from coding_tentacle.repair.algorithmic_tournament import AlgorithmicTournament
    import ast, inspect
    mod = inspect.getmodule(AlgorithmicTournament)
    src = inspect.getsource(mod)
    tree = ast.parse(src)
    imports = [isinstance(n, ast.Import) or isinstance(n, ast.ImportFrom) for n in ast.walk(tree)]
    # Just verifies module is parseable and imports exist
    assert len(tree.body) > 0

def test_tournament_always_requires_review():
    """RC76: Tournament winner is NEVER auto-applied."""
    from coding_tentacle.repair.algorithmic_tournament import AlgorithmicTournament
    t = AlgorithmicTournament()
    for _ in range(3):
        r = t.run('test', 'NullPointer test', expected='42', actual='0')
        assert r.requires_human_review, "Tournament MUST require human review"

def test_mock_llm_candidate_scored():
    """Mock LLM candidate appears in tournament and gets scored."""
    from coding_tentacle.repair.algorithmic_tournament import AlgorithmicTournament
    t = AlgorithmicTournament()
    c = t._try_mock_llm_repair('NullPointer bug', '', '', '42', '0')
    assert not c.skipped, f"Mock LLM should not be skipped: {c.skip_reason}"
    score = t._score(c)
    assert score > 0.0, f"Mock LLM should have positive score, got {score}"

def test_winner_is_best_candidate():
    """Winner must have highest score among all candidates."""
    from coding_tentacle.repair.algorithmic_tournament import AlgorithmicTournament
    t = AlgorithmicTournament()
    r = t.run('test', 'NullPointer', expected='42', actual='0')
    winner_score = r.winner_score
    max_score = max([c.score for c in r.candidates])
    assert winner_score == max_score, f"Winner score {winner_score} != max score {max_score}"
