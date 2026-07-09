import { useEffect, useMemo, useState, useCallback } from "react";
import ReactFlow, {
  Background, Controls, MiniMap, Node, Edge, Position,
} from "reactflow";
import "reactflow/dist/style.css";
import { fetchGraph, GraphOut, NodeOut } from "../api/client";

function riskColor(score: number) {
  if (score > 0.6) return "#F43F5E";
  if (score > 0.35) return "#F59E0B";
  return "#34D399";
}

export default function DigitalTwin() {
  const [graph, setGraph] = useState<GraphOut | null>(null);
  const [selected, setSelected] = useState<NodeOut | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchGraph().then(setGraph).catch(() => setError("Could not load the twin graph. Is the backend running and are you logged in?"));
  }, []);

  const { nodes, edges } = useMemo(() => {
    if (!graph) return { nodes: [] as Node[], edges: [] as Edge[] };
    const cols = 5;
    const nodes: Node[] = graph.nodes.map((n, i) => ({
      id: n.id,
      position: { x: (i % cols) * 220, y: Math.floor(i / cols) * 140 },
      data: { label: n.label, node: n },
      sourcePosition: Position.Right,
      targetPosition: Position.Left,
      style: {
        background: "#172136",
        border: `2px solid ${riskColor(n.risk_score)}`,
        borderRadius: 8,
        color: "#E6EAF2",
        fontSize: 11,
        fontFamily: "JetBrains Mono, monospace",
        padding: 8,
        width: 170,
      },
    }));
    const edges: Edge[] = graph.edges.map((e, i) => ({
      id: `e${i}-${e.source}-${e.target}`,
      source: e.source,
      target: e.target,
      animated: e.type === "connects_to",
      style: { stroke: "#1E2A44" },
    }));
    return { nodes, edges };
  }, [graph]);

  const onNodeClick = useCallback((_: unknown, node: Node) => {
    setSelected(node.data.node as NodeOut);
  }, []);

  return (
    <div>
      <header className="mb-6">
        <h1 className="text-xl font-semibold">Digital Twin</h1>
        <p className="text-sm text-muted mt-1">Interactive graph view of the organization. Click a node for detail.</p>
      </header>

      {error && <div className="card p-4 border-warning/40 text-warning text-sm mb-6">{error}</div>}

      <div className="flex gap-4">
        <div className="card flex-1 h-[560px]">
          {graph ? (
            <ReactFlow nodes={nodes} edges={edges} onNodeClick={onNodeClick} fitView>
              <Background color="#1E2A44" gap={16} />
              <Controls />
              <MiniMap
                nodeColor={(n) => riskColor((n.data.node as NodeOut).risk_score)}
                maskColor="rgba(11,18,32,0.8)"
                style={{ background: "#121A2B" }}
              />
            </ReactFlow>
          ) : (
            !error && <div className="p-6 text-sm text-muted">Loading graph...</div>
          )}
        </div>

        <aside className="w-72 shrink-0 card p-4 h-[560px] overflow-y-auto">
          <h2 className="text-sm font-semibold mb-3">Node Detail</h2>
          {!selected && <p className="text-sm text-muted">Select a node to see its trust score, connections, and risk context.</p>}
          {selected && (
            <div className="space-y-3 text-sm">
              <div>
                <p className="text-xs text-muted">ID</p>
                <p className="font-mono">{selected.id}</p>
              </div>
              <div>
                <p className="text-xs text-muted">Type</p>
                <p>{selected.type}</p>
              </div>
              <div>
                <p className="text-xs text-muted">Trust Score</p>
                <p className="font-mono">{selected.trust_score.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-xs text-muted">Risk Score</p>
                <span className={`pill ${selected.risk_score > 0.6 ? "pill-critical" : selected.risk_score > 0.35 ? "pill-warning" : "pill-success"}`}>
                  {selected.risk_score.toFixed(2)}
                </span>
              </div>
              <div>
                <p className="text-xs text-muted mb-1">Attributes</p>
                <pre className="text-xs font-mono bg-base rounded p-2 overflow-x-auto">
                  {JSON.stringify(selected.attributes, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}
