"""Extracts Cloud Spanner Property Graph data and generates an interactive HTML network visualization."""

from __future__ import annotations

import json
from pathlib import Path
from src.graph.client import GraphClient

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Enterprise Agents Architectural Guidelines — Cloud Spanner Graph Visualization</title>
  <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
  <style>
    :root {
      --bg: #0f1117;
      --card-bg: rgba(22, 27, 34, 0.85);
      --border: #30363d;
      --text: #e6edf3;
      --text-muted: #8b949e;
      --accent: #58a6ff;
      --guideline: #1f6feb;
      --pattern: #a371f7;
      --antipattern: #f85149;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background-color: var(--bg);
      color: var(--text);
      display: flex;
      height: 100vh;
      overflow: hidden;
    }
    #header {
      position: absolute;
      top: 16px;
      left: 16px;
      z-index: 10;
      background: var(--card-bg);
      backdrop-filter: blur(12px);
      padding: 14px 20px;
      border-radius: 12px;
      border: 1px solid var(--border);
      box-shadow: 0 8px 24px rgba(0,0,0,0.4);
      max-width: 480px;
    }
    #header h1 {
      font-size: 1.15rem;
      font-weight: 600;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    #header p {
      font-size: 0.82rem;
      color: var(--text-muted);
      margin-top: 4px;
    }
    .stats-bar {
      display: flex;
      gap: 12px;
      margin-top: 10px;
      font-size: 0.78rem;
    }
    .stat-pill {
      background: rgba(255,255,255,0.06);
      padding: 3px 8px;
      border-radius: 6px;
      border: 1px solid rgba(255,255,255,0.08);
    }
    .stat-pill b { color: #fff; }
    #controls {
      position: absolute;
      top: 16px;
      right: 16px;
      z-index: 10;
      background: var(--card-bg);
      backdrop-filter: blur(12px);
      padding: 14px 18px;
      border-radius: 12px;
      border: 1px solid var(--border);
      box-shadow: 0 8px 24px rgba(0,0,0,0.4);
      display: flex;
      flex-direction: column;
      gap: 10px;
      width: 320px;
    }
    .search-box {
      width: 100%;
      padding: 8px 12px;
      background: #0d1117;
      border: 1px solid var(--border);
      border-radius: 8px;
      color: #fff;
      font-size: 0.85rem;
      outline: none;
    }
    .search-box:focus { border-color: var(--accent); }
    .filter-group {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }
    .filter-btn {
      background: rgba(255,255,255,0.08);
      border: 1px solid transparent;
      color: var(--text);
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 0.76rem;
      cursor: pointer;
      transition: all 0.2s;
    }
    .filter-btn:hover { background: rgba(255,255,255,0.15); }
    .filter-btn.active {
      background: var(--accent);
      color: #0d1117;
      font-weight: 600;
    }
    #network {
      flex: 1;
      height: 100%;
    }
    #sidebar {
      width: 380px;
      background: var(--card-bg);
      backdrop-filter: blur(12px);
      border-left: 1px solid var(--border);
      height: 100%;
      overflow-y: auto;
      padding: 24px;
      display: none;
      flex-direction: column;
      box-shadow: -4px 0 20px rgba(0,0,0,0.3);
      z-index: 20;
    }
    #sidebar.open { display: flex; }
    .sidebar-close {
      align-self: flex-end;
      background: none;
      border: none;
      color: var(--text-muted);
      font-size: 1.2rem;
      cursor: pointer;
      margin-bottom: 8px;
    }
    .sidebar-close:hover { color: #fff; }
    .node-badge {
      display: inline-block;
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 0.72rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 8px;
      width: fit-content;
    }
    .badge-guideline { background: rgba(31, 111, 235, 0.25); color: #58a6ff; border: 1px solid rgba(88, 166, 255, 0.4); }
    .badge-pattern { background: rgba(163, 113, 247, 0.25); color: #d2a8ff; border: 1px solid rgba(210, 168, 255, 0.4); }
    .badge-antipattern { background: rgba(248, 81, 73, 0.25); color: #ff7b72; border: 1px solid rgba(255, 123, 114, 0.4); }
    .node-title {
      font-size: 1.1rem;
      font-weight: 600;
      margin-bottom: 12px;
      color: #fff;
      line-height: 1.35;
    }
    .node-prop {
      font-size: 0.82rem;
      color: var(--text-muted);
      margin-bottom: 14px;
      line-height: 1.5;
    }
    .node-prop strong { color: var(--text); }
    .connected-list {
      margin-top: 14px;
      list-style: none;
    }
    .connected-item {
      padding: 8px 10px;
      background: rgba(255,255,255,0.03);
      border: 1px solid var(--border);
      border-radius: 6px;
      margin-bottom: 6px;
      font-size: 0.8rem;
      cursor: pointer;
      transition: background 0.15s;
    }
    .connected-item:hover { background: rgba(88, 166, 255, 0.1); border-color: var(--accent); }
    .legend {
      display: flex;
      gap: 14px;
      align-items: center;
      margin-top: 6px;
      font-size: 0.78rem;
    }
    .legend-item { display: flex; align-items: center; gap: 6px; }
    .dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
  </style>
</head>
<body>
  <div id="header">
    <h1>🌐 Cloud Spanner Property Graph</h1>
    <p>Database: <code>arch_guidelines_graph</code> | Graph: <code>ArchGuidelinesGraph</code></p>
    <div class="stats-bar">
      <div class="stat-pill">Guidelines: <b id="stat-guidelines">0</b></div>
      <div class="stat-pill">Patterns: <b id="stat-patterns">0</b></div>
      <div class="stat-pill">Edges: <b id="stat-edges">0</b></div>
    </div>
    <div class="legend">
      <div class="legend-item"><span class="dot" style="background: var(--guideline);"></span> Guideline</div>
      <div class="legend-item"><span class="dot" style="background: var(--pattern);"></span> Pattern</div>
      <div class="legend-item"><span class="dot" style="background: var(--antipattern);"></span> Antipattern</div>
    </div>
  </div>

  <div id="controls">
    <input type="text" id="search-input" class="search-box" placeholder="Search guidelines or patterns..." />
    <div class="filter-group">
      <button class="filter-btn active" onclick="filterType('ALL')">All</button>
      <button class="filter-btn" onclick="filterType('Guideline')">Guidelines</button>
      <button class="filter-btn" onclick="filterType('Pattern')">Patterns</button>
    </div>
    <button class="filter-btn" id="physics-toggle" onclick="togglePhysics()">Pause Physics</button>
  </div>

  <div id="network"></div>

  <div id="sidebar">
    <button class="sidebar-close" onclick="closeSidebar()">&times;</button>
    <div id="sidebar-content"></div>
  </div>

  <script>
    const graphData = GRAPH_DATA_PLACEHOLDER;

    document.getElementById("stat-guidelines").innerText = graphData.guidelines_count;
    document.getElementById("stat-patterns").innerText = graphData.patterns_count;
    document.getElementById("stat-edges").innerText = graphData.edges.length;

    const container = document.getElementById("network");
    const nodes = new vis.DataSet(graphData.nodes);
    const edges = new vis.DataSet(graphData.edges);

    const options = {
      nodes: {
        font: { color: "#e6edf3", size: 13, face: "-apple-system, sans-serif" },
        borderWidth: 2,
        shadow: { enabled: true, color: "rgba(0,0,0,0.5)", size: 6 }
      },
      edges: {
        color: { color: "#484f58", highlight: "#58a6ff", hover: "#8b949e" },
        width: 1.5,
        smooth: { type: "continuous" },
        arrows: { to: { enabled: true, scaleFactor: 0.6 } }
      },
      physics: {
        forceAtlas2Based: {
          gravitationalConstant: -70,
          centralGravity: 0.015,
          springLength: 90,
          springConstant: 0.08,
          damping: 0.5
        },
        solver: "forceAtlas2Based",
        stabilization: { iterations: 150 }
      },
      interaction: {
        hover: true,
        tooltipDelay: 150
      }
    };

    const network = new vis.Network(container, { nodes, edges }, options);
    let physicsActive = true;

    function togglePhysics() {
      physicsActive = !physicsActive;
      network.setOptions({ physics: { enabled: physicsActive } });
      document.getElementById("physics-toggle").innerText = physicsActive ? "Pause Physics" : "Resume Physics";
    }

    // Node selection & detail sidebar
    network.on("selectNode", function(params) {
      if (params.nodes.length > 0) {
        const nodeId = params.nodes[0];
        const node = nodes.get(nodeId);
        showSidebar(node);
      }
    });

    network.on("deselectNode", function() {
      closeSidebar();
    });

    function showSidebar(node) {
      const sidebar = document.getElementById("sidebar");
      const content = document.getElementById("sidebar-content");
      
      const badgeClass = node.group === "Guideline" ? "badge-guideline" : (node.group === "Pattern" ? "badge-pattern" : "badge-antipattern");
      
      // Find connected nodes
      const connectedNodeIds = network.getConnectedNodes(node.id);
      const connectedNodes = nodes.get(connectedNodeIds);

      let connectedHtml = "";
      if (connectedNodes.length > 0) {
        connectedHtml = `<p style="margin-top:14px; font-weight:600; font-size:0.85rem;">Connected Nodes (${connectedNodes.length}):</p><ul class="connected-list">`;
        connectedNodes.forEach(cn => {
          connectedHtml += `<li class="connected-item" onclick="focusNode('${cn.id}')"><b>[${cn.group}]</b> ${cn.label}</li>`;
        });
        connectedHtml += "</ul>";
      }

      content.innerHTML = `
        <span class="node-badge ${badgeClass}">${node.group}</span>
        <h2 class="node-title">${node.title_full || node.label}</h2>
        <div class="node-prop"><strong>Identifier:</strong> <code>${node.id}</code></div>
        <div class="node-prop"><strong>Category:</strong> <code>#${node.category || "general"}</code></div>
        <div class="node-prop" style="margin-top:10px;">
          <strong>Summary / Description:</strong>
          <p style="margin-top:6px; color:#c9d1d9;">${node.description || node.summary || "No description available."}</p>
        </div>
        ${connectedHtml}
      `;
      sidebar.classList.add("open");
    }

    function closeSidebar() {
      document.getElementById("sidebar").classList.remove("open");
    }

    function focusNode(nodeId) {
      network.focus(nodeId, { scale: 1.2, animation: { duration: 800, easingFunction: "easeInOutQuad" } });
      network.selectNodes([nodeId]);
      const node = nodes.get(nodeId);
      showSidebar(node);
    }

    // Search functionality
    document.getElementById("search-input").addEventListener("input", function(e) {
      const val = e.target.value.toLowerCase().trim();
      if (!val) {
        nodes.update(graphData.nodes.map(n => ({ id: n.id, hidden: false })));
        return;
      }

      const matching = graphData.nodes.filter(n => 
        (n.label && n.label.toLowerCase().includes(val)) ||
        (n.id && n.id.toLowerCase().includes(val)) ||
        (n.category && n.category.toLowerCase().includes(val))
      );

      if (matching.length > 0) {
        focusNode(matching[0].id);
      }
    });

    // Filtering by type
    function filterType(type) {
      document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
      event.target.classList.add("active");

      if (type === "ALL") {
        nodes.update(graphData.nodes.map(n => ({ id: n.id, hidden: false })));
      } else {
        nodes.update(graphData.nodes.map(n => ({ id: n.id, hidden: n.group !== type })));
      }
    }
  </script>
</body>
</html>
"""


def export_graph() -> Path:
    """Query Cloud Spanner Graph and generate interactive visualization HTML."""
    print("Connecting to Cloud Spanner Graph...")
    client = GraphClient(use_mock=False)
    db = client._get_spanner_db()
    if db is None:
        raise RuntimeError("Could not connect to Cloud Spanner database.")

    nodes = []
    edges = []
    guideline_count = 0
    pattern_count = 0
    antipattern_count = 0

    with db.snapshot(multi_use=True) as s:
        print("Extracting Guideline nodes...")
        g_rows = list(s.execute_sql(
            "GRAPH ArchGuidelinesGraph MATCH (g:Guideline) RETURN g.guideline_id, g.title, g.category, g.summary, g.source_url;"
        ))
        for r in g_rows:
            gid, title, cat, summary, url = r[0], r[1], r[2], r[3], r[4]
            clean_title = title.replace(" - Document Section", "").replace(" - See https://", "")
            if len(clean_title) > 35:
                clean_title = clean_title[:32] + "..."
            nodes.append({
                "id": gid,
                "label": clean_title,
                "title_full": title,
                "group": "Guideline",
                "category": cat,
                "summary": summary,
                "color": {"background": "#1f6feb", "border": "#58a6ff"},
                "size": 22,
                "shape": "dot",
            })
            guideline_count += 1

        print("Extracting Pattern nodes...")
        p_rows = list(s.execute_sql(
            "GRAPH ArchGuidelinesGraph MATCH (p:Pattern) RETURN p.pattern_id, p.name, p.category, p.description;"
        ))
        for r in p_rows:
            pid, name, cat, desc = r[0], r[1], r[2], r[3]
            nodes.append({
                "id": pid,
                "label": name,
                "title_full": name,
                "group": "Pattern",
                "category": cat,
                "description": desc,
                "color": {"background": "#8957e5", "border": "#d2a8ff"},
                "size": 14,
                "shape": "dot",
            })
            pattern_count += 1

        print("Extracting Antipattern nodes...")
        a_rows = list(s.execute_sql(
            "GRAPH ArchGuidelinesGraph MATCH (a:Antipattern) RETURN a.antipattern_id, a.name, a.hazard, a.remedy;"
        ))
        for r in a_rows:
            aid, name, hazard, remedy = r[0], r[1], r[2], r[3]
            nodes.append({
                "id": aid,
                "label": name,
                "title_full": name,
                "group": "Antipattern",
                "category": "hazard",
                "description": f"Hazard: {hazard}\nRemedy: {remedy}",
                "color": {"background": "#da3633", "border": "#ff7b72"},
                "size": 18,
                "shape": "triangle",
            })
            antipattern_count += 1

        print("Extracting IMPLEMENTS relationships...")
        e_rows = list(s.execute_sql(
            "GRAPH ArchGuidelinesGraph MATCH (g:Guideline)-[r:IMPLEMENTS]->(p:Pattern) RETURN g.guideline_id, p.pattern_id;"
        ))
        for r in e_rows:
            edges.append({
                "from": r[0],
                "to": r[1],
                "arrows": "to",
                "color": {"color": "#30363d", "highlight": "#58a6ff"},
            })

    graph_payload = {
        "guidelines_count": guideline_count,
        "patterns_count": pattern_count,
        "antipatterns_count": antipattern_count,
        "nodes": nodes,
        "edges": edges,
    }

    out_file = Path("visualizations/spanner_knowledge_graph.html")
    out_file.parent.mkdir(parents=True, exist_ok=True)

    rendered_html = HTML_TEMPLATE.replace(
        "GRAPH_DATA_PLACEHOLDER", json.dumps(graph_payload, indent=2)
    )
    out_file.write_text(rendered_html, encoding="utf-8")
    print(f"\n✓ Graph exported successfully to: {out_file.resolve()}")
    return out_file.resolve()


if __name__ == "__main__":
    export_graph()
