"""
Explainable Assistant (Section 9.6).


Not an LLM (that's a real future upgrade requiring an API key + RAG store,
see backend/README.md). This version genuinely queries live twin state for
each question instead of matching 2-3 fixed phrases: it can look up a
specific named node, count nodes above a risk threshold, list top-N
threats, report business impact, or answer general risk questions --
all computed fresh from the current graph, not pre-written strings.
"""
import re
import difflib
from fastapi import APIRouter, Depends
from app.graph.twin import twin
from app.graph.scoring import score_all_nodes
from app import schemas, auth
from app.graph.queries.risk_queries import (
    department_risk_summary,
    impacted_if_down,
    attack_paths_summary,
)


router = APIRouter(prefix="/api/assistant", tags=["assistant"])


def _risk_band(score: float) -> str:
    if score > 0.6:
        return "critical"
    if score > 0.35:
        return "elevated"
    return "low"


# Generic words that show up in almost every question/node-id and would
# otherwise create false "matches" (e.g. every node id starts with "srv").
_STOPWORDS = {
    "srv",
    "host",
    "server",
    "node",
    "box",
    "machine",
    "asset",
    "the",
    "a",
    "an",
    "of",
    "to",
    "is",
    "are",
    "any",
    "risk",
    "there",
    "what",
    "right",
    "now",
    "how",
    "many",
}


def _tokenize(text: str) -> list:
    """Split an identifier or sentence into lowercase word/number tokens."""
    return [t for t in re.split(r"[^a-z0-9]+", text.lower()) if t]


def _node_search_terms(node_id: str, data: dict) -> set:
    """Collect every term a person might reasonably use to refer to this node:
    its id, the id split into parts (with trailing digits stripped so
    'hr01' also yields 'hr'), plus any descriptive metadata the twin
    stores on it (name, role, department, tags, ...)."""
    terms = set()
    terms.add(node_id.lower())
    for tok in _tokenize(node_id):
        terms.add(tok)
        stripped = tok.rstrip("0123456789")
        if stripped:
            terms.add(stripped)
    for field in ("name", "hostname", "label", "role", "department", "type", "tag", "tags"):
        val = data.get(field)
        if isinstance(val, str):
            terms.update(_tokenize(val))
        elif isinstance(val, (list, tuple)):
            for v in val:
                if isinstance(v, str):
                    terms.update(_tokenize(v))
    return terms - _STOPWORDS


def _find_named_node(q: str):
    """Find the node a question is about, even when it's referenced by
    role or nickname ('the hr server') rather than its exact id ('srv-hr01').

    Tries, in order, and returns (node_id, match_confidence) or (None, 0.0):
      1. exact id appears verbatim in the question (fast path)
      2. token overlap between the question and the node's id/metadata terms
      3. fuzzy string match, as a last resort for typos/near-misses
    """
    q_lower = q.lower()
    q_tokens = set(_tokenize(q)) - _STOPWORDS

    # 1. exact id appears verbatim
    for node_id in twin.graph.nodes:
        if node_id.lower() in q_lower:
            return node_id, 1.0

    # 2. token overlap against id parts + metadata
    best_id, best_overlap = None, 0
    for node_id in twin.graph.nodes:
        data = twin.get_node(node_id) or {}
        terms = _node_search_terms(node_id, data)
        overlap = len(q_tokens & terms)
        if overlap > best_overlap:
            best_id, best_overlap = node_id, overlap
    if best_id and best_overlap > 0:
        return best_id, 0.75

    # 3. fuzzy match against node ids, for typos ("srv-dc0" -> "srv-dc01")
    node_ids_lower = [n.lower() for n in twin.graph.nodes]
    candidates = difflib.get_close_matches(q_lower, node_ids_lower, n=1, cutoff=0.6)
    if candidates:
        for node_id in twin.graph.nodes:
            if node_id.lower() == candidates[0]:
                return node_id, 0.5

    return None, 0.0


