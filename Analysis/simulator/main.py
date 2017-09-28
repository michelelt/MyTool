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
            row["pieni"] = torino.pieni
            row["avg_bat_after"] = torino.avg_bat_after
            row["avg_bat_before"] = torino.avg_bat_before
            resutls = resutls.append(row, ignore_index=True)
        resutls.to_pickle(node["out"])

def plot_from_df (df, torino, provider, algorithms, ppz, parameter):
        fig = plt.figure(figsize=(30,10))
        colors = {"max_avg_time":"red", "max_parking":"blue", "max_time": "black"}
        ax = fig.gca()
        ax.set_title(provider + " Deaths prob. vs Zones with PS", fontsize=36)
        ax.grid()
     
        if provider == "car2go":
            nob = len(torino.car2go)
            noz = float(len(torino.car2go_parkings_analysis))
        else:
            nob = len(torino.enjoy)
            noz = float(len(torino.enjoy_parkings_analysis))

        for alg in algorithms:
            inside = df[
                (df["provider"]==provider) &
                (df["ppz"] == 2) &
                (df["algorithm"] == alg)]
            if parameter == "median":
                ax.plot(inside["z"], inside["median_dpc"], color=colors[alg], label=alg)
                ax.set_ylabel("Median number of death per car")
            else :
#                inside = df[
#                (df["provider"]==provider) &
#                (df["ppz"] == 2) &
#                (df["algorithm"] == alg)]
#                ax.plot(inside["z"], inside["tot_deaths"].div(nob), color=colors[alg], 
#                        label=alg+" ppz=2", marker="o")
#                
#                inside = df[
#                    (df["provider"]==provider) &
#                    (df["ppz"] == 4) &
#                    (df["algorithm"] == alg)]
#                ax.plot(inside["z"], inside["tot_deaths"].div(nob), color=colors[alg], 
#                        label=alg+" ppz=4", linestyle=":", marker="^")
#
#                
#                inside = df[
#                    (df["provider"]==provider) &
#                    (df["ppz"] == 6) &
#                    (df["algorithm"] == alg)]
#                ax.plot(inside["z"], inside["tot_deaths"].div(nob), color=colors[alg], 
#                        label=alg+" ppz=6", linestyle="--", marker="x")
                
                inside = df[
                    (df["provider"]==provider) &
                    (df["ppz"] == 8) &
                    (df["algorithm"] == alg)]
                ax.plot(inside["z"], inside["tot_deaths"].div(nob), color=colors[alg], 
                        label=alg+" ppz=8", linestyle="dotted", marker="D")
                
        labels = [item.get_text() for item in ax.get_xticklabels()]
        my_ticks = range(10,175,10)
        my_tikcs = [str(("{0:.2f}".format(x/noz))) for x in my_ticks ]
        for i in range(0,len(labels)):
            labels[i] = my_tikcs[i]
            
        ax.set_xticklabels(labels)
        for tick in ax.xaxis.get_major_ticks():
                tick.label.set_fontsize(27) 
                
        for tick in ax.yaxis.get_major_ticks():
                tick.label.set_fontsize(27) 
        
        ax.set_xlabel("Zones(%)", fontsize=36)
        ax.set_ylabel("Deaths (%)", fontsize=36)

        plt.legend(fontsize=18)
#        plt.savefig(paths.plots_path8+provider+"_zone", bbox_inches = 'tight',pad_inches = 0.25)
        plt.show()
        
def bar_plot_parkings_stats (df1, provider, column):
    if provider == "car2go" :
        color = "blue"
    else :
        color = "red"
        
    if column == "avg_duration_per_zone":
        y_label = 'Average parking time per zone'
        title = provider + ' - zones sorted per maximum avgerage parking time per zone'
    elif column == "parking_per_zone" :
        y_label = 'Parkings per zone [h]'
        title = provider + ' - zones sorted per maxmimum parkings per zone'
    elif column == "duration_per_zone" :
        y_label = "Total durations per zone [h]"
        title = provider + ' - zones sorted per total duration per zone'
    else :
        print "No column"
        return

    df1 = df1.sort_values(column, ascending=False)
    width=0.5
    ind = np.arange(len(df1.index))
    fig, ax = plt.subplots(figsize=(40,10))
    ax.bar(ind, df1[column], width, color=color)
    
    ax.set_ylabel(y_label)
    ax.set_xlabel("Zones")
    ax.set_title(title)
    ticks = [""]*len(df1.index)
    ticks[0:len(df1.index):8] = df1.index[range(0,len(ind),8)]
    
    ax.set_xticks(ind + width /32)
    ax.set_xticklabels(ticks)
    plt.savefig(paths.plots_path8+provider+"_parkings_stats_"+column, bbox_inches = 'tight',pad_inches = 0.25)

    plt.show()

def return_path(cso, alg, ppz, z):
        string = str(cso) +"_"+ str(alg) + "_" + str(ppz) + "_"+ str(z)
        return string

