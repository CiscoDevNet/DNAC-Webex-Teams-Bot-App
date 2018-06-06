import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

G = nx.Graph()
G.add_edges_from(
    [('Client', 'SSID'), ('SSID', 'AP'), ('AP', 'WLC')])

val_map = {'Client': 1.0,
           'SSID': 0.5714285714285714,
           'AP': 0.0}

values = [val_map.get(node, 0.25) for node in G.nodes()]

nx.draw(G, cmap = plt.get_cmap('jet'), node_color = values,with_labels=True)
plt.show()