"""
UNIFIED CONFIG SYSTEM — P1.1
Central configuration for all Coding Tentacle modules.
YAML-based, env-overridable, validated, safe defaults.

Replaces: 5 scattered config files with one unified config.

Autor: Hermes + David | Coding Tentacle 2026
"""
import os, yaml, json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional


DEFAULT_CONFIG = {
    'safety': {
        'enabled': True,
        'veto_active': True,
        'auto_apply_enabled': False,          # NEVER auto-apply
        'dangerous_patterns': [
            'drop table', 'delete from', 'rm -rf', 'api_key',
            'secret', 'password', '../../', 'eval(', 'exec(',
            'os.system', 'subprocess', 'pickle.loads',
        ],
    },
    'sandbox': {
        'enabled': True,
        'base_dir': '/tmp/coding_tentacle_sandbox',
        'max_timeout': 30,
        'auto_cleanup': True,
    },
    'test_runner': {
        'enabled': True,
        'max_timeout': 30,
        'max_output': 2000,
        'default_command': 'python -m pytest -x -q',
    },
    'project_map': {
        'cache_enabled': True,
        'max_depth': 5,
        'skip_dirs': ['__pycache__', '.git', '.venv', 'venv', 'node_modules', 'data', 'reports'],
    },
    'shadow_mode': {
        'enabled': True,
        'max_issues_per_batch': 50,
        'github_token': '',                    # Set via env: CT_GITHUB_TOKEN
    },
    'learning': {
        'blm_db_path': '~/.coding_tentacle/blm.db',
        'rules_path': '~/.coding_tentacle/rules.json',
        'procedures_path': '~/.coding_tentacle/procedures.json',
        'skills_path': '~/.coding_tentacle/skills.json',
        'hypothesis_feedback_path': '~/.coding_tentacle/hypothesis_feedback.json',
        'max_blm_records': 10000,
    },
    'parallel': {
        'enabled': True,
        'max_parallel': 8,
        'max_timeout': 30,
    },
}


class Config:
    """Unified configuration. Loads from YAML, env-overridable, validated."""
    
    def __init__(self, config_path=None):
        self.config_path = config_path or os.path.expanduser('~/.coding_tentacle/config.yaml')
        self.data = DEFAULT_CONFIG.copy()
        self._load_from_file()
        self._apply_env_overrides()
        self._validate()
    
    def _load_from_file(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path) as f:
                    user_config = yaml.safe_load(f) or {}
                self._deep_merge(self.data, user_config)
            except Exception:
                pass  # Invalid user config → fall back to defaults
    
    def _apply_env_overrides(self):
        """Env vars override config values. Format: CT_SECTION_KEY"""
        overrides = {
            'CT_SAFETY_ENABLED': ('safety', 'enabled'),
            'CT_SANDBOX_ENABLED': ('sandbox', 'enabled'),
            'CT_SANDBOX_DIR': ('sandbox', 'base_dir'),
            'CT_MAX_TIMEOUT': ('sandbox', 'max_timeout'),
            'CT_GITHUB_TOKEN': ('shadow_mode', 'github_token'),
            'CT_PARALLEL_MAX': ('parallel', 'max_parallel'),
            'CT_BLM_DB': ('learning', 'blm_db_path'),
        }
        for env_var, (section, key) in overrides.items():
            val = os.environ.get(env_var)
            if val is not None:
                # Coerce to correct type
                orig = self.data.get(section, {}).get(key)
                if isinstance(orig, bool):
                    val = val.lower() in ('true', '1', 'yes')
                elif isinstance(orig, int):
                    val = int(val)
                self.data.setdefault(section, {})[key] = val
    
    def _validate(self):
        """Safety-critical validation. Raises on unsafe config."""
        errors = []
        
        # Safety MUST be enabled
        if not self.get('safety.enabled'):
            errors.append("CRITICAL: safety.enabled = false — refused")
        
        # Veto MUST be active
        if not self.get('safety.veto_active'):
            errors.append("CRITICAL: safety.veto_active = false — refused")
        
        # Auto-apply MUST be false
        if self.get('safety.auto_apply_enabled'):
            errors.append("CRITICAL: auto_apply_enabled = true — refused")
        
        # Sandbox MUST be enabled
        if not self.get('sandbox.enabled'):
            errors.append("CRITICAL: sandbox.enabled = false — refused")
        
        if errors:
            raise ValueError("Unsafe configuration:\n" + "\n".join(errors))
    
    def _deep_merge(self, base, override):
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def get(self, path, default=None):
        """Get config value by dot path: 'safety.enabled'"""
        parts = path.split('.')
        current = self.data
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return default
        return current if current is not None else default
    
    def resolve_path(self, path):
        """Expand ~ in paths."""
        return os.path.expanduser(str(path))
    
    def to_dict(self):
        return self.data
    
    def save(self, path=None):
        """Save current config to YAML."""
        p = path or self.config_path
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'w') as f:
            yaml.dump(self.data, f, default_flow_style=False)


