# import logging
import osmnx as ox
import networkx as nx

# -------------- GLOBAL VARIABLES --------------
DRONE_SPEED = 50
DRONE_WORKING_DAY = 8
DRONE_DAILY_PRICE = 100
DRONE_KM_PRICE = 0.01

DENEIGEUSE1_SPEED = 10
DENEIGEUSE2_SPEED = 20
DENEIGEUSE_WORKING_DAY = 7
DENEIGEUSE1_DAILY_PRICE = 500
DENEIGEUSE2_DAILY_PRICE = 800
DENEIGEUSE1_KM_PRICE = 1.1
DENEIGEUSE2_KM_PRICE = 1.3
DENEIGEUSE1_HOUR_PRICE_LT8= 1.1
DENEIGEUSE2_HOUR_PRICE_LT8= 1.3
DENEIGEUSE1_HOUR_PRICE_GT8= 1.3
DENEIGEUSE2_HOUR_PRICE_GT8= 1.5


tab_color = ["r", "g", "y", "pink", "b", "orange"]

all_district = ["Ahuntsic-Cartierville, Montréal",
                "Anjou, Montréal",
                "Côte-des-Neiges-Notre-Dame-de-Grâce, Montréal", 
                "Lachine, Montréal",
                "LaSalle, Montréal",
                "Le Plateau-Mont-Royal, Montréal",
                "Le Sud-Ouest, Montréal",
                "L'Île-Bizard-Sainte-Geneviève, Montréal",
                "Mercier-Hochelaga-Maisonneuve, Montréal",
                "Montréal-Nord, Montréal",
                "Outremont, Montréal",
                "Pierrefonds-Roxboro, Montréal",
                "Rivière-des-Prairies-Pointe-aux-Trembles, Montréal",
                "Rosemont-La Petite-Patrie, Montréal",
                "Saint-Laurent, Montréal",
                "Saint-Léonard, Montréal",
                "Verdun, Montréal",
                "Ville-Marie, Montréal",
                "Villeray-Saint-Michel-Parc-Extension, Montréal"
                ]


# -------------- GRAPH FUNCTIONS
def get_euclidian_path(district, log=True):
    # setup  
    ox.config(use_cache=True, log_console=log)
    print("Starting...")
    # load montreal graph and convert it to an eulerian graph
    graph = ox.graph_from_place(district, network_type='drive', simplify=True) #simplify
    graph = graph.to_undirected()
    
    # compute an eulerian path
    g_aug = nx.eulerize(graph)
    path = list(nx.eulerian_circuit(g_aug))
    
    return (g_aug, path)

def plot_path(graph, path, district):
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
    name = "plan/" + district + ".png"
    ox.plot_graph(graph, node_color='w', edge_color=ec, filepath=name, save=True, show=True, close=True, node_size=ns, edge_linewidth=0.2)

# ------------- DRONE FUNCTIONS ----------------
def total_dist(graph, path):
    dist = 0
    count = 0
    for (i, j) in path:
        street = graph[i][j][0]
        dist += street["length"]
        count += 1
    return (dist, count)
    
def get_drone_price(graph, path):
    (dist, _) = total_dist(graph, path)
    dist /= 1000
    filght_time = dist / DRONE_SPEED
    nb_days = filght_time // DRONE_WORKING_DAY + 1
    return (nb_days * DRONE_DAILY_PRICE + dist * DRONE_KM_PRICE, dist)

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
        street = graph[i][j][0]
        dist += street["length"]
        currpath.append((i,j))
        if (dist + graph[i2][j2][0]["length"] > maxKmByDeneig):
            list.append((graph[i][j][0], type_t, currpath))
            dist -= maxKmByDeneig
            currpath = []
    (i,j) = path[-1]
    street = graph[i][j][0]
    dist += street["length"]
    currpath.append((i,j))
    if(dist > nb_hours*10000):
        list.append((graph[i][j][0], 2, currpath))
    else:
        list.append((graph[i][j][0], 1, currpath))
    return list
    
def plot_deneigeuse_path(graph, paths, name): #"paths" use return values of find_deneigeuse_emplacement
    ec = []
    for (u, v) in graph.edges():
        i = 0
        for (_, _, p) in paths:
            if ((u, v) in p) or ((v, u) in p):
                ec.append(tab_color[i % len(tab_color)])
                break
            i += 1

    ox.plot_graph(graph, node_color='w', edge_color=ec, filepath="./"+name+"_deneigeuses.png", save=True, show=True, close=True, node_size=1, edge_linewidth=0.2)