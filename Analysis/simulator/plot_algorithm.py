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


def plot_from_df_algorithm (df, torino, provider, column, paramter, ppz):
    
        if provider == "car2go":
            nob = float(len(torino.car2go))
            noz = float(len(torino.car2go_parkings_analysis))
            cap = 17.6
        else:
            nob = len(torino.enjoy)
            noz = float(len(torino.enjoy_parkings_analysis))
            cap = 25.2
            
        
        colors = {2:"red", 4:"blue", 6: "green", 8: "black"}
        markers = {2:"o", 4:"x", 6: "^", 8: "d"}
        labels = {2:"ppz = 2", 4:"ppz = 4", 6: "ppz = 6", 8:"ppz = 8",}
        alg_names = {"max_avg_time":"Average parking time", 
                     "max_parking":"Number of parking", 
                     "max_time": "Parking time", 
                     "best_rnd": "Best random", 
                     "mean_rnd":" Average random (190 run)"}
        
        div_facts = {"tot_deaths":nob,  "avg_bat_before": cap, "avg_bat_after": cap, "pieni": nob}
        
        titles  = {"tot_deaths": " - Bat. discharge vs Zone coverage - ppz=",
                   "avg_bat_before": " - Avg. SoC vs Zone coverage - ppz=", 
                   "avg_bat_after": " - Avg. after charnging SoC vs Zone coverage - ppz=", 
                   "pieni": " - Charging prob. vs Zone Coverage - ppz="}
        
        y_labels  = {"tot_deaths": "Battery discharge prob.",
                   "avg_bat_before": "Avg. SoC [%]", 
                   "avg_bat_after": "Avg. SoC [%]", 
                   "pieni": "Charging prob."}
        
        saving_name  = {"tot_deaths": "bat_exaust_",
                   "avg_bat_before": "SoC_Before_", 
                   "avg_bat_after": "SoC_After_", 
                   "pieni": "charging_"}
        
        dir_name  = {"tot_deaths": "bat_exaust/",
           "avg_bat_before": "soc_before/", 
           "avg_bat_after": "soc_after/", 
           "pieni": "charging_prob/"}
    
        
        if provider == "car2go":
            nob = len(torino.car2go)
            noz = float(len(torino.car2go_parkings_analysis))
            noc = float(len(torino.c2g_fleet))
            cap = 17.6
            a = noc*cap
        else:
            nob = len(torino.enjoy)
            noz = float(len(torino.enjoy_parkings_analysis))

        
        if column == "mean_rnd":
            mean_c2g = df[(df["provider"] == provider) & (df["algorithm"]=="rnd")]
            mean_c2g = mean_c2g.groupby(["z","ppz"], as_index=False).mean()
            mean_c2g["algorithm"] = "mean_rnd"
            df = mean_c2g
        
        elif column == "best_rnd":
            best_deaths = df[(df["provider"] == provider) & (df["algorithm"]=="rnd")]
            best_deaths = best_deaths.sort_values("tot_deaths").groupby(["z","ppz"], as_index=False).first()
            best_deaths = best_deaths.rename(columns={"rnd":"mean_rnd"})
            best_deaths["algorithm"] = "best_rnd"

            df = best_deaths

        else : 
            df = df[df["provider"] == provider]
        

        
        fig = plt.figure(figsize=(30,10))
        ax = fig.gca()
        ax.set_title(provider + " - " + alg_names[column] + "", fontsize=36)
        ax.grid()
        for i in ppz :
            df2 = df[(df["ppz"] ==i)]
#            df4 = df[(df["algorithm"] == column) & (df["ppz"] ==4)]
#            df6 = df[(df["algorithm"] == column) & (df["ppz"] ==6)]
#            df8 = df[(df["algorithm"] == column) & (df["ppz"] ==8)]
            ax.plot(df2["z"], df2[paramter].div(div_facts[paramter]), color=colors[i], marker=markers[i], label=labels[i])
#            ax.plot(df4["z"], df4[paramter].div(div_facts[paramter]), color=colors[4], marker=markers[4], label=labels[4])
#            ax.plot(df6["z"], df6[paramter].div(div_facts[paramter]), color=colors[6], marker=markers[6], label=labels[6])
#            ax.plot(df8["z"], df8[paramter].div(div_facts[paramter]), color=colors[8], marker=markers[8], label=labels[8])

        my_t = range( 10, 175, 10)
        my_ticks = [str(("{0:.2f}".format(x/noz))) for x in my_t ]
        labels = [""] * len(my_t)
        for i in range(0,len(labels)):
                labels[i] = int(float(my_ticks[i])*100)
        
        plt.xticks(my_t, labels)
        plt.yticks([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8])
        
