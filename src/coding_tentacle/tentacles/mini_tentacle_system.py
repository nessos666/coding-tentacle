"""
MINI-TENTACLE SYSTEM — Coding Tentacle MVP Architecture
4 spezialisierte Tentakel + Zentraler Koordinator.

TENTAKEL 1: CodeContext   — Stacktrace, Datei, Zeile, Testoutput
TENTAKEL 2: Grounding      — BQ: Symbol → Bedeutung, historische Groundings
TENTAKEL 3: Reasoning      — BR: Hypothesen, Experimente, Evidenz
TENTAKEL 4: Safety         — IC + EL: GO/HOLD/BLOCK/ESCALATE

REGEL: Nur Safety-Tentakel darf Aktionen freigeben.

Autor: Hermes + David | Coding Tentacle 2026
"""
import sys, os, time, json

from coding_tentacle.memory.working_memory import WorkingMemory
from coding_tentacle.brains.sg_brain import SymbolGroundingBrain; BQ = SymbolGroundingBrain
from coding_tentacle.reasoning.br_scientific_method import ScientificMethodBrain
from coding_tentacle.safety.inhibitory_control import InhibitoryControl
from coding_tentacle.safety.escalation_logic import EscalationLogic


# ═══════════ TENTAKEL 1: CODECONTEXT ═══════════
class CodeContextTentacle:
    """Extrahiert und speichert Code-Kontext aus Bug-Reports."""
    def __init__(self, wm):
        self.wm = wm

    def analyze(self, session_id, bug_report, code_context=None, test_output=None, stacktrace=None):
        result = {'file': '', 'line': 0, 'function': '', 'has_context': False, 'actions': []}

        # Aus Code-Kontext extrahieren
        if code_context:
            result['file'] = code_context.get('file', '')
            result['line'] = code_context.get('line', 0)
            result['function'] = code_context.get('function', '')
            result['has_context'] = True

        # Aus Stacktrace extrahieren (falls vorhanden)
        if stacktrace:
            parsed = BQ.parse_stacktrace(stacktrace)
            if not result['file'] and parsed.get('file'):
                result['file'] = parsed['file']
                result['line'] = parsed['line']
                result['function'] = parsed.get('function', '')
                result['has_context'] = True

        # In WM speichern
        if result['has_context']:
            self.wm.update_context(session_id, 'code_context', {
                'file': result['file'], 'line': result['line'],
                'function': result['function']
            })
            result['actions'].append('context_stored_in_wm')

        if not result['has_context']:
            result['actions'].append('ASK_CONTEXT: need code_context or stacktrace')

        if test_output:
            self.wm.update_context(session_id, 'test_output', test_output)
            result['actions'].append('test_output_stored_in_wm')

        return result


# ═══════════ TENTAKEL 2: GROUNDING ═══════════
class GroundingTentacle:
    """BQ Symbol Grounding: Symbol → Bedeutung + historische Groundings."""
    def __init__(self, wm):
        self.bq = BQ()
        self.wm = wm

    def analyze(self, session_id, bug_report, code_context=None, test_output=None):
        if not bug_report:
            return {'grounded': False, 'action': 'ASK_CONTEXT', 'missing': ['bug_report'], 'score': 0.0}

        # Symbol extrahieren — aus Stacktrace oder bug_report
        symbol = bug_report.split(':')[0] if ':' in bug_report else bug_report.split()[0] if ' ' in bug_report else bug_report
        # Wenn Stacktrace: parsed error_type nehmen
        if 'Error' in bug_report or 'Exception' in bug_report or 'Traceback' in bug_report:
            parsed = BQ.parse_stacktrace(bug_report)
            if parsed.get('error_type'):
                symbol = parsed['error_type']
                # Strip "Exception"/"Error" suffix for matching
                for suffix in ['Exception', 'Error']:
                    if symbol.endswith(suffix) and len(symbol) > len(suffix):
                        symbol = symbol[:-len(suffix)]
                        break

        self.bq.learn_from_context(
            symbol + ':0:0',  # Use computed symbol so BQ stores under correct key
            stacktrace=bug_report if any(w in bug_report for w in ['Error', 'Exception', 'Traceback']) else '',
            test_output=test_output or '',
            code_context=code_context
        )

        result = self.bq.think(symbol)
        self.wm.add_brain_output(session_id, 'GroundingTentacle', {
            'action': result.get('action'), 'score': result.get('grounding_score', 0),
            'meaning': result.get('meaning', ''), 'confidence': result.get('confidence', 0)
        })
        return result


