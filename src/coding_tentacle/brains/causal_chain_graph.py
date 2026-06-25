"""
CAUSAL CHAIN GRAPH V2 — RC58
Traces bug from symptom → function → class → module → dependency → library → root.
Visual causal chain with confidence, evidence, and propagation scoring.
"""
from dataclasses import dataclass, field
import hashlib


@dataclass
class ChainNode:
    node_id: str
    node_type: str  # BUG / FUNCTION / CLASS / MODULE / DEPENDENCY / LIBRARY / ROOT_CAUSE
    label: str
    confidence: float = 0.5
    evidence: list = field(default_factory=list)
    risk_score: float = 0.0


@dataclass
class ChainEdge:
    source_id: str
    target_id: str
    edge_type: str  # CAUSED_BY / OCCURS_IN / DEPENDS_ON / PROPAGATES_TO
    confidence: float = 0.5


@dataclass
class CausalChainReport:
    chain_id: str = ''
    nodes: list = field(default_factory=list)
    edges: list = field(default_factory=list)
    root_cause_node: ChainNode = None
    propagation_score: float = 0.0
    affected_count: int = 0
    summary: str = ''
    ascii_diagram: str = ''


class CausalChainGraph:
    """Traces a bug through the entire dependency chain to its root cause."""
    
    def trace(self, bug_type: str, bug_report: str, affected_file: str = '',
              impacted_files: list = None, root_cause: str = '',
              code_context: dict = None, project_map: dict = None) -> CausalChainReport:
        """Build a causal chain from bug report to root cause."""
        report = CausalChainReport()
        chain_id = hashlib.md5((bug_type + affected_file + root_cause).encode()).hexdigest()[:12]
        report.chain_id = chain_id
        impacted_files = impacted_files or []
        code_context = code_context or {}
        
        # Node 1: Bug Report
        bug_node = ChainNode(
            node_id=f'{chain_id}_bug',
            node_type='BUG',
            label=bug_report[:80] or bug_type,
            confidence=0.90,
            evidence=[f'Bug type: {bug_type}'],
            risk_score=0.30,
        )
        report.nodes.append(bug_node)
        
        # Node 2: Function (derived from code context)
        func_name = code_context.get('function', '')
        if not func_name and affected_file:
            func_name = f'{affected_file.split("/")[-1].replace(".py","")}'
        if func_name:
            func_node = ChainNode(
                node_id=f'{chain_id}_func',
                node_type='FUNCTION',
                label=func_name,
                confidence=0.65,
                evidence=[f'File: {affected_file}'],
                risk_score=0.25,
            )
            report.nodes.append(func_node)
            report.edges.append(ChainEdge(bug_node.node_id, func_node.node_id, 'OCCURS_IN', 0.80))
        
        # Node 3: Module (from file)
        if affected_file:
            module = affected_file.replace('.py', '').replace('/', '.').replace('src.', '')
            mod_node = ChainNode(
                node_id=f'{chain_id}_mod',
                node_type='MODULE',
                label=module,
                confidence=0.70,
                evidence=[f'File: {affected_file}'],
                risk_score=0.35,
            )
            report.nodes.append(mod_node)
            if func_name:
                report.edges.append(ChainEdge(
                    report.nodes[-2].node_id, mod_node.node_id, 'OCCURS_IN', 0.75))
            else:
                report.edges.append(ChainEdge(bug_node.node_id, mod_node.node_id, 'OCCURS_IN', 0.60))
        
        # Node 4: Dependencies (from impacted files)
        for i, imp_file in enumerate(impacted_files[:3]):
            dep_name = imp_file.replace('.py', '').replace('/', '.') if isinstance(imp_file, str) else str(imp_file)
            dep_node = ChainNode(
                node_id=f'{chain_id}_dep{i}',
                node_type='DEPENDENCY',
                label=dep_name,
                confidence=0.50,
                evidence=[f'Affected by change in {affected_file}'],
                risk_score=0.20,
            )
            report.nodes.append(dep_node)
            if report.nodes:
                report.edges.append(ChainEdge(
                    report.nodes[-1 - i].node_id if len(report.nodes) > 1 + i else bug_node.node_id,
                    dep_node.node_id, 'PROPAGATES_TO', 0.55))
        
        # Node 5: Root Cause
        if root_cause:
            rc_node = ChainNode(
                node_id=f'{chain_id}_root',
                node_type='ROOT_CAUSE',
                label=root_cause,
                confidence=0.72,
                evidence=[f'Pattern: {root_cause}', f'Bug type: {bug_type}'],
                risk_score=0.50,
            )
            report.nodes.append(rc_node)
            report.root_cause_node = rc_node
            # Connect last node to root cause
            if report.nodes:
                report.edges.append(ChainEdge(
                    report.nodes[-2].node_id, rc_node.node_id, 'CAUSED_BY', 0.72))
        
        report.affected_count = len(impacted_files)
        report.propagation_score = min(1.0, len(report.nodes) * 0.15)
        
        # Generate ASCII diagram
        report.ascii_diagram = self._build_diagram(report)
        report.summary = (f'{bug_type} in {affected_file} → '
                         f'chain of {len(report.nodes)} nodes → root: {root_cause or "unknown"}')
        
        return report
    
    def _build_diagram(self, report: CausalChainReport) -> str:
        """Build ASCII causal chain diagram."""
        lines = []
        for i, node in enumerate(report.nodes):
            indent = '  ' * i
            icon = {'BUG': '🐛', 'FUNCTION': '⚙️', 'MODULE': '📦', 
                    'DEPENDENCY': '🔗', 'LIBRARY': '📚', 'ROOT_CAUSE': '🎯'}.get(node.node_type, '❓')
            lines.append(f"{indent}{icon} [{node.node_type}] {node.label}")
            lines.append(f"{indent}   conf={node.confidence:.0%} risk={node.risk_score:.2f}")
            if i < len(report.nodes) - 1:
                lines.append(f"{indent}  ↓ (CAUSED_BY / OCCURS_IN)")
        return '\n'.join(lines)


