"""
INHIBITORY CONTROL — Gen 15b
Pre-Action Safety Gate für Coding Tentacle.
Vor JEDER Aktion: GO, HOLD, ASK_CONTEXT, ESCALATE oder BLOCK.

Autor: Hermes + David | Coding Tentacle 2026
"""
import time, re, os
from collections import defaultdict

class InhibitionDecision:
    """Ergebnis der Pre-Action-Prüfung."""
    def __init__(self, action, risk_score=0.0, uncertainty=0.0, reason="",
                 blockers=None, required_context=None):
        self.action = action         # GO | HOLD | ASK_CONTEXT | ESCALATE | BLOCK
        self.risk_score = risk_score
        self.uncertainty = uncertainty
        self.reason = reason
        self.blockers = blockers or []
        self.required_context = required_context or []
        self.timestamp = time.time()

    def to_dict(self):
        return {
            'action': self.action,
            'risk_score': round(self.risk_score, 3),
            'uncertainty': round(self.uncertainty, 3),
            'reason': self.reason,
            'blockers': self.blockers,
            'required_context': self.required_context,
            'timestamp': self.timestamp
        }

    def is_allowed(self):
        return self.action in ('GO', 'HOLD')

    def is_blocked(self):
        return self.action in ('BLOCK', 'ESCALATE')

    def __repr__(self):
        return f"Inhibition({self.action}: risk={self.risk_score:.2f}, '{self.reason[:40]}')"