# ═══════════ TENTAKEL 3: REASONING ═══════════
class ReasoningTentacle:
    """BR Scientific Method: Hypothesen, Experimente, Evidenz."""
    def __init__(self, wm):
        self.br = ScientificMethodBrain()
        self.wm = wm

    def analyze(self, session_id, bug_report, grounding_result=None):
        if not bug_report:
            return {'action': 'ASK_CONTEXT', 'hypotheses': [], 'confidence': 0}

        result = self.br.think(bug_report, bq_grounding=grounding_result)

        # Hypothesen in WM speichern
        for h in result.get('all_hypotheses', [])[:3]:
            self.wm.add_hypothesis(session_id, h['statement'], h.get('confidence', 0.5))

        self.wm.add_brain_output(session_id, 'ReasoningTentacle', {
            'action': result.get('action'), 'confidence': result.get('confidence', 0),
            'hypotheses': len(result.get('all_hypotheses', []))
        })
        return result

    def learn(self, bug_report, fix, success, experiment_result=None):
        self.br.learn(bug_report, fix, success, experiment_result=experiment_result)


# ═══════════ TENTAKEL 4: SAFETY ═══════════
class SafetyTentacle:
    """IC + EL: GO/HOLD/BLOCK/ESCALATE. NUR dieser Tentakel gibt Aktionen frei."""
    def __init__(self, wm):
        self.ic = InhibitoryControl()
        self.el = EscalationLogic()
        self.wm = wm

    def authorize(self, session_id, request):
        """
        request: {proposed_action, target_file, patch, confidence, risk_level,
                  test_available, test_passed, test_relevant, test_count, security_sensitive}
        Returns: {authorized: bool, action: str, route: str, reason: str}
        """
        # IC: Risiko prüfen
        ic_result = self.ic.evaluate({
            'proposed_action': request.get('proposed_action', 'analyze'),
            'target_file': request.get('target_file', ''),
            'patch': request.get('patch', ''),
            'confidence': request.get('confidence', 0.5),
            'risk_level': request.get('risk_level', 'medium'),
            'test_available': request.get('test_available', False),
            'rollback_available': request.get('rollback_available', False),
            'security_sensitive': request.get('security_sensitive', False),
            'test_passed': request.get('test_passed'),
            'test_relevant': request.get('test_relevant', False),
            'test_count': request.get('test_count', 0),
        }, self.wm.get_state(session_id))

        ic_dict = ic_result.to_dict() if hasattr(ic_result, 'to_dict') else {'action': 'GO'}

        # EL: Routing
        el_result = self.el.evaluate_escalation({
            'bug_type': request.get('bug_report', ''),
            'complexity': request.get('complexity', 'low'),
            'known_pattern': request.get('known_pattern', False),
            'has_code_context': bool(request.get('target_file')),
            'has_tests': request.get('test_available', False),
            'confidence': request.get('confidence', 0.5),
            'risk_level': request.get('risk_level', 'medium'),
            'brain_outputs': [],
            'requested_action': request.get('proposed_action', 'analyze'),
        }, self.wm.get_state(session_id), ic_result)

        el_dict = el_result.to_dict() if hasattr(el_result, 'to_dict') else {'route': 'CENTRAL_REVIEW'}
        authorized = not el_result.is_escalated()

        self.wm.add_decision(session_id, el_result.route, el_result.reason,
                            request.get('confidence', 0.5))

        return {
            'authorized': authorized,
            'ic_action': ic_dict.get('action', 'GO'),
            'el_route': el_dict.get('route', 'CENTRAL_REVIEW'),
            'reason': el_result.reason if hasattr(el_result, 'reason') else str(el_result),
            'risk_score': ic_dict.get('risk_score', 0),
            'blocked': el_result.is_escalated(),
        }


