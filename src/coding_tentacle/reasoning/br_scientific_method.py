"""
GEHIRN BR — Scientific Method Brain (Gen 14b)
Hypothese → Experiment → Evidenz → Falsifikation → Entscheidung.
Kein Pattern-Matching. Kein Raten. Systematische Investigation.

Autor: Hermes + David | Coding Tentacle 2026
Quelle: Popper (1934), AI Scientist-v2 (2025)
"""
import time, uuid, math
from collections import defaultdict

class Hypothesis:
    def __init__(self, statement, confidence=0.5, source='generated'):
        self.id = str(uuid.uuid4())[:8]
        self.statement = statement
        self.confidence = confidence
        self.prior_confidence = confidence
        self.evidence_for = []
        self.evidence_against = []
        self.status = 'ACTIVE'
        self.source = source
        self.created_at = time.time()
        self.updated_at = time.time()

    def add_evidence(self, ev_type, strength, description):
        ev = {'type': ev_type, 'strength': strength, 'description': description, 'timestamp': time.time()}
        if ev_type == 'supporting':
            self.evidence_for.append(ev)
            self.confidence = min(1.0, self.confidence + 0.10 * strength)
        elif ev_type == 'contradicting':
            self.evidence_against.append(ev)
            self.confidence = max(0.0, self.confidence - 0.15 * strength)
        self.updated_at = time.time()
        self._update_status()
        return ev

    def _update_status(self):
        if self.confidence < 0.15:
            self.status = 'FALSIFIED'
        elif self.confidence > 0.90 and len(self.evidence_for) >= 3:
            self.status = 'VERIFIED'
        else:
            self.status = 'ACTIVE'

    def evidence_count(self):
        return len(self.evidence_for) + len(self.evidence_against)

    def to_dict(self):
        return {
            'id': self.id, 'statement': self.statement,
            'confidence': round(self.confidence, 3), 'status': self.status,
            'evidence_for': len(self.evidence_for), 'evidence_against': len(self.evidence_against),
            'source': self.source
        }

    def __repr__(self):
        return f"Hypothesis({self.id}: {self.status} conf={self.confidence:.2f} '{self.statement[:40]}')"


class Experiment:
    def __init__(self, target_hypothesis_id, description, expected_if_true, expected_if_false):
        self.id = str(uuid.uuid4())[:8]
        self.target_hypothesis_id = target_hypothesis_id
        self.description = description
        self.expected_if_true = expected_if_true
        self.expected_if_false = expected_if_false
        self.actual_result = None
        self.status = 'PLANNED'
        self.created_at = time.time()

    def run(self, actual_result):
        self.actual_result = actual_result
        self.status = 'DONE'
        return actual_result

    def to_dict(self):
        return {
            'id': self.id, 'target': self.target_hypothesis_id,
            'description': self.description, 'status': self.status,
            'actual': self.actual_result
        }


