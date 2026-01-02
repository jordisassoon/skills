from pyvis.network import Network
import networkx as nx
import json
from matplotlib import colormaps as cmaps
import matplotlib.colors as mcolors

with open("data/skills.json") as f:
    skills = json.load(f)

G = nx.DiGraph()

# Choose a colormap: "RdYlGn" goes Red → Yellow → Green
# Define vibrant colors
vibrant_colors = ["#ff0000", "#ffff00", "#00ff00"]  # Red → Yellow → Green

# Create a LinearSegmentedColormap
cmap = mcolors.LinearSegmentedColormap.from_list("VibrantRdYlGn", vibrant_colors)

def completion_to_color(p):
    """
    p: completion 0-100
    returns: HEX color
    """
    norm_p = p / 100  # normalize 0-1
    rgba = cmap(norm_p)  # returns RGBA tuple (0-1 floats)
    # Convert to hex
    return mcolors.to_hex(rgba)

# Add nodes and edges
completion_values = []
for skill, data in skills.items():
    completion_values.append(data.get("completion", 0))
    
    # Rich HTML tooltip# Mandatory resources
    if data['mandatory_resources']:
        mandatory_resources = "".join(
            f'<li><a href="{r["url"]}" target="_blank">{r["name"]}</a></li>' 
            for r in data['mandatory_resources']
        )
    else:
        mandatory_resources = "<li>None</li>"

    # Optional resources
    if data['optional_resources']:
        optional_resources = "".join(
            f'<li><a href="{r["url"]}" target="_blank">{r["name"]}</a></li>' 
            for r in data['optional_resources']
        )
    else:
        optional_resources = "<li>None</li>"

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
      size=30,
      borderWidth=2
    )

    for dep in data["depends_on"]:
        G.add_edge(dep, skill)


# Store all node attributes
node_attrs = {n: G.nodes[n] for n in G.nodes}

# Perform transitive reduction (returns a new graph)
G_reduced = nx.transitive_reduction(G)

# Reassign node attributes
for n, attrs in node_attrs.items():
    G_reduced.nodes[n].update(attrs)

G = G_reduced

# Compute global completion
global_completion = sum(completion_values) / len(completion_values)

# Initialize PyVis Network
net = Network(
    height="100vh",          # full page height
    width="100%",            # full page width
    bgcolor="rgba(0,0,0,0)",   # ← transparent
    font_color="black",
    directed=True,
    cdn_resources="in_line",
)

# Load the NetworkX graph
net.from_nx(G)

# Physics layout (force-directed)
net.force_atlas_2based(
    gravity=-100,
    overlap=0,
)

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

title = f"""
<div style="
    position: absolute;
    top: 10px;
    left: 10px;
    padding: 10px 15px;
    background-color: #2c2c2c;
    color: white;
    font-size: 16px;
    font-weight: bold;
    border-radius: 8px;
    z-index: 9999;
">
A Performance Engineer's Guide to Success
<br><br>

Super Based Links:
<br>
<a href="https://www.youtube.com/@GPUMODE/videos">GPUMODE YT</a>
<br>
<a href="https://www.youtube.com/@Eleuther_AI/videos">EleutherAI YT</a>
</div>
"""


# Info panel HTML (clickable node info)
info_panel_html = """
<div id="info-panel" style="
       position:absolute;
       bottom:-250px;  /* hidden by default */
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
        background: transparent;
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
    {title}
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