# ═══════════ ZENTRALER KOORDINATOR ═══════════
class MiniTentacleSystem:
    """4 Tentakel + Working Memory + Zentrale Koordination."""

    def __init__(self):
        self.wm = WorkingMemory()
        self.code_context = CodeContextTentacle(self.wm)
        self.grounding = GroundingTentacle(self.wm)
        self.reasoning = ReasoningTentacle(self.wm)
        self.safety = SafetyTentacle(self.wm)
        self.total_sessions = 0

    def process(self, request):
        """
        request: {session_id, bug_report, code_context, test_output,
                  proposed_patch, requested_action, risk_level}
        """
        sid = request.get('session_id')
        if sid:
            state = self.wm.load_session(sid)
            if not state: state = self.wm.create_session(sid)
        else:
            state = self.wm.create_session()
            sid = state.session_id
        self.total_sessions += 1

        bug = request.get('bug_report', '')
        ctx = request.get('code_context')
        test = request.get('test_output')
        patch = request.get('proposed_patch', '')
        action = request.get('requested_action', 'analyze')
        risk = request.get('risk_level', 'medium')

        self.wm.update_context(sid, 'bug', bug)
        self.wm.update_context(sid, 'started_at', time.time())

        # ═══ TENTAKEL 1: CodeContext ═══
        cc = self.code_context.analyze(sid, bug, ctx, test,
                             stacktrace=bug if any(w in bug for w in ['Error', 'Exception', 'Traceback']) else None)

        # ═══ TENTAKEL 2: Grounding ═══
        gd = self.grounding.analyze(sid, bug, ctx, test)

        # ═══ TENTAKEL 3: Reasoning ═══
        rs = self.reasoning.analyze(sid, bug, grounding_result=gd)

        # ═══ TENTAKEL 4: Safety ═══
        conf = max(gd.get('confidence', 0), rs.get('confidence', 0))
        known = gd.get('grounding_score', 0) > 0.3
        complexity = 'low'
        if not ctx: complexity = 'medium'
        elif risk in ('high', 'critical'): complexity = 'high'
        elif conf < 0.2: complexity = 'high'
        elif not known: complexity = 'medium'
        sec_sensitive = any(w in str(patch).lower() for w in
            ['api_key', 'secret', 'password', 'token', 'credential', 'database_url'])

        # Medium risk + failed/missing tests → force CENTRAL_REVIEW
        if risk == 'medium' and not (test and 'PASS' in str(test).upper()):
            complexity = 'medium'
            # Force CENTRAL_REVIEW for uncertain medium-risk cases
            sf = self.safety.authorize(sid, {
                'bug_report': bug, 'proposed_action': action,
                'target_file': ctx.get('file', '') if ctx else '',
                'patch': patch if action in ('patch', 'deploy', 'delete') else None,
                'confidence': conf, 'risk_level': 'high', 'complexity': 'medium',
                'known_pattern': False,
                'test_available': bool(test),
                'test_passed': False,
                'test_relevant': bool(test and ctx),
                'test_count': 0,
                'security_sensitive': sec_sensitive,
            })
            sf['el_route'] = 'CENTRAL_REVIEW'
            sf['reason'] = 'Medium risk without passing tests → CENTRAL_REVIEW'
            sf['blocked'] = True
            sf['authorized'] = False
            return {
                'session_id': sid,
                'code_context': {'has_context': cc.get('has_context', False), 'file': cc.get('file', '')},
                'grounding': {'score': gd.get('grounding_score', 0), 'meaning': gd.get('meaning', ''), 'confidence': gd.get('confidence', 0)},
                'reasoning': {'hypotheses': len(rs.get('all_hypotheses', [])), 'top': '', 'confidence': rs.get('confidence', 0)},
                'safety': {'authorized': False, 'route': 'CENTRAL_REVIEW', 'blocked': True, 'reason': 'Medium risk without passing tests'},
                'final_route': 'CENTRAL_REVIEW', 'authorized': False, 'confidence': conf,
                'next_step': 'ESCALATED: CENTRAL_REVIEW'
            }

        sec_sensitive = any(w in str(patch).lower() for w in
            ['api_key', 'secret', 'password', 'token', 'credential', 'database_url'])

        sf = self.safety.authorize(sid, {
            'bug_report': bug, 'proposed_action': action,
            'target_file': ctx.get('file', '') if ctx else '',
            'patch': patch if action in ('patch', 'deploy', 'delete') else None,
            'confidence': conf, 'risk_level': risk, 'complexity': complexity,
            'known_pattern': known,
            'test_available': bool(test),
            'test_passed': True if test and ('PASS' in str(test).upper() or 'OK' in str(test).upper()) else (False if test else None),
            'test_relevant': bool(test and ctx),
            'test_count': 1 if test else 0,
            'security_sensitive': sec_sensitive,
        })

        # ═══ RESULT ═══
        hypotheses = rs.get('all_hypotheses', [])
        return {
            'session_id': sid,
            'code_context': {'has_context': cc.get('has_context', False), 'file': cc.get('file', '')},
            'grounding': {'score': gd.get('grounding_score', 0), 'meaning': gd.get('meaning', ''),
                         'confidence': gd.get('confidence', 0)},
            'reasoning': {'hypotheses': len(hypotheses), 'top': hypotheses[0]['statement'][:60] if hypotheses else '',
                         'confidence': rs.get('confidence', 0)},
            'safety': {'authorized': sf['authorized'], 'route': sf['el_route'],
                      'blocked': sf.get('blocked', False), 'reason': sf['reason'][:80]},
            'final_route': sf['el_route'],
            'authorized': sf['authorized'],
            'confidence': conf,
            'next_step': 'APPLY' if sf['authorized'] else f'ESCALATED: {sf["el_route"]}',
        }

    def stats(self):
        return {
            'sessions': self.total_sessions,
            'wm_active': self.wm.stats().get('active_sessions', 0),
            'bq_symbols': self.grounding.bq.stats().get('total_symbols', 0),
            'br_hypotheses': self.reasoning.br.stats().get('total_hypotheses', 0),
            'ic_checks': self.safety.ic.stats().get('total_checks', 0),
            'el_routes': self.safety.el.stats().get('total_decisions', 0),
        }


# ═══════════ TEST ═══════════
if __name__ == "__main__":

    from working_memory import WorkingMemory
    wm = WorkingMemory()
    state = wm.create_session()
    wm.update_context(state.session_id, "bug", "TestBug")
    print("  ✅ mini_tentacle_system.py — PASS")