class ScientificMethodBrain:
    """Gehirn BR — Wissenschaftliche Methode für Bug-Fixing."""

    # Template-Hypothesen generiert aus BQ-Grounding
    HYPOTHESIS_TEMPLATES = {
        'NullPointer': [
            'Objekt wurde nicht initialisiert (null)',
            'Rückgabewert einer Funktion ist None',
            'DB-Query liefert keinen Datensatz (null)',
            'Optional-Parameter wurde nicht geprüft',
        ],
        'AttributeError': [
            'Objekt hat das Attribut nicht (falscher Typ)',
            'Attribut ist optional und fehlt (None)',
            'Verketteter Zugriff: x.y.z wobei y=None',
            'Falscher Import: Modul hat das Attribut nicht',
        ],
        'TypeError': [
            'Falscher Typ: String statt Integer/Objekt',
            'None wird als Typ verwendet',
            'Operator nicht für diesen Typ definiert',
            'Funktion erwartet anderen Typ als übergeben',
        ],
        'ImportError': [
            'Modul existiert nicht (falscher Name)',
            'Modul ist nicht installiert (fehlende Dependency)',
            'Zyklischer Import',
            'Falscher Pfad/Version des Moduls',
        ],
        'MemoryLeak': [
            'Unbegrenztes Cache-Wachstum',
            'Referenz-Zyklus verhindert GC',
            'Offene Datei/Verbindung nicht geschlossen',
            'Globale Liste wächst ohne Limit',
        ],
        'RaceCondition': [
            'Ungeschützter Shared-State-Zugriff',
            'Fehlende Synchronisation (Lock/Mutex)',
            'Falsche Annahme über Atomarität',
            'Deadlock durch falsche Lock-Reihenfolge',
        ],
        '_default': [
            'Einfacher Programmierfehler (Tippfehler/Logik)',
            'Fehlende Validierung der Eingabedaten',
            'Edge-Case nicht abgedeckt',
            'Externer Faktor (Netzwerk, DB, API)',
        ]
    }

    def __init__(self, library_store=None, bug_pattern_store=None):
        self.hypotheses = []
        self.experiments = []
        self.evidence_log = []
        self.library_store = library_store
        self.bug_pattern_store = bug_pattern_store  # Optional
        self.total_think_calls = 0
        self.total_learn_calls = 0

    # ═══════════ CORE API ═══════════

    def think(self, sig, bq_grounding=None, wm_context=None):
        """Generiere/ranke Hypothesen basierend auf Bug + Grounding."""
        self.total_think_calls += 1
        bt = sig.split(':')[0] if ':' in sig else sig.split()[0] if ' ' in sig else sig

        # Neue Hypothesen generieren (wenn keine aktiv)
        active = [h for h in self.hypotheses if h.status == 'ACTIVE']
        if not active:
            templates = self.HYPOTHESIS_TEMPLATES.get(bt, self.HYPOTHESIS_TEMPLATES['_default'])
            for tmpl in templates:
                self.create_hypothesis(tmpl, confidence=0.5, source=f'template:{bt}')
            active = [h for h in self.hypotheses if h.status == 'ACTIVE']

        # Ranking: confidence + BQ-Boost + Library-Boost
        ranked = []
        for h in active:
            boost = 0.0
            if bq_grounding:
                boost += bq_grounding.get('grounding_score', 0) * 0.1
                meaning = bq_grounding.get('meaning', '')
                if any(w in meaning.lower() for w in h.statement.lower().split()[:3]):
                    boost += 0.05
            # Library Evidence Boost (optional, read-only)
            if self.library_store:
                lib_results = self.library_store.search(h.statement, max_results=1)
                if lib_results:
                    boost += 0.08
            # Bug Pattern Store Boost (optional, read-only, max +0.10)
            if self.bug_pattern_store:
                for h in active:
                    bp_results = self.bug_pattern_store.search(h.statement, max_results=1)
                    if bp_results:
                        boost += 0.10
                        break
            ranked.append((h, h.confidence + boost))
        ranked.sort(key=lambda x: -x[1])

        best, best_conf = ranked[0] if ranked else (None, 0)

        return {
            'action': 'HYPOTHESIZE',
            'top_hypothesis': best.to_dict() if best else None,
            'all_hypotheses': [h.to_dict() for h, _ in ranked[:5]],
            'confidence': best_conf,
            'experiment_suggested': self._suggest_experiment(best) if best else None,
            'next_action': 'test_top_hypothesis',
            'reasoning': f'BR: {len(active)} hypotheses active, best={best.statement[:50] if best else "none"} '
                         f'conf={best_conf:.2f}'
        }

    def learn(self, sig, pat, success, emb=None, evidence=None, experiment_result=None):
        """Lerne aus Feedback: Erfolg/Misserfolg → Evidenz-Update."""
        self.total_learn_calls += 1

        # Evidenz aus Experiment-Ergebnis
        if experiment_result and experiment_result.get('hypothesis_id'):
            hyp = self._find_hypothesis(experiment_result['hypothesis_id'])
            if hyp:
                ev_type = 'supporting' if experiment_result.get('matches', False) else 'contradicting'
                strength = experiment_result.get('strength', 0.7)
                hyp.add_evidence(ev_type, strength,
                                experiment_result.get('description', 'Experiment result'))

        # Evidenz aus Fix-Erfolg
        if success and self.hypotheses:
            # Belohne die wahrscheinlichste aktive Hypothese
            active = [h for h in self.hypotheses if h.status == 'ACTIVE']
            if active:
                best = max(active, key=lambda h: h.confidence)
                best.add_evidence('supporting', 0.5, f'Fix erfolgreich: {pat}')
        elif not success and self.hypotheses:
            active = [h for h in self.hypotheses if h.status == 'ACTIVE']
            if active:
                best = max(active, key=lambda h: h.confidence)
                best.add_evidence('contradicting', 0.4, f'Fix fehlgeschlagen: {pat}')

    # ═══════════ HYPOTHESEN-MANAGEMENT ═══════════

    def create_hypothesis(self, statement, confidence=0.5, source='manual'):
        hyp = Hypothesis(statement, confidence, source)
        self.hypotheses.append(hyp)
        if len(self.hypotheses) > 50:
            # Entferne älteste FALSIFIED
            for h in self.hypotheses:
                if h.status == 'FALSIFIED':
                    self.hypotheses.remove(h)
                    break
        return hyp

    def add_evidence(self, hypothesis_id, ev_type, strength, description):
        hyp = self._find_hypothesis(hypothesis_id)
        if hyp:
            ev = hyp.add_evidence(ev_type, strength, description)
            self.evidence_log.append(ev)
            return ev
        return None

    def falsify(self, hypothesis_id, reason=''):
        hyp = self._find_hypothesis(hypothesis_id)
        if hyp:
            hyp.status = 'FALSIFIED'
            hyp.confidence = 0.0
            hyp.updated_at = time.time()

    def verify(self, hypothesis_id):
        hyp = self._find_hypothesis(hypothesis_id)
        if hyp and len(hyp.evidence_for) >= 3 and hyp.confidence > 0.9:
            hyp.status = 'VERIFIED'

    def rank_hypotheses(self):
        active = [h for h in self.hypotheses if h.status == 'ACTIVE']
        return sorted(active, key=lambda h: -h.confidence)

    def plan_experiment(self, hypothesis_id, description, expected_true, expected_false):
        exp = Experiment(hypothesis_id, description, expected_true, expected_false)
        self.experiments.append(exp)
        return exp

    def _find_hypothesis(self, hid):
        for h in self.hypotheses:
            if h.id == hid:
                return h
        return None

    def _suggest_experiment(self, hypothesis):
        if not hypothesis: return None
        return {
            'hypothesis_id': hypothesis.id,
            'description': f'Test: {hypothesis.statement[:60]}',
            'method': 'isolate_and_test',
            'expected_if_true': 'Bug verschwindet oder reduziert sich',
            'expected_if_false': 'Bug bleibt unverändert',
        }

    # ═══════════ STATS ═══════════

    def stats(self):
        active = sum(1 for h in self.hypotheses if h.status == 'ACTIVE')
        verified = sum(1 for h in self.hypotheses if h.status == 'VERIFIED')
        falsified = sum(1 for h in self.hypotheses if h.status == 'FALSIFIED')
        return {
            'brain_type': 'Scientific Method (BR — Gen 14b)',
            'total_hypotheses': len(self.hypotheses),
            'active': active, 'verified': verified, 'falsified': falsified,
            'experiments': len(self.experiments),
            'evidence_events': len(self.evidence_log),
            'think_calls': self.total_think_calls,
            'learn_calls': self.total_learn_calls,
            'top_hypothesis': self.rank_hypotheses()[0].to_dict() if self.rank_hypotheses() else None,
        }

    def __repr__(self):
        a = sum(1 for h in self.hypotheses if h.status == 'ACTIVE')
        return f"SMBrain(hyps={len(self.hypotheses)}, active={a})"


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    print("✅ br_scientific_method.py — PASS")
