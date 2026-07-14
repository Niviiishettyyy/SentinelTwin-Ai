"""
Scoring Method Benchmark.

Compares the composite risk-scoring formula (app.graph.scoring) against
three naive baselines, computed on the same live twin graph:

  1. anomaly_only    -- just the classifier's anomaly score, no topology
  2. pagerank_only    -- pure structural importance, no behavioral signal
  3. criticality_only -- pure asset-value tag, no behavior or topology

This exists to answer a specific question with evidence rather than
assertion: does combining behavioral, structural, and business signals
actually rank assets differently -- and more usefully -- than any single
signal alone? Agreement/disagreement between methods is reported via
Spearman rank correlation, and the nodes with the largest ranking
disagreement are surfaced explicitly, since those are the cases where
the composite formula's added context matters most.
"""
import networkx as nx
from scipy.stats import spearmanr
from app.graph.scoring import score_all_nodes, CRITICALITY_MAP


def _anomaly_only(graph: nx.DiGraph) -> dict:
    return {n: round(d.get("anomaly_score", 0.0), 4) for n, d in graph.nodes(data=True)}


def _pagerank_only(graph: nx.DiGraph) -> dict:
    if graph.number_of_nodes() < 2:
        return {n: 0.0 for n in graph.nodes}
    pr = nx.pagerank(graph, weight="weight")
    max_pr = max(pr.values()) if pr else 1.0
    return {n: round(v / max_pr, 4) if max_pr > 0 else 0.0 for n, v in pr.items()}


def _criticality_only(graph: nx.DiGraph) -> dict:
    return {
        n: CRITICALITY_MAP.get(d.get("criticality", "low"), 0.2)
        for n, d in graph.nodes(data=True)
    }


def _rank_of(scores: dict) -> dict:
    """Maps node -> rank position (1 = highest risk) for a score dict."""
    ordered = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return {node: i + 1 for i, (node, _) in enumerate(ordered)}


def run_benchmark(graph: nx.DiGraph, top_n_disagreements: int = 5) -> dict:
    composite = score_all_nodes(graph)
    methods = {
        "composite": composite,
        "anomaly_only": _anomaly_only(graph),
        "pagerank_only": _pagerank_only(graph),
        "criticality_only": _criticality_only(graph),
    }

    nodes = list(graph.nodes)
    if len(nodes) < 2:
        return {"methods": methods, "correlations": {}, "top_disagreements": []}

    composite_rank = _rank_of(composite)

    correlations = {}
    for name, scores in methods.items():
        if name == "composite":
            continue
        aligned_composite = [composite[n] for n in nodes]
        aligned_other = [scores.get(n, 0.0) for n in nodes]
        rho, p_value = spearmanr(aligned_composite, aligned_other)
        correlations[name] = {
            "spearman_rho": round(float(rho), 4) if rho == rho else 0.0,  # guard against NaN
            "p_value": round(float(p_value), 4) if p_value == p_value else 1.0,
        }

    # Surface nodes where composite disagrees most with the *average* of
    # the naive baselines -- these are the cases that argue for combining
    # signals rather than trusting any single one.
    disagreements = []
    for n in nodes:
        naive_avg = (methods["anomaly_only"][n] + methods["pagerank_only"][n] + methods["criticality_only"][n]) / 3
        disagreements.append({
            "node": n,
            "composite_score": composite[n],
            "naive_average": round(naive_avg, 4),
            "gap": round(abs(composite[n] - naive_avg), 4),
            "composite_rank": composite_rank[n],
        })
    disagreements.sort(key=lambda d: d["gap"], reverse=True)

    return {
        "methods": methods,
        "correlations": correlations,
        "top_disagreements": disagreements[:top_n_disagreements],
    }