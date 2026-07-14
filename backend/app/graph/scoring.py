"""
Risk scoring and defense-recommendation ranking formulas (Section 9b).

Implements:
  risk(node)   = w1*anomaly_score + w2*path_centrality + w3*asset_criticality + w4*exposure_factor
  score(action)= alpha*risk_reduction - beta*operational_cost + gamma*historical_success

Also implements an adaptive UCB1 (Upper Confidence Bound) multi-armed
bandit layer on top of the base utility score, so recommendation ranking
improves from real logged outcomes over time instead of relying purely
on the fixed alpha/beta/gamma weights.
"""
import math
import networkx as nx

# --- Node risk score weights ---
W1_ANOMALY = 0.40
W2_CENTRALITY = 0.20
W3_CRITICALITY = 0.25
W4_EXPOSURE = 0.15

CRITICALITY_MAP = {"low": 0.2, "medium": 0.5, "high": 0.8, "critical": 1.0}
EXPOSURE_MAP = {"internal": 0.3, "external": 1.0}

# --- Recommendation ranking weights ---
ALPHA_RISK_REDUCTION = 0.5
BETA_OPERATIONAL_COST = 0.3
GAMMA_HISTORICAL_SUCCESS = 0.2

# --- Bandit exploration constant (UCB1) ---
EXPLORATION_CONSTANT = 0.15


def compute_centrality(graph: nx.DiGraph) -> dict:
    if graph.number_of_nodes() < 2:
        return {n: 0.0 for n in graph.nodes}
    return nx.betweenness_centrality(graph, weight="weight")


def node_risk_score(graph: nx.DiGraph, node_id: str, centrality: dict = None) -> float:
    data = graph.nodes[node_id]
    centrality = centrality or compute_centrality(graph)

    anomaly = data.get("anomaly_score", 0.0)
    path_centrality = centrality.get(node_id, 0.0)
    criticality = CRITICALITY_MAP.get(data.get("criticality", "low"), 0.2)
    exposure = EXPOSURE_MAP.get(data.get("exposure", "internal"), 0.3)

    score = (
        W1_ANOMALY * anomaly
        + W2_CENTRALITY * path_centrality
        + W3_CRITICALITY * criticality
        + W4_EXPOSURE * exposure
    )
    return round(min(score, 1.0), 4)


def score_all_nodes(graph: nx.DiGraph) -> dict:
    centrality = compute_centrality(graph)
    return {n: node_risk_score(graph, n, centrality) for n in graph.nodes}


def recommendation_score(risk_reduction: float, operational_cost: float, historical_success: float) -> float:
    """Static formula (kept for backward compatibility / cold-start use)."""
    score = (
        ALPHA_RISK_REDUCTION * risk_reduction
        - BETA_OPERATIONAL_COST * operational_cost
        + GAMMA_HISTORICAL_SUCCESS * historical_success
    )
    return round(score, 4)


def adaptive_recommendation_score(
    risk_reduction: float,
    operational_cost: float,
    avg_reward: float,
    action_trials: int,
    total_trials: int,
) -> tuple:
    """
    UCB1-style adaptive score: base utility (using the action's real
    observed average reward instead of a static prior) plus an
    exploration bonus that shrinks as an action accumulates more trials,
    and grows for actions that have been tried less often relative to
    the pattern's total trial count. This is what lets the recommendation
    engine's ranking genuinely shift over time based on logged outcomes.

    Returns (final_score, exploration_bonus).
    """
    exploitation = (
        ALPHA_RISK_REDUCTION * risk_reduction
        - BETA_OPERATIONAL_COST * operational_cost
        + GAMMA_HISTORICAL_SUCCESS * avg_reward
    )
    exploration_bonus = EXPLORATION_CONSTANT * math.sqrt(
        2 * math.log(total_trials + 1) / (action_trials + 1)
    )
    final_score = exploitation + exploration_bonus
    return round(final_score, 4), round(exploration_bonus, 4)