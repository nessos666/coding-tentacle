"""
BUDGET GUARD — RC75
Cost + time limits for LLM repair agents.
Prevents runaway cost. Hard stops.
"""
import time
from dataclasses import dataclass


@dataclass
class BudgetResult:
    allowed: bool = True
    reason: str = ''
    tokens_used: int = 0
    elapsed_s: float = 0.0
    attempts: int = 0


class BudgetGuard:
    """Enforces strict limits on LLM repair attempts."""
    
    def __init__(self, max_tokens: int = 8000, max_seconds: int = 30,
                 max_attempts: int = 3, max_patch_bytes: int = 50000,
                 max_files_changed: int = 5):
        self.max_tokens = max_tokens
        self.max_seconds = max_seconds
        self.max_attempts = max_attempts
        self.max_patch_bytes = max_patch_bytes
        self.max_files_changed = max_files_changed
        
        self.tokens_used = 0
        self.start_time = time.time()
        self.attempts = 0
    
    def check(self, tokens: int = 0, patch_bytes: int = 0,
              files_changed: int = 0) -> BudgetResult:
        """Check if operation fits within budget."""
        elapsed = time.time() - self.start_time
        self.tokens_used += tokens
        self.attempts += 1
        
        # Check each limit
        if self.tokens_used > self.max_tokens:
            return BudgetResult(False, f'Token budget exceeded: {self.tokens_used}/{self.max_tokens}',
                              self.tokens_used, elapsed, self.attempts)
        
        if elapsed > self.max_seconds:
            return BudgetResult(False, f'Time budget exceeded: {elapsed:.1f}s/{self.max_seconds}s',
                              self.tokens_used, elapsed, self.attempts)
        
        if self.attempts > self.max_attempts:
            return BudgetResult(False, f'Attempt budget exceeded: {self.attempts}/{self.max_attempts}',
                              self.tokens_used, elapsed, self.attempts)
        
        if patch_bytes > self.max_patch_bytes:
            return BudgetResult(False, f'Patch too large: {patch_bytes}/{self.max_patch_bytes} bytes',
                              self.tokens_used, elapsed, self.attempts)
        
        if files_changed > self.max_files_changed:
            return BudgetResult(False, f'Too many files: {files_changed}/{self.max_files_changed}',
                              self.tokens_used, elapsed, self.attempts)
        
        return BudgetResult(True, 'OK', self.tokens_used, elapsed, self.attempts)


# Self-test
if __name__ == "__main__":
    passed = 0
    
    print("BUDGET GUARD — Self-Test")
    print("=" * 40)
    
    # T1: Normal operation
    bg = BudgetGuard()
    r = bg.check(tokens=100, patch_bytes=500, files_changed=1)
    t1 = r.allowed
    if t1: passed += 1
    print(f"  {'✅' if t1 else '❌'} T1: Normal → allowed={r.allowed}")
    
    # T2: Token budget exceeded
    bg2 = BudgetGuard(max_tokens=10)
    r2 = bg2.check(tokens=9000)
    t2 = not r2.allowed
    if t2: passed += 1
    print(f"  {'✅' if t2 else '❌'} T2: Token budget → allowed={r2.allowed} reason={r2.reason[:40]}")
    
    # T3: Time budget exceeded
    # Can't test realistically, test large patch
    bg3 = BudgetGuard(max_patch_bytes=100)
    r3 = bg3.check(patch_bytes=50000)
    t3 = not r3.allowed
    if t3: passed += 1
    print(f"  {'✅' if t3 else '❌'} T3: Patch too large → allowed={r3.allowed}")
    
    # T4: Attempt budget exceeded
    bg4 = BudgetGuard(max_attempts=2)
    bg4.check()
    bg4.check()
    r4 = bg4.check()
    t4 = not r4.allowed
    if t4: passed += 1
    print(f"  {'✅' if t4 else '❌'} T4: Attempt limit → allowed={r4.allowed}")
    
    print(f"\n  ERGEBNIS: {passed}/4 Tests")
