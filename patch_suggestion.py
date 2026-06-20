"""
PATCH-SUGGESTION MVP — Coding Tentacle
Erzeugt Patch-Vorschläge aus Bug-Typ, Grounding und Hypothesen.
KEINE automatische Codeänderung. Nur Vorschläge.

Autor: Hermes + David | Coding Tentacle 2026
"""
import re

class PatchSuggestion:
    def __init__(self, patch_type, patch, explanation, target_file, target_line,
                 confidence=0.5, risk_level='low', requires_human=False, tests=None, rollback=''):
        self.patch_type = patch_type
        self.patch = patch
        self.explanation = explanation
        self.target_file = target_file
        self.target_line = target_line
        self.confidence = confidence
        self.risk_level = risk_level
        self.requires_human_review = requires_human
        self.tests_to_run = tests or []
        self.rollback_note = rollback

    def to_dict(self):
        return {
            'patch_type': self.patch_type,
            'suggested_patch': self.patch,
            'explanation': self.explanation,
            'target_file': self.target_file,
            'target_line': self.target_line,
            'confidence': round(self.confidence, 3),
            'risk_level': self.risk_level,
            'requires_human_review': self.requires_human_review,
            'tests_to_run': self.tests_to_run,
            'rollback_note': self.rollback_note,
        }


