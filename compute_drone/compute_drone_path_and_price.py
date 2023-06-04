import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")

from threading import Thread
from compute_path import *

res = [None] * len(all_district)
res2 = [None] * len(all_district)

def compute_district(district, index):
    print("\033[93mGenerate " + district + " graph...\033[0m")
    (graph, path) = get_euclidian_path(district, log=False)
    (price_district, drone_km) = get_drone_price(graph, path)
    print(district, "price:", price_district)
    print(district, "distance:", drone_km)
    res2[index] = (price_district, drone_km)

sum_price = 0
km = 0

for i in range(len(all_district)):
    thread = Thread(target=compute_district, args=(all_district[i],i))
    res[i] = thread
    thread.start()

for i in range(len(res)):
    res[i].join()
    (price_district, drone_km) = res2[i]
    print(all_district[i] + " done !")
    km += drone_km
    sum_price += price_district

print("total price of drone:", sum_price)
print("total distance of drone:", km)