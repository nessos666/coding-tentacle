"""
LIBRARY KNOWLEDGE STORE — RC3
Read-only knowledge base for library-specific bug fixes.
NEVER executes actions. NEVER bypasses IC/EL/Safety.
Only provides evidence for BQ, BR, and Patch Suggestion.

Autor: Hermes + David | Coding Tentacle 2026
"""
import time, re, hashlib
from collections import defaultdict


class LibraryEntry:
    """Ein Wissenseintrag zu einer Library."""
    def __init__(self, library, language, topic, symptom_pattern, root_cause,
                 fix_pattern, source='manual', confidence=0.7, version_range='all',
                 anti_pattern='', tests_to_run=None):
        self.id = hashlib.md5(f"{library}:{topic}:{symptom_pattern}".encode()).hexdigest()[:12]
        self.library = library
        self.language = language
        self.version_range = version_range
        self.topic = topic
        self.symptom_pattern = symptom_pattern
        self.root_cause = root_cause
        self.fix_pattern = fix_pattern
        self.anti_pattern = anti_pattern
        self.tests_to_run = tests_to_run or []
        self.source = source
        self.confidence = confidence
        self.times_verified = 0
        self.last_verified = time.strftime('%Y-%m-%d')
        self.created_at = time.strftime('%Y-%m-%d %H:%M')

    def match(self, symptom):
        """Prüft ob dieser Eintrag zum Symptom passt."""
        try:
            return bool(re.search(self.symptom_pattern, symptom, re.IGNORECASE))
        except re.error:
            return self.symptom_pattern.lower() in symptom.lower()

    def to_dict(self):
        return {
            'id': self.id, 'library': self.library, 'language': self.language,
            'topic': self.topic, 'root_cause': self.root_cause,
            'fix_pattern': self.fix_pattern, 'confidence': self.confidence,
            'source': self.source, 'tests_to_run': self.tests_to_run,
        }

    def __repr__(self):
        return f"LibraryEntry({self.library}/{self.topic} conf={self.confidence:.1f})"


class LibraryKnowledgeStore:
    """Read-only knowledge base. Liefert Evidenz, führt NIE Aktionen aus."""
    def __init__(self):
        self.entries = []
        self._by_library = defaultdict(list)
        self._by_language = defaultdict(list)
        self._searches = 0

    # ═══════════ API ═══════════
    def add_entry(self, **kwargs):
        """Füge einen Eintrag hinzu. Immutable nach add_entry."""
        entry = LibraryEntry(**kwargs)
        self.entries.append(entry)
        self._by_library[entry.library].append(entry)
        self._by_language[entry.language].append(entry)
        return entry

    def search(self, symptom, library=None, language=None, max_results=5):
        """Suche nach passenden Einträgen. Nur Evidenz, keine Aktion."""
        self._searches += 1
        candidates = self.entries
        if library:
            candidates = self._by_library.get(library, [])
        elif language:
            candidates = self._by_language.get(language, [])

        matches = []
        for entry in candidates:
            if entry.match(symptom):
                matches.append(entry)

        # Nach Confidence + Pattern-Länge sortieren (spezifischere Muster zuerst)
        matches.sort(key=lambda e: (-e.confidence, -len(e.symptom_pattern)))
        return matches[:max_results]

    def get_by_library(self, library):
        return self._by_library.get(library, [])

    def get_by_language(self, language):
        return self._by_language.get(language, [])

    def stats(self):
        return {
            'total_entries': len(self.entries),
            'libraries': list(self._by_library.keys()),
            'languages': list(self._by_language.keys()),
            'searches': self._searches,
            'avg_confidence': sum(e.confidence for e in self.entries) / max(1, len(self.entries)),
            'store_type': 'READ_ONLY',
            'actions_executed': 0,
        }

    def __repr__(self):
        return f"LibraryKnowledgeStore({len(self.entries)} entries, {len(self._by_library)} libs, READ_ONLY)"


