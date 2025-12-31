from pyvis.network import Network
import networkx as nx
import json

with open("data/skills.json") as f:
    skills = json.load(f)

G = nx.DiGraph()

def completion_to_color(p):
    if p < 30:
        return "#e74c3c"
    elif p < 70:
        return "#f1c40f"
    else:
        return "#2ecc71"

# Add nodes and edges
completion_values = []
for skill, data in skills.items():
    completion_values.append(data.get("completion", 0))
    
    # Rich HTML tooltip
    mandatory_resources = "".join(f'<li><a href="#">{r}</a></li>' for r in data['mandatory_resources']) if data['mandatory_resources'] else "<li>None</li>"
    optional_resources = "".join(f'<li><a href="#">{r}</a></li>' for r in data['optional_resources']) if data['optional_resources'] else "<li>None</li>"
    tooltip = f"""
    <h3>{skill}</h3>
    <p>Completion: {data['completion']}%</p>
    <b>Mandatory Resources:</b>
    <ul>{mandatory_resources}</ul>
    <b>Optional Resources:</b>
    <ul>{optional_resources}</ul>
    """

    G.add_node(
        skill,
        label=skill,
        title=tooltip,
        color=completion_to_color(data["completion"]),
        shape="dot",
        size=15
    )

    for dep in data["depends_on"]:
        G.add_edge(dep, skill)

# Compute global completion
global_completion = sum(completion_values) / len(completion_values)

# Initialize PyVis Network
net = Network(
    height="100vh",          # full page height
    width="100%",            # full page width
    bgcolor="#1e1e1e",       # dark background
    font_color="white",
    directed=True,
    cdn_resources="in_line",
)

# Load the NetworkX graph
net.from_nx(G)

# Physics layout (force-directed)
net.force_atlas_2based()
# Generate full HTML as string
html_str = net.generate_html(notebook=False)

# Global completion badge HTML
global_html = f"""
<div style="
    position: absolute;
    top: 10px;
    right: 10px;
    padding: 10px 15px;
    background-color: #2c2c2c;
    color: white;
    font-size: 16px;
    font-weight: bold;
    border-radius: 8px;
    z-index: 9999;
">
Global Completion: {global_completion:.2f}%
</div>
"""

# Info panel HTML (clickable node info)
info_panel_html = """
<div id="info-panel" style="
       position:absolute;
       bottom:0;
       left:0;
       width:100%;
       max-height:250px;
       overflow:auto;
       background:#2c2c2c;
       color:white;
       padding:10px;
       font-family:sans-serif;
       border-top: 2px solid #444;
       z-index: 9999;
">
Click a node to see details here
</div>
"""

# Write final HTML
with open("docs/index.html", "w") as f:
    f.write(f"""
<html>
  <head>
    <title>Skill Graph</title>
    <style>
      html, body {{
        margin: 0;
        padding: 0;
        width: 100%;
        height: 100%;
        background: #1e1e1e;
        overflow: hidden;
        display: flex;
        justify-content: center;
        align-items: center;
      }}
      #mynetwork {{
        width: 100%;
        height: 100%;
      }}
      a {{
        color: #1abc9c;
      }}
    </style>
  </head>
  <body>
    {global_html}
    {info_panel_html}
    {html_str}
    <script type="text/javascript">
      // Auto-fit network
      network.fit({{animation:{{duration:1000}}}});
      
      // Update info panel on node click
      network.on("click", function(params) {{
          if(params.nodes.length > 0){{
              var nodeId = params.nodes[0];
              var node = network.body.nodes[nodeId];
              document.getElementById("info-panel").innerHTML = node.options.title;
              document.getElementById("info-panel").style.bottom = "0";  // slide in if hidden
          }}
      }});

      // Update info panel on node click
        document.getElementById("info-panel").ondblclick = function() {{
            this.style.bottom = "-250px"; // slide off-screen
        }};
    </script>
  </body>
</html>
""")

print("Skill graph generated: docs/index.html")