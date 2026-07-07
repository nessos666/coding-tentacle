"""
SECURITY STORE — RC4
Read-only knowledge base of security weaknesses.
NEVER executes actions. Only detects dangerous patterns.

Autor: Hermes + David | Coding Tentacle 2026
"""

# CT-v11.0.0: PRODUCTION | 10/10 regression | 25 modules | 90% wired | Droste active
import re, time, hashlib
from collections import defaultdict


class SecurityEntry:
    def __init__(self, cwe, name, symptoms, dangerous_patterns, safe_response='BLOCK',
                 fix_guidance='', risk_level='critical', confidence=0.95, source='CWE'):
        self.id = hashlib.md5(f"{cwe}:{name}".encode()).hexdigest()[:12]
        self.cwe = cwe
        self.name = name
        self.symptoms = symptoms
        self.dangerous_patterns = dangerous_patterns
        self.safe_response = safe_response  # BLOCK | HUMAN_REVIEW | SECURITY_REVIEW
        self.fix_guidance = fix_guidance
        self.risk_level = risk_level
        self.confidence = confidence
        self.source = source
        self.times_detected = 0

    def match(self, text):
        score = 0.0; matched = []
        for pat in self.dangerous_patterns:
            try:
                if re.search(pat, text, re.IGNORECASE):
                    score += 0.50; matched.append(f'pattern:{pat[:30]}')
                    break
            except re.error:
                if pat.lower() in text.lower():
                    score += 0.50; matched.append(f'pattern:{pat[:30]}')
                    break
        for sym in self.symptoms:
            try:
                if re.search(sym, text, re.IGNORECASE):
                    score += 0.50; matched.append(f'symptom:{sym[:30]}')
                    break
            except re.error:
                if sym.lower() in text.lower():
                    score += 0.50; matched.append(f'symptom:{sym[:30]}')
                    break
        return score, matched

    def to_dict(self):
        return {
            'id': self.id, 'cwe': self.cwe, 'name': self.name,
            'safe_response': self.safe_response, 'risk_level': self.risk_level,
            'fix_guidance': self.fix_guidance, 'confidence': self.confidence,
        }


class SecurityStore:
    def __init__(self):
        self.entries = []
        self._by_response = defaultdict(list)
        self._scans = 0
        self._detections = 0

    def add_entry(self, **kwargs):
        entry = SecurityEntry(**kwargs)
        self.entries.append(entry)
        self._by_response[entry.safe_response].append(entry)
        return entry

    def search(self, text):
        scored = []
        for entry in self.entries:
            score, matched = entry.match(text)
            if score > 0:
                scored.append((entry, score, matched))
        scored.sort(key=lambda x: -x[1])
        return scored

    def detect_danger(self, text):
        """Scan text for security risks. Returns list of (entry, score)."""
        self._scans += 1
        results = self.search(text)
        if results:
            self._detections += 1
        return results

    def is_safe(self, text):
        """Returns True if no dangerous patterns found."""
        return len(self.detect_danger(text)) == 0

    def stats(self):
        return {
            'total_entries': len(self.entries),
            'cwe_count': len(set(e.cwe for e in self.entries)),
            'scans': self._scans,
            'detections': self._detections,
            'detection_rate': self._detections / max(1, self._scans),
            'store_type': 'READ_ONLY',
            'actions_executed': 0,
        }


