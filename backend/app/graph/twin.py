"""
Digital Twin graph model (Section 8b / 9.2).
"""
import csv
import os
import random
import networkx as nx

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sample_flows.csv")


def _is_num(v) -> bool:
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        return False


class DigitalTwin:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.seed_from_csv(DATA_PATH)

    def seed_from_csv(self, path: str):
        if not os.path.exists(path):
            return
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self._ingest_flow(row)

    def _ingest_flow(self, row: dict):
        src, dst = row["src_ip"], row["dst_ip"]
        node_type_src = row.get("src_type", "device")
        node_type_dst = row.get("dst_type", "device")

        for node_id, ntype, criticality in [
            (src, node_type_src, row.get("src_criticality", "low")),
            (dst, node_type_dst, row.get("dst_criticality", "low")),
        ]:
            if node_id not in self.graph:
                inferred_exposure = "external" if ntype == "external" else "internal"
                self.graph.add_node(
                    node_id,
                    type=ntype,
                    label=node_id,
                    trust_score=round(random.uniform(0.55, 0.95), 2),
                    anomaly_score=0.0,
                    criticality=criticality,
                    exposure=inferred_exposure,
                )

        anomaly = float(row.get("anomaly_score", 0.0))
        try:
            from app.ml.predict import predict_anomaly_score
            numeric_features = {k: float(v) for k, v in row.items() if k not in
                                 ("src_ip", "dst_ip", "src_type", "dst_type", "protocol", "label") and _is_num(v)}
            if numeric_features:
                anomaly = predict_anomaly_score(numeric_features)
        except Exception as e:
            print("MODEL PREDICT FAILED:", repr(e))
        self.graph.nodes[dst]["anomaly_score"] = max(
            self.graph.nodes[dst]["anomaly_score"], anomaly
        )

        self.graph.add_edge(
            src, dst,
            type="connects_to",
            protocol=row.get("protocol", "tcp"),
            port=row.get("dst_port", ""),
            flagged=row.get("label", "benign") != "benign",
            weight=1.0 + anomaly * 3,
        )

    def all_nodes(self):
        return self.graph.nodes(data=True)

    def all_edges(self):
        return self.graph.edges(data=True)

    def get_node(self, node_id: str):
        if node_id not in self.graph:
            return None
        return self.graph.nodes[node_id]

    def neighbors(self, node_id: str):
        if node_id not in self.graph:
            return []
        return list(self.graph.successors(node_id))


twin = DigitalTwin()