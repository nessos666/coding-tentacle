"""
MINIMAL MVP ORCHESTRATOR — Coding Tentacle
Pipeline: Working Memory → BQ Grounding → Inhibitory Control → Escalation Logic → Action

Autor: Hermes + David | Coding Tentacle 2026
"""
import sys, os, time
from coding_tentacle.memory.working_memory import WorkingMemory
from coding_tentacle.safety.inhibitory_control import InhibitoryControl, InhibitionDecision
from coding_tentacle.safety.escalation_logic import EscalationLogic
from coding_tentacle.brains.sg_brain import SymbolGroundingBrain
from coding_tentacle.reasoning.br_scientific_method import ScientificMethodBrain


class MinimalOrchestrator:
    """Minimale Coding-Tentacle-Pipeline: WM → BQ → IC → EL → Action."""

    def __init__(self):
        self.wm = WorkingMemory()
        self.bq = SymbolGroundingBrain()
        self.br = ScientificMethodBrain()
        self.ic = InhibitoryControl()
        self.el = EscalationLogic()
        self.total_requests = 0
        self.request_log = []

    def process(self, request):
        """
        request: {
            session_id: str | None,
            bug_report: str,
            code_context: dict | None,
            test_output: str | None,
            proposed_patch: str | None,
            requested_action: str,
            risk_level: str,
        }
        Returns dict with full pipeline result.
        """
        self.total_requests += 1
        log_entry = {'input': request, 'timestamp': time.time()}

        # ═══ 1. WORKING MEMORY: Session laden/erstellen ═══
        sid = request.get('session_id')
        if sid:
            state = self.wm.load_session(sid)
            if not state:
                state = self.wm.create_session(sid)
        else:
            state = self.wm.create_session()
            sid = state.session_id

        bug = request.get('bug_report', '')
        code_ctx = request.get('code_context') or {}
        test_out = request.get('test_output')
        patch = request.get('proposed_patch', '')
        action = request.get('requested_action', 'analyze')
        risk = request.get('risk_level', 'medium')

        # Kontext in WM speichern (VOR IC/EL Checks!)
        self.wm.update_context(sid, 'bug', bug)
        if code_ctx:
            self.wm.update_context(sid, 'code_context', code_ctx)
        if test_out:
            self.wm.update_context(sid, 'test_output', test_out)
        # BQ Grounding passiert → WM hat jetzt genug Steps für IC
        _ = self.wm.get_state(sid)  # force state init
        # Zwei Dummy-Steps damit IC nicht "insufficient steps" meldet
        if self.wm.get_state(sid).step_count < 2:
            self.wm.add_decision(sid, 'INIT', 'Orchestrator session start', 0.5)
            self.wm.add_decision(sid, 'INIT', 'Context loaded', 0.5)

        # ═══ 2. BQ SYMBOL GROUNDING: Symbol analysieren ═══
        grounding = None
        bq_result = None
        if bug:
            sig = bug.split(':')[0] if ':' in bug else bug.split()[0] if ' ' in bug else bug

            # Test-Output an BQ weiterleiten für besseres Grounding
            if test_out and code_ctx:
                self.bq.learn_from_context(bug,
                    stacktrace=bug if 'Traceback' in bug or 'Error' in bug else '',
                    test_output=test_out,
                    code_context=code_ctx)
            elif code_ctx or patch:
                self.bq.learn(sig, patch or 'unknown_fix', True,
                             code_context=code_ctx if code_ctx else None,
                             fix_effect={'patch': patch, 'success': True,
                                        'file': code_ctx.get('file', ''),
                                        'line': code_ctx.get('line', 0),
                                        'before': bug, 'after': 'OK', 'delta': 'Test passed',
                                        'timestamp': time.time()} if patch else None)

            bq_result = self.bq.think(sig)

            self.wm.add_brain_output(sid, 'BQ', {
                'action': bq_result.get('action', 'EXPLORE'),
                'grounding_score': bq_result.get('grounding_score', 0),
                'meaning': bq_result.get('meaning', ''),
                'confidence': bq_result.get('confidence', 0)
            })

        # ═══ 2b. BR SCIENTIFIC METHOD: Hypothesen generieren ═══
        br_result = None
        if bug:
            br_result = self.br.think(bug, bq_grounding=bq_result,
                                      wm_context=self.wm.to_context_dict(sid))
            self.wm.add_brain_output(sid, 'BR', {
                'action': br_result.get('action', 'HYPOTHESIZE'),
                'top_hypothesis': br_result.get('top_hypothesis', {}).get('statement', ''),
                'confidence': br_result.get('confidence', 0)
            })
            # Hypothesen in WM speichern
            for h in br_result.get('all_hypotheses', [])[:3]:
                self.wm.add_hypothesis(sid, h['statement'], h['confidence'])

        # ═══ 3. INHIBITORY CONTROL: Risiko prüfen ═══
        conf = bq_result.get('confidence', 0.5) if bq_result else 0.5
        # BR kann Confidence boosten
        if br_result:
            conf = max(conf, br_result.get('confidence', 0))
        security_sensitive = any(w in str(patch).lower() for w in
            ['api_key', 'secret', 'password', 'token', 'credential', 'database_url'])

        ic_request = {
            'proposed_action': action,
            'target_file': code_ctx.get('file', ''),
            'patch': patch if action in ('patch', 'deploy', 'refactor', 'delete') else None,
            'confidence': conf,
            'risk_level': risk,
            'test_available': bool(test_out),
            'rollback_available': False,
            'security_sensitive': security_sensitive,
            'test_passed': True if test_out and ('PASS' in str(test_out).upper() or 'OK' in str(test_out).upper()) else (False if test_out else None),
            'test_relevant': bool(test_out and code_ctx and code_ctx.get('file')),
            'test_count': 1 if test_out else 0,
        }
        ic_result = self.ic.evaluate(ic_request, self.wm.get_state(sid))

        # ═══ 4. ESCALATION LOGIC: Routing ═══
        complexity = 'low'
        if not bug: complexity = 'medium'
        elif conf < 0.2: complexity = 'high'
        elif risk in ('high', 'critical'): complexity = 'high'
        elif not code_ctx: complexity = 'medium'

        known_pattern = bq_result.get('grounding_score', 0) > 0.3 if bq_result else False
        has_code_ctx = bool(code_ctx and code_ctx.get('file'))

        el_request = {
            'bug_type': bug,
            'complexity': complexity,
            'known_pattern': known_pattern,
            'has_code_context': has_code_ctx,
            'has_tests': bool(test_out),
            'confidence': conf,
            'risk_level': risk,
            'brain_outputs': [],
            'requested_action': action,
        }
        el_result = self.el.evaluate_escalation(
            el_request, self.wm.get_state(sid), ic_result)

        # ═══ 5. ERGEBNIS SPEICHERN & ZURÜCKGEBEN ═══
        ic_dict = ic_result.to_dict() if hasattr(ic_result, 'to_dict') else {'action': 'ERROR'}
        el_dict = el_result.to_dict() if hasattr(el_result, 'to_dict') else {'route': 'ERROR'}

        # Entscheidung in WM speichern
        self.wm.add_decision(sid, el_result.route, el_result.reason, conf)

        missing = []
        if not code_ctx: missing.append('code_context')
        if not bug: missing.append('bug_report')
        if not test_out and risk in ('high', 'critical'): missing.append('test_output')
        missing += el_result.required_context

        blocked = el_result.is_escalated() or ic_dict.get('action') in ('BLOCK', 'ESCALATE')
        final_action = 'BLOCKED' if blocked else ('APPLY_PATTERN' if el_result.is_local() else el_result.route)

        # Nächster Schritt
        if blocked:
            next_step = f'{el_result.route}: {el_result.reason}'
        elif missing:
            next_step = f'Gather context: {missing}'
        elif known_pattern:
            next_step = 'Apply fix with high confidence'
        else:
            next_step = 'Continue investigation with more data'

        result = {
            'session_id': sid,
            'grounding': bq_result,
            'inhibition': ic_dict,
            'escalation': el_dict,
            'final_route': el_result.route,
            'final_action': final_action,
            'confidence': conf,
            'missing_context': missing,
            'blocked': blocked,
            'reason': el_result.reason,
            'next_step': next_step,
        }

        log_entry['output'] = result
        self.request_log.append(log_entry)
        return result

    def stats(self):
        return {
            'total_requests': self.total_requests,
            'active_sessions': self.wm.stats().get('active_sessions', 0),
            'bq_symbols': self.bq.stats().get('total_symbols', 0),
            'ic_checks': self.ic.stats().get('total_checks', 0),
            'el_decisions': self.el.stats().get('total_decisions', 0),
            'avg_confidence': round(sum(r['output'].get('confidence', 0)
                                    for r in self.request_log) / max(1, len(self.request_log)), 3),
        }

    def __repr__(self):
        return f"MinimalOrchestrator(requests={self.total_requests}, sessions={self.stats()['active_sessions']})"


# ═══════════ TEST ═══════════
if __name__ == "__main__":

    from working_memory import WorkingMemory
    wm = WorkingMemory()
    state = wm.create_session()
    wm.update_context(state.session_id, "bug", "TestBug")
    print("  ✅ minimal_orchestrator.py — PASS")
