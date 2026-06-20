"""Coding Tentacle — Portable Configuration"""
from pathlib import Path

# ═══ PROJECT ROOT (auto-detected) ═══
PROJECT_ROOT = Path(__file__).resolve().parent

# ═══ DATA DIRS ═══
DATA_DIR = PROJECT_ROOT / ".data"
HISTORY_DIR = DATA_DIR / "history"
REPORTS_DIR = PROJECT_ROOT / ".reports"

# Auto-create dirs
for d in [DATA_DIR, HISTORY_DIR, REPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ═══ DEFAULT PATHS ═══
BQ_HISTORY_PATH = HISTORY_DIR / "grounding_history.json"
BOTTLENECK_REPORT_PATH = REPORTS_DIR / "bottleneck_analysis.json"

# ═══ BRAIN LIBRARY ═══
BRAIN_DIR = PROJECT_ROOT  # Brains are in subdirs of PROJECT_ROOT
BQ_BRAIN_DIR = PROJECT_ROOT / "71_symbol_grounding"
