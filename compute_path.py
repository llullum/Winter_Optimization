import osmnx as ox
import networkx as nx

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
    graph = ox.graph_from_place('Outremont, Montréal', network_type='drive', simplify=True) #simplify
    graph = graph.to_undirected()

    # compute an eulerian path
    graph = nx.eulerize(graph)
    path = list(nx.eulerian_path(graph))

    return (graph, path)

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
    

tab_color = ["r", "g", "y", "w", "b", "orange"]
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

# -------------------- Main section -----------------------

(graph, path) = get_euclidian_path(log=False)
print(get_drone_price(graph, path))
list = find_deneigeuse_emplacement(graph, path, 1, onlyT1model=True)
plot_deneigeuse_path(graph, list)