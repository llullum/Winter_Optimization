# import logging
import itertools
import osmnx as ox
import networkx as nx
from postman_problems.solver import cpp

import copy
import pandas as pd
import matplotlib.pyplot as plt

# -------------- GLOBAL VARIABLES --------------
DRONE_SPEED = 50
DRONE_WORKING_DAY = 8
DRONE_DAYLY_PRICE = 100
DRONE_KM_PRICE = 0.01

# -------------- GRAPH FUNCTIONS
def get_euclidian_path(log=True):
    # setup  
    ox.config(use_cache=True, log_console=log)

    # load montreal graph and convert it to an eulerian graph
    graph = ox.graph_from_place('Montréal', network_type='drive', simplify=True) #simplify
    graph = graph.to_undirected()
    edges = (graph.edges)
    ed = []
    # for u, v, k in edges:
    #     ed.append((u,v, graph[u][v][k]["length"]))
    # writeInFile("info.txt", ed)
    # edgelist= [(0,1)] # single edge (0,1)
    # G = nx.Graph(edgelist)
    # compute an eulerian path
    g_aug= eule(graph)
    path= list(nx.eulerian_circuit(g_aug))
    #path = create_eulerian_circuit(g_aug, graph )
    #print(path)
    #for u, v, k in g_aug.edges:
        #print(g_aug[u][v][k]["length"])
    #path, graph = cpp(edgelist_filename='info.txt',start_node='29239079')

    #graph = nx.eulerize(graph)
    #path = list(nx.eulerian_path(graph))

    return (g_aug, path)

#------------ TEST ZONE ------------------
def create_eulerian_circuit(graph_augmented, graph_original, starting_node=None):
    """Create the eulerian path using only edges from the original graph."""
    euler_circuit = []
    naive_circuit = list(nx.eulerian_circuit(graph_augmented, source=starting_node))
    
    for edge in naive_circuit:
        edge_data = graph_augmented.get_edge_data(edge[0], edge[1])    
        print(edge_data[0])
        if edge_data[0]['trail'] != 'augmented':
            # If `edge` exists in original graph, grab the edge attributes and add to eulerian circuit.
            edge_att = graph_original[edge[0]][edge[1]]
            euler_circuit.append((edge[0], edge[1], edge_att)) 
        else: 
            aug_path = nx.shortest_path(graph_original, edge[0], edge[1], weight='length')
            aug_path_pairs = list(zip(aug_path[:-1], aug_path[1:]))
            
            print('Filling in edges for augmented edge: {}'.format(edge))
            print('Augmenting path: {}'.format(' => '.join(aug_path)))
            print('Augmenting path pairs: {}\n'.format(aug_path_pairs))
            
            # If `edge` does not exist in original graph, find the shortest path between its nodes and 
            #  add the edge attributes for each link in the shortest path.
            for edge_aug in aug_path_pairs:
                edge_aug_att = graph_original[edge_aug[0]][edge_aug[1]]
                euler_circuit.append((edge_aug[0], edge_aug[1], edge_aug_att))
                                      
    return euler_circuit

def get_shortest_paths_distances(graph, pairs, edge_weight_name):
    """Compute shortest distance between each pair of nodes in a graph.  Return a dictionary keyed on node pairs (tuples)."""
    distances = {}
    for pair in pairs:
        distances[pair] = nx.dijkstra_path_length(graph, pair[0], pair[1], weight=edge_weight_name)
    return distances

    
def create_complete_graph(pair_weights, flip_weights=True):
    """
    Create a completely connected graph using a list of vertex pairs and the shortest path distances between them
    Parameters: 
        pair_weights: list[tuple] from the output of get_shortest_paths_distances
        flip_weights: Boolean. Should we negate the edge attribute in pair_weights?
    """
    g = nx.Graph()
    for k, v in pair_weights.items():
        wt_i = - v if flip_weights else v
        #print(v)
        # g.add_edge(k[0], k[1], {'distance': v, 'weight': wt_i})  # deprecated after NX 1.11 
        g.add_edge(k[0], k[1], **{'length': v, 'weight': wt_i})  
    return g

def add_augmenting_path_to_graph(graph, min_weight_pairs,g_odd_complete):
    """
    Add the min weight matching edges to the original graph
    Parameters:
        graph: NetworkX graph (original graph from trailmap)
        min_weight_pairs: list[tuples] of node pairs from min weight matching
    Returns:
        augmented NetworkX graph
    """
    # We need to make the augmented graph a MultiGraph so we can add parallel edges
    graph_aug = nx.MultiGraph(graph.copy())
    for pair in min_weight_pairs:
        print(g_odd_complete[pair[0]][pair[1]]["length"])   
        graph_aug.add_edge(pair[0], 
                           pair[1], 
                           **{'length': g_odd_complete[pair[0]][pair[1]]["length"], 'trail': 'augmented'}
                           # attr_dict={'distance': nx.dijkstra_path_length(graph, pair[0], pair[1]),
                           #            'trail': 'augmented'}  # deprecated after 1.11
                          )
    return graph_aug