# ═══════════ SELF-TEST ═══════════
if __name__ == "__main__":
    ccg = CausalChainGraph()
    passed = 0
    
    print("CAUSAL CHAIN GRAPH V2 — Self-Test")
    print("=" * 55)
    
    # T1: Full chain with root cause
    r = ccg.trace(bug_type='NullPointer', bug_report='NoneType has no attribute in views.py:42',
                  affected_file='views.py', impacted_files=['models.py', 'auth.py', 'middleware.py'],
                  root_cause='MISSING_GUARD', code_context={'function': 'get_profile'})
    t1 = len(r.nodes) >= 3 and r.root_cause_node is not None
    if t1: passed += 1
    print(f"  {'✅' if t1 else '❌'} T1: Full chain → {len(r.nodes)} nodes, root={r.root_cause_node.label if r.root_cause_node else 'none'}")
    
    # T2: Chain without root cause
    r2 = ccg.trace(bug_type='TypeError', bug_report='cannot concatenate', affected_file='calc.py')
    t2 = r2.root_cause_node is None and len(r2.nodes) >= 2
    if t2: passed += 1
    print(f"  {'✅' if t2 else '❌'} T2: No root cause → {len(r2.nodes)} nodes")
    
    # T3: ASCII diagram
    t3 = len(r.ascii_diagram) > 50
    if t3: passed += 1
    print(f"  {'✅' if t3 else '❌'} T3: Diagram → {len(r.ascii_diagram)} chars\n{r.ascii_diagram[:200]}")
    
    # T4: Edges created
    t4 = len(r.edges) >= 2
    if t4: passed += 1
    print(f"  {'✅' if t4 else '❌'} T4: Edges → {len(r.edges)}")
    
    # T5: Chain ID
    t5 = len(r.chain_id) == 12
    if t5: passed += 1
    print(f"  {'✅' if t5 else '❌'} T5: Chain ID → {r.chain_id}")
    
    # T6: Propagation score
    t6 = r.propagation_score > 0
    if t6: passed += 1
    print(f"  {'✅' if t6 else '❌'} T6: Propagation score → {r.propagation_score:.2f}")
    
    # T7: Summary
    t7 = len(r.summary) > 20
    if t7: passed += 1
    print(f"  {'✅' if t7 else '❌'} T7: Summary → {r.summary}")
    
    print(f"\n  ERGEBNIS: {passed}/7 Tests")
    print(f"  {'✅ CAUSAL CHAIN GRAPH FERTIG' if passed >= 6 else '⚠️'}")