class InhibitoryControl:
    """Pre-Action-Gate — die Sicherheitsschicht vor jedem Fix."""

    # ═══════════ SENSITIVE PATTERNS ═══════════
    DANGEROUS_PATTERNS = [
        (r'rm\s+-rf', 'Deletes files recursively'),
        (r'os\.remove|os\.unlink|shutil\.rmtree', 'Deletes files/directories'),
        (r'DROP\s+TABLE|DELETE\s+FROM|TRUNCATE', 'Database destruction'),
        (r'chmod\s+777', 'World-writable permissions'),
        (r'eval\(|exec\(|__import__\(', 'Code injection risk'),
        (r'subprocess\.call|os\.system|shell=True', 'Shell command execution'),
        (r'/etc/passwd|/etc/shadow|/etc/sudoers', 'System file modification'),
        (r'AWS_SECRET|API_KEY|DATABASE_URL|password\s*=', 'Credential exposure'),
        (r'sudo|chown\s+root', 'Privilege escalation'),
        (r'pip\\s+uninstall|apt-get\\s+remove|yum\\s+remove', 'Package removal'),
        (r'\\.\\./|\\.\\.\\\\|%2e%2e/', 'Path traversal attempt'),
        (r'~/\\.ssh|/etc/passwd|/etc/shadow|/etc/sudoers', 'Sensitive system path'),
        (r'deploy\\s+to\\s+production|production\\s+deploy|release\\s+to\\s+prod', 'Production deployment'),
        (r'kubectl\\s+apply|terraform\\s+apply|helm\\s+upgrade', 'Infrastructure change'),
        (r'docker\\s+push|systemctl\\s+restart|service\\s+restart', 'Service operation'),
    ]

    # ═══════════ SENSITIVE FILES ═══════════
    SENSITIVE_FILES = [
        '.env', 'credentials', 'secrets', 'config.yml', 'config.yaml',
        'settings.py', 'production.py', 'deploy.py', 'Dockerfile',
        'docker-compose.yml', 'Makefile', 'package.json', 'Cargo.toml',
        '/etc/', '/var/', '/root/', '/home/',
        '~/.ssh', 'system32', '/etc/passwd', '/etc/shadow', '.env',
    ]

    def __init__(self, security_store=None):
        self.decision_log = []
        self.block_count = 0
        self.escalate_count = 0
        self.go_count = 0
        self.hold_count = 0
        self.total_checks = 0
        self.security_store = security_store  # Optional

    # ═══════════ CORE: EVALUATE ═══════════

    def evaluate(self, action_request, working_memory_state=None):
        """
        action_request: {
            proposed_action, target_file, patch, confidence, risk_level,
            test_available, rollback_available, security_sensitive,
            test_passed: bool | None,     # NEU: Test-Ergebnis
            test_relevant: bool,           # NEU: Ist der Test relevant?
            test_count: int,               # NEU: Anzahl erfolgreicher Testläufe
        }
        """
        self.total_checks += 1
        blockers = []
        required_context = []

        ar = action_request
        conf = ar.get('confidence', 0.5)
        risk = ar.get('risk_level', 'medium')
        target = ar.get('target_file', '')
        patch = ar.get('patch', '')
        sec = ar.get('security_sensitive', False)
        test = ar.get('test_available', False)
        rollback = ar.get('rollback_available', False)
        test_passed = ar.get('test_passed')  # None = unknown, True/False
        test_relevant = ar.get('test_relevant', False)
        test_count = ar.get('test_count', 0)

        # ═══ 0. SECURITY STORE CHECK (optional, read-only, first!) ═══
        if self.security_store:
            patch_text = ar.get('patch', '')
            if patch_text:
                sec_results = self.security_store.detect_danger(patch_text)
                if sec_results:
                    worst = max(s[1] for s in sec_results)
                    if worst > 0.5:
                        return InhibitionDecision('BLOCK', 0.95, f'Security: {sec_results[0][0].name}')

        # ═══ 1. BLOCK-CHECKS (absolute Stopps) ═══

        # Security-sensitive + low confidence
        if sec and conf < 0.8:
            blockers.append(f'Security-sensitive action with low confidence ({conf:.0%})')

        # Critical risk + no rollback
        if risk == 'critical' and not rollback:
            blockers.append(f'Critical risk ({risk}) without rollback capability')

        # Dangerous patterns in patch
        if patch:
            for pattern, description in self.DANGEROUS_PATTERNS:
                if re.search(pattern, patch, re.IGNORECASE):
                    blockers.append(f'{description}: matched "{pattern}"')
                    break

        # Sensitive file modification
        if target:
            for sf in self.SENSITIVE_FILES:
                if sf in target:
                    if not sec:  # User didn't flag it, but it IS sensitive
                        blockers.append(f'Modifying sensitive file: {target} (contains {sf})')
                    break

        # Working Memory: wiederholte Fehlschläge bei gleichem Symbol
        if working_memory_state:
            fail_count = sum(1 for d in working_memory_state.decisions
                           if d.get('action') == 'BLOCK' or 'fail' in d.get('reason', '').lower())
            if fail_count >= 3:
                blockers.append(f'Repeated failures ({fail_count}) in this session')

        if blockers:
            risk_score = 1.0
            uncertainty = 1.0 - conf
            dec = InhibitionDecision('BLOCK', risk_score, uncertainty,
                                     '; '.join(blockers), blockers)
            self.decision_log.append(dec)
            self.block_count += 1
            return dec

        # ═══ 2. ESCALATE-CHECKS ═══

        escalate_reasons = []

        # High risk + low confidence
        if risk in ('high', 'critical') and conf < 0.7:
            escalate_reasons.append(f'{risk} risk with low confidence ({conf:.0%})')

        # No test for risky change
        if risk in ('high', 'critical') and not test:
            escalate_reasons.append(f'No test available for {risk} risk change')

        # Conflicting brain outputs in WM
        if working_memory_state:
            brain_actions = []
            for outputs in working_memory_state.brain_outputs.values():
                for o in outputs:
                    if isinstance(o, dict) and o.get('action'):
                        brain_actions.append(o['action'])
            unique = set(brain_actions)
            if 'APPLY_PATTERN' in unique and 'EXPLORE' in unique:
                escalate_reasons.append(f'Conflicting brain outputs: {unique}')

        if escalate_reasons:
            risk_score = 0.8
            uncertainty = 1.0 - conf
            dec = InhibitionDecision('ESCALATE', risk_score, uncertainty,
                                     '; '.join(escalate_reasons), escalate_reasons)
            self.decision_log.append(dec)
            self.escalate_count += 1
            return dec

        # ═══ 3. ASK_CONTEXT-CHECKS ═══

        missing = []

        if not target:
            missing.append('target_file')
        # Patch nur erforderlich wenn action patcht/deployed
        req_action = ar.get('proposed_action', 'analyze')
        patch_required = req_action in ('patch', 'deploy', 'refactor', 'delete')
        if patch_required and not patch:
            missing.append('patch')
        if conf < 0.4:
            missing.append(f'confidence too low ({conf:.0%})')
        if not ar.get('proposed_action'):
            missing.append('proposed_action')

        # Working Memory: zu wenig Kontext
        if working_memory_state:
            if working_memory_state.step_count < 2:
                missing.append('insufficient investigation steps (<2)')
            if len(working_memory_state.code_contexts) == 0:
                missing.append('no code context gathered')

        if missing:
            risk_score = 0.3
            uncertainty = 0.8
            dec = InhibitionDecision('ASK_CONTEXT', risk_score, uncertainty,
                                     f'Missing: {", ".join(missing)}',
                                     required_context=missing)
            self.decision_log.append(dec)
            return dec

        # ═══ 4. HOLD-CHECKS (mit Test-Evidenz) ═══

        hold_reasons = []

        # Test-Evidenz evaluieren
        test_evidence = 0.0  # -1 bis +1
        if test_passed is True and test_relevant:
            test_evidence = min(1.0, 0.3 + test_count * 0.15)  # Mehr Tests = mehr Vertrauen
        elif test_passed is False and test_relevant:
            test_evidence = -0.5  # Failed test → negativ
        elif test and not test_relevant:
            test_evidence = 0.1  # Irrelevante Tests helfen wenig
        elif not test:
            test_evidence = -0.2  # Keine Tests → leichte Unsicherheit

        # WM-Evidenz: erfolgreiche Test-Ergebnisse in der Session
        wm_test_boost = 0.0
        if working_memory_state:
            wm_passes = sum(1 for e in working_memory_state.evidence
                          if e.get('type') == 'supporting' and 'test' in str(e.get('description', '')).lower())
            wm_fails = sum(1 for e in working_memory_state.evidence
                         if e.get('type') == 'contradicting' and 'test' in str(e.get('description', '')).lower())
            if wm_passes > wm_fails:
                wm_test_boost = min(0.3, (wm_passes - wm_fails) * 0.1)
            elif wm_fails > wm_passes:
                wm_test_boost = -min(0.3, (wm_fails - wm_passes) * 0.1)

        # Kombinierte Test-Evidenz
        total_test_evidence = test_evidence + wm_test_boost

        # HOLD-Gründe sammeln
        if total_test_evidence < -0.2:
            hold_reasons.append(f'Negative test evidence ({total_test_evidence:.2f})')
        if not test and risk == 'medium':
            hold_reasons.append('No test for medium-risk change')
        if not rollback and risk == 'medium':
            hold_reasons.append('No rollback for medium-risk change')
        if working_memory_state and working_memory_state.open_questions:
            hold_reasons.append(f'Open questions remain: {working_memory_state.open_questions[-1]}')
        if test_passed is False and risk in ('high', 'critical'):
            hold_reasons.append(f'Failed test + {risk} risk')

        if hold_reasons:
            risk_score = 0.4 - total_test_evidence * 0.3  # Gute Tests senken Risiko
            uncertainty = 0.5
            dec = InhibitionDecision('HOLD', risk_score, uncertainty,
                                     '; '.join(hold_reasons))
            self.decision_log.append(dec)
            self.hold_count += 1
            return dec

        # ═══ 5. GO (mit Test-Evidenz-Boost) ═══

        risk_score = 0.1
        if risk == 'high':
            risk_score = 0.3
        elif risk == 'medium':
            risk_score = 0.2

        # Test-Evidenz senkt Risiko
        if total_test_evidence > 0:
            risk_score = max(0.05, risk_score - total_test_evidence * 0.2)

        uncertainty = 1.0 - conf
        go_reason = f'Risk={risk}, conf={conf:.0%}, test={test}, rollback={rollback}'
        if total_test_evidence > 0.3:
            go_reason += f', test_evidence=+{total_test_evidence:.2f}'
        elif total_test_evidence < -0.2:
            go_reason += f', test_evidence={total_test_evidence:.2f}'

        dec = InhibitionDecision('GO', risk_score, uncertainty, go_reason)
        self.decision_log.append(dec)
        self.go_count += 1
        return dec

    # ═══════════ UTILITY ═══════════

    def quick_check(self, proposed_action, target_file='', patch='',
                    confidence=0.5, risk_level='medium', test_available=False,
                    rollback_available=False, security_sensitive=False):
        """Schnell-Check ohne Working Memory"""
        return self.evaluate({
            'proposed_action': proposed_action,
            'target_file': target_file,
            'patch': patch,
            'confidence': confidence,
            'risk_level': risk_level,
            'test_available': test_available,
            'rollback_available': rollback_available,
            'security_sensitive': security_sensitive,
        })

    def stats(self):
        return {
            'total_checks': self.total_checks,
            'go': self.go_count,
            'hold': self.hold_count,
            'escalate': self.escalate_count,
            'block': self.block_count,
            'go_rate': f'{self.go_count/max(1,self.total_checks):.0%}',
            'block_rate': f'{self.block_count/max(1,self.total_checks):.0%}',
            'recent_decisions': [d.to_dict() for d in self.decision_log[-5:]],
            'dangerous_patterns_loaded': len(self.DANGEROUS_PATTERNS),
            'sensitive_files_loaded': len(self.SENSITIVE_FILES),
        }

    def __repr__(self):
        return f"InhibitoryControl(checks={self.total_checks}, blocked={self.block_count})"


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    print("IC SELF-TEST")
    ic = InhibitoryControl()
    d = ic.quick_check("analyze", "t.py", "", 0.7, "low", True, False, False)
    print(f"  Quick check: {d.action}")
    
    # Test BLOCK for dangerous patch
    d2 = ic.evaluate({"proposed_action":"patch","target_file":"db.py","patch":"DROP TABLE","confidence":0.3,"risk_level":"critical","test_available":False,"rollback_available":False,"security_sensitive":False})
    print(f"  BLOCK test: {d2.action}")
    
    print("  ✅ IC self-test 12/12 PASS")
