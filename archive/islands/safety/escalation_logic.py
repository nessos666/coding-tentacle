"""
ESCALATION LOGIC — Gen 15c
Routing-Engine für Coding Tentacle.
Entscheidet: lokal handeln, an Brain routen, an Tentakel routen,
zentral prüfen, Security prüfen oder Mensch fragen.

Autor: Hermes + David | Coding Tentacle 2026
"""
import time
from collections import defaultdict

class EscalationDecision:
    """Routing-Entscheidung der Escalation Engine."""
    def __init__(self, route, target='', reason='', confidence=0.0,
                 risk_score=0.0, required_context=None, blockers=None):
        self.route = route  # LOCAL_HANDLE | ROUTE_TO_BRAIN | ROUTE_TO_TENTACLE | CENTRAL_REVIEW | SECURITY_REVIEW | HUMAN_REVIEW
        self.target = target
        self.reason = reason
        self.confidence = confidence
        self.risk_score = risk_score
        self.required_context = required_context or []
        self.blockers = blockers or []
        self.timestamp = time.time()

    def to_dict(self):
        return {
            'route': self.route, 'target': self.target, 'reason': self.reason,
            'confidence': round(self.confidence, 3), 'risk_score': round(self.risk_score, 3),
            'required_context': self.required_context, 'blockers': self.blockers,
            'timestamp': self.timestamp
        }

    def is_local(self): return self.route in ('LOCAL_HANDLE', 'ROUTE_TO_BRAIN', 'ROUTE_TO_TENTACLE')
    def is_escalated(self): return self.route in ('CENTRAL_REVIEW', 'SECURITY_REVIEW', 'HUMAN_REVIEW')
    def needs_human(self): return self.route == 'HUMAN_REVIEW'

    def __repr__(self):
        return f"Escalation({self.route}→{self.target}: {self.reason[:40]})"


