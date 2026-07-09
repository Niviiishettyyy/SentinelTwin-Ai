from app.graph.twin import twin
from app.graph.scoring import score_all_nodes

def main():
    print("Nodes in twin:")
    print(list(twin.graph.nodes))

    risk_scores = score_all_nodes(twin.graph)
    print("\nRisk scores:")
    for node_id, score in risk_scores.items():
        print(f"{node_id}: {score:.2f}")

    sample_id = next(iter(twin.graph.nodes), None)
    if sample_id:
        data = twin.get_node(sample_id)
        neighbors = twin.neighbors(sample_id)
        print(f"\nSample node: {sample_id}")
        print("Metadata:", data)
        print("Neighbors:", neighbors)

    flagged = [(s, t, d) for s, t, d in twin.all_edges() if d.get("flagged")]
    print("\nFlagged edges:")
    for s, t, d in flagged:
        print(f"{s} -> {t}, data={d}")

if __name__ == "__main__":
    main()