def plot_clorophlet_colorbar_solutions (my_city, provider, algorithm, column, z,ppz):
    
    if provider == "car2go":
        color = "blue"
        gdf = torino.car2go_parkings_analysis
    else:
        color = "red"
        gdf = torino.enjoy_parkings_analysis
    
    gdf["taken"] = 0
    k=torino.place_stations(z * ppz,
                      ppz,
                      provider,
                      algorithm=algorithm,
                     station_type=1)
    k=k.keys()
    gdf.loc[k, "taken"] = 1000
    
    
    fig, ax = plt.subplots(1, 1, figsize=(10,10))
    
    cmap = colors.ListedColormap(['white', color])
    gdf.plot(column="taken", cmap=cmap, ax=ax, linewidth=1)
    if column == "avg_duration_per_zone":
        algorithm = 'Average parking time per zone'
    elif column == "parking_per_zone" :
        algorithm = 'Parkings per zone [h]'
    elif column == "duration_per_zone" :
        algorithm = "Total durations per zone [h]"
    else :
        print "No column"
        return
    title = provider + " - chosen zone for " + algorithm +"\n"
    title += "Zones: "+ str(z) + "; Power Supplies per zones: " + str(ppz)
    plt.title(title, fontsize = 18)
    ax.grid(linestyle='-', linewidth=1.0)
    plt.xticks([])
    plt.yticks([])
#    plt.xlabel("Latitude", fontproperties=font)
#    plt.ylabel("Longitude", fontproperties=font)

    cax = fig.add_axes([0.9, 0.1, 0.03, 0.8,])
    sm_ = plt.cm.ScalarMappable(cmap=cmap )
    sm_._A = []
    fig.colorbar(sm_, cax=cax)
    cbar = plt.colorbar(sm_, cax=cax)
    cbar.ax.tick_params(labelsize=14)
    cbar.set_ticks([0.25,0.75])
    cbar.set_ticklabels(["Not in solution", "In solution"])
#    cbar.set_label('Mean car parking time per hour', rotation=270, fontsize=18, labelpad=30)
#    gdf.apply(lambda x: ax.annotate(s=x.N, xy=(x.geometry.centroid.x, x.geometry.centroid.y), ha='center'),axis=1)
    
    fig.savefig(paths.plots_path8+provider+"_"+column, bbox_inches='tight',dpi=250)
    plt.show()
#    plt.savefig("clorophlet_" + str(column) + "_" + str(slot) + ".pdf", format="pdf")
    
    return

if __name__ == "__main__":
    ## build the city ##
#    init_time = time.time()
    
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
    n_z = range(10,175, 10)
    n_ppz = [2,4,6,8]
    algorithms = ['max_parking', 'max_avg_time' ,'max_time']
    commands = {}
    j=0
    for cso in ["car2go"]:
        for alg in algorithms :
            for ppz in n_ppz:
                d = {}
                d["alg"] = alg
                d["ppz"] = ppz
                d["out"] =  paths.sym_path_3_alg_final+"3_alg_fin_"+str(j) 
                d["cso"] = cso
                commands[j] = d
                j=j+1
    
    
    ## builidng the coomand lists
    node_sim_list=[]
    process_list = []
    for i in commands.keys():
        node_sim_list.append(commands[i])
#        
#    ## run
#    init_time = time.time()
#    for node in node_sim_list:
#        p = Process(target=worker, args=(node,))
#        process_list.append(p)
#        p.start()
#    
#    for p in process_list:
#        p.join()
#    print time.time() - init_time
    
    
    ## rebuilding the resutls
    res = pd.DataFrame()
    for node in node_sim_list:
        res = res.append(pd.read_pickle(node["out"]), ignore_index=True)
        
#    zzz = res[res["algorithm"] == "duration_per_zone"]
    plot_from_df(res, torino, "car2go", ['max_parking', 'max_avg_time' ,'max_time'], 4, "tot" )
#    plot_from_df(res, torino, "enjoy", ["max_parking"], 4, "tot" )
#    
#    plot_from_df(res, "car2go", ["max_avg_time", "rnd", "max_parking"], 10, "tot" )
#    plot_from_df(res, "enjoy", ["max_avg_time", "rnd", "max_parking"], 10, "tot" )

    
#    bar_plot_parkings_stats(torino.car2go_parkings_analysis, "car2go", "parking_per_zone")
#    bar_plot_parkings_stats(torino.car2go_parkings_analysis, "car2go", "duration_per_zone")
#    bar_plot_parkings_stats(torino.car2go_parkings_analysis, "car2go", "avg_duration_per_zone")
# 
#    bar_plot_parkings_stats(torino.enjoy_parkings_analysis, "enjoy", "parking_per_zone")
#    bar_plot_parkings_stats(torino.enjoy_parkings_analysis, "enjoy", "duration_per_zone")
#    bar_plot_parkings_stats(torino.enjoy_parkings_analysis, "enjoy", "avg_duration_per_zone")
    
#    torino.car2go_parkings_analysis["taken"] = 0
#    k=torino.place_stations(50 * 10,
#                      10,
#                      "car2go",
#                      algorithm="max_parking",
#                     station_type=1)
#    k=set(k.keys())
#    
#    torino.car2go_parkings_analysis.loc[k, "taken"] = 1000
#    plot_clorophlet_colorbar_solutions(torino, "car2go", "max_parking","parking_per_zone", 50, 10)
#    plot_clorophlet_colorbar_solutions(torino, "enjoy","max_parking", "parking_per_zone", 50, 10)
    
    

#    plot_clorophlet_colorbar_solutions(torino.car2go_parkings_analysis, "car2go", "duration_per_zone")
#    plot_clorophlet_colorbar_solutions(torino.car2go_parkings_analysis, "car2go", "avg_duration_per_zone")
#    
#    plot_clorophlet_colorbar_solutions(torino.enjoy_parkings_analysis, "enjoy", "parking_per_zone")
#    plot_clorophlet_colorbar_solutions(torino.enjoy_parkings_analysis, "enjoy", "duration_per_zone")
#    plot_clorophlet_colorbar_solutions(torino.enjoy_parkings_analysis, "enjoy", "avg_duration_per_zone") 

    
    
    

    


