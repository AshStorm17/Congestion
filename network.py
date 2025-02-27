import networkx as nx
import matplotlib.pyplot as plt

# Create graph
G = nx.Graph()

# Add nodes
nodes = ["h1", "h2", "h3", "h4", "h5", "h6", "h7", "s1", "s2", "s3", "s4"]
G.add_nodes_from(nodes)

# Add edges
edges = [
    ("h1", "s1"), ("h2", "s1"),
    ("h3", "s2"),
    ("h4", "s3"), ("h5", "s3"),
    ("h6", "s4"), ("h7", "s4"),
    ("s1", "s2"), ("s2", "s3"), ("s3", "s4")
]
G.add_edges_from(edges)

# Draw the graph
plt.figure(figsize=(8, 6))
pos = nx.spring_layout(G)  # Position nodes
nx.draw(G, pos, with_labels=True, node_size=3000, node_color="lightblue", edge_color="gray", font_size=10)
plt.title("Mininet Topology")
plt.show()
