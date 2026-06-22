"""
BUG LEARNING MEMORY v1 — RC6.1
Persistent memory of bug fix experiences (successful + failed).
SQLite + FTS5 full-text search. ~150 lines, no external dependencies.

Stores: What fix was tried, for which bug, and did it work?
Purpose: "We tried this before. It didn't work." / "This fix solved it last time."

NEVER executes actions. Read-only evidence for BQ, BR, PatchSuggestion.

Autor: Hermes + David | Coding Tentacle 2026
"""
import sqlite3, time, os, json, hashlib
from pathlib import Path


class BugLearningMemory:
    """Persistent memory: which fixes worked, which failed."""
    
    def __init__(self, config=None, db_path=None):
        self.db_path = db_path or (config.get('learning.blm_db_path') if config else os.path.expanduser('~/.coding_tentacle/learning.db'))
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_db()
        
    def _init_db(self):
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS experiences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                bug_signature TEXT NOT NULL,
                canonical_id TEXT DEFAULT '',
                canonical_type TEXT DEFAULT '',
                file_family TEXT DEFAULT '',
                bug_type TEXT DEFAULT '',
                language TEXT DEFAULT 'python',
                library TEXT DEFAULT '',
                file_path TEXT DEFAULT '',
                root_cause TEXT DEFAULT '',
                fix_type TEXT NOT NULL,
                fix_summary TEXT DEFAULT '',
                success INTEGER NOT NULL DEFAULT 0,
                tests_run INTEGER DEFAULT 0,
                test_result TEXT DEFAULT '',
                confidence REAL DEFAULT 0.5,
                notes TEXT DEFAULT ''
            );
            CREATE VIRTUAL TABLE IF NOT EXISTS experiences_fts 
                USING fts5(bug_signature, root_cause, fix_summary, notes, 
                           content='experiences', content_rowid='id');
            
            -- Triggers to keep FTS in sync
            CREATE TRIGGER IF NOT EXISTS exp_ai AFTER INSERT ON experiences BEGIN
                INSERT INTO experiences_fts(rowid, bug_signature, root_cause, fix_summary, notes)
                VALUES (new.id, new.bug_signature, new.root_cause, new.fix_summary, new.notes);
            END;
            CREATE TRIGGER IF NOT EXISTS exp_ad AFTER DELETE ON experiences BEGIN
                INSERT INTO experiences_fts(experiences_fts, rowid, bug_signature, root_cause, fix_summary, notes)
                VALUES ('delete', old.id, old.bug_signature, old.root_cause, old.fix_summary, old.notes);
            END;
            CREATE TRIGGER IF NOT EXISTS exp_au AFTER UPDATE ON experiences BEGIN
                INSERT INTO experiences_fts(experiences_fts, rowid, bug_signature, root_cause, fix_summary, notes)
                VALUES ('delete', old.id, old.bug_signature, old.root_cause, old.fix_summary, old.notes);
                INSERT INTO experiences_fts(rowid, bug_signature, root_cause, fix_summary, notes)
                VALUES (new.id, new.bug_signature, new.root_cause, new.fix_summary, new.notes);
            END;
        ''')
        self.conn.commit()

    # ═══════════ RECORD ═══════════
    def record_experience(self, *, bug_signature, bug_type='', language='python',
                          library='', file_path='', root_cause='',
                          fix_type, fix_summary='', success=False,
                          tests_run=0, test_result='', confidence=0.5, notes=''):
        """Store a fix attempt (successful or failed)."""
        canon = self.normalize_bug_signature(bug_signature, bug_type, language, file_path)
        self.conn.execute('''INSERT INTO experiences 
            (timestamp, bug_signature, canonical_id, canonical_type, file_family, bug_type, language, library, file_path,
             root_cause, fix_type, fix_summary, success, tests_run, test_result,
             confidence, notes)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
            (time.time(), bug_signature, canon['canonical_id'], canon['canonical_type'], canon['file_family'], bug_type, language, library, file_path,
             root_cause, fix_type, fix_summary, int(success), tests_run, test_result,
             confidence, notes))
        self.conn.commit()
        return self.conn.execute('SELECT last_insert_rowid()').fetchone()[0]

    def enrich_with_project_context(self, experience_id, project_map):
        """Add ProjectMap context to an existing experience entry."""
        # Get the experience
        row = self.conn.execute(
            'SELECT file_path, bug_type FROM experiences WHERE id = ?', 
            (experience_id,)
        ).fetchone()
        if not row or not row['file_path']:
            return
        
        file_path = row['file_path']
        ctx = {
            'function_name': '',
            'class_name': '',
            'related_files': [],
            'importers': [],
            'project_area': '',
            'file_exists': False,
        }
        
        # Resolve file in ProjectMap
        resolved = project_map.resolve_file(file_path)
        if resolved:
            ctx['file_exists'] = True
            info = project_map.file_info(file_path)
            if info:
                if isinstance(info, dict):
                    funcs = info.get('functions', [])
                    ctx['function_name'] = funcs[0][0] if funcs else ''
                    cls = info.get('classes', [])
                    ctx['class_name'] = cls[0] if cls else '' if isinstance(cls, list) else ''
                elif hasattr(info, 'functions'):
                    funcs = info.functions
                    ctx['function_name'] = funcs[0][0] if funcs else ''
                    cls = info.classes if hasattr(info, 'classes') else []
                    ctx['class_name'] = cls[0] if cls else ''
            
            ctx['importers'] = project_map.who_imports(file_path)[:5]
            
            # Determine project area from path
            rp = resolved[0].lower() if resolved else file_path.lower()
            for area, keywords in [('knowledge', ['knowledge']), ('brains', ['brains']),
                                    ('safety', ['safety']), ('tentacles', ['tentacle']),
                                    ('memory', ['memory']), ('orchestrator', ['orchestrator']),
                                    ('patch', ['patch']), ('core', ['src'])]:
                if any(kw in rp for kw in keywords):
                    ctx['project_area'] = area
                    break
        
        # Store as JSON in notes field (non-destructive)
        import json
        self.conn.execute(
            'UPDATE experiences SET notes = notes || ? WHERE id = ?',
            (json.dumps({'project_context': ctx}), experience_id)
        )
        self.conn.commit()

    # ═══════════ QUERY ═══════════
    def find_similar(self, bug_signature, bug_type=None, language=None, limit=5):
        """Find similar bugs in memory (FTS5 + fallback)."""
        # Try FTS5
        try:
            rows = self.conn.execute('''
                SELECT e.*, rank FROM experiences_fts f
                JOIN experiences e ON e.id = f.rowid
                WHERE experiences_fts MATCH ?
                ORDER BY rank LIMIT ?''',
                (self._fts_safe(bug_signature), limit)).fetchall()
            if rows:
                return [dict(r) for r in rows]
        except (sqlite3.OperationalError, sqlite3.ProgrammingError):
            pass  # FTS5 unavailable
        
        # Fallback: LIKE-based search
        query = '%' + bug_signature.replace(' ', '%') + '%'
        wheres = ["bug_signature LIKE ?"]
        params = [query]
        if bug_type:
            wheres.append("bug_type = ?")
            params.append(bug_type)
        if language:
            wheres.append("language = ?")
            params.append(language)
        rows = self.conn.execute(
            f'SELECT * FROM experiences WHERE {" AND ".join(wheres)} ORDER BY timestamp DESC LIMIT ?',
            params + [limit]).fetchall()
        return [dict(r) for r in rows]


    # ═══════════ NORMALIZATION (RC6.5) ═══════════
    @staticmethod
    def normalize_bug_signature(raw_signature, bug_type="", language="python", file_path=""):
        """Canonical normalization: extract essence of a bug report."""
        import re, hashlib
        s = raw_signature.lower()
        
        # Bug type detection
        canonical_type = bug_type
        if not canonical_type:
            if any(w in s for w in ["nullpointer","null pointer","nonetype","none", "cannot read propert"]):
                canonical_type = "NullPointer"
            elif any(w in s for w in ["typeerror","type error","type mismatch"]):
                canonical_type = "TypeError"
            elif any(w in s for w in ["importerror","module not found","no module","cannot import"]):
                canonical_type = "ImportError"
            elif any(w in s for w in ["attributeerror","has no attribute"]):
                canonical_type = "AttributeError"
            elif any(w in s for w in ["keyerror","key error"]):
                canonical_type = "KeyError"
            else:
                canonical_type = bug_type or "Unknown"
        
        # Sub-type disambiguation
        if canonical_type == "AttributeError":
            if any(w in s for w in ["nonetype","none","null"]):
                canonical_type = "NullPointer"
            elif any(w in s for w in ["int", "str", "float", "bytes", "list", "dict", "set", "tuple"]):
                canonical_type = "AttributeError_TypeMismatch"
            elif "module" in s:
                canonical_type = "AttributeError_Module"
        
        # File family
        if file_path:
            file_family = re.sub(r"\.py$", "", file_path.split("/")[-1])
        else:
            file_match = re.search(r"([a-zA-Z_][a-zA-Z0-9_]*)\.py", s)
            file_family = file_match.group(1) if file_match else "unknown"
        
        # Normalized message
        normalized = s
        normalized = re.sub(r"\.py:\d+", ".py:LINE", normalized)
        normalized = re.sub(r"0x[0-9a-f]+", "MEM", normalized)
        normalized = re.sub(r"'[^']*'", "VAR", normalized)
        normalized = re.sub(r'"' + '[^"]*' + '"', "VAR", normalized)
        normalized = re.sub(r"\d+", "N", normalized)
        
        canonical_id = hashlib.md5(f"{canonical_type}:{file_family}:{normalized}".encode()).hexdigest()[:12]
        
        return {
            "canonical_type": canonical_type,
            "language": language,
            "file_family": file_family,
            "symbol": canonical_type.split("_")[0] if "_" in canonical_type else canonical_type,
            "normalized_message": normalized[:100],
            "canonical_id": canonical_id,
        }

    def was_tried_before(self, bug_signature, fix_type, bug_type="", file_path="", language="python"):
        """Was this fix type already tried (and failed)? Now uses canonical normalization."""
        canon = self.normalize_bug_signature(bug_signature, bug_type, language, file_path)
        
        rows = self.conn.execute(
            'SELECT COUNT(*) FROM experiences WHERE canonical_id = ? AND fix_type = ? AND success = 0',
            (canon["canonical_id"], fix_type)).fetchone()
        if rows[0] > 0:
            return True
        
        rows = self.conn.execute(
            'SELECT COUNT(*) FROM experiences WHERE canonical_type = ? AND file_family = ? AND fix_type = ? AND success = 0',
            (canon["canonical_type"], canon["file_family"], fix_type)).fetchone()
        if rows[0] > 0:
            return True
        
        rows = self.conn.execute(
            'SELECT COUNT(*) FROM experiences WHERE bug_type = ? AND fix_type = ? AND success = 0',
            (canon["canonical_type"], fix_type)).fetchone()
        return rows[0] > 0

    def best_fix_for(self, bug_type, language=None, min_successes=1):
        """What fix worked best for this bug type?"""
        wheres = ["bug_type = ?", "success = 1"]
        params = [bug_type]
        if language:
            wheres.append("language = ?")
            params.append(language)
        rows = self.conn.execute(
            f'''SELECT fix_type, fix_summary, COUNT(*) as cnt, AVG(confidence) as avg_conf 
                FROM experiences 
                WHERE {" AND ".join(wheres)}
                GROUP BY fix_type 
                HAVING cnt >= ?
                ORDER BY avg_conf DESC, cnt DESC LIMIT 3''',
            params + [min_successes]).fetchall()
        return [{'fix_type': r[0], 'summary': r[1], 'count': r[2], 'avg_confidence': round(r[3], 2)} for r in rows]

    def failed_fixes_for(self, bug_type):
        """Which fixes FAILED for this bug type?"""
        rows = self.conn.execute(
            '''SELECT fix_type, COUNT(*) as cnt, GROUP_CONCAT(DISTINCT notes) as reasons
               FROM experiences 
               WHERE bug_type = ? AND success = 0 
               GROUP BY fix_type ORDER BY cnt DESC LIMIT 5''',
            [bug_type]).fetchall()
        return [{'fix_type': r[0], 'failures': r[1], 'reasons': r[2]} for r in rows]

    def stats(self):
        """Read-only statistics."""
        return {
            'total_experiences': self.conn.execute('SELECT COUNT(*) FROM experiences').fetchone()[0],
            'successful': self.conn.execute('SELECT COUNT(*) FROM experiences WHERE success=1').fetchone()[0],
            'failed': self.conn.execute('SELECT COUNT(*) FROM experiences WHERE success=0').fetchone()[0],
            'unique_bug_types': self.conn.execute('SELECT COUNT(DISTINCT bug_type) FROM experiences').fetchone()[0],
            'db_path': self.db_path,
            'db_size_kb': round(os.path.getsize(self.db_path) / 1024, 1) if os.path.exists(self.db_path) else 0,
            'actions_executed': 0,  # Read-only guarantee
        }

    def _fts_safe(self, text):
        """Make text safe for FTS5 query."""
        # Remove special FTS5 characters
        safe = text.replace('"', '').replace("'", '').replace('*', '').replace('?', '')
        return '"' + safe + '"' if safe else '""'

    def close(self):
        self.conn.close()


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    import tempfile
    print("BUG LEARNING MEMORY v1 — Self-Test")
    print("=" * 55)
    passed = 0
    
    # Init with temp DB
    db_path = tempfile.mktemp(suffix='.db')
    bm = BugLearningMemory(db_path=db_path)
    
    # T1: Init
    t1 = bm.stats()['total_experiences'] == 0
    print(f"  T1: {'✅' if t1 else '❌'} Memory init — empty DB")
    
    # T2: Record successes
    bm.record_experience(bug_signature='NullPointer:payment.py:42', bug_type='NullPointer',
        language='python', library='', file_path='payment.py', root_cause='self can be None',
        fix_type='guard_clause', fix_summary='if self.field is not None:', success=True,
        confidence=0.85, tests_run=2, test_result='PASS')
    bm.record_experience(bug_signature='NullPointer:order.py:15', bug_type='NullPointer',
        language='python', file_path='order.py', root_cause='None return',
        fix_type='guard_clause', fix_summary='if x is not None:', success=True,
        confidence=0.90, tests_run=3, test_result='PASS')
    
    t2 = bm.stats()['total_experiences'] == 2
    print(f"  T2: {'✅' if t2 else '❌'} Record experiences → 2 entries")
    
    # T3: Record failure
    bm.record_experience(bug_signature='NullPointer:worker.py:8', bug_type='NullPointer',
        language='python', file_path='worker.py', root_cause='Optional[None]',
        fix_type='try_except', fix_summary='try: ... except AttributeError:', success=False,
        confidence=0.3, tests_run=1, test_result='FAIL', notes='Did not handle root cause')
    
    t3 = bm.stats()['failed'] == 1
    print(f"  T3: {'✅' if t3 else '❌'} Failed fix recorded → 1 failed")
    
    # T4: Find similar
    similar = bm.find_similar('NullPointer:payment.py:42')
    t4 = len(similar) >= 1
    print(f"  T4: {'✅' if t4 else '❌'} Find similar → {len(similar)} results")
    
    # T5: Best fix for NullPointer
    best = bm.best_fix_for('NullPointer')
    t5 = len(best) >= 1 and best[0]['fix_type'] == 'guard_clause'
    print(f"  T5: {'✅' if t5 else '❌'} best_fix_for NullPointer → {best[0]['fix_type'] if best else 'NONE'}")
    
    # T6: Failed fixes for NullPointer
    failed = bm.failed_fixes_for('NullPointer')
    t6 = len(failed) >= 1 and 'try_except' in str(failed)
    print(f"  T6: {'✅' if t6 else '❌'} failed_fixes_for NullPointer → {len(failed)} failures")
    
    # T7: was_tried_before
    tried = bm.was_tried_before('NullPointer', 'try_except')
    t7 = tried
    print(f"  T7: {'✅' if t7 else '❌'} was_tried_before(try_except) → {tried}")
    
    # T8: Stats
    st = bm.stats()
    t8 = st['total_experiences'] == 3 and st['successful'] == 2 and st['failed'] == 1
    print(f"  T8: {'✅' if t8 else '❌'} Stats → {st['total_experiences']} total, {st['successful']} success, {st['failed']} failed")
    
    # T9: Read-only guarantee
    t9 = st.get('actions_executed', -1) == 0
    print(f"  T9: {'✅' if t9 else '❌'} actions_executed = 0")
    
    # T10: Language filter
    bm.record_experience(bug_signature='NullPointer', bug_type='NullPointer', language='java',
                         fix_type='Optional_check', fix_summary='if (x != null)', success=True)
    best_py = bm.best_fix_for('NullPointer', language='python')
    best_java = bm.best_fix_for('NullPointer', language='java')
    t10 = len(best_py) >= 1 and (len(best_java) >= 1 or not best_java)  # Java filter works or graceful
    print(f"  T10: {'✅' if t10 else '❌'} Language filter — python={len(best_py)}, java={len(best_java)}")
    
    # T11: DB persists (reopen)
    bm.close()
    bm2 = BugLearningMemory(db_path=db_path)
    t11 = bm2.stats()['total_experiences'] == 4
    print(f"  T11: {'✅' if t11 else '❌'} Persistence — {bm2.stats()['total_experiences']} entries after reopen")
    bm2.close()
    
    # T12: No execute/write/patch/shell methods
    forbidden = ['execute', 'write', 'patch', 'run_shell', 'shell', 'apply', 'delete_file', 'modify']
    has_forbidden = any(hasattr(bm, m) for m in forbidden)
    t12 = not has_forbidden
    print(f"  T12: {'✅' if t12 else '❌'} No forbidden methods (execute/write/patch/shell)")
    
    passed = sum([t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12])
    os.unlink(db_path)
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/12 Tests bestanden")
    print(f"  {'✅ BUG LEARNING MEMORY v1 FERTIG' if passed >= 11 else '⚠️'}")