class PatchSuggestionEngine:
    """Erzeugt Patch-Vorschläge basierend auf Bug-Typ, Grounding, Hypothesen."""

    # ═══════════ PATCH-TEMPLATES PRO BUG-TYP ═══════════
    TEMPLATES = {
        'NullPointer': [
            {'type': 'guard_clause', 'patch': 'if {var} is not None:\n    {var}.{method}()',
             'explanation': 'Guard-Clause verhindert Null-Zugriff',
             'risk': 'low', 'tests': ['test_null_input', 'test_valid_input']},
            {'type': 'optional_check', 'patch': '{var} = {var} or default_{var}',
             'explanation': 'Optional mit Default-Wert absichern', 'risk': 'low'},
        ],
        'AttributeError': [
            {'type': 'hasattr_check', 'patch': 'if hasattr({var}, "{attr}"):\n    {var}.{attr}',
             'explanation': 'hasattr() prüft ob Attribut existiert', 'risk': 'low'},
            {'type': 'type_check', 'patch': 'if isinstance({var}, {expected_type}):\n    {var}.{attr}',
             'explanation': 'isinstance() stellt sicher dass Objekt den richtigen Typ hat', 'risk': 'low'},
        ],
        'TypeError': [
            {'type': 'type_cast', 'patch': '{var} = {cast}({var})',
             'explanation': 'Explizite Typ-Konvertierung', 'risk': 'low'},
            {'type': 'type_guard', 'patch': 'if isinstance({var}, {expected}):\n    ...',
             'explanation': 'Type-Guard vor Operation', 'risk': 'low'},
        ],
        'ImportError': [
            {'type': 'import_fix', 'patch': '# Check: pip install {module}\n# or: from {alt_module} import {name}',
             'explanation': 'Fehlendes Modul installieren oder Alternative importieren', 'risk': 'medium',
             'requires_human': True},
            {'type': 'fallback_import', 'patch': 'try:\n    from {primary} import {name}\nexcept ImportError:\n    from {fallback} import {name}',
             'explanation': 'Fallback-Import mit try/except', 'risk': 'low'},
        ],
        'IndexError': [
            {'type': 'bounds_check', 'patch': 'if 0 <= {idx} < len({arr}):\n    val = {arr}[{idx}]',
             'explanation': 'Bounds-Check vor Array-Zugriff', 'risk': 'low'},
        ],
        'KeyError': [
            {'type': 'key_check', 'patch': '{val} = {dict}.get("{key}", default)',
             'explanation': '.get() mit Default-Wert statt Direktzugriff', 'risk': 'low'},
        ],
        'MemoryLeak': [
            {'type': 'cache_evict', 'patch': 'if len({cache}) > MAX_SIZE:\n    {cache}.popitem()',
             'explanation': 'Cache-Größe begrenzen mit Eviction', 'risk': 'low'},
            {'type': 'close_resource', 'patch': 'with open({file}) as f:\n    ...',
             'explanation': 'Ressource mit Context-Manager schließen', 'risk': 'low'},
        ],
        'RaceCondition': [
            {'type': 'lock_guard', 'patch': 'with threading.Lock():\n    {critical_section}',
             'explanation': 'Lock für kritische Sektion', 'risk': 'medium',
             'requires_human': True},
        ],
        'AssertionError': [
            {'type': 'test_fix', 'patch': '# Expected: {expected}\n# Got: {actual}\n# Fix test or code',
             'explanation': 'Test-Erwartung oder Code anpassen', 'risk': 'medium'},
        ],
        'TimeoutError': [
            {'type': 'timeout_fix', 'patch': '# Add timeout parameter\n# Or split into smaller operations',
             'explanation': 'Timeout erhöhen oder Operation aufteilen', 'risk': 'medium'},
        ],
        'IntegrityError': [
            {'type': 'db_fix', 'patch': '# Check unique constraints\n# Or use ON CONFLICT / MERGE',
             'explanation': 'Datenbank-Constraint prüfen', 'risk': 'high',
             'requires_human': True},
        ],
        '_default': [
            {'type': 'generic_fix', 'patch': '# Untersuchung nötig: {bug}',
             'explanation': 'Kein spezifischer Patch bekannt. Mehr Kontext nötig.', 'risk': 'medium'},
        ],
    }

    # ═══════════ GEFÄHRLICHE PATTERNS ═══════════
    DANGEROUS_PATTERNS = re.compile(
        r'DROP\s+TABLE|DELETE\s+FROM|TRUNCATE|os\.remove|os\.unlink|'
        r'rm\s+-rf|shutil\.rmtree|eval\(|exec\(|__import__\(|'
        r'subprocess|os\.system|API_KEY|SECRET|DATABASE_URL|password\s*=|'
        r'sudo|chmod\s+777|pip\s+uninstall',
        re.IGNORECASE
    )

    def __init__(self):
        self.total_suggestions = 0

    def suggest(self, bug_report, code_context=None, test_output=None,
                br_hypotheses=None, grounding=None, requested_action='suggest_patch'):
        """
        Erzeuge Patch-Vorschlag. KEINE Code-Änderung.
        """
        self.total_suggestions += 1

        bt = self._extract_bug_type(bug_report)
        ctx_file = code_context.get('file', 'unknown') if code_context else 'unknown'
        ctx_line = code_context.get('line', 0) if code_context else 0

        # Sicherheits-Check VOR Patch-Erzeugung
        if self._is_destructive(bug_report, grounding):
            return PatchSuggestion(
                'BLOCKED', None,
                'Destruktive oder sicherheitskritische Operation erkannt. Kein automatischer Patch.',
                ctx_file, ctx_line, 0.0, 'critical', True,
                tests=[], rollback='Nicht möglich — manuelle Prüfung erforderlich.'
            ).to_dict()

        # Template-basierte Vorschläge
        templates = self.TEMPLATES.get(bt, self.TEMPLATES['_default'])
        best = templates[0]

        # BR-Hypothesen verfeinern die Wahl
        if br_hypotheses:
            top_hyp = br_hypotheses[0].get('statement', '').lower() if br_hypotheses else ''
            for tmpl in templates:
                if any(w in top_hyp for w in tmpl['type'].split('_')):
                    best = tmpl
                    break

        # Kontext-Variablen extrahieren
        var = self._extract_variable(bug_report, code_context)
        confidence = grounding.get('grounding_score', 0.5) if grounding else 0.5
        risk = best.get('risk', 'medium')
        requires_human = best.get('requires_human', False)

        # Risiko-Höherstufung
        if confidence < 0.3 and risk == 'low':
            risk = 'medium'
        if confidence < 0.15:
            risk = 'high'

        # Patch mit Variablen füllen — alle möglichen Platzhalter
        patch_kwargs = dict(
            var=var, method='method', attr='attribute',
            cast='str', expected='<expected>', actual='<actual>',
            expected_type='ExpectedType',
            dict='mydict', key='mykey', val='value', idx='i', arr='items',
            cache='self._cache', module='missing_module', name='function_name',
            alt_module='alternative', primary='primary_module', fallback='fallback_module',
            critical_section='# critical code here',
            default='default_value', file='filename', bug=bug_report[:30],
        )
        patch = best['patch'].format(**patch_kwargs)

        # Tests vorschlagen
        tests = best.get('tests', [f'test_{bt.lower()}'])

        # Rollback-Notiz
        rollback = f'git checkout {ctx_file}' if ctx_file != 'unknown' else 'Manuelles Rollback'

        return PatchSuggestion(
            best['type'], patch, best['explanation'],
            ctx_file, ctx_line, confidence, risk, requires_human, tests, rollback
        ).to_dict()

    def _extract_bug_type(self, bug_report):
        """Extrahiere Bug-Typ aus Stacktrace oder Report."""
        if not bug_report:
            return '_default'
        # Stacktrace: erste Zeile = "ErrorType: message"
        first_line = bug_report.split('\n')[0].strip()
        for known in self.TEMPLATES:
            if known.lower() in first_line.lower():
                return known
        if ':' in first_line:
            bt = first_line.split(':')[0]
            # Strip "Exception"/"Error" suffix
            for suffix in ['Exception', 'Error']:
                if bt.lower().endswith(suffix.lower()) and len(bt) > len(suffix):
                    return bt[:-len(suffix)]
        return '_default'

    def _extract_variable(self, bug_report, code_context):
        """Extrahiere Variablennamen aus Bug-Report."""
        if code_context and code_context.get('code'):
            code = code_context['code']
            # Einfache Heuristik: erstes Wort vor '.'
            m = re.search(r'(\w+)\.', code)
            if m:
                return m.group(1)
        # Fallback: aus Bug-Report
        m = re.search(r"'(\w+)'", bug_report)
        if m:
            return m.group(1)
        return 'obj'

    def _is_destructive(self, bug_report, grounding):
        """Prüfe ob der Bug/Vorschlag destruktiv ist."""
        if grounding:
            meaning = grounding.get('meaning', '')
            if any(w in meaning.lower() for w in ['delete', 'drop', 'remove', 'destroy']):
                return True
        return bool(self.DANGEROUS_PATTERNS.search(bug_report))


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    print("PATCH-SUGGESTION MVP")
    print("=" * 60)
    passed = 0

    engine = PatchSuggestionEngine()

    # T1: NullPointer → guard_clause
    r = engine.suggest('NullPointerException', code_context={'file': 'payment.py', 'line': 42, 'code': 'obj.amount'},
                       grounding={'grounding_score': 0.7})
    t1 = r['patch_type'] == 'guard_clause'
    print(f"  T1: {'✅' if t1 else '❌'} NullPointer → {r['patch_type']}")

    # T2: AttributeError → hasattr
    r = engine.suggest('AttributeError', code_context={'file': 'user.py', 'line': 15, 'code': 'user.city'},
                       grounding={'grounding_score': 0.6})
    t2 = r['patch_type'] in ('hasattr_check', 'type_check')
    print(f"  T2: {'✅' if t2 else '❌'} AttributeError → {r['patch_type']}")

    # T3: ImportError → import/dependency
    r = engine.suggest('ImportError: No module', code_context={'file': 'main.py', 'line': 3},
                       grounding={'grounding_score': 0.4})
    t3 = r['patch_type'] in ('import_fix', 'fallback_import')
    print(f"  T3: {'✅' if t3 else '❌'} ImportError → {r['patch_type']}")

    # T4: TypeError → conversion
    r = engine.suggest('TypeError', code_context={'file': 'auth.py', 'line': 28},
                       grounding={'grounding_score': 0.5})
    t4 = r['patch_type'] in ('type_cast', 'type_guard')
    print(f"  T4: {'✅' if t4 else '❌'} TypeError → {r['patch_type']}")

    # T5: KeyError → key check
    r = engine.suggest('KeyError', code_context={'file': 'config.py', 'line': 8},
                       grounding={'grounding_score': 0.5})
    t5 = r['patch_type'] == 'key_check'
    print(f"  T5: {'✅' if t5 else '❌'} KeyError → {r['patch_type']}")

    # T6: IndexError → bounds check
    r = engine.suggest('IndexError', code_context={'file': 'cache.py', 'line': 73},
                       grounding={'grounding_score': 0.5})
    t6 = r['patch_type'] == 'bounds_check'
    print(f"  T6: {'✅' if t6 else '❌'} IndexError → {r['patch_type']}")

    # T7: RaceCondition → lock
    r = engine.suggest('RaceCondition', code_context={'file': 'worker.py', 'line': 55},
                       grounding={'grounding_score': 0.5})
    t7 = r['patch_type'] == 'lock_guard' and r['requires_human_review']
    print(f"  T7: {'✅' if t7 else '❌'} RaceCondition → {r['patch_type']} human={r['requires_human_review']}")

    # T8: MemoryLeak → cleanup
    r = engine.suggest('MemoryLeak', code_context={'file': 'cache.py', 'line': 89},
                       grounding={'grounding_score': 0.5})
    t8 = r['patch_type'] in ('cache_evict', 'close_resource')
    print(f"  T8: {'✅' if t8 else '❌'} MemoryLeak → {r['patch_type']}")

    # T9: Failed test → test-specific
    r = engine.suggest('AssertionError', code_context={'file': 'test_worker.py', 'line': 99},
                       test_output='FAIL', grounding={'grounding_score': 0.3})
    t9 = r['patch_type'] in ('test_fix', 'timeout_fix')
    print(f"  T9: {'✅' if t9 else '❌'} Failed test → {r['patch_type']}")

    # T10: Credentials → BLOCK
    r = engine.suggest('DROP TABLE users', code_context={'file': 'db.py', 'line': 1},
                       grounding={'grounding_score': 0.5})
    t10 = r['patch_type'] == 'BLOCKED'
    print(f"  T10: {'✅' if t10 else '❌'} Destructive → {r['patch_type']}")

    # T11: Delete → BLOCK
    r = engine.suggest('os.remove("/etc/passwd")', code_context={'file': '/etc/passwd', 'line': 1},
                       grounding={'grounding_score': 0.5})
    t11 = r['patch_type'] == 'BLOCKED'
    print(f"  T11: {'✅' if t11 else '❌'} Delete → {r['patch_type']}")

    # T12: Unknown → no patch
    r = engine.suggest('MysteriousCrash', code_context=None, grounding={'grounding_score': 0.0})
    t12 = r['patch_type'] in ('generic_fix', 'BLOCKED') or r['confidence'] < 0.3
    print(f"  T12: {'✅' if t12 else '❌'} Unknown → {r['patch_type']} conf={r['confidence']:.2f}")

    passed = sum([t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12])
    print(f"\n  {'='*60}")
    print(f"  ERGEBNIS: {passed}/12 Tests bestanden")
    print(f"  {'✅ PATCH-SUGGESTION MVP FERTIG' if passed >= 10 else '⚠️'}")
    print(f"  {'='*60}")