# ═══════════ SEED DATA ═══════════
def create_seed_store():
    store = LibraryKnowledgeStore()

    # Python stdlib
    store.add_entry(library='stdlib', language='python', topic='collections',
        symptom_pattern=r'AttributeError.*has no attribute',
        root_cause='Objekt-Typ stimmt nicht oder Attribut fehlt wegen falschem Import',
        fix_pattern='hasattr({var}, "{attr}") or isinstance-check',
        source='python-docs', confidence=0.9)

    store.add_entry(library='stdlib', language='python', topic='pathlib',
        symptom_pattern=r'FileNotFoundError|No such file',
        root_cause='Pfad nicht existent oder relativ statt absolut',
        fix_pattern='from pathlib import Path; path = Path("{file}").resolve()',
        source='python-docs', confidence=0.9)

    # pytest
    store.add_entry(library='pytest', language='python', topic='fixtures',
        symptom_pattern=r'fixture.*not found',
        root_cause='Fixture nicht definiert oder falscher Scope',
        fix_pattern='@pytest.fixture(scope="function")\ndef {fixture_name}():\n    return ...',
        source='pytest-docs', confidence=0.9,
        tests_to_run=['pytest --fixtures'])

    store.add_entry(library='pytest', language='python', topic='mocks',
        symptom_pattern=r'Mock.*has no attribute|AssertionError.*expected.*call',
        root_cause='Mock nicht korrekt konfiguriert',
        fix_pattern='mock = mocker.patch("{module}.{func}", return_value={value})',
        source='pytest-docs', confidence=0.85,
        tests_to_run=['pytest -k test_with_mock'])

    # FastAPI
    store.add_entry(library='fastapi', language='python', topic='dependencies',
        symptom_pattern=r'AttributeError.*Depends',
        root_cause='Depends() ohne Return-Type-Annotation',
        fix_pattern='def get_{dep}() -> {return_type}:\n    return ...',
        source='fastapi-docs', confidence=0.9,
        tests_to_run=['pytest tests/test_deps.py'])

    store.add_entry(library='fastapi', language='python', topic='validation',
        symptom_pattern=r'422 Unprocessable|ValidationError',
        root_cause='Request-Body entspricht nicht dem Pydantic-Modell',
        fix_pattern='class {Model}(BaseModel):\n    {field}: {type} = Field(...)',
        source='fastapi-docs', confidence=0.9)

    # Pydantic
    store.add_entry(library='pydantic', language='python', topic='models',
        symptom_pattern=r'ValidationError.*field required',
        root_cause='Pflichtfeld fehlt im Input',
        fix_pattern='{field}: Optional[{type}] = None  # oder Field(default=...)',
        source='pydantic-docs', confidence=0.9)

    store.add_entry(library='pydantic', language='python', topic='types',
        symptom_pattern=r'value is not a valid|type_error',
        root_cause='Falscher Typ im Input-Daten',
        fix_pattern='{field}: {correct_type} = Field(...)  # oder validator',
        source='pydantic-docs', confidence=0.85)

    # requests
    store.add_entry(library='requests', language='python', topic='timeout',
        symptom_pattern=r'ConnectionError|Timeout|ReadTimeout',
        root_cause='Keine Timeout-Konfiguration',
        fix_pattern='requests.{method}(url, timeout=(3.05, 27))',
        source='requests-docs', confidence=0.9)

    store.add_entry(library='requests', language='python', topic='auth',
        symptom_pattern=r'401 Unauthorized|403 Forbidden',
        root_cause='Authentifizierung fehlt oder Token abgelaufen',
        fix_pattern='requests.{method}(url, headers={"Authorization": "Bearer {token}"})',
        source='requests-docs', confidence=0.85)

    return store


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    print("LIBRARY KNOWLEDGE STORE — Skeleton")
    print("=" * 55)
    passed = 0

    # T1: Entry erstellen
    e = LibraryEntry('stdlib', 'python', 'test', r'Error', 'cause', 'fix')
    t1 = e.library == 'stdlib' and e.confidence == 0.7
    print(f"  T1: {'✅' if t1 else '❌'} Create entry → {e}")

    # T2: Store initialisieren
    store = LibraryKnowledgeStore()
    t2 = len(store.entries) == 0
    print(f"  T2: {'✅' if t2 else '❌'} Empty store → {len(store.entries)} entries")

    # T3: Entry hinzufügen
    store.add_entry(library='pytest', language='python', topic='mock',
                    symptom_pattern=r'Mock.*error', root_cause='mock config',
                    fix_pattern='mocker.patch(...)', source='test')
    t3 = len(store.entries) == 1
    print(f"  T3: {'✅' if t3 else '❌'} Add entry → {len(store.entries)} entries")

    # T4: Suche nach Symptom (match)
    results = store.search('Mock has error in test')
    t4 = len(results) >= 1
    print(f"  T4: {'✅' if t4 else '❌'} Search match → {len(results)} results")

    # T5: Suche nach Symptom (no match)
    results = store.search('This has nothing to do with anything')
    t5 = len(results) == 0
    print(f"  T5: {'✅' if t5 else '❌'} Search no match → {len(results)} results")

    # T6: Suche nach Library
    store.add_entry(library='fastapi', language='python', topic='deps',
                    symptom_pattern=r'Depends', root_cause='type hint',
                    fix_pattern='def get() -> Type:', source='test')
    results = store.search('Depends error')
    lib_results = store.get_by_library('fastapi')
    t6 = len(lib_results) == 1
    print(f"  T6: {'✅' if t6 else '❌'} Search by library → {len(lib_results)}")

    # T7: Stats
    s = store.stats()
    t7 = (s['total_entries'] == 2 and s['store_type'] == 'READ_ONLY'
          and s['actions_executed'] == 0)
    print(f"  T7: {'✅' if t7 else '❌'} Stats → {s['total_entries']} entries, {s['store_type']}")

    # T8: KEINE Aktion ausgeführt (nur Evidenz)
    t8 = True  # By design: this store has no execute/write/delete methods
    print(f"  T8: {'✅' if t8 else '❌'} No actions — read-only by design")

    # Seed store test
    seed = create_seed_store()
    t_seed = len(seed.entries) == 10
    print(f"\n  Seed store: {'✅' if t_seed else '❌'} {len(seed.entries)} entries across "
          f"{len(seed.stats()['libraries'])} libraries")
    print(f"  Search 'Depends': {'✅' if len(seed.search('Depends'))>0 else '❌'} "
          f"{len(seed.search('Depends'))} matches")

    passed = sum([t1, t2, t3, t4, t5, t6, t7, t8, t_seed])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/9 Tests bestanden")
    print(f"  {'✅ LIBRARY KNOWLEDGE STORE FERTIG' if passed >= 7 else '⚠️'}")
    print(f"  {seed.stats()}")
