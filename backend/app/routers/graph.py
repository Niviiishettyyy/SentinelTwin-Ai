from fastapi import APIRouter, Depends
from app.graph.twin import twin
from app.graph.scoring import score_all_nodes
from app import schemas, auth

router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.get("", response_model=schemas.GraphOut)
def get_graph(current_user=Depends(auth.get_current_user)):
    risk_scores = score_all_nodes(twin.graph)
    nodes = [
        schemas.NodeOut(
            id=n,
            type=data.get("type", "device"),
            label=data.get("label", n),
            trust_score=data.get("trust_score", 0.5),
            risk_score=risk_scores.get(n, 0.0),
            attributes={k: v for k, v in data.items() if k not in ("type", "label", "trust_score")},
        )
        for n, data in twin.all_nodes()
    ]
    edges = [
        schemas.EdgeOut(source=s, target=t, type=data.get("type", "connects_to"), weight=data.get("weight", 1.0))
        for s, t, data in twin.all_edges()
    ]
    return schemas.GraphOut(nodes=nodes, edges=edges)


@router.get("/node/{node_id}", response_model=schemas.NodeOut)
def get_node(node_id: str, current_user=Depends(auth.get_current_user)):
    data = twin.get_node(node_id)
    if data is None:
        return schemas.NodeOut(id=node_id, type="unknown", label=node_id, trust_score=0.0, risk_score=0.0)
    risk_scores = score_all_nodes(twin.graph)
    return schemas.NodeOut(
        id=node_id, type=data.get("type", "device"), label=data.get("label", node_id),
        trust_score=data.get("trust_score", 0.5), risk_score=risk_scores.get(node_id, 0.0),
        attributes={k: v for k, v in data.items() if k not in ("type", "label", "trust_score")},
    )
