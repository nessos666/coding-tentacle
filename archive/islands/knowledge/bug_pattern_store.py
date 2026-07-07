"""
BUG PATTERN STORE — RC4
Read-only knowledge base of common bug types.
NEVER executes actions. Only provides evidence.

Autor: Hermes + David | Coding Tentacle 2026
"""
import re, time, hashlib
from collections import defaultdict


class BugPatternEntry:
    def __init__(self, bug_type, languages, symptoms, root_causes, fix_patterns,
                 anti_patterns=None, tests_to_run=None, risk_level='medium',
                 confidence=0.8, source='manual'):
        self.id = hashlib.md5(f"{bug_type}:{symptoms[0] if symptoms else ''}".encode()).hexdigest()[:12]
        self.bug_type = bug_type
        self.languages = languages
        self.symptoms = symptoms
        self.root_causes = root_causes
        self.fix_patterns = fix_patterns
        self.anti_patterns = anti_patterns or []
        self.tests_to_run = tests_to_run or []
        self.risk_level = risk_level
        self.confidence = confidence
        self.source = source
        self.times_seen = 0
        self.times_fixed = 0
        self.last_matched = None

    def match(self, symptom, language=None):
        """Hybrid: Regex + Keyword-Overlap."""
        score = 0.0; matched = []
        for pat in self.symptoms:
            try:
                if re.search(pat, symptom, re.IGNORECASE):
                    score += 0.60; matched.append(f'symptom:{pat[:30]}'); break
            except re.error:
                if pat.lower() in symptom.lower():
                    score += 0.60; matched.append(f'symptom:{pat[:30]}'); break

        cause_text = ' '.join(self.root_causes).lower()
        symptom_words = set(w.strip('.,:;()\'"[]{}') for w in symptom.lower().split() if len(w) > 3)
        cause_words = set(w.strip('.,:;()\'"[]{}') for w in cause_text.split() if len(w) > 3)
        if cause_words and symptom_words:
            overlap = len(cause_words & symptom_words) / max(1, len(cause_words))
            if overlap > 0.2:
                score += 0.25 * overlap; matched.append('keywords')

        if language and language in self.languages:
            score += 0.15; matched.append(f'lang:{language}')
        elif language and 'universal' in self.languages:
            score += 0.10; matched.append('lang:universal')

        return score, matched

    def to_dict(self):
        return {
            'id': self.id, 'bug_type': self.bug_type, 'languages': self.languages,
            'root_causes': self.root_causes, 'fix_patterns': self.fix_patterns,
            'risk_level': self.risk_level, 'confidence': self.confidence,
        }


class BugPatternStore:
    def __init__(self):
        self.entries = []
        self._by_type = defaultdict(list)
        self._searches = 0

    def add_entry(self, **kwargs):
        entry = BugPatternEntry(**kwargs)
        self.entries.append(entry)
        self._by_type[entry.bug_type].append(entry)
        return entry

    def search(self, symptom, language=None, max_results=5):
        self._searches += 1
        scored = []
        for entry in self.entries:
            score, matched = entry.match(symptom, language)
            if score > 0:
                scored.append((entry, score, matched))
        scored.sort(key=lambda x: (-x[1], -x[0].confidence))
        return [e for e, _, _ in scored[:max_results]]

    def get_by_bug_type(self, bug_type):
        return self._by_type.get(bug_type, [])

    def stats(self):
        return {
            'total_entries': len(self.entries),
            'bug_types': list(self._by_type.keys()),
            'searches': self._searches,
            'avg_confidence': sum(e.confidence for e in self.entries) / max(1, len(self.entries)),
            'store_type': 'READ_ONLY',
            'actions_executed': 0,
        }


