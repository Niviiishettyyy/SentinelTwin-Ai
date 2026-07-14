"""
Attack Simulation engine (Section 9.4 / 9c).

Runs a safe, in-memory traversal of the twin graph starting from a chosen
(or highest-risk) entry node, following edges weighted by anomaly/risk,
and records a step-by-step log used to drive the frontend's animated
timeline. Nothing here touches real infrastructure -- it only reads the
in-memory NetworkX graph.

MITRE ATT&CK mapping note: technique IDs below are assigned by a
heuristic based on step order and target node type/role (e.g. "first
step into an externally-exposed node" -> Initial Access; "reaching a
domain-controller-like node" -> Privilege Escalation). This is a rule-based
labeling layer for analyst context, not a claim that these exact
techniques were observed in real traffic -- the underlying flow data has
no ATT&CK ground-truth labels to derive this from directly.
"""
import heapq
from app.graph.scoring import score_all_nodes


def pick_entry_node(graph):
    """
    Default entry point for a simulation, when the caller doesn't specify
    one: prefer externally-exposed nodes with outgoing edges (realistic
    attacker footholds), falling back to the highest-risk node with
    successors, then any node.
    """
    external_candidates = [
        n for n, d in graph.nodes(data=True)
        if d.get("exposure") == "external" and graph.out_degree(n) > 0
    ]
    scores = score_all_nodes(graph)
    if external_candidates:
        return max(external_candidates, key=lambda n: scores.get(n, 0.0))

    nodes_with_successors = [n for n in graph.nodes if graph.out_degree(n) > 0]
    if nodes_with_successors:
        return max(nodes_with_successors, key=lambda n: scores.get(n, 0.0))

    return max(scores, key=scores.get) if scores else None


def _map_attack_technique(step_index: int, node_id: str, node_data: dict):
    """
    Heuristically assigns a MITRE ATT&CK tactic + technique to a
    simulation step, based on step order and the target node's type,
    criticality, and naming convention. Returns (tactic, technique_id,
    technique_name).
    """
    node_type = node_data.get("type", "device")
    criticality = node_data.get("criticality", "low")
    name = node_id.lower()

    if step_index == 0:
        return ("Initial Access", "T1190", "Exploit Public-Facing Application")

    if "dc" in name or (node_type == "server" and criticality == "critical"):
        return ("Privilege Escalation", "T1078.002", "Valid Accounts: Domain Accounts")

    if "db" in name:
        return ("Exfiltration", "T1041", "Exfiltration Over C2 Channel")

    if node_type == "server":
        return ("Lateral Movement", "T1021.002", "Remote Services: SMB/Windows Admin Shares")

    return ("Lateral Movement", "T1021.001", "Remote Services: Remote Desktop Protocol")


def run_simulation(graph, entry_node: str = None, max_steps: int = 8):
    if graph.number_of_nodes() == 0:
        return {"steps": [], "peak_risk": 0.0}

    entry_node = entry_node or pick_entry_node(graph)
    if entry_node not in graph:
        return {"steps": [], "peak_risk": 0.0}

    scores = score_all_nodes(graph)
    visited = set()
    steps = []
    peak_risk = 0.0

    # priority queue of (-risk, node) so we always expand the riskiest frontier next
    frontier = [(-scores.get(entry_node, 0.0), entry_node)]
    step_index = 0

    while frontier and step_index < max_steps:
        neg_risk, node = heapq.heappop(frontier)
        if node in visited:
            continue
        visited.add(node)
        risk = -neg_risk
        peak_risk = max(peak_risk, risk)

        action = "initial compromise" if step_index == 0 else "lateral movement"
        node_data = graph.nodes[node]
        tactic, technique_id, technique_name = _map_attack_technique(step_index, node, node_data)

        steps.append({
            "step_index": step_index,
            "node": node,
            "action": action,
            "risk_delta": risk,
            "description": (
                f"{action.capitalize()} at node '{node}' (risk={risk:.2f}) "
                f"— {tactic}: {technique_id} {technique_name}"
            ),
            "tactic": tactic,
            "technique_id": technique_id,
            "technique_name": technique_name,
        })
        step_index += 1

        for neighbor in graph.successors(node):
            if neighbor not in visited:
                heapq.heappush(frontier, (-scores.get(neighbor, 0.0), neighbor))

    return {"steps": steps, "peak_risk": round(peak_risk, 4)}