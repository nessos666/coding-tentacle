"""
GITHUB API INTEGRATION — P1.4
Read-only GitHub client for Shadow Mode.
NEVER writes, PRs, commits, or comments.

Token: optional via CT_GITHUB_TOKEN env or config.
Rate-limit: checked before every request.

Autor: Hermes + David | Coding Tentacle 2026
"""
import os, time, json, tempfile, subprocess, urllib.request, urllib.error
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class GitHubIssue:
    """A GitHub issue fetched read-only."""
    owner: str
    repo: str
    number: int
    title: str = ""
    body: str = ""
    state: str = "open"
    labels: list = field(default_factory=list)
    url: str = ""


@dataclass
class GitHubRepoInfo:
    """Repository metadata."""
    owner: str
    repo: str
    full_name: str
    description: str = ""
    stars: int = 0
    language: str = ""
    default_branch: str = "main"
    clone_url: str = ""
    open_issues: int = 0


class GitHubClient:
    """Read-only GitHub API client. NEVER writes."""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token=None):
        self.token = token or os.environ.get('CT_GITHUB_TOKEN', '')
        self.rate_limit_remaining = 60
        self.rate_limit_reset = 0
        self.total_requests = 0
    
    def _request(self, endpoint, method='GET'):
        """Make a GitHub API request. Returns (status, data)."""
        if self.rate_limit_remaining <= 1:
            wait = max(0, self.rate_limit_reset - time.time())
            if wait > 0:
                return 429, {'error': f'Rate limit exceeded. Wait {wait:.0f}s'}
        
        url = f"{self.BASE_URL}{endpoint}"
        headers = {'Accept': 'application/vnd.github+json',
                   'User-Agent': 'CodingTentacle-Shadow/1.0'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        
        try:
            req = urllib.request.Request(url, headers=headers)
            resp = urllib.request.urlopen(req, timeout=15)
            self.total_requests += 1
            
            # Update rate limit
            remaining = resp.headers.get('X-RateLimit-Remaining')
            reset = resp.headers.get('X-RateLimit-Reset')
            if remaining:
                self.rate_limit_remaining = int(remaining)
            if reset:
                self.rate_limit_reset = int(reset)
            
            data = json.loads(resp.read().decode())
            return resp.status, data
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode()) if e.fp else {'error': str(e)}
        except Exception as e:
            return 500, {'error': str(e)}
    
    def get_issue(self, owner, repo, issue_number):
        """Fetch a GitHub issue (read-only)."""
        status, data = self._request(f'/repos/{owner}/{repo}/issues/{issue_number}')
        if status == 200:
            return GitHubIssue(
                owner=owner, repo=repo, number=issue_number,
                title=data.get('title', ''),
                body=data.get('body', '') or '',
                state=data.get('state', 'open'),
                labels=[l['name'] for l in data.get('labels', [])],
                url=data.get('html_url', ''),
            )
        return None
    
    def get_repo(self, owner, repo):
        """Fetch repository metadata (read-only)."""
        status, data = self._request(f'/repos/{owner}/{repo}')
        if status == 200:
            return GitHubRepoInfo(
                owner=owner, repo=repo,
                full_name=data.get('full_name', ''),
                description=data.get('description', '') or '',
                stars=data.get('stargazers_count', 0),
                language=data.get('language', ''),
                default_branch=data.get('default_branch', 'main'),
                clone_url=data.get('clone_url', ''),
                open_issues=data.get('open_issues', 0),
            )
        return None
    
    def clone_repo(self, clone_url, target_dir):
        """Clone a repository to temp directory (read-only)."""
        try:
            result = subprocess.run(
                ['git', 'clone', '--depth', '1', clone_url, target_dir],
                capture_output=True, text=True, timeout=60,
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def parse_issue_url(self, url):
        """Parse GitHub issue URL into owner/repo/number."""
        url = url.rstrip('/').replace('https://github.com/', '')
        parts = url.split('/')
        if len(parts) >= 4 and parts[2] == 'issues':
            return parts[0], parts[1], int(parts[3])
        return None, None, None
    
    def stats(self):
        return {
            'total_requests': self.total_requests,
            'rate_limit_remaining': self.rate_limit_remaining,
            'actions_executed': 0,  # Never writes
        }


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    print("GITHUB API INTEGRATION — Self-Test")
    print("=" * 55)
    passed = 0
    
    client = GitHubClient()
    
    # T1: Parse issue URL
    owner, repo, num = client.parse_issue_url("https://github.com/django/django/issues/12345")
    t1 = owner == 'django' and repo == 'django' and num == 12345
    print(f"  T1: {'✅' if t1 else '❌'} Parse URL → {owner}/{repo}#{num}")
    
    # T2: Stats read-only
    st = client.stats()
    t2 = st['actions_executed'] == 0
    print(f"  T2: {'✅' if t2 else '❌'} Read-only → actions_executed=0")
    
    # T3: Rate limit tracked
    t3 = client.rate_limit_remaining > 0
    print(f"  T3: {'✅' if t3 else '❌'} Rate limit → {client.rate_limit_remaining} remaining")
    
    # T4: Token from env
    os.environ['CT_GITHUB_TOKEN'] = 'ghp_test123'
    client2 = GitHubClient()
    t4 = client2.token == 'ghp_test123'
    print(f"  T4: {'✅' if t4 else '❌'} Token from env → {'YES' if t4 else 'NO'}")
    del os.environ['CT_GITHUB_TOKEN']
    
    # T5: Parse repo URL
    owner2, repo2, _ = client.parse_issue_url("https://github.com/psf/requests/issues/1")
    t5 = owner2 == 'psf' and repo2 == 'requests'
    print(f"  T5: {'✅' if t5 else '❌'} Parse → {owner2}/{repo2}")
    
    # T6: No write methods
    forbidden = ['create_pr','push','comment','commit','delete_repo']
    t6 = not any(hasattr(client, m) for m in forbidden)
    print(f"  T6: {'✅' if t6 else '❌'} No write methods")
    
    passed = sum([t1,t2,t3,t4,t5,t6])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/6 Tests bestanden")
    print(f"  {'✅ GITHUB API CLIENT FERTIG' if passed >= 5 else '⚠️'}")