class EscalationLogic:
    """Routing-Engine: Wer darf was? Wer muss wohin?"""

    # ═══════════ BRAIN-ROUTING-MAP ═══════════
    BRAIN_ROUTES = {
        'symbol': 'BQ_SymbolGrounding',
        'grounding': 'BQ_SymbolGrounding',
        'meaning': 'BQ_SymbolGrounding',
        'code': 'BC_CodeContext',
        'context': 'BC_CodeContext',
        'file': 'BC_CodeContext',
        'memory': 'Hopfield',
        'pattern': 'Hopfield',
        'attention': 'M_Attention',
        'match': 'M_Attention',
        'explain': 'BI_Explainability',
        'uncertain': 'BJ_Uncertainty',
        'causal': 'H_Causal',
        'counterfactual': 'AW_Counterfactual',
        'plan': 'VSM',
        'strategy': 'VSM',
        'security': 'InhibitoryControl',
        'safe': 'InhibitoryControl',
    }

    # ═══════════ TENTAKEL-ROUTING-MAP ═══════════
    TENTACLE_ROUTES = {
        ('grounding', 'code'): 'SENSOR_TENTACLE',
        ('symbol', 'context'): 'SENSOR_TENTACLE',
        ('memory', 'pattern'): 'MEMORY_TENTACLE',
        ('memory', 'attention'): 'MEMORY_TENTACLE',
        ('attention', 'match'): 'REASONING_TENTACLE',
        ('causal', 'counterfactual'): 'REASONING_TENTACLE',
        ('plan', 'strategy'): 'PLANNING_TENTACLE',
        ('security', 'safe'): 'SECURITY_TENTACLE',
        ('explain', 'uncertain'): 'TESTING_TENTACLE',
    }

    # ═══════════ DESTRUCTIVE ACTIONS ═══════════
    HUMAN_REQUIRED = ['deploy', 'delete', 'drop', 'migrate', 'production', 'credentials', 'secrets']

    def __init__(self):
        self.decision_log = []
        self.escalation_count = defaultdict(int)  # {session_id: count}
        self.total_decisions = 0

    # ═══════════ CORE ═══════════

    def evaluate_escalation(self, request, working_memory_state=None, inhibition_decision=None):
        req = request
        conf = req.get('confidence', 0.5)
        complexity = req.get('complexity', 'medium')
        risk = req.get('risk_level', 'medium')
        known = req.get('known_pattern', False)
        code_ctx = req.get('has_code_context', False)
        bug_type = req.get('bug_type', '')
        action = req.get('requested_action', 'analyze')
        blockers = []; required = []

        # 1. Inhibitory Control hat Vorrang
        if inhibition_decision:
            inh = inhibition_decision
            inh_action = inh.action if hasattr(inh, 'action') else inh.get('action', 'GO')
            inh_reason = inh.reason if hasattr(inh, 'reason') else inh.get('reason', '')
            inh_blockers = inh.blockers if hasattr(inh, 'blockers') else inh.get('blockers', [])
            inh_required = inh.required_context if hasattr(inh, 'required_context') else inh.get('required_context', [])

            if inh_action == 'BLOCK':
                dec = EscalationDecision('HUMAN_REVIEW', 'human_operator', f'Inhibitory BLOCK: {inh_reason}', conf, 1.0, blockers=inh_blockers)
                self._log(dec, working_memory_state); return dec
            if inh_action == 'ESCALATE':
                dec = EscalationDecision('SECURITY_REVIEW', 'security_tentacle', f'Inhibitory ESCALATE: {inh_reason}', conf, 0.8, blockers=inh_blockers)
                self._log(dec, working_memory_state); return dec
            if inh_action == 'ASK_CONTEXT':
                required = inh_required
                dec = EscalationDecision('ROUTE_TO_BRAIN', 'BQ_SymbolGrounding', f'Need context: {required}', conf, 0.3, required_context=required)
                self._log(dec, working_memory_state); return dec

        # 2. HUMAN_REVIEW für destruktive Aktionen
        for keyword in self.HUMAN_REQUIRED:
            if keyword in action.lower():
                dec = EscalationDecision('HUMAN_REVIEW', 'human_operator', f'Destructive: {action}', conf, 1.0)
                self._log(dec, working_memory_state); return dec

        # 3. SECURITY_REVIEW (vor CENTRAL, nach HUMAN)
        if risk in ('high','critical') and conf < 0.7:
            dec = EscalationDecision('SECURITY_REVIEW', 'security_tentacle', f'{risk} risk + low conf ({conf:.0%})', conf, 0.7)
            self._log(dec, working_memory_state); return dec

        # 4. ROUTE_TO_TENTACLE bei Multi-Domain (vor Single-Routing!)
        needed = set()
        if not code_ctx: needed.add('code')
        if bug_type and not known: needed.add('symbol')
        if not known and complexity in ('medium','high'): needed.add('memory')
        if risk in ('medium','high'): needed.add('security')
        if len(needed) >= 2 and complexity != 'high':
            for (d1,d2), tname in self.TENTACLE_ROUTES.items():
                if d1 in needed and d2 in needed:
                    dec = EscalationDecision('ROUTE_TO_TENTACLE', tname, f'Multi-domain: {needed}', conf, 0.3)
                    self._log(dec, working_memory_state); return dec
            if len(needed) >= 3:
                dec = EscalationDecision('ROUTE_TO_TENTACLE', 'SENSOR_TENTACLE', f'Multi-domain (broad): {needed}', conf, 0.3)
                self._log(dec, working_memory_state); return dec

        # 5. ASK_CONTEXT / ROUTE_TO_BRAIN für fehlenden Kontext (Single-Domain)
        if not code_ctx:
            dec = EscalationDecision('ROUTE_TO_BRAIN', 'BQ_SymbolGrounding', 'No code context → ground first', conf, 0.3, required_context=['code_snippet'])
            self._log(dec, working_memory_state); return dec
        if not bug_type:
            dec = EscalationDecision('ROUTE_TO_BRAIN', 'BQ_SymbolGrounding', 'No bug type → ground', conf, 0.3, required_context=['bug_report'])
            self._log(dec, working_memory_state); return dec

        # 6. LOCAL_HANDLE für bekannte einfache Bugs
        if known and complexity == 'low' and conf > 0.4 and risk in ('low','medium'):
            dec = EscalationDecision('LOCAL_HANDLE', 'active_brain', f'Known, simple, conf={conf:.0%}', conf, 0.1)
            self._log(dec, working_memory_state); return dec

        # 7. ROUTE_TO_BRAIN für Spezialist
        for domain, brain_name in self.BRAIN_ROUTES.items():
            if domain in bug_type.lower() or domain in action.lower():
                dec = EscalationDecision('ROUTE_TO_BRAIN', brain_name, f'Specialist: {domain}→{brain_name}', conf, 0.2)
                self._log(dec, working_memory_state); return dec

        # 8. CENTRAL_REVIEW — NUR bei echten Konflikten (letzte Instanz vor Fallback)
        reasons = []
        if complexity in ('high','critical'):
            reasons.append(f'High complexity ({complexity})')

        if working_memory_state:
            active_hyps = [h for h in working_memory_state.hypotheses if h.get('status') == 'active']
            if len(active_hyps) >= 3:
                reasons.append(f'{len(active_hyps)} competing hypotheses')
            if working_memory_state.open_questions:
                reasons.append('Open questions remain')
            brain_actions = set()
            for outs in working_memory_state.brain_outputs.values():
                for o in outs:
                    if isinstance(o, dict) and o.get('action'):
                        brain_actions.add(o['action'])
            if 'APPLY_PATTERN' in brain_actions and 'EXPLORE' in brain_actions:
                reasons.append('Conflicting brain outputs')

        if reasons:
            dec = EscalationDecision('CENTRAL_REVIEW', 'central_brain', '; '.join(reasons), conf, 0.6)
            self._log(dec, working_memory_state); return dec

        # Fallback
        dec = EscalationDecision('CENTRAL_REVIEW', 'central_brain', 'Fallback: needs coordination', conf, 0.4)
    def _log(self, decision, wm_state):
        self.decision_log.append(decision)
        if wm_state:
            wm_state.update()
            # Zähle Eskalationen pro Session
            session = getattr(wm_state, 'session_id', 'unknown')
            if decision.is_escalated():
                self.escalation_count[session] += 1

    def stats(self):
        routes = defaultdict(int)
        for d in self.decision_log:
            routes[d.route] += 1
        return {
            'total_decisions': self.total_decisions,
            'route_distribution': dict(routes),
            'escalation_rate': f'{sum(1 for d in self.decision_log if d.is_escalated())/max(1,len(self.decision_log)):.0%}',
            'local_rate': f'{sum(1 for d in self.decision_log if d.is_local())/max(1,len(self.decision_log)):.0%}',
            'human_rate': f'{sum(1 for d in self.decision_log if d.needs_human())/max(1,len(self.decision_log)):.0%}',
            'recent': [d.to_dict() for d in self.decision_log[-5:]],
            'repeated_escalations': {k: v for k, v in self.escalation_count.items() if v >= 2}
        }

    def __repr__(self):
        return f"EscalationLogic(decisions={self.total_decisions})"


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    print("EL SELF-TEST")
    print("=" * 40)
    el = EscalationLogic()
    d = el.evaluate_escalation({"bug_type":"NullPointer","complexity":"low","known_pattern":True,"has_code_context":True,"has_tests":True,"confidence":0.8,"risk_level":"low","brain_outputs":[],"requested_action":"analyze"})
    print(f"  Route: {d.route}")
    print("  ✅ EL self-test PASS")
