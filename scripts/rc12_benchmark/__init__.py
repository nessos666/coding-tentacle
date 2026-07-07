"""
CT RC12 BENCHMARK FRAMEWORK

Modules:
  benchmark_runner.py  — JSONL→Pipeline→Metrics→Report (CLI)
  metric_collector.py  — 17 standardized metrics per repair
  explainability.py    — Decision Trace per repair
  report_generator.py  — Markdown + JSON reports
  curate_datasets.py   — Golden dataset generator (10 types, 1000 bugs)
  batch_runner.py      — Batch runner + Scorecard + Learning Curves
"""

from .metric_collector import MetricCollector, BenchmarkResult
from .explainability import ExplainabilityEngine, DecisionTrace
from .report_generator import ReportGenerator
from .benchmark_runner import BenchmarkRunner, BenchmarkRun
from .curate_datasets import DatasetCurator, GoldenCase
from .batch_runner import BatchRunner, CTScorecard, ScorecardEngine, LearningCurveExperiment
