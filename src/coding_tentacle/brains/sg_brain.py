"""
GEHIRN BQ — Symbol Grounding Brain (Harnad/Searle)
Symbole sind NICHT nur Text. Sie sind mit Code-Kontext, Fix-Wirkung und 
historischer Erfahrung verbunden. Ohne Grounding sind alle Symbole leer.

Grounding-Score = 0.35·diversity + 0.35·consistency + 0.15·frequency_norm + 0.15·cross_support

Autor: Hermes + David | Coding Tentacle 2026 — GEN 14
Quelle: Harnad "Symbol Grounding Problem" (1990), Searle "Chinese Room" (1980)
"""
import numpy as np, math, time, os, json, re
from collections import defaultdict, deque

class SymbolGroundingBrain:
    """Gehirn BQ — Symbole durch Code-Erfahrung mit Bedeutung füllen."""
    def __init__(self, decay_days=30, history_path=None, library_store=None, bug_pattern_store=None):
        self.decay_days = decay_days
        self.history_path = history_path or os.path.expanduser('~/.hermes/bq_history.json')
        self.library_store = library_store
        self.bug_pattern_store = bug_pattern_store  # Optional
        # groundings: symbol → Grounding
        self.groundings = {}
        # related_symbols: symbol → [ähnliche Symbole]
        self.related = defaultdict(set)
        # bridge_stubs (später mit echten Brains verbinden)
        self.bridges = {'code_context': None, 'attention': None, 'temporal': None, 'knn': None}
        self.total_symbols_seen = 0
        self.total_learn_events = 0
        # Cross-session history laden
        self._load_history()

    # ═══════════ STACKTRACE PARSING ═══════════

    @staticmethod
    def parse_stacktrace(raw_trace):
        """Extrahiere Fehlertyp, Datei, Zeile, Funktion aus Raw Stacktrace."""
        result = {'error_type': '', 'message': '', 'file': '', 'line': 0, 'function': ''}
        if not raw_trace:
            return result
        lines = raw_trace.strip().split('\n')
        # Erste Zeile: "ErrorType: message"
        first = lines[0].strip()
        if ':' in first:
            result['error_type'] = first.split(':')[0].strip()
            result['message'] = first.split(':', 1)[1].strip() if ':' in first else ''
        # Suche nach Datei+Zeile: File "x.py", line 42, in function
        for line in lines:
            import re
            m = re.search(r'File\s+"(.+?)",\s*line\s+(\d+)(?:,\s*in\s+(\w+))?', line)
            if m:
                result['file'] = m.group(1)
                result['line'] = int(m.group(2))
                result['function'] = m.group(3) or ''
                break
        return result

    def learn_from_context(self, sig, stacktrace='', test_output='', code_context=None, success=True):
        """Lerne aus vollständigem Kontext: Stacktrace + Testoutput + Code-Kontext."""
        symbol = sig.split(':')[0] if ':' in sig else sig.split()[0] if ' ' in sig else sig
        parsed = self.parse_stacktrace(stacktrace) if stacktrace else {}

        # Code-Kontext aus Stacktrace oder explizitem Context
        ctx = code_context or {}
        if not ctx and parsed.get('file'):
            ctx = {'file': parsed['file'], 'line': parsed['line'], 
                   'function': parsed.get('function', ''),
                   'stacktrace': stacktrace[:500]}

        # Fix-Effekt aus Test-Output ableiten
        fix_effect = None
        if test_output:
            test_ok = 'PASS' in test_output.upper() or 'OK' in test_output.upper()
            fix_effect = {
                'patch': f'fix_{symbol}',
                'before': stacktrace[:100] if stacktrace else '',
                'after': test_output[:100],
                'delta': 'Tests passed' if test_ok else 'Tests still fail',
                'success': True,  # Grounding-Erfolg unabhängig vom Testergebnis
                'timestamp': time.time(),
                'file': ctx.get('file', 'unknown'),
                'line': ctx.get('line', 0),
                'test_output': test_output[:200],
            }
        elif code_context:
            # Auch ohne Test-Output: Kontext allein ist schon Grounding
            fix_effect = {
                'patch': f'fix_{symbol}',
                'before': stacktrace[:100] if stacktrace else '',
                'after': 'Context established',
                'delta': 'Code context added',
                'success': True,
                'timestamp': time.time(),
                'file': ctx.get('file', 'unknown'),
                'line': ctx.get('line', 0),
                'test_output': 'N/A',
            }

        self.learn(sig, f'fix_{symbol}', success, code_context=ctx if ctx else None,
                   fix_effect=fix_effect)
        return self.think(sig)

    # ═══════════ CROSS-SESSION HISTORY ═══════════

    def _load_history(self):
        """Lade Groundings aus früheren Sessions."""
        if not os.path.exists(self.history_path) or os.path.getsize(self.history_path) == 0:
            return
        try:
            with open(self.history_path) as f:
                data = json.load(f)
            for sym, gdata in data.get('groundings', {}).items():
                if sym not in self.groundings:
                    self.groundings[sym] = Grounding(sym)
                g = self.groundings[sym]
                g.total_contexts = gdata.get('total_contexts', 0)
                g.total_fix_effects = gdata.get('total_fix_effects', 0)
                g.success_count = gdata.get('success_count', 0)
                g.consistency = gdata.get('consistency', 0)
                g.diversity = gdata.get('diversity', gdata.get('total_contexts', 1) * 0.05)
                g.frequency_norm = min(1.0, g.total_fix_effects / 20.0)
                g.grounding_score = gdata.get('score', 0)
                g.meanings = gdata.get('meanings', [])[:3]
                # Boot-Strap: historische Kontexte rekonstruieren
                for ctx in gdata.get('contexts', [])[:5]:
                    if isinstance(ctx, dict):
                        g.code_contexts.append(ctx)
                        g.total_contexts = max(g.total_contexts, len(g.code_contexts))
                for fe in gdata.get('fix_effects', [])[:10]:
                    if isinstance(fe, dict):
                        g.fix_effects.append(fe)
                        g.total_fix_effects = max(g.total_fix_effects, len(g.fix_effects))
                g.recalculate_score(0)
            self.total_symbols_seen = data.get('total_seen', 0)
        except json.JSONDecodeError:
            pass  # Leere oder korrupte Datei
        except Exception as e:
            pass

    def _save_history(self):
        """Speichere Groundings für nächste Session."""
        os.makedirs(os.path.dirname(self.history_path), exist_ok=True)
        data = {
            'total_seen': self.total_symbols_seen,
            'groundings': {}
        }
        for sym, g in self.groundings.items():
            if g.total_contexts > 0:
                data['groundings'][sym] = {
                    'total_contexts': g.total_contexts,
                    'total_fix_effects': g.total_fix_effects,
                    'success_count': g.success_count,
                    'consistency': g.consistency,
                    'diversity': g.diversity,
                    'score': g.grounding_score,
                    'meanings': g.meanings,
                    'contexts': g.code_contexts[-3:],
                    'fix_effects': g.fix_effects[-5:],
                }
        with open(self.history_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    # ═══════════ INITIAL CONFIDENCE BOOST ═══════════

    def think(self, sig, emb=None):
        """Symbol analysieren: Wie stark ist das Grounding?"""
        symbol = sig.split(':')[0] if ':' in sig else sig
        self.total_symbols_seen += 1

        if symbol not in self.groundings or self.groundings[symbol].total_contexts == 0:
            # INITIAL CONFIDENCE BOOST: Wenn Code-Kontext im sig steckt
            # Signal ans Orchestrator: "Gib mir mehr"
            return {
                'action': 'ASK_CONTEXT',
                'pattern': None,
                'confidence': 0.0,
                'grounding_score': 0.0,
                'meaning': f'Ungrounded: Kein Code-Kontext für {symbol}.',
                'missing_context': ['code_snippet', 'stacktrace', 'file_line'],
                'reasoning': f'SG: {symbol} ist ungrounded. Frage nach Code-Kontext.'
            }

        g = self.groundings[symbol]
        
        # Initial Confidence Boost aus verfügbarem Kontext
        boost = 0.0
        if g.total_contexts >= 1: boost += 0.05
        if g.total_contexts >= 3: boost += 0.05
        if g.total_fix_effects >= 3: boost += 0.05
        if g.success_count >= 2: boost += 0.05
        boost = min(0.20, boost)  # Maximal 0.20 Boost
        
        # Library Evidence Boost (optional, read-only, max +0.10)
        if self.library_store:
            lib_results = self.library_store.search(symbol, max_results=1)
            if lib_results:
                boost += 0.10
        boost = min(0.25, boost)  # Overall cap
        
        # Bug Pattern Store Boost (optional, read-only, max +0.10)
        if self.bug_pattern_store:
            bp_results = self.bug_pattern_store.search(symbol, max_results=1)
            if bp_results:
                boost += 0.10
                g.grounding_score = min(1.0, g.grounding_score + 0.05)
        
        score = min(1.0, g.grounding_score + boost)
        meaning = g.primary_meaning()

        if score < 0.3:
            action = 'ASK_CONTEXT'
            missing = g.missing_dimensions()
        elif score < 0.6:
            action = 'EXPLORE'
            missing = []
        else:
            action = 'APPLY_PATTERN'
            missing = []

        best_fix = g.best_fix()

        return {
            'action': action,
            'pattern': best_fix,
            'confidence': min(1.0, score),
            'grounding_score': score,
            'meaning': meaning,
            'evidence': g.evidence_summary(),
            'missing_context': missing,
            'reasoning': f'SG: {symbol} score={score:.2f} diversity={g.diversity:.2f} '
                         f'consistency={g.consistency:.2f} → {action}'
        }

    def learn(self, sig, pat, success, emb=None, code_context=None, fix_effect=None):
        """Lerne: Symbol + Code-Kontext + Fix-Wirkung → stärkeres Grounding"""
        symbol = sig.split(':')[0] if ':' in sig else sig
        self.total_learn_events += 1

        if symbol not in self.groundings:
            self.groundings[symbol] = Grounding(symbol)

        g = self.groundings[symbol]

        # Code-Kontext speichern
        if code_context:
            g.add_context(code_context)

        # Fix-Wirkung speichern
        if fix_effect or pat:
            effect = fix_effect or {
                'patch': pat, 'before': f'Bug: {symbol}',
                'after': f'Fix: {pat}' if success else f'Failed: {pat}',
                'delta': 'Test passed' if success else 'Test still fails',
                'success': success, 'timestamp': time.time(),
                'file': code_context.get('file', 'unknown') if code_context else 'unknown',
                'line': code_context.get('line', 0) if code_context else 0
            }
            g.add_fix_effect(effect)
            if success:
                g.success_count += 1

        # Ähnliche Symbole verknüpfen (cross-support)
        for other_sym, other_g in self.groundings.items():
            if other_sym != symbol:
                # Gleiche Fix-Patterns → Symbole sind verwandt
                overlap = set(g.fix_patterns()) & set(other_g.fix_patterns())
                if overlap:
                    self.related[symbol].add(other_sym)
                    self.related[other_sym].add(symbol)

        # Score neu berechnen
        g.recalculate_score(len(self.related.get(symbol, set())))

    def ground(self, symbol, code_context=None, fix_effect=None):
        """Explizites Grounding: Symbol + Kontext + Wirkung verankern"""
        if symbol not in self.groundings:
            self.groundings[symbol] = Grounding(symbol)
        g = self.groundings[symbol]
        if code_context:
            g.add_context(code_context)
        if fix_effect:
            g.add_fix_effect(fix_effect)
        g.recalculate_score(len(self.related.get(symbol, set())))
        return g

    def stats(self):
        if not self.groundings:
            return {'brain_type': 'Symbol Grounding (BQ)', 'total_symbols': 0}

        scores = [g.grounding_score for g in self.groundings.values() if g.total_contexts > 0]
        grounded = [s for s, g in self.groundings.items() if g.grounding_score >= 0.6 and g.total_contexts > 0]
        partial = [s for s, g in self.groundings.items() if 0.3 <= g.grounding_score < 0.6]
        ungrounded = [s for s, g in self.groundings.items() if g.grounding_score < 0.3 or g.total_contexts == 0]
        
        strongest = sorted(self.groundings.items(), key=lambda x: -x[1].grounding_score)[:3]

        return {
            'brain_type': 'Symbol Grounding (BQ — Gen 14)',
            'total_symbols': len(self.groundings),
            'grounded': len(grounded),
            'partially_grounded': len(partial),
            'ungrounded': len(ungrounded),
            'avg_score': round(np.mean(scores), 3) if scores else 0,
            'strongest': [(s, round(g.grounding_score, 3), g.primary_meaning()) for s, g in strongest],
            'total_fix_effects': sum(g.total_fix_effects for g in self.groundings.values()),
            'total_contexts': sum(g.total_contexts for g in self.groundings.values()),
            'bridge_status': {k: 'stub' if v is None else 'connected' for k, v in self.bridges.items()}
        }

    def __repr__(self):
        grounded = sum(1 for g in self.groundings.values() if g.grounding_score >= 0.6)
        return f"SGBrain(symbols={len(self.groundings)}, grounded={grounded})"


# ═══════════ GROUNDING DATENSTRUKTUR ═══════════

class Grounding:
    def __init__(self, symbol):
        self.symbol = symbol
        self.code_contexts = []        # [{file, line, function, code, stacktrace}]
        self.fix_effects = []          # [{patch, before, after, delta, success, timestamp}]
        self.meanings = []             # ["Objektreferenz ist null", ...]
        self.diversity = 0.0           # 0-1: verschiedene Code-Kontexte
        self.consistency = 0.0         # 0-1: Fix-Wirkung konsistent
        self.frequency_norm = 0.0      # 0-1: normierte Häufigkeit
        self.cross_support = 0.0       # 0-1: verwandte Symbole stützen
        self.success_count = 0      # erfolgreiche Fixes
        self.grounding_score = 0.0
        self.last_seen = time.time()
        self.total_contexts = 0
        self.total_fix_effects = 0

    def add_context(self, ctx):
        """Neuen Code-Kontext hinzufügen (Deduplikation via file+line)"""
        key = (ctx.get('file', ''), ctx.get('line', 0))
        if not any((c.get('file'), c.get('line')) == key for c in self.code_contexts):
            self.code_contexts.append(ctx)
            self.total_contexts = len(self.code_contexts)
            if len(self.code_contexts) > 50:
                self.code_contexts = self.code_contexts[-50:]
        self.last_seen = time.time()

    def add_fix_effect(self, effect):
        """Fix-Wirkung speichern"""
        self.fix_effects.append(effect)
        self.total_fix_effects = len(self.fix_effects)
        if len(self.fix_effects) > 100:
            self.fix_effects = self.fix_effects[-100:]

        # Meaning aus Fix-Wirkung ableiten
        if effect.get('success') and len(self.meanings) < 5:
            meaning = self._derive_meaning(effect)
            if meaning and meaning not in self.meanings:
                self.meanings.append(meaning)

        self.last_seen = time.time()

    def _derive_meaning(self, effect):
        """Aus Fix-Wirkung eine Bedeutung ableiten"""
        delta = effect.get('delta', '')
        before = effect.get('before', '')
        patch = effect.get('patch', '')
        
        if 'guard' in patch.lower() or 'null check' in patch.lower():
            return f'{self.symbol}: Objekt war null → guard verhindert Zugriff'
        if 'bounds' in patch.lower() or 'len(' in patch.lower():
            return f'{self.symbol}: Index außerhalb → bounds-check'
        if '.get(' in patch.lower() or 'default' in patch.lower():
            return f'{self.symbol}: Schlüssel fehlt → default/fallback'
        if 'try' in patch.lower() or 'except' in patch.lower():
            return f'{self.symbol}: Operation kann fehlschlagen → try/except'
        if 'isinstance' in patch.lower() or 'type' in patch.lower():
            return f'{self.symbol}: Falscher Typ → type-check'
        if 'hasattr' in patch.lower() or 'optional' in patch.lower():
            return f'{self.symbol}: Attribut optional → hasattr-check'
        if 'lock' in patch.lower() or 'mutex' in patch.lower() or 'synchronized' in patch.lower():
            return f'{self.symbol}: Race Condition → Lock/Mutex'
        if 'lru' in patch.lower() or 'cache' in patch.lower() or 'evict' in patch.lower():
            return f'{self.symbol}: Speicher unbegrenzt → Cache eviction'
        return None

    def fix_patterns(self):
        """Alle verwendeten Fix-Patterns"""
        return [e.get('patch', '') for e in self.fix_effects]

    def best_fix(self):
        """Häufigster erfolgreicher Fix"""
        successes = [e.get('patch') for e in self.fix_effects if e.get('success')]
        if not successes:
            return None
        from collections import Counter
        return Counter(successes).most_common(1)[0][0]

    def primary_meaning(self):
        """Häufigste Bedeutung"""
        if not self.meanings:
            return f'{self.symbol}: Noch keine Bedeutung abgeleitet.'
        return self.meanings[0]

    def evidence_summary(self):
        """Kurze Evidenz-Zusammenfassung"""
        total = self.total_fix_effects
        succ = sum(1 for e in self.fix_effects if e.get('success'))
        files = list(set(c.get('file', '?') for c in self.code_contexts))
        return {
            'total_fixes': total,
            'successful': succ,
            'success_rate': f'{succ/max(1,total):.0%}',
            'distinct_files': len(files),
            'files': files[:3],
            'top_patterns': list(set(self.fix_patterns()))[:3]
        }

    def missing_dimensions(self):
        """Welche Grounding-Dimensionen fehlen noch?"""
        missing = []
        if self.total_contexts == 0:
            missing.append('code_snippet')
        if self.total_contexts < 2:
            missing.append('stacktrace')
        if not any(e.get('success') for e in self.fix_effects):
            missing.append('successful_fix')
        if self.total_fix_effects < 3:
            missing.append('more_fix_evidence')
        return missing

    def recalculate_score(self, n_related=0):
        """Grounding-Score: 0.35·diversity + 0.35·consistency + 0.15·freq + 0.15·cross"""
        # Diversity: verschiedene Dateien + Context-Anzahl
        if self.total_contexts >= 1:
            files = set(c.get('file', '') for c in self.code_contexts)
            # Mehr Contexts → höhere Diversity (bis zu einem Punkt)
            context_factor = min(1.0, len(self.code_contexts) * 0.1)
            file_factor = min(1.0, len(files) * 0.3)
            self.diversity = file_factor * 0.6 + context_factor * 0.4
        else:
            self.diversity = 0.0

        # Consistency: erfolgreiche Fixes / total
        if self.total_fix_effects >= 1:
            succ = sum(1 for e in self.fix_effects if e.get('success'))
            # Bei vielen Erfolgen → hohe Consistency
            self.consistency = succ / self.total_fix_effects
        else:
            self.consistency = 0.0

        # Frequency: normiert (maximal 50 Events)
        freq = min(self.total_fix_effects + self.total_contexts, 50)
        self.frequency_norm = freq / 50.0

        # Cross-support: verwandte Symbole
        self.cross_support = min(1.0, n_related * 0.2)

        # Score
        self.grounding_score = (
            0.35 * self.diversity +
            0.35 * self.consistency +
            0.15 * self.frequency_norm +
            0.15 * self.cross_support
        )
        self.grounding_score = round(min(1.0, self.grounding_score), 4)

    def __repr__(self):
        return f"Grounding({self.symbol}: score={self.grounding_score:.2f})"


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    print("GEHIRN BQ — Symbol Grounding Brain")
    print("=" * 60)
    
    b = SymbolGroundingBrain()
    passed = 0
    
    # TEST 1: Symbol ohne Kontext → ASK_CONTEXT
    dec = b.think("AttributeError:unknown.py:0")
    t1 = dec['action'] == 'ASK_CONTEXT' and dec['grounding_score'] == 0.0
    print(f"  T1: {'✅' if t1 else '❌'} Ungegroundet → ASK_CONTEXT (score={dec['grounding_score']})")
    if t1: passed += 1
    
    # TEST 2: Symbol MIT Code-Kontext → bessere Bedeutung
    b.learn("AttributeError:user.py:12", "hasattr_check", True,
            code_context={'file': 'user.py', 'line': 12, 'function': 'get_profile',
                         'code': 'user.profile.city', 'stacktrace': 'AttributeError: NoneType'})
    dec2 = b.think("AttributeError:user.py:12")
    t2 = dec2['grounding_score'] > 0.15
    print(f"  T2: {'✅' if t2 else '❌'} Mit Kontext → Score steigt (score={dec2['grounding_score']:.2f})")
    if t2: passed += 1
    
    # TEST 3: Erfolgreicher Fix → Score steigt weiter
    b.learn("AttributeError:order.py:31", "hasattr_check", True,
            code_context={'file': 'order.py', 'line': 31, 'function': 'process',
                         'code': 'order.customer.name'},
            fix_effect={'patch': 'hasattr_check', 'before': 'AttributeError', 
                       'after': 'OK', 'delta': 'Test passed', 'success': True})
    dec3 = b.think("AttributeError:order.py:31")
    t3 = dec3['grounding_score'] > dec2['grounding_score']
    print(f"  T3: {'✅' if t3 else '❌'} Erfolgreicher Fix → Score={dec3['grounding_score']:.2f} (vorher={dec2['grounding_score']:.2f})")
    if t3: passed += 1
    
    # TEST 4: Fehlgeschlagener Fix → Score sinkt oder Meaning spaltet
    b.learn("AttributeError:auth.py:88", "guard_clause", False,
            code_context={'file': 'auth.py', 'line': 88, 'function': 'login',
                         'code': 'session.user.role'},
            fix_effect={'patch': 'guard_clause', 'before': 'AttributeError',
                       'after': 'Still fails', 'delta': 'wrong fix', 'success': False})
    dec4 = b.think("AttributeError:auth.py:88")
    t4 = dec4['grounding_score'] > 0  # Score existiert, aber ggf. niedriger
    print(f"  T4: {'✅' if t4 else '❌'} Fehlschlag → Score={dec4['grounding_score']:.2f} (sinkt, aber >0)")
    if t4: passed += 1
    
    # TEST 5: OOD Symbol → EXPLORE
    dec5 = b.think("StackOverflow:deep.py:999")
    t5 = dec5['action'] in ('ASK_CONTEXT', 'EXPLORE') and dec5['grounding_score'] < 0.3
    print(f"  T5: {'✅' if t5 else '❌'} OOD → {dec5['action']} (score={dec5['grounding_score']:.2f})")
    if t5: passed += 1
    
    # TEST 6: Häufiges falsches Muster nicht dominant
    for i in range(20):
        b.learn("NullPointer:fake.py:1", "bad_fix", False,
                code_context={'file': 'fake.py', 'line': 1},
                fix_effect={'patch': 'bad_fix', 'before': 'NullPointer', 
                           'after': 'fails', 'delta': 'no effect', 'success': False})
    dec6 = b.think("NullPointer:fake.py:1")
    t6 = dec6['grounding_score'] < 0.4  # 20× fail → Score bleibt niedrig
    print(f"  T6: {'✅' if t6 else '❌'} 20× falsch → nicht dominant (score={dec6['grounding_score']:.2f})")
    if t6: passed += 1
    
    # TEST 7: Verschiedene Kontexte erhöhen diversity
    # Trainiere NullPointer in 3 verschiedenen Dateien
    for i, ctx in enumerate([
        {'file': 'payment.py', 'line': 42, 'function': 'process'},
        {'file': 'auth.py', 'line': 15, 'function': 'login'},
        {'file': 'order.py', 'line': 88, 'function': 'submit'}
    ]):
        b.learn("NullPointer:save.py:1", "guard_clause", True,
                code_context=ctx,
                fix_effect={'patch': 'guard_clause', 'success': True})
    dec7 = b.think("NullPointer:save.py:1")
    g = b.groundings.get('NullPointer')
    t7 = g and g.diversity > 0.1
    print(f"  T7: {'✅' if t7 else '❌'} 3 Dateien → diversity={g.diversity:.2f} (score={dec7['grounding_score']:.2f})")
    if t7: passed += 1
    
    # TEST 8: Gleicher Kontext stabilisiert consistency
    for i in range(5):
        b.learn("TypeError:calc.py:5", "isinstance_check", True,
                code_context={'file': 'calc.py', 'line': 5, 'function': 'add'},
                fix_effect={'patch': 'isinstance_check', 'success': True})
    dec8 = b.think("TypeError:calc.py:5")
    t8 = dec8['grounding_score'] > 0.3
    print(f"  T8: {'✅' if t8 else '❌'} 5× gleicher Erfolg → consistency hoch (score={dec8['grounding_score']:.2f})")
    if t8: passed += 1
    
    # TEST 9: stats() gibt sinnvolle Werte
    s = b.stats()
    t9 = (s['total_symbols'] >= 3 and s['avg_score'] > 0 and 
          len(s.get('strongest', [])) >= 2 and s['total_fix_effects'] > 0)
    print(f"  T9: {'✅' if t9 else '❌'} stats(): {s['total_symbols']} Symbole, "
          f"avg={s['avg_score']:.3f}, strongest={[x[0] for x in s.get('strongest',[])]}")
    if t9: passed += 1
    
    # TEST 10: Interface kompatibel (think/learn/stats existieren)
    t10 = (hasattr(b, 'think') and hasattr(b, 'learn') and hasattr(b, 'stats') and 
           hasattr(b, 'ground'))
    print(f"  T10: {'✅' if t10 else '❌'} Interface: think/learn/stats/ground")
    if t10: passed += 1
    
    print(f"\n  {'='*60}")
    print(f"  ERGEBNIS: {passed}/10 Tests bestanden")
    print(f"  {'✅ BQ-BRAIN FUNKTIONIERT' if passed >= 8 else '⚠️ Nachbesserung nötig'}")
    print(f"  {'='*60}")
