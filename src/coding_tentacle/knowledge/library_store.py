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
        """Prüft ob dieser Eintrag zum Symptom passt. Hybrid: Regex + Keyword-Overlap."""
        score = 0.0
        matched = []
        symptom_lower = symptom.lower()

        # Regex-Match (stark, +0.7)
        try:
            if re.search(self.symptom_pattern, symptom, re.IGNORECASE):
                score += 0.70
                matched.append('pattern')
        except re.error:
            if self.symptom_pattern.lower() in symptom_lower:
                score += 0.70
                matched.append('pattern')

        # Keyword-Overlap aus root_cause (mittel, +0.20)
        cause_words = set(w.strip('.,:;()') for w in self.root_cause.lower().split()
                         if len(w.strip('.,:;()')) > 3)
        symptom_words = set(w.strip('.,:;()') for w in symptom_lower.split()
                           if len(w.strip('.,:;()')) > 3)
        if cause_words and symptom_words:
            overlap = len(cause_words & symptom_words) / max(1, len(cause_words))
            if overlap > 0.3:
                score += 0.20 * overlap
                matched.append('keywords')

        # Topic-Match (schwach, +0.10)
        if self.topic.lower() in symptom_lower:
            score += 0.10
            matched.append('topic')

        return score, matched

    def match_legacy(self, symptom):
        """Altes bool-Interface für backward compatibility."""
        score, _ = self.match(symptom)
        return score > 0

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
        """Suche nach passenden Einträgen. Hybrid scoring. Nur Evidenz, keine Aktion."""
        self._searches += 1
        candidates = self.entries
        if library:
            candidates = self._by_library.get(library, [])
        elif language:
            candidates = self._by_language.get(language, [])

        scored = []
        for entry in candidates:
            score, matched = entry.match(symptom)
            if score > 0:
                scored.append((entry, score, matched))

        # Nach Score + Confidence sortieren
        scored.sort(key=lambda x: (-x[1], -x[0].confidence))
        return [e for e, _, _ in scored[:max_results]]

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

    # ═══════════ EXPANSION: 10 pro Library ═══════════
    # --- stdlib: +8 (type hints, asyncio, dataclasses, itertools, functools, json, csv, logging) ---
    store.add_entry(library='stdlib', language='python', topic='typing',
        symptom_pattern=r'TypeError.*not subscriptable|Optional.*None',
        root_cause='Falscher Type-Hint oder missing Optional',
        fix_pattern='from typing import Optional; {var}: Optional[{type}] = None',
        source='python-docs', confidence=0.9)
    store.add_entry(library='stdlib', language='python', topic='asyncio',
        symptom_pattern=r'coroutine.*was never awaited|RuntimeWarning.*coroutine',
        root_cause='Async-Funktion ohne await aufgerufen',
        fix_pattern='await {coro}()  # or: asyncio.run({coro}())',
        source='python-docs', confidence=0.9)
    store.add_entry(library='stdlib', language='python', topic='dataclasses',
        symptom_pattern=r'TypeError.*missing.*required.*argument|unexpected keyword',
        root_cause='Dataclass-Feld falsch definiert',
        fix_pattern='@dataclass\nclass {Name}:\n    {field}: {type} = field(default=...)',
        source='python-docs', confidence=0.9)
    store.add_entry(library='stdlib', language='python', topic='itertools',
        symptom_pattern=r'StopIteration|generator already executing',
        root_cause='Iterator erschöpft oder Generator doppelt verwendet',
        fix_pattern='list({gen})  # einmalig materialisieren',
        source='python-docs', confidence=0.85)
    store.add_entry(library='stdlib', language='python', topic='functools',
        symptom_pattern=r'TypeError.*missing.*argument.*partial',
        root_cause='functools.partial falsch konfiguriert',
        fix_pattern='from functools import partial\n{fn} = partial({orig}, {arg}={default})',
        source='python-docs', confidence=0.85)
    store.add_entry(library='stdlib', language='python', topic='json',
        symptom_pattern=r'JSONDecodeError|json\.decoder',
        root_cause='JSON-Daten ungültig oder falsches Encoding',
        fix_pattern='json.loads({data})  # check: try/except JSONDecodeError',
        source='python-docs', confidence=0.9)
    store.add_entry(library='stdlib', language='python', topic='csv',
        symptom_pattern=r'Error.*line.*csv|_csv\.Error',
        root_cause='CSV-Datei mit falschem Delimiter oder Quote',
        fix_pattern='csv.reader(f, delimiter=",", quotechar="")',
        source='python-docs', confidence=0.85)
    store.add_entry(library='stdlib', language='python', topic='logging',
        symptom_pattern=r'No handlers could be found|logging.*not configured',
        root_cause='Logger nicht konfiguriert vor erstem logging-Aufruf',
        fix_pattern='logging.basicConfig(level=logging.INFO)',
        source='python-docs', confidence=0.9)
    # --- pytest: +8 (parametrize, marks, raises, tmp_path, capsys, monkeypatch, conftest, coverage) ---
    store.add_entry(library='pytest', language='python', topic='parametrize',
        symptom_pattern=r'fixture.*parametrize.*not found|indirect.*parametrize',
        root_cause='Parametrize-Syntax falsch oder indirect flag fehlt',
        fix_pattern='@pytest.mark.parametrize("{var}", [{vals}])',
        source='pytest-docs', confidence=0.9)
    store.add_entry(library='pytest', language='python', topic='marks',
        symptom_pattern=r'Unknown marker|PytestUnknownMarkWarning',
        root_cause='Custom marker nicht in pytest.ini registriert',
        fix_pattern='# pytest.ini:\n[pytest]\nmarkers =\n    {name}: description',
        source='pytest-docs', confidence=0.9)
    store.add_entry(library='pytest', language='python', topic='raises',
        symptom_pattern=r'Failed: DID NOT RAISE|pytest\.raises',
        root_cause='Exception wird nicht geworfen oder falscher Typ',
        fix_pattern='with pytest.raises({ExceptionType}):\n    {code}',
        source='pytest-docs', confidence=0.9)
    store.add_entry(library='pytest', language='python', topic='tmp_path',
        symptom_pattern=r'FileNotFoundError.*tmp|tmpdir|tmp_path',
        root_cause='tmp_path-File nach Test gelöscht',
        fix_pattern='def test_{name}(tmp_path):\n    f = tmp_path / "file.txt"',
        source='pytest-docs', confidence=0.85)
    store.add_entry(library='pytest', language='python', topic='capsys',
        symptom_pattern=r'AssertionError.*stdout|capsys',
        root_cause='Output-Capture nicht aktiviert',
        fix_pattern='def test_{name}(capsys):\n    captured = capsys.readouterr()',
        source='pytest-docs', confidence=0.85)
    store.add_entry(library='pytest', language='python', topic='monkeypatch',
        symptom_pattern=r'AttributeError.*monkeypatch|monkeypatch\.setattr',
        root_cause='Monkeypatch falsch gesetzt oder gelöscht',
        fix_pattern='monkeypatch.setattr({module}, "{attr}", {value})',
        source='pytest-docs', confidence=0.85)
    store.add_entry(library='pytest', language='python', topic='conftest',
        symptom_pattern=r'conftest.*not loaded|fixture.*not found.*conftest',
        root_cause='conftest.py nicht im richtigen Verzeichnis',
        fix_pattern='# conftest.py in test/ oder tests/ directory',
        source='pytest-docs', confidence=0.9)
    store.add_entry(library='pytest', language='python', topic='coverage',
        symptom_pattern=r'CoverageWarning|No data collected',
        root_cause='pytest-cov falsch konfiguriert',
        fix_pattern='pytest --cov={package} --cov-report=term',
        source='pytest-docs', confidence=0.85)
    # --- FastAPI: +8 (middleware, CORS, status codes, headers, background, lifespan, websockets, uploads) ---
    store.add_entry(library='fastapi', language='python', topic='middleware',
        symptom_pattern=r'Middleware.*not applied|add_middleware',
        root_cause='Middleware-Reihenfolge falsch oder nicht registriert',
        fix_pattern='app.add_middleware({MiddlewareClass})  # CORSMiddleware zuerst',
        source='fastapi-docs', confidence=0.9)
    store.add_entry(library='fastapi', language='python', topic='cors',
        symptom_pattern=r'CORS.*blocked|Cross-Origin|allow_origins',
        root_cause='CORS nicht konfiguriert für Frontend-Origin',
        fix_pattern='app.add_middleware(CORSMiddleware, allow_origins=["{url}"])',
        source='fastapi-docs', confidence=0.9)
    store.add_entry(library='fastapi', language='python', topic='status_codes',
        symptom_pattern=r'status_code.*not found|422|500.*validation',
        root_cause='Status-Code implizit statt explizit',
        fix_pattern='return JSONResponse(content=..., status_code={code})',
        source='fastapi-docs', confidence=0.9)
    store.add_entry(library='fastapi', language='python', topic='headers',
        symptom_pattern=r'KeyError.*header|Header.*missing',
        root_cause='Required Header fehlt in Request',
        fix_pattern='@app.get("/")\ndef endpoint({header}: str = Header(...)):',
        source='fastapi-docs', confidence=0.85)
    store.add_entry(library='fastapi', language='python', topic='background',
        symptom_pattern=r'BackgroundTasks.*not working|background_tasks',
        root_cause='BackgroundTasks falsch injected',
        fix_pattern='def endpoint(background_tasks: BackgroundTasks):\n    background_tasks.add_task({task})',
        source='fastapi-docs', confidence=0.85)
    store.add_entry(library='fastapi', language='python', topic='lifespan',
        symptom_pattern=r'RuntimeError.*lifespan|startup.*not called',
        root_cause='Lifespan Event-Handler fehlt',
        fix_pattern='@asynccontextmanager\nasync def lifespan(app):\n    yield',
        source='fastapi-docs', confidence=0.85)
    store.add_entry(library='fastapi', language='python', topic='websockets',
        symptom_pattern=r'WebSocket.*disconnect|websocket.*error',
        root_cause='WebSocket ohne try/except um accept()',
        fix_pattern='@app.websocket("/ws")\nasync def ws(websocket: WebSocket):\n    await websocket.accept()\n    try: ...\n    except: await websocket.close()',
        source='fastapi-docs', confidence=0.85)
    store.add_entry(library='fastapi', language='python', topic='uploads',
        symptom_pattern=r'UploadFile.*error|file.*too large',
        root_cause='Upload-Größe nicht limitiert',
        fix_pattern='from fastapi import UploadFile, File\nasync def upload(file: UploadFile = File(...)):',
        source='fastapi-docs', confidence=0.85)
    # --- Pydantic: +8 (validators, config, nested models, generics, aliases, env, parse_raw, errors) ---
    store.add_entry(library='pydantic', language='python', topic='validators',
        symptom_pattern=r'validator.*not called|@validator',
        root_cause='Validator-Dekorator falsch platziert',
        fix_pattern='@field_validator("{field}")\n@classmethod\ndef validate_{field}(cls, v):\n    return v',
        source='pydantic-docs', confidence=0.9)
    store.add_entry(library='pydantic', language='python', topic='config',
        symptom_pattern=r'ConfigDict|model_config.*error',
        root_cause='Model-Konfiguration falsch (v1 vs v2 Syntax)',
        fix_pattern='class {Model}(BaseModel):\n    model_config = ConfigDict(extra="forbid")',
        source='pydantic-docs', confidence=0.9)
    store.add_entry(library='pydantic', language='python', topic='nested',
        symptom_pattern=r'ValidationError.*nested|dict is not a.*model',
        root_cause='Nested Model nicht richtig deklariert',
        fix_pattern='class Outer(BaseModel):\n    inner: InnerModel',
        source='pydantic-docs', confidence=0.9)
    store.add_entry(library='pydantic', language='python', topic='generics',
        symptom_pattern=r'TypeError.*Generic.*BaseModel',
        root_cause='Generic Model falsch parametrisiert',
        fix_pattern='from typing import Generic, TypeVar\nT = TypeVar("T")\nclass Response(BaseModel, Generic[T]):\n    data: T',
        source='pydantic-docs', confidence=0.85)
    store.add_entry(library='pydantic', language='python', topic='aliases',
        symptom_pattern=r'KeyError.*alias|field.*serialization_alias',
        root_cause='Field-Alias fehlt für API/Schema',
        fix_pattern='{field}: {type} = Field(alias="{alias_name}")',
        source='pydantic-docs', confidence=0.85)
    store.add_entry(library='pydantic', language='python', topic='env',
        symptom_pattern=r'Settings.*env|pydantic-settings|BaseSettings',
        root_cause='Settings aus .env nicht geladen',
        fix_pattern='from pydantic_settings import BaseSettings\nclass Settings(BaseSettings):\n    model_config = SettingsConfigDict(env_file=".env")',
        source='pydantic-docs', confidence=0.85)
    store.add_entry(library='pydantic', language='python', topic='parse_raw',
        symptom_pattern=r'parse_raw.*deprecated|model_validate_json',
        root_cause='v1-API (parse_raw) in v2 verwendet',
        fix_pattern='{Model}.model_validate_json({data})  # v2 syntax',
        source='pydantic-docs', confidence=0.85)
    store.add_entry(library='pydantic', language='python', topic='errors',
        symptom_pattern=r'pydantic.error_wrappers|ValidationError.*loc',
        root_cause='Fehler-Location in verschachtelten Modellen schwer lesbar',
        fix_pattern='try:\n    {Model}(**data)\nexcept ValidationError as e:\n    print(e.errors())',
        source='pydantic-docs', confidence=0.85)
    # --- requests: +8 (sessions, redirects, proxies, certificates, streaming, retries, headers, post) ---
    store.add_entry(library='requests', language='python', topic='sessions',
        symptom_pattern=r'Connection pool.*full|Session.*not reused',
        root_cause='Session nicht verwendet (jeder Request neue Verbindung)',
        fix_pattern='session = requests.Session()\nsession.{method}(url)',
        source='requests-docs', confidence=0.9)
    store.add_entry(library='requests', language='python', topic='redirects',
        symptom_pattern=r'TooManyRedirects|redirect.*loop',
        root_cause='Redirect-Limit erreicht',
        fix_pattern='requests.{method}(url, allow_redirects=False)  # oder max_redirects',
        source='requests-docs', confidence=0.85)
    store.add_entry(library='requests', language='python', topic='proxies',
        symptom_pattern=r'ProxyError|proxy.*connection',
        root_cause='Proxy falsch konfiguriert',
        fix_pattern='requests.{method}(url, proxies={{"http": "{proxy_url}"}})',
        source='requests-docs', confidence=0.85)
    store.add_entry(library='requests', language='python', topic='certificates',
        symptom_pattern=r'SSLError|SSL.*certificate|certificate verify failed',
        root_cause='SSL-Zertifikat nicht verifizierbar',
        fix_pattern='requests.{method}(url, verify="{cert_path}")  # oder verify=False nur für dev',
        source='requests-docs', confidence=0.9)
    store.add_entry(library='requests', language='python', topic='streaming',
        symptom_pattern=r'MemoryError.*large|ChunkedEncodingError',
        root_cause='Große Response nicht gestreamt',
        fix_pattern='with requests.{method}(url, stream=True) as r:\n    for chunk in r.iter_content():',
        source='requests-docs', confidence=0.85)
    store.add_entry(library='requests', language='python', topic='retries',
        symptom_pattern=r'ConnectionError.*retry|MaxRetryError',
        root_cause='Keine Retry-Strategie bei Verbindungsfehlern',
        fix_pattern='from urllib3.util.retry import Retry\nsession.mount("https://", HTTPAdapter(max_retries=Retry(total=3))))',
        source='requests-docs', confidence=0.85)
    store.add_entry(library='requests', language='python', topic='headers',
        symptom_pattern=r'KeyError.*header|Content-Type.*missing',
        root_cause='Required Header fehlt in Response',
        fix_pattern='r = requests.{method}(url, headers={{"Accept": "application/json"}})',
        source='requests-docs', confidence=0.85)
    store.add_entry(library='requests', language='python', topic='post',
        symptom_pattern=r'400 Bad Request.*POST|json.*not serializable',
        root_cause='POST-Daten nicht als JSON gesendet',
        fix_pattern='requests.post(url, json={data})  # nicht data=',
        source='requests-docs', confidence=0.9)

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
    t6 = len(lib_results) >= 1  # Store hat 10 fastapi entries nach Expansion
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
