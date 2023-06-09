import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")

from compute_path import *
from threading import Thread

all_district = [
                "Le Plateau-Mont-Royal, Montréal",
                "Outremont, Montréal",
                "Rivière-des-Prairies-Pointe-aux-Trembles, Montréal",
                "Saint-Léonard, Montréal",
                "Verdun, Montréal"
                ]

res = [None] * len(all_district)
res2 = [None] * len(all_district)
graphs = [None] * len(all_district)

def compute_price_deneigeuse(graph, paths, district):
    sum_price = 0
    sum_dist = 0
    for (_, type, path) in paths:
        # print(district + ": deneigeuse no", nbd, "type: ", type)
        sum_price+= DENEIGEUSE1_DAILY_PRICE if (type == 1) else DENEIGEUSE2_DAILY_PRICE
        (dist, count) = total_dist(graph, path)
        dist/=1000
        dist_price = dist* (DENEIGEUSE1_KM_PRICE if (type == 1) else DENEIGEUSE2_KM_PRICE)
        time_price = dist* (DENEIGEUSE1_HOUR_PRICE_LT8 if (type == 1) else DENEIGEUSE2_HOUR_PRICE_LT8)
        sum_price+= dist_price + time_price
        sum_dist += dist
    return (sum_price, sum_dist)


def compute_district(district, index):
    print("\033[93mGenerate " + district + " graph...\033[0m")
    (graph, path) = get_euclidian_path(district, log=False)
    list = find_deneigeuse_emplacement(graph, path, DENEIGEUSE_WORKING_DAY)
    res2[index] = compute_price_deneigeuse(graph, list, district)
    graphs[index] = (graph, list, district)

def get_deneigeuse_info(list):
    nbL1 = 0
    nbL2 = 0
    for _, t, _ in list:
        if t == 1:
            nbL1 += 1
        else:
            nbL2 += 1
    return (nbL1, nbL2)

sum_price = 0
km = 0

for i in range(len(all_district)):
    thread = Thread(target=compute_district, args=(all_district[i],i))
    res[i] = thread
    thread.start()

for i in range(len(res)):
    res[i].join()
    (price_district, dist) = res2[i]
    (nbL1, nbL2) = get_deneigeuse_info(graphs[i][1])
    print(all_district[i] + ":", "price:", round(price_district, 2), "$, dist:", round(dist, 2), "Km, number of type 1:", nbL1, ", number of type 2:", nbL2)
    sum_price += price_district
    km+= dist

for (g, p, n) in graphs:
    plot_deneigeuse_path(g, p, n)
    

print("total price of deneigeuses:", round(sum_price, 2))
print("total distance of deneigeuses:", round(km, 2))
