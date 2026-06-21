"""
WORKING MEMORY — Gen 15a
Zentraler Kontext-Puffer für Coding Tentacle.
Ohne Working Memory: Jeder think()-Aufruf ist ein Neustart.
Mit Working Memory: Debugging-Sessions mit persistentem Kontext.

Autor: Hermes + David | Coding Tentacle 2026
"""
import time, json, os, uuid
from collections import defaultdict, deque

class WorkingMemoryState:
    """Persistenter Zustand einer Debugging-Session."""
    def __init__(self, session_id):
        self.session_id = session_id
        self.active_bug = None
        self.code_contexts = []       # [{file, line, function, code, stacktrace}]
        self.test_outputs = []         # [{test_name, result, output}]
        self.hypotheses = []           # [{text, confidence, status}]
        self.evidence = []             # [{hypothesis_id, type, strength, description}]
        self.decisions = []            # [{action, reason, timestamp}]
        self.brain_outputs = {}        # {brain_name: [outputs]}
        self.open_questions = []       # ["Warum schlägt Test X fehl?"]
        self.confidence_history = []   # [(step, confidence)]
        self.fix_attempts = []          # [{bug, fix_type, success, confidence, ...}]
        self.created_at = time.time()
        self.updated_at = time.time()
        self.step_count = 0

    def update(self):
        self.updated_at = time.time()
        self.step_count += 1

    def summary(self):
        return {
            'session_id': self.session_id,
            'steps': self.step_count,
            'active_bug': self.active_bug,
            'contexts': len(self.code_contexts),
            'hypotheses': len(self.hypotheses),
            'active_hypotheses': [h for h in self.hypotheses if h.get('status') == 'active'],
            'decisions': len(self.decisions),
            'last_decision': self.decisions[-1] if self.decisions else None,
            'confidence_trend': [c[1] for c in self.confidence_history[-5:]],
            'open_questions': self.open_questions[-3:],
            'brains_consulted': list(self.brain_outputs.keys()),
            'duration_seconds': round(time.time() - self.created_at, 1)
        }

    def to_dict(self):
        return {
            'session_id': self.session_id,
            'active_bug': self.active_bug,
            'code_contexts': self.code_contexts[-10:],
            'hypotheses': self.hypotheses[-10:],
            'evidence': self.evidence[-20:],
            'decisions': self.decisions[-10:],
            'open_questions': self.open_questions[-5:],
            'confidence_history': self.confidence_history[-20:],
            'step_count': self.step_count,
            'brains_consulted': list(self.brain_outputs.keys()),
        }


