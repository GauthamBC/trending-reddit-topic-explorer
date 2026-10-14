"""Self-contained interactive SVG topic network for Streamlit.

No external JS libraries are required. The layout is computed server-side and
rendered as an inline SVG, which makes it more reliable inside Streamlit's
components iframe than CDN-dependent graph packages.
"""
from __future__ import annotations

import html
import json
import math
from collections import defaultdict

import networkx as nx


WIDTH = 980
HEIGHT = 600
PADDING = 70


def _json(value):
    return json.dumps(value, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def _clamp(value, low, high):
    return max(low, min(high, value))


def _scale_sizes(values, min_size, max_size):
    if not values:
        return {}
    lo = min(values.values())
    hi = max(values.values())
    out = {}
    for key, val in values.items():
        if hi == lo:
            out[key] = round((min_size + max_size) / 2, 2)
        else:
            t = (val - lo) / (hi - lo)
            out[key] = round(min_size + (max_size - min_size) * t, 2)
    return out


def _normalise_positions(pos):
    xs = [xy[0] for xy in pos.values()]
    ys = [xy[1] for xy in pos.values()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = max(max_x - min_x, 1e-6)
    span_y = max(max_y - min_y, 1e-6)

    output = {}
    for node_id, (x, y) in pos.items():
        nxv = PADDING + ((x - min_x) / span_x) * (WIDTH - 2 * PADDING)
        nyv = PADDING + ((y - min_y) / span_y) * (HEIGHT - 2 * PADDING)
        output[node_id] = (round(nxv, 2), round(nyv, 2))
    return output


def build_graph(posts, topics, dark=True):
    grouped = defaultdict(list)
    for p in posts:
        grouped[p["subreddit"]].append(p)

    ranked_subs = sorted(
        grouped,
        key=lambda sub: (sum(p["heat"] for p in grouped[sub]), len(grouped[sub])),
        reverse=True,
    )[:20]
    topic_slice = topics[:20]

    if not ranked_subs or not topic_slice:
        return "<html><body style='margin:0;background:#0f1726;color:#e8eef8;font-family:system-ui'><div style='padding:24px'>Not enough network data to render.</div></body></html>"

    G = nx.Graph()
    details = {}
    node_labels = {}
    node_kind = {}
    node_signal = {}

    # Subreddit nodes
    for sub in ranked_subs:
        node_id = f"s:{sub.lower()}"
        entries = sorted(grouped[sub], key=lambda p: p["heat"], reverse=True)
        signal = sum(p["heat"] for p in entries)
        G.add_node(node_id)
        node_labels[node_id] = f"r/{sub}"
        node_kind[node_id] = "subreddit"
        node_signal[node_id] = signal
        details[node_id] = {
            "name": f"r/{sub}",
            "type": "Subreddit",
            "description": f"{len(entries)} relevant posts · attention {round(signal)}",
            "links": [
                {
                    "title": p["title"],
                    "url": p["url"],
                    "subreddit": p["subreddit"],
                    "heat": p["heat"],
                }
                for p in entries[:10]
            ],
        }

    # Topic nodes and edges
    for t in topic_slice:
        topic_id = f"t:{t['term']}"
        topic_signal = t["attention"]
        G.add_node(topic_id)
        node_labels[topic_id] = t["term"].title()
        node_kind[topic_id] = "topic"
        node_signal[topic_id] = topic_signal
        details[topic_id] = {
            "name": t["term"].title(),
            "type": "Topic",
            "description": f"{t['posts']} posts · {t['communities']} communities · attention {round(t['attention'])}",
            "links": t["links"],
        }
        for sub, count in t["subreddits"].items():
            sid = f"s:{sub.lower()}"
            if sid in G.nodes:
                G.add_edge(topic_id, sid, weight=count)

    # Keep only connected nodes.
    isolates = [n for n in G.nodes if G.degree(n) == 0]
    if isolates:
        G.remove_nodes_from(isolates)
        for n in isolates:
            details.pop(n, None)
            node_labels.pop(n, None)
            node_kind.pop(n, None)
            node_signal.pop(n, None)

    if not G.nodes:
        return "<html><body style='margin:0;background:#0f1726;color:#e8eef8;font-family:system-ui'><div style='padding:24px'>Not enough connected topics to render.</div></body></html>"

    # Stronger edges pull nodes together.
    pos = nx.spring_layout(G, seed=14, weight="weight", k=1.8 / math.sqrt(max(len(G.nodes), 1)), iterations=300)
    pos = _normalise_positions(pos)

    size_map = _scale_sizes(node_signal, 16, 44)
    edge_weights = [G.edges[e].get("weight", 1) for e in G.edges]
    edge_lo = min(edge_weights) if edge_weights else 1
    edge_hi = max(edge_weights) if edge_weights else 1

    nodes = []
    for node_id in G.nodes:
        x, y = pos[node_id]
        radius = size_map.get(node_id, 22)
        kind = node_kind[node_id]
        nodes.append(
            {
                "id": node_id,
                "x": x,
                "y": y,
                "r": radius,
                "label": node_labels[node_id],
                "kind": kind,
                "signal": round(node_signal[node_id], 1),
            }
        )

    edges = []
    for source, target, attrs in G.edges(data=True):
        weight = attrs.get("weight", 1)
        if edge_hi == edge_lo:
            stroke = 2.4
            alpha = 0.42
        else:
            t = (weight - edge_lo) / (edge_hi - edge_lo)
            stroke = 1.3 + 3.8 * t
            alpha = 0.22 + 0.38 * t
        edges.append(
            {
                "source": source,
                "target": target,
                "weight": weight,
                "stroke": round(stroke, 2),
                "alpha": round(alpha, 3),
            }
        )

    colors = {
        "bg": "#08111f",
        "panel": "#101a2c",
        "panel2": "#0d1626",
        "line": "#24354f",
        "line_soft": "#1a2940",
        "text": "#edf4ff",
        "muted": "#94a8c6",
        "sub_fill": "#4ea1ff",
        "sub_stroke": "#a4d1ff",
        "topic_fill": "#ff5f9b",
        "topic_stroke": "#ffc1d8",
        "edge": "#5f7898",
        "chip": "rgba(9,17,31,.75)",
    }

    # Neighbour map for highlighting.
    neighbours = {node_id: sorted(G.neighbors(node_id)) for node_id in G.nodes}

    return f"""<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <style>
    * {{ box-sizing:border-box; }}
    html, body {{ margin:0; padding:0; background:{colors['bg']}; color:{colors['text']}; font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; }}
    .wrap {{ display:grid; grid-template-columns:minmax(0,1fr) 320px; height:600px; border:1px solid {colors['line']}; border-radius:16px; overflow:hidden; background:linear-gradient(180deg, #0b1424 0%, #08111f 100%); }}
    .canvas {{ position:relative; min-width:0; background:
      radial-gradient(circle at top left, rgba(78,161,255,.12), transparent 34%),
      radial-gradient(circle at bottom right, rgba(255,95,155,.10), transparent 30%),
      linear-gradient(180deg, #091424 0%, #08111f 100%); }}
    .detail {{ background:linear-gradient(180deg, {colors['panel']} 0%, {colors['panel2']} 100%); border-left:1px solid {colors['line']}; overflow:auto; padding:18px 18px 20px; }}
    .legend {{ position:absolute; top:14px; left:14px; display:flex; gap:8px; flex-wrap:wrap; z-index:2; }}
    .legend-chip {{ display:inline-flex; align-items:center; gap:7px; padding:7px 10px; border:1px solid {colors['line']}; border-radius:999px; background:rgba(10,18,32,.78); font-size:11px; color:{colors['text']}; }}
    .legend-dot {{ width:10px; height:10px; border-radius:50%; display:inline-block; }}
    .helper {{ position:absolute; right:14px; top:14px; z-index:2; padding:8px 10px; border-radius:10px; font-size:11px; color:{colors['muted']}; background:rgba(10,18,32,.68); border:1px solid {colors['line']}; }}
    .label {{ font-size:11px; font-weight:800; letter-spacing:1px; text-transform:uppercase; color:#70beff; margin-bottom:10px; }}
    h3 {{ margin:0 0 8px; font-size:20px; line-height:1.2; }}
    p {{ margin:0 0 12px; font-size:13px; line-height:1.55; color:{colors['muted']}; }}
    .entry {{ padding:12px 0; border-top:1px solid {colors['line_soft']}; }}
    .entry a {{ color:{colors['text']}; text-decoration:none; font-size:13px; line-height:1.45; font-weight:600; }}
    .entry a:hover {{ color:#8cc7ff; }}
    .meta {{ margin-top:6px; font-size:11px; color:{colors['muted']}; }}
    svg {{ width:100%; height:100%; display:block; cursor:grab; }}
    svg.dragging {{ cursor:grabbing; }}
    .edge {{ stroke:{colors['edge']}; stroke-linecap:round; }}
    .node-circle {{ filter: drop-shadow(0 0 12px rgba(0,0,0,.18)); }}
    .node-subreddit {{ fill:{colors['sub_fill']}; stroke:{colors['sub_stroke']}; }}
    .node-topic {{ fill:{colors['topic_fill']}; stroke:{colors['topic_stroke']}; }}
    .node-label {{ fill:{colors['text']}; font-size:12px; font-weight:700; pointer-events:none; dominant-baseline:middle; text-anchor:middle; }}
    .node-chip {{ fill:{colors['chip']}; stroke:{colors['line']}; stroke-width:1; opacity:.92; }}
    .bubble-value {{ fill:{colors['muted']}; font-size:10px; font-weight:700; pointer-events:none; text-anchor:middle; dominant-baseline:middle; }}
    .faded {{ opacity:.14; }}
    .selected .node-circle {{ stroke-width:2.8 !important; }}
    .selected .node-chip {{ opacity:1; }}
    @media (max-width: 860px) {{
      .wrap {{ grid-template-columns:1fr; grid-template-rows:390px 1fr; height:780px; }}
      .detail {{ border-left:none; border-top:1px solid {colors['line']}; }}
    }}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <div class=\"canvas\">
      <div class=\"legend\">
        <div class=\"legend-chip\"><span class=\"legend-dot\" style=\"background:{colors['sub_fill']}; box-shadow:0 0 0 1px {colors['sub_stroke']} inset\"></span> Subreddit</div>
        <div class=\"legend-chip\"><span class=\"legend-dot\" style=\"background:{colors['topic_fill']}; box-shadow:0 0 0 1px {colors['topic_stroke']} inset\"></span> Topic</div>
      </div>
      <div class=\"helper\">Drag to pan · Scroll to zoom · Click a node</div>
      <svg id=\"networkSvg\" viewBox=\"0 0 {WIDTH} {HEIGHT}\" aria-label=\"Reddit topic network\">
        <defs>
          <filter id=\"softGlow\" x=\"-30%\" y=\"-30%\" width=\"160%\" height=\"160%\">
            <feDropShadow dx=\"0\" dy=\"0\" stdDeviation=\"5\" flood-color=\"rgba(0,0,0,.35)\"/>
          </filter>
        </defs>
        <g id=\"viewport\">
          <g id=\"edgeLayer\"></g>
          <g id=\"nodeLayer\"></g>
        </g>
      </svg>
    </div>
    <aside class=\"detail\" id=\"detailPanel\">
      <div class=\"label\">Interactive network</div>
      <h3>Explore the conversation</h3>
      <p>Bubble size reflects the amount of discussion captured in this scan. Topic bubbles aggregate repeated phrases from post titles; subreddit bubbles represent communities with relevant posts.</p>
      <p>Select a node to inspect the source posts on the right.</p>
    </aside>
  </div>

<script>
const nodes = {_json(nodes)};
const edges = {_json(edges)};
const details = {_json(details)};
const neighbours = {_json(neighbours)};
const svg = document.getElementById('networkSvg');
const viewport = document.getElementById('viewport');
const edgeLayer = document.getElementById('edgeLayer');
const nodeLayer = document.getElementById('nodeLayer');
const panel = document.getElementById('detailPanel');
const NS = 'http://www.w3.org/2000/svg';

const nodeMap = Object.fromEntries(nodes.map(n => [n.id, n]));
const nodeElements = new Map();
const edgeElements = [];

function el(name, attrs = {{}}) {{
  const e = document.createElementNS(NS, name);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  return e;
}}

function nodeColors(kind) {{
  if (kind === 'topic') return {{fill:'{colors['topic_fill']}', stroke:'{colors['topic_stroke']}'}};
  return {{fill:'{colors['sub_fill']}', stroke:'{colors['sub_stroke']}'}};
}}

function draw() {{
  edges.forEach(edge => {{
    const a = nodeMap[edge.source], b = nodeMap[edge.target];
    if (!a || !b) return;
    const line = el('line', {{
      x1: a.x, y1: a.y, x2: b.x, y2: b.y,
      'stroke-width': edge.stroke,
      'stroke-opacity': edge.alpha,
      class: 'edge',
      'data-source': edge.source,
      'data-target': edge.target
    }});
    edgeLayer.appendChild(line);
    edgeElements.push({{ edge, element: line }});
  }});

  nodes.forEach(node => {{
    const g = el('g', {{ class: 'node-group', 'data-id': node.id, tabindex: '0', role: 'button' }});

    const circle = el('circle', {{
      cx: node.x, cy: node.y, r: node.r,
      class: `node-circle ${{node.kind === 'topic' ? 'node-topic' : 'node-subreddit'}}`,
      'stroke-width': 2,
      filter: 'url(#softGlow)'
    }});
    g.appendChild(circle);

    const metric = el('text', {{ x: node.x, y: node.y + 0.5, class: 'bubble-value' }});
    metric.textContent = Math.round(node.signal);
    g.appendChild(metric);

    const labelText = node.label;
    const chipWidth = Math.max(64, Math.min(170, labelText.length * 7.1 + 18));
    const chipHeight = 24;
    const chipY = node.y + node.r + 10;
    const chip = el('rect', {{
      x: node.x - chipWidth / 2,
      y: chipY,
      rx: 12, ry: 12,
      width: chipWidth,
      height: chipHeight,
      class: 'node-chip'
    }});
    g.appendChild(chip);

    const label = el('text', {{ x: node.x, y: chipY + chipHeight / 2 + 0.5, class: 'node-label' }});
    label.textContent = labelText;
    g.appendChild(label);

    g.addEventListener('click', (event) => {{ event.stopPropagation(); selectNode(node.id); }});
    g.addEventListener('keydown', (event) => {{ if (event.key === 'Enter' || event.key === ' ') {{ event.preventDefault(); selectNode(node.id); }} }});
    nodeLayer.appendChild(g);
    nodeElements.set(node.id, g);
  }});
}}

function renderDetail(id) {{
  const d = details[id];
  if (!d) return;
  panel.replaceChildren();
  const label = document.createElement('div');
  label.className = 'label';
  label.textContent = d.type;
  panel.appendChild(label);
  const h = document.createElement('h3');
  h.textContent = d.name;
  panel.appendChild(h);
  const p = document.createElement('p');
  p.textContent = d.description;
  panel.appendChild(p);
  (d.links || []).forEach(item => {{
    const row = document.createElement('div');
    row.className = 'entry';
    const a = document.createElement('a');
    a.textContent = item.title;
    if (item.url && /^https:\/\/www\.reddit\.com\//.test(item.url)) {{
      a.href = item.url;
      a.target = '_blank';
      a.rel = 'noopener noreferrer nofollow';
    }}
    row.appendChild(a);
    const meta = document.createElement('div');
    meta.className = 'meta';
    meta.textContent = 'r/' + item.subreddit + ' · Attention ' + Math.round(item.heat || 0);
    row.appendChild(meta);
    panel.appendChild(row);
  }});
}}

let selectedId = null;
function selectNode(id) {{
  selectedId = id;
  const keep = new Set([id, ...(neighbours[id] || [])]);
  for (const [nodeId, element] of nodeElements.entries()) {{
    element.classList.toggle('selected', nodeId === id);
    element.classList.toggle('faded', !keep.has(nodeId));
  }}
  edgeElements.forEach((item) => {{
    const edge = item.edge;
    const element = item.element;
    const connected = edge.source === id || edge.target === id;
    element.classList.toggle('faded', !connected);
    element.setAttribute('stroke-opacity', connected ? Math.min(0.92, edge.alpha + 0.28) : 0.08);
  }});
  renderDetail(id);
}}

function clearSelection() {{
  selectedId = null;
  for (const element of nodeElements.values()) {{
    element.classList.remove('selected', 'faded');
  }}
  edgeElements.forEach((item) => {{
    const edge = item.edge;
    const element = item.element;
    element.classList.remove('faded');
    element.setAttribute('stroke-opacity', edge.alpha);
  }});
}}

// Basic pan and zoom.
let scale = 1;
let panX = 0;
let panY = 0;
let dragging = false;
let start = null;

function applyTransform() {{
  viewport.setAttribute('transform', `translate(${{panX}} ${{panY}}) scale(${{scale}})`);
}}

svg.addEventListener('wheel', (event) => {{
  event.preventDefault();
  const direction = event.deltaY > 0 ? 0.92 : 1.08;
  scale = Math.max(0.65, Math.min(2.8, scale * direction));
  applyTransform();
}}, {{ passive: false }});

svg.addEventListener('mousedown', (event) => {{
  if (event.target.closest('.node-group')) return;
  dragging = true;
  start = {{ x: event.clientX - panX, y: event.clientY - panY }};
  svg.classList.add('dragging');
}});
window.addEventListener('mousemove', (event) => {{
  if (!dragging) return;
  panX = event.clientX - start.x;
  panY = event.clientY - start.y;
  applyTransform();
}});
window.addEventListener('mouseup', () => {{
  dragging = false;
  svg.classList.remove('dragging');
}});
svg.addEventListener('click', (event) => {{
  if (!event.target.closest('.node-group')) clearSelection();
}});

// Touch panning.
svg.addEventListener('touchstart', (event) => {{
  if (event.touches.length !== 1 || event.target.closest('.node-group')) return;
  const t = event.touches[0];
  dragging = true;
  start = {{ x: t.clientX - panX, y: t.clientY - panY }};
}}, {{ passive: true }});
svg.addEventListener('touchmove', (event) => {{
  if (!dragging || event.touches.length !== 1) return;
  const t = event.touches[0];
  panX = t.clientX - start.x;
  panY = t.clientY - start.y;
  applyTransform();
}}, {{ passive: true }});
svg.addEventListener('touchend', () => {{ dragging = false; }});

draw();
if (nodes.length) selectNode(nodes[0].id);
</script>
</body>
</html>"""
