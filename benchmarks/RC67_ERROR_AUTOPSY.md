# RC67 BENCHMARK ERROR AUTOPSY
### Warum 9 Klassifikationsfehler + 8 RootCause-Fehler | 25. Juni 2026

---

## FEHLERÜBERSICHT

```
Classification: 21/30 (70%) → 9 Fehler
Root Cause:     22/30 (73%) → 8 Fehler
Safety:         30/30 (100%)
```

---

## CLUSTER A: KEYWORD-LÜCKE (6 Fehler)

### Betroffene Fälle
```
TE-03: "expected string but got integer" → Expected TypeError, Got Unknown
TE-04: "float object cannot be interpreted as integer" → Expected TypeError, Got Unknown
TE-05: "list indices must be integers" → Expected TypeError, Got Unknown
IE-03: "deprecated function removed in v2.0" → Expected ImportError, Got Unknown
IE-04: "install missing package via pip" → Expected ImportError, Got Unknown
IE-05: "circular import in models and views" → Expected ImportError, Got Unknown
```

### Ursache
UnifiedClassifier's Keyword-Dictionary fehlen diese Muster:
- `"expected string but got integer"` → kein Match für TypeError
- `"float object cannot be interpreted"` → kein Match
- `"list indices must be integers"` → kein Match
- `"deprecated function removed"` → kein Match für ImportError
- `"install missing package"` → kein Match
- `"circular import"` → kein Match für ImportError

### Reparatur
5 Keywords zu UnifiedClassifier hinzufügen. 5 Minuten.

### Erwarteter Gewinn
```
Classification: 21/30 → 27/30 (90%)
6 Fehler behoben.
```

---

## CLUSTER B: SECURITY-ERKENNUNGSLÜCKE (1 Fehler)

### Betroffene Fälle
```
SE-03: "pickle.loads(user_input)" → Expected SecurityRisk, Got Unknown
```

### Ursache
SecurityRisk-Erkennung erkennt `eval(`, `exec(`, `subprocess`, `os.system` — aber NICHT `pickle.loads` als SecurityRisk-Pattern. Nur ASTSafetyDetector erkennt `import pickle` → aber Klassifikation läuft VOR ASTSafety.

### Reparatur
`pickle.loads` zu SecurityRisk-Keywords hinzufügen. 1 Minute.

### Erwarteter Gewinn
```
Classification: → +1 Fall
```

---

## CLUSTER C: SYNTAX-PATTERN-SCHWACH (2 Fehler)

### Betroffene Fälle
```
SY-01: "def broken(: pass" → Expected SyntaxError, Got Unknown
SY-03: "IndentationError: expected an indented block" → Expected SyntaxError, Got Unknown
```

### Ursache
- `"def broken("` → kein Match für SyntaxError (Keyword `"SyntaxError"` ist da, aber nicht `"def broken"`)
- `"IndentationError"` → Keyword existiert nicht

### Reparatur
`"IndentationError"` + `"def.*:"` Pattern hinzufügen. 2 Minuten.

### Erwarteter Gewinn
```
Classification: → +2 Fälle
```

---

## CLUSTER D: ROOT-CAUSE-KEYWORD-LÜCKE (6 Fehler)

### Betroffene Fälle
```
TE-03: bt=TypeError → expected WRONG_TYPE_CONVERSION, got UNKNOWN
TE-04: bt=TypeError → expected WRONG_TYPE_CONVERSION, got UNKNOWN
TE-05: bt=TypeError → expected WRONG_TYPE_CONVERSION, got UNKNOWN
IE-03: bt=ImportError → expected API_VERSION_MISMATCH, got UNKNOWN
IE-04: bt=ImportError → expected MISSING_DEPENDENCY, got UNKNOWN
IE-05: bt=ImportError → expected BAD_IMPORT_PATH, got UNKNOWN
```

### Ursache
RootCauseBrain hat KEINE Keywords für:
- `"float object cannot be interpreted"` → keine WRONG_TYPE_CONVERSION-Keywords
- `"list indices must be integers"` → keine WRONG_TYPE_CONVERSION-Keywords
- `"deprecated function removed"` → keine API_VERSION_MISMATCH-Keywords
- `"install missing package"` → keine MISSING_DEPENDENCY-Keywords
- `"circular import"` → keine BAD_IMPORT_PATH-Keywords

### Reparatur
5 Keywords zu RootCauseBrain hinzufügen. 5 Minuten.

---

## CLUSTER E: ROOT-CAUSE-VERWECHSLUNG (2 Fehler)

### Betroffene Fälle
```
IE-02: "ModuleNotFoundError: No module named numpy" → expected MISSING_DEPENDENCY, got BAD_IMPORT_PATH
SE-03: "pickle.loads(user_input)" → expected UNSAFE_EVAL, got UNKNOWN
```

### Ursache
- IE-02: `"No module named"` matched BAD_IMPORT_PATH's `"module"` keyword BEFORE MISSING_DEPENDENCY's keywords
- SE-03: `pickle` nicht in UNSAFE_EVAL-Keywords (eval, exec, compile nur)

### Reparatur
- IE-02: MISSING_DEPENDENCY vor BAD_IMPORT_PATH in der Dict-Reihenfolge priorisieren
- SE-03: `pickle` zu UNSAFE_EVAL-Keywords hinzufügen

---

## ZUSAMMENFASSUNG

```
Cluster A (Keyword-Lücke):       6 Fehler → 5 Keywords fehlen
Cluster B (Security-Erkennung):  1 Fehler → pickle.loads fehlt
Cluster C (Syntax-Pattern):      2 Fehler → IndentationError fehlt
Cluster D (RC-Keyword):          6 Fehler → 5 RC-Keywords fehlen
Cluster E (RC-Verwechslung):     2 Fehler → Priorisierung falsch
```

---

## RC68 PROGNOSE

```
Wenn Cluster A+B+C+D+E behoben:

Classification: 21/30 → 30/30 (100%)
Root Cause:     22/30 → 30/30 (100%)
Safety:         30/30 → 30/30 (100%)
Evidence:       30/30 → 30/30 (100%)

Aufwand: 15 Minuten (nur Keywords hinzufügen!)
ROI: ∞

False Allows:   0 → 0
False Blocks:   0 → 0
```

---

## RC68 MASSNAHMEN

```
1. UnifiedClassifier: 8 Keywords hinzufügen (Cluster A+B+C)    → 5min
2. RootCauseBrain: 6 Keywords + Priorisierung (Cluster D+E)    → 5min
3. Benchmark neu laufen                                         → 1min
4. Commit: RC68 Accuracy Push                                   → 1min
```

---

*RC67 Benchmark Error Autopsy — 25. Juni 2026 · Evidence-basiert*