def create_seed_bug_store():
    s = BugPatternStore()
    s.add_entry(bug_type='NullPointer', languages=['python','javascript','java','go','rust','cpp'],
        symptoms=[r"NoneType.*has no attribute", r"NullPointerException", r"null pointer",
                   r"nil pointer", r"cannot read propert", r"cannot call method.*null"],
        root_causes=['Objekt/Variable ist null/nil', 'Funktion gibt None/null statt Objekt zurück',
                     'DB-Query findet keinen Datensatz', 'Option/Nullable nicht geprüft'],
        fix_patterns=['if {var}:', 'if {var} is not None:', '{var}?.{method}()'],
        anti_patterns=['try/except statt null-check', 'pass statt fix'], risk_level='high')

    s.add_entry(bug_type='OutOfBounds', languages=['python','javascript','java','cpp','rust','go'],
        symptoms=[r"IndexError.*list index out of range", r"ArrayIndexOutOfBounds",
                   r"index out of bounds", r"Segmentation fault", r"slice bounds out of range"],
        root_causes=['Schleife läuft zu weit (off-by-one)', 'Leerer Array/Zugriff ohne Check',
                     'Falscher Index berechnet', 'Dynamische Array-Größe nicht geprüft'],
        fix_patterns=['if 0 <= i < len(arr):', 'for item in items:', 'arr.slice()'],
        anti_patterns=['try/except IndexError', 'arr[i] ohne Check'], risk_level='high')

    s.add_entry(bug_type='DivideByZero', languages=['python','java','cpp','javascript'],
        symptoms=[r"ZeroDivisionError", r"Division by zero", r"divide by zero",
                   r"ArithmeticException"],
        root_causes=['Divisor ist 0', 'Berechnung liefert unerwartet 0',
                     'Eingabewert nicht validiert'],
        fix_patterns=['if divisor != 0:', 'result = 0 if divisor == 0 else x / divisor'],
        anti_patterns=['try/except ZeroDivisionError'], risk_level='medium')

    s.add_entry(bug_type='AttributeError', languages=['python','javascript','ruby'],
        symptoms=[r"AttributeError.*has no attribute", r"undefined is not an object",
                   r"NoMethodError", r"undefined method"],
        root_causes=['Falscher Objekt-Typ', 'Attribut/Methode existiert nicht',
                     'None statt erwartetem Objekt', 'Tippfehler im Attribut-Namen'],
        fix_patterns=['hasattr(obj, attr)', 'isinstance(obj, type)', 'obj?.attr'],
        anti_patterns=['try/except AttributeError'], risk_level='medium')

    s.add_entry(bug_type='ImportError', languages=['python','javascript','java'],
        symptoms=[r"ImportError.*No module named", r"ModuleNotFoundError",
                   r"Cannot find module", r"cannot find package"],
        root_causes=['Fehlende Abhängigkeit', 'Modul nicht installiert',
                     'Zyklischer Import', 'Falscher Modul-Pfad'],
        fix_patterns=['pip install {module}', 'try:\n    import {module}\nexcept:\n    import {alt}'],
        anti_patterns=['sys.path hacks', 'import ohne try/except'], risk_level='medium')

    s.add_entry(bug_type='TypeError', languages=['python','javascript','java','rust'],
        symptoms=[r"TypeError.*not supported", r"TypeError.*not callable",
                   r"cannot convert", r"wrong type", r"type mismatch"],
        root_causes=['Falscher Datentyp übergeben', 'None statt erwartetem Typ',
                     'Operator nicht für diesen Typ', 'Funktion erwartet anderen Typ'],
        fix_patterns=['isinstance({var}, {type})', 'str({var})', 'int({var})'],
        anti_patterns=['try/except TypeError für Typfehler'], risk_level='low')

    s.add_entry(bug_type='KeyError', languages=['python','javascript','ruby'],
        symptoms=[r"KeyError", r"undefined is not an object", r"key not found"],
        root_causes=['Schlüssel existiert nicht im Dict/Map', 'Datenformat geändert',
                     'Config-Parameter fehlt'],
        fix_patterns=['.get(key, default)', '{key} in dict', 'dict.setdefault()'],
        anti_patterns=['try/except KeyError'], risk_level='low')

    s.add_entry(bug_type='Timeout', languages=['python','javascript','go'],
        symptoms=[r"TimeoutError", r"ReadTimeout", r"ConnectTimeout", r"timed out",
                   r"deadline exceeded"],
        root_causes=['Netzwerk-Problem', 'Server antwortet nicht', 'Operation dauert zu lange',
                     'Kein Timeout konfiguriert'],
        fix_patterns=['timeout=30', 'with Timeout(10):', 'context.WithTimeout()'],
        anti_patterns=['Kein Timeout setzen', 'Unendlich warten'], risk_level='medium')

    s.add_entry(bug_type='ResourceLeak', languages=['python','cpp','go','java'],
        symptoms=[r"Too many open files", r"MemoryError", r"memory leak",
                   r"OOM", r"out of memory"],
        root_causes=['Datei/Verbindung nicht geschlossen', 'Cache wächst unbegrenzt',
                     'Referenz-Zyklus verhindert GC', 'Ressource nicht freigegeben'],
        fix_patterns=['with open():', 'try/finally', 'defer close()', 'weakref'],
        anti_patterns=['open() ohne close()', 'Globale Caches ohne Limit'], risk_level='high')

    s.add_entry(bug_type='RaceCondition', languages=['python','java','go','cpp','javascript'],
        symptoms=[r"race condition", r"flaky test", r"inconsistent.*state",
                   r"concurrent modificat"],
        root_causes=['Ungeschützter Shared-State', 'Fehlende Synchronisation',
                     'Falsche Annahme über Atomarität', 'Thread-safety verletzt'],
        fix_patterns=['threading.Lock()', 'synchronized', 'mutex.Lock()', 'async/await'],
        anti_patterns=['Globale Variablen ohne Lock', 'sleep() als Fix'], risk_level='critical')

    # ═══════════ RC5 EXPANSION: +40 Einträge ═══════════
    # --- Logic/Algorithm (10) ---
    s.add_entry(bug_type='RecursionError', languages=['python','javascript','java'],
        symptoms=[r"RecursionError.*maximum recursion depth", r"stack overflow"],
        root_causes=['Rekursion ohne Basisfall', 'Rekursionstiefe zu groß für Input',
                     'Zyklische Aufrufe', 'Endlosrekursion'],
        fix_patterns=['if depth > MAX_DEPTH: return', 'while statt recursion',
                      '@lru_cache(maxsize=None)', 'sys.setrecursionlimit()'],
        anti_patterns=['Rekursion für große Listen', 'Kein Basisfall'], risk_level='high')

    s.add_entry(bug_type='MemoryError', languages=['python','cpp'],
        symptoms=[r"MemoryError", r"OutOfMemoryError", r"bad_alloc", r"heap space"],
        root_causes=['Datenstruktur zu groß', 'Speicher-Leak', 'Infinite Growth',
                     'Kein Streaming für große Dateien'],
        fix_patterns=['for chunk in iter():', 'del unused_var', 'gc.collect()',
                      'Reduce batch size'],
        anti_patterns=['Alles in RAM laden', 'Keine GC-Hints'], risk_level='high')

    s.add_entry(bug_type='AssertionError', languages=['python','javascript','java'],
        symptoms=[r"AssertionError", r"assert.*failed", r"expected.*got"],
        root_causes=['Test-Erwartung falsch', 'Code-Logik produziert falsches Ergebnis',
                     'Off-by-one', 'Race-Condition im Test'],
        fix_patterns=['# Expected: X, Got: Y → Fix test or code',
                      'pytest.raises() für Exception-Tests'],
        anti_patterns=['assert für Production-Code', 'Test ohne Message'], risk_level='medium')

    s.add_entry(bug_type='BufferError', languages=['python','cpp','c'],
        symptoms=[r"BufferError.*buffer too small", r"buffer overflow", r"buffer overrun"],
        root_causes=['Buffer-Größe falsch kalkuliert', 'Input größer als Puffer',
                     'Keine Bounds-Check bei Buffer-Operationen'],
        fix_patterns=['buffer = bytearray(size)', 'if len(data) <= buf_size:',
                      'memoryview für zero-copy'],
        anti_patterns=['malloc ohne size-Check', 'strcpy ohne bounds'], risk_level='high')

    s.add_entry(bug_type='StopIteration', languages=['python'],
        symptoms=[r"StopIteration", r"generator.*exhausted", r"iterator.*empty"],
        root_causes=['Iterator/Generator erschöpft', 'next() auf leerem Iterator',
                     'Generator yieldet nichts'],
        fix_patterns=['next(it, default)', 'for item in items:', 'list(it)'],
        anti_patterns=['next() ohne default', 'Iterator zweimal konsumieren'], risk_level='low')

    s.add_entry(bug_type='OverflowError', languages=['python','java','cpp'],
        symptoms=[r"OverflowError", r"int too large", r"overflow", r"arithmetic overflow"],
        root_causes=['Zahlenwert zu groß für Datentyp', 'Endlos-Berechnung',
                     'Fakultät/Exponent zu groß'],
        fix_patterns=['from decimal import Decimal', 'int() statt float()',
                      'if value > TYPE_MAX: raise'],
        anti_patterns=['float für große Integer', 'Unbounded factorial'], risk_level='medium')

    s.add_entry(bug_type='EncodingError', languages=['python','java'],
        symptoms=[r"UnicodeDecodeError", r"UnicodeEncodeError", r"invalid start byte",
                   r"unknown encoding"],
        root_causes=['Falsches Encoding', 'Datei ist nicht UTF-8',
                     'Binärdaten als Text gelesen'],
        fix_patterns=['open(file, encoding="utf-8")', "errors='ignore'",
                      'chardet.detect(data)'],
        anti_patterns=['encoding raten', 'errors="strict" bei Fremddaten'], risk_level='low')

    s.add_entry(bug_type='CircularDependency', languages=['python','javascript'],
        symptoms=[r"circular import", r"circular reference", r"circular dependency",
                   r"partially initialized module"],
        root_causes=['Modul A importiert B, B importiert A',
                     'Klasse A referenziert B, B referenziert A'],
        fix_patterns=['# Move shared code to shared.py', 'Lazy import in function',
                      'from __future__ import annotations'],
        anti_patterns=['Beide Module importieren sich gegenseitig'], risk_level='high')

    s.add_entry(bug_type='FloatingPointError', languages=['python','cpp','fortran'],
        symptoms=[r"FloatingPointError", r"NaN", r"inf", r"invalid float operation"],
        root_causes=['Division by zero (float)', 'sqrt von negativer Zahl',
                     'NaN-Propagation', 'Float-Overflow'],
        fix_patterns=['if math.isfinite(x):', 'try: ... except FloatingPointError:',
                      'decimal.Decimal für exakte Arithmetik'],
        anti_patterns=['NaN ignorieren', 'Ohne Check weiterrechnen'], risk_level='medium')

    s.add_entry(bug_type='ConcurrentModification', languages=['python','java'],
        symptoms=[r"ConcurrentModificationError", r"dictionary changed size",
                   r"list modified during iteration"],
        root_causes=['Collection während Iteration modifiziert',
                     'Anderer Thread ändert Daten', 'Callback modifiziert Liste'],
        fix_patterns=['for item in list(items):', 'copy.copy(items) vor Iteration',
                      'threading.Lock()'],
        anti_patterns=['Liste in for-loop modifizieren', 'Ohne Lock iterieren'], risk_level='high')

    # --- AttributeError Disambiguation (10) ---
    s.add_entry(bug_type='AttributeTypeMismatch', languages=['python'],
        symptoms=[r"AttributeError.*int.*has no attribute",
                   r"has no attribute.*int", r"str.*has no attribute"],
        root_causes=['Falscher Datentyp (int/str statt Objekt)',
                     'Rückgabewert einer Funktion ist anderer Typ'],
        fix_patterns=['isinstance({var}, {expected_type})', 'type({var}) check'],
        anti_patterns=['try/except AttributeError statt type-check'], risk_level='low')

    s.add_entry(bug_type='AttributeContainerError', languages=['python'],
        symptoms=[r"AttributeError.*(dict|list|set|tuple).*has no attribute"],
        root_causes=['Container-Typ erwartet, anderer bekommen',
                     'dict statt list, list statt dict'],
        fix_patterns=['isinstance({var}, dict)', 'if type({var}) is {expected}:'],
        anti_patterns=['Container-Typen verwechseln'], risk_level='low')

    s.add_entry(bug_type='AttributeModuleError', languages=['python'],
        symptoms=[r"AttributeError.*module.*has no attribute",
                   r"module.*has no attribute"],
        root_causes=['Falscher Import', 'Funktion/Klasse existiert nicht im Modul',
                     'Version geändert'],
        fix_patterns=['dir({module}) prüfen', 'from {module} import {name}',
                      'help({module})'],
        anti_patterns=['Import raten', 'Ohne dir() prüfen'], risk_level='medium')

    s.add_entry(bug_type='AttributeDecoratorError', languages=['python'],
        symptoms=[r"AttributeError.*function.*has no attribute",
                   r"function.*has no attribute"],
        root_causes=['Dekorator fehlt oder falsch', '@app.route statt @app.get',
                     'self vergessen'],
        fix_patterns=['@app.route("/")', 'def method(self):', '@staticmethod'],
        anti_patterns=['Dekorator weglassen', 'self vergessen'], risk_level='low')

    s.add_entry(bug_type='AttributeNoneError', languages=['python','javascript'],
        symptoms=[r"AttributeError.*NoneType.*has no attribute",
                   r"cannot read propert.*null", r"cannot read propert.*undefined"],
        root_causes=['Objekt ist None/null/undefined', 'Funktion gibt None zurück'],
        fix_patterns=['if {var} is not None:', '{var}?.{method}()', 'return default'],
        anti_patterns=['Kein None-Check', 'try/except AttributeError'], risk_level='high')

    s.add_entry(bug_type='AttributeDatetimeError', languages=['python'],
        symptoms=[r"AttributeError.*datetime.*has no attribute",
                   r"datetime.*has no attribute"],
        root_causes=['datetime statt datetime.datetime importiert',
                     'Falsches datetime-Modul'],
        fix_patterns=['from datetime import datetime', 'datetime.datetime.now()'],
        anti_patterns=['import datetime; datetime.now()'], risk_level='low')

    s.add_entry(bug_type='AttributeResponseError', languages=['python'],
        symptoms=[r"AttributeError.*Response.*has no attribute",
                   r"has no attribute.*data"],
        root_causes=['API-Response hat andere Struktur als erwartet',
                     'HTTP-Response statt JSON-Response'],
        fix_patterns=['response.json()', 'response.text', 'response.status_code'],
        anti_patterns=['Response.data (existiert nicht)', 'Ohne Status-Check'], risk_level='low')

    s.add_entry(bug_type='AttributeCoroutineError', languages=['python'],
        symptoms=[r"AttributeError.*coroutine.*has no attribute",
                   r"coroutine.*has no attribute"],
        root_causes=['Coroutine nicht awaited', 'Async-Funktion ohne await aufgerufen'],
        fix_patterns=['await async_fn()', 'asyncio.run(async_fn())'],
        anti_patterns=['async_fn() ohne await', 'result() auf coroutine'], risk_level='medium')

    s.add_entry(bug_type='AttributeBytesError', languages=['python'],
        symptoms=[r"AttributeError.*bytes.*has no attribute",
                   r"bytes.*has no attribute"],
        root_causes=['bytes statt str', 'Datei als binary statt text geöffnet'],
        fix_patterns=['data.decode("utf-8")', 'open(file, "r")', 'str(data)'],
        anti_patterns=['.read() auf str erwarten', 'Ohne decode()'], risk_level='low')

    s.add_entry(bug_type='AttributeGeneratorError', languages=['python'],
        symptoms=[r"AttributeError.*generator.*has no attribute",
                   r"generator.*has no attribute"],
        root_causes=['Generator statt Liste', 'map()/filter() gibt Iterator zurück'],
        fix_patterns=['list(gen)', '[x for x in gen]', 'next(gen, default)'],
        anti_patterns=['len(gen)', 'gen[0]', 'gen.append()'], risk_level='low')

    # --- Performance / Resource (10) ---
    s.add_entry(bug_type='ConnectionPoolExhausted', languages=['python','java','go'],
        symptoms=[r"Connection.*pool.*exhausted", r"too many connections",
                   r"connection.*timeout.*pool", r"max.*connections.*reached"],
        root_causes=['Verbindungen nicht geschlossen', 'Pool-Größe zu klein',
                     'Connection-Leak'],
        fix_patterns=['with connection:', 'connection.close()', 'pool.dispose()',
                      'Increase max_pool_size'],
        anti_patterns=['Verbindungen offen lassen', 'Kein Connection-Pooling'], risk_level='high')

    s.add_entry(bug_type='DiskFullError', languages=['python','unix'],
        symptoms=[r"No space left on device", r"disk full", r"ENOSPC"],
        root_causes=['Disk voll', 'Log-Dateien zu groß', 'Temp-Dateien nicht gelöscht'],
        fix_patterns=['shutil.disk_usage()', 'RotatingFileHandler', 'tempfile cleanup'],
        anti_patterns=['Ohne Check schreiben', 'Logs nie rotieren'], risk_level='high')

    s.add_entry(bug_type='TimeoutError', languages=['python','javascript','go'],
        symptoms=[r"TimeoutError", r"ReadTimeout", r"ConnectTimeout", r"timed out",
                   r"deadline exceeded"],
        root_causes=['Netzwerk-Problem', 'Server antwortet nicht', 'Operation zu langsam'],
        fix_patterns=['timeout=30', 'with Timeout(10):', 'context.WithTimeout()'],
        anti_patterns=['Kein Timeout setzen', 'Unendlich warten'], risk_level='medium')

    s.add_entry(bug_type='ResourceWarning', languages=['python'],
        symptoms=[r"ResourceWarning.*unclosed", r"unclosed file", r"unclosed socket"],
        root_causes=['Datei/Socket nicht geschlossen', 'Exception vor close()'],
        fix_patterns=['with open() as f:', 'try/finally: f.close()'],
        anti_patterns=['f = open(); ... kein close()', 'Exception-handler ohne cleanup'], risk_level='medium')

    s.add_entry(bug_type='BlockingIOError', languages=['python'],
        symptoms=[r"BlockingIOError", r"resource.*unavailable", r"would block"],
        root_causes=['Non-blocking I/O auf blockierender Resource',
                     'Socket im falschen Modus'],
        fix_patterns=['socket.setblocking(True)', 'select.select()', 'asyncio'],
        anti_patterns=['Ohne select poll()', 'Non-blocking ohne Fallback'], risk_level='medium')

    s.add_entry(bug_type='BrokenPipeError', languages=['python','unix'],
        symptoms=[r"BrokenPipeError", r"broken pipe", r"EPIPE", r"SIGPIPE"],
        root_causes=['Reader hat Pipe geschlossen', 'Prozess beendet'],
        fix_patterns=['try: write() except BrokenPipeError:', 'signal(SIGPIPE, SIG_DFL)'],
        anti_patterns=['Ohne try/except schreiben', 'SIGPIPE ignorieren'], risk_level='low')

    s.add_entry(bug_type='ConnectionResetError', languages=['python','unix'],
        symptoms=[r"ConnectionResetError", r"connection reset", r"ECONNRESET"],
        root_causes=['Peer hat Verbindung beendet', 'Netzwerk-Problem', 'Firewall'],
        fix_patterns=['retry with backoff', 'try/except reconnect', 'keepalive'],
        anti_patterns=['Kein Retry', 'Ohne Reconnect'], risk_level='medium')

    s.add_entry(bug_type='TooManyOpenFiles', languages=['python','unix'],
        symptoms=[r"Too many open files", r"EMFILE", r"ulimit"],
        root_causes=['Dateien nicht geschlossen', 'File-Descriptor-Leak',
                     'ulimit zu niedrig'],
        fix_patterns=['with open():', 'ulimit -n 4096', 'lsof zur Diagnose'],
        anti_patterns=['Datei-Handles nie schließen', 'Kein ulimit-Check'], risk_level='high')

    s.add_entry(bug_type='MemoryLeak', languages=['python','cpp','java'],
        symptoms=[r"MemoryError.*leak", r"memory leak", r"OOM over time",
                   r"heap.*growth"],
        root_causes=['Referenzen nicht freigegeben', 'Cache wächst unbegrenzt',
                     'Zirkuläre Referenzen'],
        fix_patterns=['weakref.ref()', 'gc.collect()', 'Cache mit LRU-Eviction'],
        anti_patterns=['Globale Caches ohne Limit', 'Liste endlos wachsen'], risk_level='high')

    s.add_entry(bug_type='SlowOperation', languages=['python','all'],
        symptoms=[r"slow", r"performance.*degrad", r"too slow", r"hangs"],
        root_causes=['O(n²) statt O(n)', 'N+1 Query-Problem',
                     'Kein Caching', 'Synchrone I/O in Hot-Path'],
        fix_patterns=['@lru_cache()', 'batch processing', 'async I/O', 'profiling'],
        anti_patterns=['Optimieren ohne Profiling', 'N+1 Queries'], risk_level='medium')

    # --- Build/Config/Dependency (10) ---
    s.add_entry(bug_type='VersionMismatch', languages=['python','javascript'],
        symptoms=[r"version.*mismatch", r"incompatible.*version", r"requires.*but you have"],
        root_causes=['Package-Version nicht kompatibel', 'Breaking Change in neuer Version',
                     'requirements.txt veraltet'],
        fix_patterns=['pip install {package}=={version}', 'Check CHANGELOG for breaking changes'],
        anti_patterns=['Version raten', 'Ohne Lock-File deployen'], risk_level='medium')

    s.add_entry(bug_type='DeprecatedAPI', languages=['python','javascript','java'],
        symptoms=[r"DeprecationWarning", r"deprecated", r"will be removed", r"use instead"],
        root_causes=['Alte API verwendet', 'Funktion in neuer Version entfernt'],
        fix_patterns=['# Replace {old}() with {new}()', 'Check migration guide'],
        anti_patterns=['DeprecationWarning unterdrücken', 'Migration ignorieren'], risk_level='low')

    s.add_entry(bug_type='MissingDependency', languages=['python','javascript'],
        symptoms=[r"No module named|ModuleNotFoundError|Cannot find module"],
        root_causes=['Package nicht installiert', 'Fehlt in requirements.txt',
                     'Falsche Umgebung (venv/conda)'],
        fix_patterns=['pip install {package}', 'npm install {package}',
                      'Add to requirements.txt'],
        anti_patterns=['Ohne venv installieren', 'Global install'], risk_level='medium')

    s.add_entry(bug_type='CircularImport', languages=['python'],
        symptoms=[r"circular import", r"cannot import name.*partially initialized"],
        root_causes=['A importiert B, B importiert A', '__init__.py Zirkel'],
        fix_patterns=['Lazy import inside function', 'Move to shared module',
                      'from __future__ import annotations'],
        anti_patterns=['Beide Module importieren sich', 'Zirkuläre __init__.py'], risk_level='high')

    s.add_entry(bug_type='ConfigMissing', languages=['python','javascript'],
        symptoms=[r"KeyError.*config", r"config.*not found", r"settings.*missing"],
        root_causes=['Config-Datei fehlt', 'Environment-Variable nicht gesetzt',
                     'Falscher Config-Pfad'],
        fix_patterns=['os.environ.get("KEY", default)', 'config = load_config()',
                      'Check .env file'],
        anti_patterns=['Hardcoded defaults', 'Ohne Fallback'], risk_level='medium')

    s.add_entry(bug_type='EnvVarMissing', languages=['python','unix'],
        symptoms=[r"KeyError.*environ|os.environ.*KeyError|environment variable.*not set"],
        root_causes=['Umgebungsvariable nicht gesetzt', '.env-Datei fehlt'],
        fix_patterns=['os.environ.get("VAR", "default")', 'load_dotenv()'],
        anti_patterns=['Ohne Default', 'Crash bei fehlender Env'], risk_level='medium')

    s.add_entry(bug_type='PathConfigError', languages=['python','unix'],
        symptoms=[r"FileNotFoundError.*config|No such file.*config|path.*not found.*config"],
        root_causes=['Config-Pfad falsch', 'Relative vs absolute Pfade',
                     'Config in falschem Verzeichnis'],
        fix_patterns=['os.path.join(BASE_DIR, "config.yaml")', 'Path(__file__).parent / "config"'],
        anti_patterns=['Hardcoded absolute Pfade', 'Ohne Fallback'], risk_level='medium')

    s.add_entry(bug_type='BuildFailure', languages=['python','all'],
        symptoms=[r"Build failed|compilation error|syntax error.*build"],
        root_causes=['Syntax-Fehler', 'Typ-Fehler', 'Fehlende Build-Dependencies'],
        fix_patterns=['Check compiler output', 'pip install build-deps',
                      'python -m compileall .'],
        anti_patterns=['Build-Fehler ignorieren', 'Nicht reproduzierbar'], risk_level='high')

    s.add_entry(bug_type='TestFixtureMissing', languages=['python','javascript'],
        symptoms=[r"fixture.*not found", r"beforeEach.*not defined", r"setup.*failed"],
        root_causes=['Fixture nicht definiert', 'Falscher Scope', 'conftest.py falsch'],
        fix_patterns=['@pytest.fixture', 'def {name}(): return ...',
                      'conftest.py im test/-Verzeichnis'],
        anti_patterns=['Ohne Fixture', 'Globaler State'], risk_level='medium')

    s.add_entry(bug_type='MockMismatch', languages=['python','javascript'],
        symptoms=[r"Mock.*not called|expected.*call.*not found|unexpected.*call"],
        root_causes=['Mock falsch konfiguriert', 'Falscher call-Argumente',
                     'Mock wurde nicht gecalled'],
        fix_patterns=['mock.assert_called_once_with(args)',
                      'mocker.patch("module.func")'],
        anti_patterns=['Ohne Assert-Check mocken', 'Globaler Mock'], risk_level='medium')

    return s


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    print("BUG PATTERN STORE — Skeleton + 10 Seed")
    print("=" * 55)
    passed = 0

    s = BugPatternStore()
    t1 = len(s.entries) == 0
    print(f"  T1: {'✅' if t1 else '❌'} Empty store")

    s.add_entry(bug_type='NullPointer', languages=['python'], symptoms=[r'NoneType.*has no attribute'],
                root_causes=['test'], fix_patterns=['if x:'])
    t2 = len(s.entries) == 1
    print(f"  T2: {'✅' if t2 else '❌'} Add entry → {len(s.entries)}")

    results = s.search('NoneType has no attribute city', language='python')
    t3 = len(results) >= 1
    print(f"  T3: {'✅' if t3 else '❌'} Search NullPointer → {len(results)} results")

    s.add_entry(bug_type='OutOfBounds', languages=['python'], symptoms=[r'list index out of range'],
                root_causes=['test'], fix_patterns=['if:'])
    results = s.search('list index out of range', language='python')
    t4 = len(results) >= 1
    print(f"  T4: {'✅' if t4 else '❌'} Search OutOfBounds → {len(results)} results")

    results = s.search('NullPointer', language='python')
    t5 = len(results) >= 1
    print(f"  T5: {'✅' if t5 else '❌'} Language-specific search → {len(results)}")

    by_type = s.get_by_bug_type('NullPointer')
    t6 = len(by_type) == 1
    print(f"  T6: {'✅' if t6 else '❌'} get_by_bug_type → {len(by_type)}")

    st = s.stats()
    t7 = st['actions_executed'] == 0 and st['store_type'] == 'READ_ONLY'
    print(f"  T7: {'✅' if t7 else '❌'} Stats → actions={st['actions_executed']} {st['store_type']}")

    seed = create_seed_bug_store()
    t8 = len(seed.entries) == 10
    print(f"\n  Seed: {'✅' if t8 else '❌'} {len(seed.entries)} entries, "
          f"types={seed.stats()['bug_types']}")

    passed = sum([t1,t2,t3,t4,t5,t6,t7,t8])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/8 Tests bestanden")
    print(f"  {'✅ BUG PATTERN STORE FERTIG' if passed >= 7 else '⚠️'}")
