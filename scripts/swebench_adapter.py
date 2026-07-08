"""
CT 11.x — SWE-BENCH ADAPTER

Lädt SWE-bench-format JSONL, konvertiert zu CT GitHubIssueRun,
führt Pipeline aus, generiert predictions.jsonl.

Realistischer Scope:
- Lokale Evaluation ohne Docker-Harness
- Misst: Klassifikation, Security, Routing, Reflection
- Output im SWE-bench predictions-Format

CT-v11.0.0: PRODUCTION | SWE-bench Integration
"""

import json, sys, os, time
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class SWEBenchPrediction:
    """SWE-bench prediction format."""
    instance_id: str
    model_name_or_path: str = "coding-tentacle-v11.0.0"
    model_patch: str = ""


class SWEBenchAdapter:
    """
    Adapter: SWE-bench JSONL → CT Pipeline → Predictions.
    
    Usage:
        adapter = SWEBenchAdapter(runner)
        predictions = adapter.run('swebench_lite.jsonl', limit=10)
        adapter.save_predictions(predictions, 'predictions.jsonl')
    """
    
    def __init__(self, runner=None):
        self.runner = runner
    
    def load_instances(self, path, limit=None):
        """Lade SWE-bench JSONL instances."""
        instances = []
        with open(path) as f:
            for i, line in enumerate(f):
                if limit and i >= limit:
                    break
                instances.append(json.loads(line))
        return instances
    
    def instance_to_ct_format(self, instance):
        """Konvertiere SWE-bench instance → CT GitHubIssueRun."""
        from coding_tentacle.orchestrator.shadow_mode import GitHubIssueRun
        
        repo = instance.get('repo', 'unknown/repo')
        instance_id = instance.get('instance_id', '')
        problem = instance.get('problem_statement', instance.get('issue_title', ''))
        body = instance.get('hints_text', instance.get('issue_body', ''))
        
        return GitHubIssueRun(
            repo_url=f"https://github.com/{repo}",
            issue_url=f"https://github.com/{repo}/issues/{instance_id}",
            issue_title=problem[:100] if problem else instance_id,
            issue_body=body[:2000] if body else problem[:2000],
        )
    
    def run_single(self, instance) -> dict:
        """Führe CT Pipeline für eine Instance aus."""
        ct_issue = self.instance_to_ct_format(instance)
        
        if self.runner is None:
            from coding_tentacle.orchestrator.shadow_mode import ShadowModeRunner
            self.runner = ShadowModeRunner()
        
        report = self.runner.analyze_issue(ct_issue)
        
        return {
            'instance_id': instance.get('instance_id', ''),
            'detected_bug_type': report.detected_bug_type,
            'confidence': report.confidence,
            'security_blocked': report.security_blocked,
            'security_risk_score': getattr(report, 'security_risk_score', 0.0),
            'engine_used': getattr(report, 'engine_used', ''),
            'generated_diff': report.generated_diff[:500] if report.generated_diff else '',
            'droste_nodes': report.droste_nodes,
            'reflection': report.reflection.get('success') if report.reflection else None,
            'transferable_lesson': report.transferable_lesson[:200],
            'lessons_applied': report.lessons_applied,
            'prompt_learning_used': getattr(report, 'prompt_learning_used', False),
            'duration_ms': report.duration_ms,
        }
    
    def run(self, path, limit=None):
        """Führe CT auf allen Instanzen aus."""
        instances = self.load_instances(path, limit)
        results = []
        
        for i, inst in enumerate(instances):
            print(f"[{i+1}/{len(instances)}] {inst.get('instance_id','?')[:60]}", end=' ', flush=True)
            try:
                result = self.run_single(inst)
                results.append(result)
                status = '🛡️' if result['security_blocked'] else ('✅' if result['generated_diff'] else '⚠️')
                print(f"{status} {result['detected_bug_type']}")
            except Exception as e:
                print(f'❌ {e}')
                results.append({'instance_id': inst.get('instance_id', ''), 'error': str(e)})
        
        return results
    
    def to_predictions(self, results, model_name="coding-tentacle-v11.0.0"):
        """Konvertiere CT-Ergebnisse zu SWE-bench prediction Format."""
        predictions = []
        for r in results:
            pred = SWEBenchPrediction(
                instance_id=r.get('instance_id', ''),
                model_name_or_path=model_name,
                model_patch=r.get('generated_diff', ''),
            )
            predictions.append(asdict(pred))
        return predictions
    
    def save_predictions(self, predictions, path):
        """Speichere predictions als JSONL."""
        with open(path, 'w') as f:
            for p in predictions:
                f.write(json.dumps(p) + '\n')
        return path
    
    def compute_stats(self, results):
        """Berechne Statistiken aus CT-Ergebnissen."""
        total = len(results)
        if total == 0:
            return {}
        
        classified = sum(1 for r in results if r.get('detected_bug_type') != 'Unknown')
        blocked = sum(1 for r in results if r.get('security_blocked'))
        with_diff = sum(1 for r in results if r.get('generated_diff'))
        droste_avg = sum(r.get('droste_nodes', 0) for r in results) / total
        reflection_success = sum(1 for r in results if r.get('reflection') == True)
        
        return {
            'total_instances': total,
            'classification_rate': f"{100*classified//total}%",
            'security_blocks': blocked,
            'diffs_generated': with_diff,
            'avg_droste_nodes': round(droste_avg, 1),
            'reflection_success_rate': f"{100*reflection_success//total}%",
            'pipeline_coverage': f"{100*classified//total}% classified | {blocked} blocked | {with_diff} diffs",
        }


# ─── Self-Tests ─────────────────────────────────────────────────────────

if __name__ == '__main__':
    import tempfile
    
    # Create sample SWE-bench-format instances
    sample = [
        {
            'instance_id': 'django__django-10097',
            'repo': 'django/django',
            'issue_title': 'NullPointer in QuerySet.filter() when chaining',
            'problem_statement': 'QuerySet.filter() raises AttributeError: NoneType when chaining multiple filters on a null relation.',
            'hints_text': 'Similar to #10095. Check null handling in _filter_or_exclude.',
        },
        {
            'instance_id': 'pytest__pytest-5221',
            'repo': 'pytest-dev/pytest',
            'issue_title': 'TypeError when formatting test output with None',
            'problem_statement': 'TypeError: can only concatenate str (not "NoneType") to str in test output formatting.',
        },
        {
            'instance_id': 'requests__requests-4356',
            'repo': 'psf/requests',
            'issue_title': 'KeyError accessing missing header in response',
            'problem_statement': 'KeyError raised when accessing response.headers for a missing key instead of returning None.',
        },
    ]
    
    # Save as temp JSONL
    tmp = tempfile.mktemp(suffix='.jsonl')
    with open(tmp, 'w') as f:
        for s in sample:
            f.write(json.dumps(s) + '\n')
    
    # Run
    print("CT SWE-BENCH ADAPTER — Self-Test\n")
    adapter = SWEBenchAdapter()
    results = adapter.run(tmp, limit=3)
    
    stats = adapter.compute_stats(results)
    print(f"\n{'='*50}")
    print(f"SWE-BENCH RESULT:")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    
    # Predictions
    preds = adapter.to_predictions(results)
    pred_path = tempfile.mktemp(suffix='_preds.jsonl')
    adapter.save_predictions(preds, pred_path)
    print(f"\nPredictions saved: {pred_path}")
    
    os.unlink(tmp)
    os.unlink(pred_path)
    print("✅ SWE-BENCH ADAPTER FERTIG")