#        ax.set_xticklabels(labels)
        for tick in ax.xaxis.get_major_ticks():
                tick.label.set_fontsize(27) 
                
        for tick in ax.yaxis.get_major_ticks():
                tick.label.set_fontsize(27) 
        
        ax.set_xlabel("Zones(%)", fontsize=36)
        ax.set_ylabel(y_labels[paramter], fontsize=36)
        

 
        plt.legend(fontsize=36)
#        /home/mc/Scrivania/Tesi/toptesi/figures/_results/car2go/algorithms
#        /home/mc/Scrivania/Tesi/toptesi/figures/_results/car2go/algorithms/car2go_best_rnd_tot_deaths
#        my_path = "/home/mc/Scrivania/Tesi/toptesi/figures/_results/"
#        my_path += provider+"/"
#        my_path += "algorithms/"
#        my_path += provider+"_"+column +"_"+ paramter
        my_path="/home/mc/Immagini/pres_im/pzz_"+str(len(ppz))
        
        plt.savefig(my_path, bbox_inches = 'tight')
#        print my_path
        plt.show()
        
        
        

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


res2 = pd.DataFrame()
root = "/home/mc/Scrivania/Tesi/MyTool/pickles/"
myDir = "sym_res_corr_rnd/"
name = ""
for j in range(0,760):
    res2 = res2.append(pd.read_pickle(root+myDir+name+str(j)), ignore_index=True)
    
myDir = "sym_res_corr_eur/"
name = ""
for j in range(0,6):
    res2 = res2.append(pd.read_pickle(root+myDir+name+str(j)), ignore_index=True)


#df = res2
#provider = 'car2go'
#best_deaths = df[(df["provider"] == provider) & (df["algorithm"]=="rnd")]
#best_deaths = df[(df["provider"] == provider) & (df["algorithm"]!="rnd")]


#best_deaths = best_deaths.sort_values("tot_deaths").groupby(["z","ppz"], as_index=False).first()
#best_deaths = best_deaths.rename(columns={"rnd":"mean_rnd"})
#best_deaths["algorithm"] = "best_rnd"


#best_deaths = best_deaths.groupby(["z","ppz"], as_index=False).mean()
#best_deaths = best_deaths.rename(columns={"rnd":"mean_rnd"})
#best_deaths["algorithm"] = "mean_rnd"

#best_deaths["pieni"] = best_deaths["pieni"].div(len(torino.car2go))*100
#best_deaths["z"] = best_deaths["z"].mul(100).div(238).astype(int)
#best_deaths = best_deaths[["z", "ppz", "algorithm", "pieni"]]
#best_deaths = best_deaths[(best_deaths["z"] == 25) & (best_deaths["ppz"] == 6)]
#
#aab = aaa["distance"]
#bat = pd.DataFrame()
#myDir ="sym_res_bat/"
#for j in range(0,3):
#    bat = bat.append(pd.read_pickle(root+myDir+name+"bat_"+str(j)), ignore_index=True)

        
plot_from_df_algorithm (res2, torino, "car2go", "mean_rnd", "tot_deaths", [2]) 
plot_from_df_algorithm (res2, torino, "car2go", "mean_rnd", "tot_deaths", [2,4]) 
plot_from_df_algorithm (res2, torino, "car2go", "mean_rnd", "tot_deaths", [2,4,6]) 
plot_from_df_algorithm (res2, torino, "car2go", "mean_rnd", "tot_deaths", [2,4,6,8]) 
#aaa = aaa[aaa["z"] == 60]
#aaa["tot_deaths"] = aaa["tot_deaths"].div(len(torino.car2go)).mul(100)
#plot_from_df_algorithm (res2, torino, "enjoy", "max_time", "tot_deaths") 
#plot_from_df_algorithm (res2, torino, "enjoy", "max_avg_time", "tot_deaths") 
#plot_from_df_algorithm (res2, torino, "car2go", "best_rnd", 'avg_bat_before') 
#plot_from_df_algorithm (res2, torino, "car2go", "mean_rnd", 'avg_bat_before') 

#plot_from_df_algorithm (res2, torino, "enjoy", "max_parking") 
#plot_from_df_algorithm (res2, torino, "enjoy", "max_time") 
#plot_from_df_algorithm (res2, torino, "enjoy", "max_avg_time") 
#plot_from_df_algorithm (res2, torino, "car2go", "best_rnd", 'tot_deaths') 
#plot_from_df_algorithm (res2, torino, "car2go", "mean_rnd", 'avg_bat_before') 
