@router.post("", response_model=schemas.AssistantAnswer)
def ask_assistant(payload: schemas.AssistantQuery, current_user=Depends(auth.get_current_user)):
    q = payload.question.lower().strip()
    risk_scores = score_all_nodes(twin.graph)

    if not risk_scores:
        return schemas.AssistantAnswer(
            answer="The digital twin has no data loaded yet.",
            confidence=0.0,
            sources=[],
        )

    # 1. Named / referenced node -> real lookup, not a template.
    # Matches exact ids AND role/nickname references like "the hr server".
    named, match_confidence = _find_named_node(q)
    if named:
        data = twin.get_node(named)
        score = risk_scores[named]
        neighbors = twin.neighbors(named)
        prefix = "" if match_confidence >= 1.0 else f"Matching your question to '{named}': "
        return schemas.AssistantAnswer(
            answer=(
                f"{prefix}'{named}' is a {data.get('type')} with {_risk_band(score)} risk "
                f"(score {score:.2f}, trust {data.get('trust_score', 0):.2f}, "
                f"{data.get('exposure', 'unknown')} exposure, {data.get('criticality', 'unknown')} criticality). "
                f"It connects outward to {len(neighbors)} node(s)"
                f"{': ' + ', '.join(neighbors[:5]) if neighbors else ''}."
            ),
            confidence=round(0.9 * match_confidence, 2),
            sources=[f"graph:node:{named}", "scoring:node_risk_score"],
        )

    # 2. Count / threshold questions ("how many critical nodes", "nodes above 0.5")
    threshold_match = re.search(r"(above|over|greater than)\s+([0-9]*\.?[0-9]+)", q)
    if threshold_match or "critical" in q or "how many" in q:
        threshold = float(threshold_match.group(2)) if threshold_match else 0.6
        matching = [n for n, s in risk_scores.items() if s > threshold]
        return schemas.AssistantAnswer(
            answer=(
                f"{len(matching)} of {len(risk_scores)} monitored assets currently score above {threshold:.2f} risk: "
                f"{', '.join(matching) if matching else 'none right now'}."
            ),
            confidence=0.88,
            sources=["graph:score_all_nodes"],
        )

    # 3. Riskiest / highest risk
    if "riskiest" in q or "highest risk" in q or "top risk" in q:
        top = sorted(risk_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        node, score = top[0]
        others = ", ".join(f"{n} ({s:.2f})" for n, s in top[1:])
        return schemas.AssistantAnswer(
            answer=(
                f"The highest-risk node right now is '{node}' with a risk score of {score:.2f} "
                f"({_risk_band(score)}). Next highest: {others}."
                if others
                else f"The highest-risk node right now is '{node}' with a risk score of {score:.2f}."
            ),
            confidence=0.9,
            sources=[f"graph:node:{node}", "scoring:node_risk_score"],
        )

    # 4a. Attack paths -- detailed, ranked by dest risk
    if "attack" in q or "path" in q:
        flagged = attack_paths_summary(risk_scores)
        if not flagged:
            return schemas.AssistantAnswer(
                answer="No flagged attack paths detected in the current twin state.",
                confidence=0.75,
                sources=["graph:flagged_edges"],
            )
        lines = []
        for s, t, d in flagged[:3]:
            lines.append(
                f"{s} -> {t} (dest. risk {risk_scores.get(t, 0):.2f}, "
                f"protocol {d.get('protocol')}, port {d.get('port')})"
            )
        return schemas.AssistantAnswer(
            answer=(
                f"{len(flagged)} flagged path(s) detected. "
                "The most concerning chain includes steps like: "
                + "; ".join(lines)
            ),
            confidence=0.85,
            sources=[f"graph:edge:{s}->{t}" for s, t, _ in flagged[:3]],
        )

    # 4b. Threat summary -- reuse same flagged edges, different wording
    if "threat" in q or "threats" in q:
        flagged = attack_paths_summary(risk_scores)
        if not flagged:
            return schemas.AssistantAnswer(
                answer="No active threats are flagged in the current twin state.",
                confidence=0.8,
                sources=["graph:flagged_edges"],
            )
        return schemas.AssistantAnswer(
            answer=(
                f"We've detected {len(flagged)} active threat(s) in the form of flagged attack paths. "
                "These paths represent potential movement from less trusted assets towards "
                "more critical servers such as applications, databases, and the domain controller."
            ),
            confidence=0.85,
            sources=["graph:flagged_edges"],
        )

    # 5. Average / overall risk
    if "average" in q or "overall" in q:
        avg = sum(risk_scores.values()) / len(risk_scores)
        return schemas.AssistantAnswer(
            answer=f"Average risk across {len(risk_scores)} monitored assets is {avg:.2f} ({_risk_band(avg)}).",
            confidence=0.9,
            sources=["graph:score_all_nodes"],
        )

    # 6. Impact if a specific asset goes down
    if "down" in q or "fails" in q or "offline" in q:
        named, match_confidence = _find_named_node(q)
        if named:
            impact = impacted_if_down(named)
            return schemas.AssistantAnswer(
                answer=(
                    f"If '{named}' goes down, it directly touches {len(impact['direct'])} asset(s): "
                    f"{', '.join(impact['direct']) or 'none'}. "
                    f"Indirectly, {len(impact['indirect'])} more asset(s) are connected: "
                    f"{', '.join(set(impact['indirect'])) or 'none'}."
                ),
                confidence=round(0.85 * match_confidence, 2),
                sources=[f"graph:node:{named}", "graph:neighbors"],
            )

    # 7. Nothing matched -- tell the user what actually exists instead of a
    # static canned paragraph, so "is there risk to the HR server" (when
    # there is no HR server in the twin) gets an honest, useful answer.
    known_assets = ", ".join(sorted(twin.graph.nodes))
    return schemas.AssistantAnswer(
        answer=(
            "I couldn't match that to a monitored asset or a supported question type. "
            f"Currently tracked assets: {known_assets}. "
            "You can ask about a specific asset by name or role, a risk threshold ('how many nodes above 0.5'), "
            "the riskiest node, flagged attack paths, detected threats, or overall/average risk -- "
            "all computed live from the current twin."
        ),
        confidence=0.5,
        sources=["graph:nodes"],
    )