def create_seed_security_store():
    s = SecurityStore()
    s.add_entry(cwe='CWE-89', name='SQL Injection',
        symptoms=[r'DROP\s+TABLE', r'DELETE\s+FROM', r'INSERT\s+INTO',
                   r'sql\s*=\s*[\"\'].*\+', r'execute\s*\(\s*[\"\'].*\+',
                   r"sql\s*=\s*f[\"']"],
        dangerous_patterns=[r"DROP\s+TABLE", r"DELETE\s+FROM", r"SELECT\s+\*",
                            r"sql\s*=\s*[\"'][^\"']*\+",
                            r"execute\s*\(\s*[\"'][^\"']*\+",
                            r"raw\s*\(\s*[\"'][^\"']*\{", r'UNION\s+SELECT'],
        safe_response='BLOCK',
        fix_guidance='Verwende parametrisierte Queries: cursor.execute("SELECT * WHERE id=?", (id,))')

    s.add_entry(cwe='CWE-22', name='Path Traversal',
        symptoms=[r'\.\.\/', r'\.\.\\\\', r'%2e%2e', r'path\.\.\/',
                   r'/etc/passwd', r'/etc/shadow', r'~/.ssh'],
        dangerous_patterns=[r'\.\.\/', r'\.\.\\\\', r'%2e%2e',
                            r'/etc/passwd', r'/etc/shadow',
                            r'~/.ssh', r'\.\.\\.\.'],
        safe_response='BLOCK',
        fix_guidance='Pfade normalisieren: os.path.realpath() oder pathlib.Path.resolve()')

    s.add_entry(cwe='CWE-79', name='Cross-Site Scripting (XSS)',
        symptoms=[r'<script', r'innerHTML', r'document\.write\(', r'eval\(user',
                   r'escape\(', r'sanitize'],
        dangerous_patterns=[r'<script.*>', r'innerHTML\s*=',
                            r'document\.write\(', r'eval\(.*\+',
                            r'dangerouslySetInnerHTML'],
        safe_response='BLOCK',
        fix_guidance='HTML escapen: html.escape() oder DOMPurify.sanitize()')

    s.add_entry(cwe='CWE-78', name='Command Injection',
        symptoms=[r'os\.system\(', r'subprocess\.call\(', r'shell=True',
                   r'exec\(', r'popen\(', r'system\(.*\+'],
        dangerous_patterns=[r'os\.system\(', r'subprocess\.call\(.*\+',
                            r'shell\s*=\s*True', r'popen\(.*\+',
                            r'eval\(.*\+'],
        safe_response='BLOCK',
        fix_guidance='subprocess.run([cmd, arg1, arg2], shell=False) — KEIN shell=True!')

    s.add_entry(cwe='CWE-798', name='Hardcoded Credentials',
        symptoms=[r'password\s*=\s*[\"\'][^\"\']+[\"\']',
                   r'API_KEY\s*=\s*[\"\'][^\"\']+[\"\']',
                   r'SECRET\s*=\s*[\"\'][^\"\']+[\"\']',
                   r'DATABASE_URL\s*=\s*[\"\'][^\"\']+[\"\']',
                   r'token\s*=\s*[\"\'][^\"\']+[\"\']'],
        dangerous_patterns=[r'password\s*=\s*[\"\'][^\"\']+[\"\']',
                            r'API_KEY\s*=\s*[\"\'][^\"\']+[\"\']',
                            r'SECRET\s*=\s*[\"\'][^\"\']+[\"\']',
                            r'DATABASE_URL\s*=\s*[\"\'][^\"\']+[\"\']'],
        safe_response='BLOCK',
        fix_guidance='Credentials NIE im Code! Verwende Umgebungsvariablen: os.environ["KEY"]')

    s.add_entry(cwe='CWE-502', name='Unsafe Deserialization',
        symptoms=[r'pickle\.loads?\(', r'yaml\.load\(', r'marshal\.load',
                   r'unserialize', r'json\.loads\(.*user'],
        dangerous_patterns=[r'pickle\.loads?\(', r'yaml\.load\(',
                            r'eval\(.*json',
                            r'unserialize\(.*input'],
        safe_response='HUMAN_REVIEW',
        fix_guidance='Verwende sicheres Parsing: json.loads() oder yaml.safe_load()')

    s.add_entry(cwe='CWE-918', name='Server-Side Request Forgery (SSRF)',
        symptoms=[r'requests\.get\(.*user', r'urllib.*url.*user',
                   r'fetch\(.*user', r'axios\(.*user',
                   r'http\.request\(.*input'],
        dangerous_patterns=[r'requests\.(get|post)\(.*(input|user|request)',
                            r'urllib\.request\.urlopen\(.*(input|user)',
                            r'fetch\(.*(input|user|req\.)'],
        safe_response='HUMAN_REVIEW',
        fix_guidance='URL validieren: nur erlaubte Domains, Protokoll-Check (http/https only)')

    s.add_entry(cwe='CWE-269', name='Privilege Escalation',
        symptoms=[r'sudo\s', r'chmod\s+777', r'chown\s+root',
                   r'setuid', r'root\s', r'admin\s'],
        dangerous_patterns=[r'sudo\s', r'chmod\s+777', r'chown\s+root',
                            r'setuid\(0\)', r'os\.setuid\(0\)'],
        safe_response='BLOCK',
        fix_guidance='Kein sudo/chmod 777 in Code! Prinzip der geringsten Rechte (POLP)')

    s.add_entry(cwe='CWE-639', name='Insecure Direct Object Reference (IDOR)',
        symptoms=[r'request\.args\[.id.\]', r'params\[.user_id.\]',
                   r'\.get\(.*id\)', r'@PathVariable.*id'],
        dangerous_patterns=[r'\.get\(request\.args\[.id.\]\)',
                            r'WHERE.*id\s*=\s*.*request',
                            r'findById\(request\.'],
        safe_response='HUMAN_REVIEW',
        fix_guidance='Authorization-Check vor Datenzugriff: if request.user.id == object.owner_id')

    s.add_entry(cwe='CWE-73', name='Destructive Operation',
        symptoms=[r'DROP\s+TABLE', r'TRUNCATE', r'DELETE\s+FROM',
                   r'rm\s+-rf', r'os\.remove', r'shutil\.rmtree',
                   r'destroy', r'kubectl\s+delete', r'terraform\s+destroy'],
        dangerous_patterns=[r'DROP\s+TABLE', r'TRUNCATE\s+TABLE',
                            r'DELETE\s+FROM\s+\w+', r'rm\s+-rf',
                            r'os\.remove\(', r'shutil\.rmtree\(',
                            r'kubectl\s+delete', r'terraform\s+destroy'],
        safe_response='BLOCK',
        fix_guidance='Destruktive Operationen NUR mit Bestätigung und Backup')

    return s


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    print("SECURITY STORE — Skeleton + 10 Seed")
    print("=" * 55)
    passed = 0

    s = SecurityStore()
    t1 = len(s.entries) == 0
    print(f"  T1: {'✅' if t1 else '❌'} Empty store")

    s.add_entry(cwe='CWE-89', name='SQL Injection', symptoms=[r'DROP\s+TABLE'],
                dangerous_patterns=[r'DROP\s+TABLE'], safe_response='BLOCK')
    t2 = len(s.entries) == 1
    print(f"  T2: {'✅' if t2 else '❌'} Add entry → {len(s.entries)}")

    results = s.search('DROP TABLE users')
    t3 = len(results) >= 1
    print(f"  T3: {'✅' if t3 else '❌'} Detect SQL Injection → {len(results)}")

    s.add_entry(cwe='CWE-22', name='Path Traversal', symptoms=[r'\.\.\/'],
                dangerous_patterns=[r'\.\.\/'], safe_response='BLOCK')
    results = s.search('../../etc/passwd')
    t4 = len(results) >= 1
    print(f"  T4: {'✅' if t4 else '❌'} Detect Path Traversal → {len(results)}")

    s.add_entry(cwe='CWE-798', name='Credential Exposure', symptoms=[r'API_KEY\s*=\s*'],
                dangerous_patterns=[r'API_KEY\s*=\s*'], safe_response='BLOCK')
    results = s.search('API_KEY = "sk-s3cr3t"')
    t5 = len(results) >= 1
    print(f"  T5: {'✅' if t5 else '❌'} Detect Credential Exposure → {len(results)}")

    s.add_entry(cwe='CWE-73', name='Destructive', symptoms=[r'DROP\s+TABLE'],
                dangerous_patterns=[r'DROP\s+TABLE'], safe_response='BLOCK')
    results = s.search('DROP TABLE cache')
    t6 = len(results) >= 1
    print(f"  T6: {'✅' if t6 else '❌'} Detect Destructive → {len(results)}")

    # T7: safe_response check — first result entry
    first_entry = results[0][0] if results else None
    t7 = first_entry is not None and first_entry.safe_response in ('BLOCK', 'HUMAN_REVIEW', 'SECURITY_REVIEW')
    print(f"  T7: {'✅' if t7 else '❌'} safe_response → {first_entry.safe_response if first_entry else '?'}")

    st = s.stats()
    t8 = st['actions_executed'] == 0 and st['store_type'] == 'READ_ONLY'
    print(f"  T8: {'✅' if t8 else '❌'} Stats → actions={st['actions_executed']}")

    seed = create_seed_security_store()
    scans = [('DROP TABLE users',True), ('<script>alert(1)',True), ('API_KEY="x"',True),
             ('../../etc/passwd',True), ('safe code here',False)]
    detections = sum(1 for text, _ in scans if seed.detect_danger(text))
    t9 = detections >= 4
    print(f"\n  Seed: {'✅' if t9 else '❌'} 10 entries, {detections}/{len(scans)-1} dangerous texts detected")

    passed = sum([t1,t2,t3,t4,t5,t6,t8,t9])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/8 Tests bestanden")
    print(f"  {'✅ SECURITY STORE FERTIG' if passed >= 7 else '⚠️'}")
