import pandas as pd
import geopandas as gpd
import numpy as np
import datetime
import time
import random
import sys
import os.path
sys.path.insert(0, '/home/mc/Scrivania/Tesi/MyTool/Analysis/')
import paths as paths
from DataBaseProxy import DataBaseProxy
sys.path.insert(0, '/home/mc/Scrivania/Tesi/MyTool/Analysis/simulator')
from util import Utility
from car import Car
from city import City
from shapely.geometry import Point, Polygon
from station import Station
import threading
from multiprocessing import Process
import matplotlib.pyplot as plt
from matplotlib import colors

## service functions
def worker(node):
        resutls = pd.DataFrame()
        for cso in ["car2go", "enjoy"]:
            for ppz in [2,4,6,8]:
                for z in [30,60,90,120,150,180,210,238]:
                    node['ppz'] = ppz
                    node["cso"] = cso
                    
                    torino.place_stations(z*node["ppz"],
                                          node['ppz'],
                                          node["cso"],
                                          algorithm=node["alg"],
                                         station_type=1)
                    c2g_stats = torino.run(node["cso"], threshold=0)
                    row = pd.Series()
                    row["z"] = z
                    row["ppz"] = node["ppz"]
                    row["p"] = z*node["ppz"]
                    row["provider"] = node["cso"]
                    row["algorithm"] = node["alg"]
                    row["mean_dpc"] = c2g_stats["deaths"].mean()
                    row["median_dpc"] = c2g_stats["deaths"].median()
                    row["tot_deaths"] = c2g_stats["deaths"].sum()
                    row["pieni"] = torino.pieni
                    row["avg_bat_after"] = torino.avg_bat_after
                    row["avg_bat_before"] = torino.avg_bat_before
                    row["rech_cars"] = torino.rech_cars
                    resutls = resutls.append(row, ignore_index=True)
                    
        resutls.to_pickle(node["out"])


def return_path(cso, alg, ppz, z):
        string = str(cso) +"_"+ str(alg) + "_" + str(ppz) + "_"+ str(z)
        return string

    

if __name__ == "__main__":
    ## build the city ##

    year = 2017
    month = 5
    day = 6
    start = datetime.datetime(year, month, day, 0, 0, 0)
    end = datetime.datetime(year, month +2, day, 23, 59, 0)
    torino = City("Torino", start,end)
    torino.set_c2g_datasets(from_pickle=True)
    torino.set_enj_datasets(from_pickle=True)
    torino.get_fleet("car2go")
    torino.get_fleet("enjoy")
    
    Series = torino.car2go_parkings_analysis.iloc[0]
    DataFrame = torino.car2go_parkings_analysis

    
    # parameter for the parallel simulation ##
#    n_z = [30,60,90,120,150,180,210,238]
#    n_ppz = [2]
    algorithms = ['max_parking', 'max_time', 'max_avg_time']
#    algorithms = ["rnd"]
    commands = {}
    
    j= 0
    init_time = time.time()
    print "start at: " +  time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(init_time))
    print j
#    for cso in ["car2go"]:
    for alg in algorithms :
#            for ppz in n_ppz:
        d = {}
        d["alg"] = alg
        d["out"] =  paths.sym_path_bat+"bat_"+str(j) 
#        d["cso"] = 'car2go'
        commands[j] = d
        j=j+1
        
        
    ## builidng the coomand lists
    node_sim_list=[]
    process_list = []
    print commands.keys()
    for i in commands.keys():
        node_sim_list.append(commands[i])
        
     ## run
    for node in node_sim_list:
        p = Process(target=worker, args=(node,))
        process_list.append(p)
        p.start()
    
    for p in process_list:
        p.join()
    final_time = time.time() - init_time

    print "ends at: " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print "duration: " + str(final_time)
    print
    
    print "END"
    # rebuilding the resutls
#    res = pd.DataFrame()
#    root = "/home/mc/Scrivania/Tesi/MyTool/pickles/"
#    myDir = "sym_res_rnd/"
#    name = "rnd_"
#    for j in range(0,56):
#        res = res.append(pd.read_pickle(root+myDir+name+str(j)), ignore_index=True)
#    
#    myDir = "sym_res_rnd_c2g/"
#    name = "res_rnd"
#    for j in range(0,200):
#        res = res.append(pd.read_pickle(root+myDir+name+str(j)), ignore_index=True)
#        
#    myDir = "sym_res_3_alg_no_rand_final/"
#    name = "sym_res_3_alg_no_rand_final3_alg_fin_"
#    for j in range(0,24):
#        res = res.append(pd.read_pickle(root+myDir+name+str(j)), ignore_index=True)
#    
    
    


