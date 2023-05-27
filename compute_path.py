import osmnx as ox
import networkx as nx

# setup
ox.config(use_cache=True, log_console=False)

# load montreal graph and convert it to an eulerian graph
graph = ox.graph_from_place('Outremont, Montréal', network_type='drive', simplify=True) #simplify
graph = graph.to_undirected()

# compute an eulerian path
graph = nx.eulerize(graph)
path = list(nx.eulerian_path(graph))

# generate path.png
ns = []
for n in graph.nodes():
    if n == path[len(path) - 1][1]:
        ns.append(10)
    elif n == path[0][0]:
        ns.append(100)
    else:
        ns.append(1)

ec = ['b' if ((u, v) in path or (v, u) in path) else 'w' for u, v, k in graph.edges(keys=True)]
ox.plot_graph(graph, node_color='w', edge_color=ec, filepath="./path.png", save=True, show=True, close=True, node_size=ns, edge_linewidth=0.2)

# compute travel distance
dist = 0
count = 0
for (i, j) in path:
    street = graph[i][j][0]
    dist += street["length"]
    count += 1


print("distance traveled (in meters):", dist)
print("number of streets traversed:", count)