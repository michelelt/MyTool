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

## service functions
def worker(node):
        resutls = pd.DataFrame()  
        for z in n_z:
            torino.place_stations(z * node["ppz"],
                                  node["ppz"],
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
            resutls = resutls.append(row, ignore_index=True)
        resutls.to_pickle(node["out"])

def plot_from_df (df, provider, algorithm, ppz, parameter):
        fig = plt.figure(figsize=(10,10))
        colors = {"max_avg_time":"red", "max_parking":"blue", "rnd": "black"}
    
        ax = fig.gca()
        ax.set_title("Deaths vs Number of PS", fontsize=36)
        for alg in algorithm:
        
            inside = df[
                (df["provider"]==provider) &
                (df["ppz"] == ppz) &
                (df["algorithm"] == alg)]
            if parameter == "median":
                ax.plot(inside["p"], inside["median_dpc"], color=colors[alg], label=alg)
                ax.set_ylabel("Median number of death per car")
            else :
                ax.plot(inside["p"], inside["tot_deaths"], color=colors[alg], label=alg)
                ax.set_ylabel("Total number of deaths")
        
        ax.set_xlabel("Total number of power supply")
        plt.legend(fontsize=18)
    #    plt.savefig(paths.)
        plt.show()

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
    
    ## parameter for the parallel simulation ##
    n_z = range(5,205, 50)
    n_ppz = [3, 9]
    commands = {}
    j=0
    for cso in ["car2go", "enjoy"]:
        for alg in ["max_parking", "rnd", "max_avg_time"] :
            for ppz in n_ppz:
                d = {}
                d["alg"] = alg
                d["ppz"] = ppz
                d["out"] =  "/home/mc/Scrivania/Tesi/MyTool/pickles/sym_res/sym_res_"+str(j) 
                d["cso"] = cso
                commands[j] = d
                j=j+1
    
    
    ## builidng the coomand lists
    node_sim_list=[]
    process_list = []
    for i in commands.keys():
        node_sim_list.append(commands[i])
        
    ## run
    init_time = time.time()
    for node in node_sim_list:
        p = Process(target=worker, args=(node,))
        process_list.append(p)
        p.start()
    
    for p in process_list:
        p.join()
        
    print time.time() - init_time
    
    res = pd.DataFrame()
    
    ## rebuilding the resutls
    for node in node_sim_list:
        res = res.append(pd.read_pickle(node["out"]), ignore_index=True)
    
    
    plot_from_df(res, "car2go", ["max_avg_time", "rnd", "max_parking"], 3, "tot" )
    plot_from_df(res, "car2go", ["max_avg_time", "rnd", "max_parking"], 9, "tot" )