def eule(g):
    # print("in eule")
    # print('\033[91m' + "in eule" + '\033[0m')
    print('\033[92m' + "in " +  '\033[94m' + '\033[4m' + "eule" + '\033[0m')
    nodes_odd_degree = [v for v, d in g.degree() if d % 2 == 1]
    #print(g_aug)
    odd_node_pairs = list(itertools.combinations(nodes_odd_degree, 2))
    odd_node_pairs_shortest_paths = get_shortest_paths_distances(g, odd_node_pairs, 'length')
    g_odd_complete = create_complete_graph(odd_node_pairs_shortest_paths, flip_weights=True)
    #print(g_odd_complete)
    odd_matching_dupes = nx.algorithms.max_weight_matching(g_odd_complete, True)
    odd_matching = list(pd.unique([tuple(sorted([k, v])) for k, v in odd_matching_dupes.items()]))
    print(odd_matching)
    g_aug = add_augmenting_path_to_graph(g, odd_matching,g_odd_complete)
    #print(g_aug)
    return g_aug


    
#--------- SUITE GRAPH SECTION ----------------
def plot_path(graph, path):
    # generate path.png
    ns = []
    for n in graph.nodes():
        if n == path[len(path) - 1][1]:
            ns.append(10)
        elif n == path[0][0]:
            ns.append(100)
        else:
            ns.append(1)

    ec = ['r' if ((u, v) in path or (v, u) in path) else 'w' for u, v, k in graph.edges(keys=True)]
    ox.plot_graph(graph, node_color='w', edge_color=ec, filepath="./path.png", save=True, show=True, close=True, node_size=ns, edge_linewidth=0.2)

# ------------- DRONE FUNCTIONS ----------------
def total_dist(graph, path):
    dist = 0
    count = 0
    for (i, j) in path:
        street = graph[i][j][0]
        dist += street["length"]
        count += 1
    print("distance traveled (in meters):", dist)
    print("number of streets traversed:", count)
    return (dist, count)
    
def get_drone_price(graph, path):
    (dist, _) = total_dist(graph, path)
    dist /= 1000
    filght_time = dist / DRONE_SPEED
    nb_days = filght_time // DRONE_WORKING_DAY + 1
    return nb_days * DRONE_DAYLY_PRICE + dist * DRONE_KM_PRICE

# -------------- DENEGEUSES FUNCTIONS --------------------
def find_deneigeuse_emplacement(graph, path, nb_hours, onlyT1model = False):
    dist = 0
    list = []
    type_t = 1 if onlyT1model else 2
    maxKmByDeneig = 10000*nb_hours*type_t
    currpath = []
    for k in range(len(path)-1):
        (i,j) = path[k]
        (i2,j2) = path[k+1]
        add = False
        street = graph[i][j][0]
        #print(street)
        dist += street["length"]
        currpath.append((i,j))
        if (dist + graph[i2][j2][0]["length"] > maxKmByDeneig):
            list.append((graph[i][j][0], type_t, currpath))
            dist -= maxKmByDeneig
            add = True
            currpath = []
    (i,j) = path[-1]
    street = graph[i][j][0]
    dist += street["length"]
    currpath.append((i,j))
    if(dist > nb_hours*10000):
        list.append((graph[i][j][0], 2, currpath))
    else:
        list.append((graph[i][j][0], 1, currpath))
    # for (n, t, p) in list:
    #     print((n["name"], t, p))
    return list
    

tab_color = ["r", "g", "y", "pink", "b", "orange"]
def plot_deneigeuse_path(graph, paths):
    print(len(paths))
    ec = []
    for (u, v) in graph.edges():
        i = 0
        for (_, _, p) in paths:
            if ((u, v) in p) or ((v, u) in p):
                ec.append(tab_color[i % len(tab_color)])
                break
            i += 1

    ox.plot_graph(graph, node_color='w', edge_color=ec, filepath="./deneigeuses_path.png", save=True, show=True, close=True, node_size=1, edge_linewidth=0.2)

# -------------------- Aux -----------------------
def writeInFile(filename, data):
    f = open(filename, "a")
    f.write("[")
    i = 0
    for u, v, m in data:
        # write each item on a new line
        if i == 0:
            f.write("('"+str(u)+"', '"+str(v)+"', {'distance':"+str(m)+"})")
            i+=1
        else:
            f.write(",('"+str(u)+"', '"+str(v)+"', {'distance':"+str(m)+"})")
    f.write("]")
    f.close()

# -------------------- Main section -----------------------
#info (node1, node2, length)
(graph, path) = get_euclidian_path(log=False)
print(get_drone_price(graph, path))
list = find_deneigeuse_emplacement(graph, path, 1, onlyT1model=True)
plot_deneigeuse_path(graph, list)