class WorkingMemory:
    """Zentraler Working-Memory-Manager für Coding Tentacle."""
    def __init__(self, max_sessions=100, storage_dir=None):
        self.max_sessions = max_sessions
        self.storage_dir = storage_dir or os.path.expanduser('~/.hermes/working_memory')
        self.sessions = {}  # {session_id: WorkingMemoryState}
        self._ensure_storage()

    def _ensure_storage(self):
        os.makedirs(self.storage_dir, exist_ok=True)

    # ═══════════ SESSION MANAGEMENT ═══════════

    def create_session(self, session_id=None):
        sid = session_id or str(uuid.uuid4())[:8]
        if sid in self.sessions:
            return self.sessions[sid]
        self.sessions[sid] = WorkingMemoryState(sid)
        if len(self.sessions) > self.max_sessions:
            oldest = min(self.sessions.keys(), key=lambda k: self.sessions[k].updated_at)
            del self.sessions[oldest]
        return self.sessions[sid]

    def load_session(self, session_id):
        if session_id in self.sessions:
            return self.sessions[session_id]
        # Try loading from disk
        path = os.path.join(self.storage_dir, f'{session_id}.json')
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
            state = WorkingMemoryState(session_id)
            state.active_bug = data.get('active_bug')
            state.code_contexts = data.get('code_contexts', [])
            state.hypotheses = data.get('hypotheses', [])
            state.evidence = data.get('evidence', [])
            state.decisions = data.get('decisions', [])
            state.step_count = data.get('step_count', 0)
            state.confidence_history = data.get('confidence_history', [])
            state.open_questions = data.get('open_questions', [])
            self.sessions[session_id] = state
            return state
        return None

    def reset_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]
        return self.create_session(session_id)

    def get_state(self, session_id):
        return self.sessions.get(session_id)

    # ═══════════ CONTEXT UPDATES ═══════════

    def update_context(self, session_id, key, value):
        """Update aktiven Bug-Kontext"""
        state = self.sessions.get(session_id)
        if not state: return None
        if key == 'bug':
            state.active_bug = value
        elif key == 'code_context':
            state.code_contexts.append(value)
            if len(state.code_contexts) > 20:
                state.code_contexts = state.code_contexts[-20:]
        elif key == 'test_output':
            state.test_outputs.append(value)
            if len(state.test_outputs) > 20:
                state.test_outputs = state.test_outputs[-20:]
        elif key == 'question':
            state.open_questions.append(value)
            if len(state.open_questions) > 10:
                state.open_questions = state.open_questions[-10:]
        state.update()
        return state

    def add_brain_output(self, session_id, brain_name, output):
        """Brain-Ergebnis speichern"""
        state = self.sessions.get(session_id)
        if not state: return None
        if brain_name not in state.brain_outputs:
            state.brain_outputs[brain_name] = []
        state.brain_outputs[brain_name].append(output)
        if len(state.brain_outputs[brain_name]) > 10:
            state.brain_outputs[brain_name] = state.brain_outputs[brain_name][-10:]
        state.update()
        return state

    def add_hypothesis(self, session_id, text, confidence=0.5):
        """Hypothese speichern"""
        state = self.sessions.get(session_id)
        if not state: return None
        hyp = {
            'text': text,
            'confidence': confidence,
            'status': 'active',
            'created_at': time.time(),
            'id': len(state.hypotheses) + 1
        }
        state.hypotheses.append(hyp)
        if len(state.hypotheses) > 20:
            state.hypotheses = state.hypotheses[-20:]
        state.update()
        return hyp

    def add_evidence(self, session_id, hypothesis_id, ev_type, strength, description):
        """Evidenz speichern"""
        state = self.sessions.get(session_id)
        if not state: return None
        ev = {
            'hypothesis_id': hypothesis_id,
            'type': ev_type,
            'strength': strength,
            'description': description,
            'timestamp': time.time()
        }
        state.evidence.append(ev)
        if len(state.evidence) > 50:
            state.evidence = state.evidence[-50:]
        state.update()
        return ev

    def add_decision(self, session_id, action, reason, confidence=0.0):
        """Entscheidung speichern"""
        state = self.sessions.get(session_id)
        if not state: return None
        dec = {
            'action': action,
            'reason': reason,
            'confidence': confidence,
            'timestamp': time.time()
        }
        state.decisions.append(dec)
        state.confidence_history.append((state.step_count, confidence))
        if len(state.decisions) > 20:
            state.decisions = state.decisions[-20:]
        if len(state.confidence_history) > 50:
            state.confidence_history = state.confidence_history[-50:]
        state.open_questions = [q for q in state.open_questions if q not in reason]
        return dec

    def add_fix_attempt(self, session_id, bug_signature, bug_type, fix_type, success, confidence=0.5, notes=""):
        """Fix-Versuch in WM speichern."""
        state = self.sessions.get(session_id)
        if not state:
            return None
        state.update()
        fa = {"bug_signature": bug_signature, "bug_type": bug_type,
              "fix_type": fix_type, "success": success, "confidence": confidence,
              "notes": notes, "timestamp": time.time()}
        state.fix_attempts.append(fa)
        return fa

    def get_session_results(self, session_id):
        """Alle Fix-Versuche einer Session abrufen."""
        state = self.sessions.get(session_id)
        return state.fix_attempts if state else []

        state.update()
        return dec

    def summarize(self, session_id):
        """Zusammenfassung des aktuellen Zustands"""
        state = self.sessions.get(session_id)
        if not state: return {'error': 'Session not found'}
        return state.summary()

    def to_context_dict(self, session_id):
        """Kontext als Dict für Brain.think()"""
        state = self.sessions.get(session_id)
        if not state: return {}
        return state.to_dict()

    # ═══════════ PERSISTENZ ═══════════

    def save_session(self, session_id):
        """Session auf Disk speichern"""
        state = self.sessions.get(session_id)
        if not state:
            return False
        path = os.path.join(self.storage_dir, f'{session_id}.json')
        with open(path, 'w') as f:
            json.dump(state.to_dict(), f, indent=2, default=str)
        return True

    def stats(self):
        return {
            'total_sessions': len(self.sessions),
            'active_sessions': sum(1 for s in self.sessions.values() if s.step_count > 0),
            'total_steps': sum(s.step_count for s in self.sessions.values()),
            'avg_steps': round(sum(s.step_count for s in self.sessions.values()) / max(1, len(self.sessions)), 1),
            'storage_dir': self.storage_dir,
            'disk_sessions': len([f for f in os.listdir(self.storage_dir) if f.endswith('.json')])
        }


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    print("GEN 15a — WORKING MEMORY CORE")
    wm = WorkingMemory()
    state = wm.create_session()
    wm.update_context(state.session_id, "bug", "TestBug")
    print("  ✅ working_memory.py — PASS")