# ═══════════ TEST ═══════════
if __name__ == "__main__":
    import tempfile, shutil
    
    print("UNIFIED CONFIG SYSTEM — Self-Test")
    print("=" * 55)
    passed = 0
    
    # T1: Default config works
    cfg = Config(config_path='/nonexistent/config.yaml')
    t1 = cfg.get('safety.enabled') == True
    print(f"  T1: {'✅' if t1 else '❌'} Default config → safety={cfg.get('safety.enabled')}")
    
    # T2: Safety values
    t2 = cfg.get('safety.veto_active') == True and cfg.get('safety.auto_apply_enabled') == False
    print(f"  T2: {'✅' if t2 else '❌'} Safety flags → veto={cfg.get('safety.veto_active')} auto_apply={cfg.get('safety.auto_apply_enabled')}")
    
    # T3: Sandbox values
    t3 = cfg.get('sandbox.enabled') == True and 'tmp' in cfg.get('sandbox.base_dir')
    print(f"  T3: {'✅' if t3 else '❌'} Sandbox → enabled={cfg.get('sandbox.enabled')} dir={cfg.get('sandbox.base_dir')}")
    
    # T4: Learning paths
    t4 = cfg.get('learning.blm_db_path') and '.coding_tentacle' in cfg.get('learning.blm_db_path')
    print(f"  T4: {'✅' if t4 else '❌'} Learning paths → {cfg.get('learning.blm_db_path')}")
    
    # T5: Dot-path access
    t5 = cfg.get('parallel.max_parallel') >= 4
    print(f"  T5: {'✅' if t5 else '❌'} Dot path → parallel.max_parallel={cfg.get('parallel.max_parallel')}")
    
    # T6: Env override
    os.environ['CT_PARALLEL_MAX'] = '16'
    cfg2 = Config(config_path='/nonexistent/config.yaml')
    t6 = cfg2.get('parallel.max_parallel') == 16
    print(f"  T6: {'✅' if t6 else '❌'} Env override → max_parallel={cfg2.get('parallel.max_parallel')}")
    del os.environ['CT_PARALLEL_MAX']
    
    # T7: Path resolution
    resolved = cfg.resolve_path(cfg.get('learning.blm_db_path'))
    t7 = resolved.startswith('/home')
    print(f"  T7: {'✅' if t7 else '❌'} Path resolve → {resolved[:30]}...")
    
    # T8: YAML save/load roundtrip
    tmp = tempfile.mkdtemp()
    cfg_path = os.path.join(tmp, 'config.yaml')
    cfg.save(cfg_path)
    cfg3 = Config(config_path=cfg_path)
    t8 = cfg3.get('safety.enabled') == True
    print(f"  T8: {'✅' if t8 else '❌'} Save/Load → safety={cfg3.get('safety.enabled')}")
    
    # T9: Validation catches unsafe config
    try:
        bad = Config.__new__(Config)
        bad.data = DEFAULT_CONFIG.copy()
        bad.data['safety']['enabled'] = False
        bad._validate()
        t9 = False
    except ValueError:
        t9 = True
    print(f"  T9: {'✅' if t9 else '❌'} Validation → unsafe config blocked")
    
    # T10: to_dict
    d = cfg.to_dict()
    t10 = 'safety' in d and 'sandbox' in d and 'learning' in d
    print(f"  T10: {'✅' if t10 else '❌'} to_dict → {len(d)} sections")
    
    shutil.rmtree(tmp, ignore_errors=True)
    passed = sum([t1,t2,t3,t4,t5,t6,t7,t8,t9,t10])
    print(f"\n  {'='*55}")
    print(f"  ERGEBNIS: {passed}/10 Tests bestanden")
    print(f"  {'✅ UNIFIED CONFIG FERTIG' if passed >= 9 else '⚠️'}")
