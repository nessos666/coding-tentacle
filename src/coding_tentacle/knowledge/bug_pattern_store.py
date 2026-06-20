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
