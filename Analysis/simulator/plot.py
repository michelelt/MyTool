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


def plot_from_df (df, torino, provider, ppz, column, inputs):
        fig = plt.figure(figsize=(30,10))
        
        if provider == "car2go":
            nob = float(len(torino.car2go))
            noz = float(len(torino.car2go_parkings_analysis))
            cap = 17.6
        else:
            nob = len(torino.enjoy)
            noz = float(len(torino.enjoy_parkings_analysis))
            cap = 25.2

        colors = {"max_avg_time":"red", "max_parking":"blue", "max_time": "black", "best_rnd": "gray", "mean_rnd":"green"}
        markers = {"max_avg_time":"o", "max_parking":"x", "max_time": "^", "best_rnd": "d", "mean_rnd":"+"}
        labels = {"max_avg_time":"max average parking time", "max_parking":"max number of parking", "max_time": "max parking time", "best_rnd": "best random", "mean_rnd":"average random(190 run)"}
        div_facts = {"tot_deaths":nob,  "avg_bat_before": cap, "avg_bat_after": cap, "pieni": nob}
        
        titles  = {"tot_deaths": " - Bat. discharge vs Zone coverage - ppz=",
                   "avg_bat_before": " - Avg. SoC vs Zone coverage - ppz=", 
                   "avg_bat_after": " - Avg. after charnging SoC vs Zone coverage - ppz=", 
                   "pieni": " - Charging prob. vs Zone Coverage - ppz="}
        
        y_labels  = {"tot_deaths": "Battery discharge prob.",
                   "avg_bat_before": "Avg. SoC prob.", 
                   "avg_bat_after": "Avg. SoC - After charging prob.", 
                   "pieni": "Charging prob."}
        
        saving_name  = {"tot_deaths": "bat_exaust_",
                   "avg_bat_before": "SoC_Before_", 
                   "avg_bat_after": "SoC_After_", 
                   "pieni": "charging_"}
        
        dir_name  = {"tot_deaths": "bat_exaust/",
           "avg_bat_before": "soc_before/", 
           "avg_bat_after": "soc_after/", 
           "pieni": "charging_prob/"}

#        res = df[(df["z"]>=80) & (df["z"]<=100)]

        res = df
        mean_c2g = res[(res["provider"] == provider) & (res["algorithm"]=="rnd")]
        mean_c2g = mean_c2g.groupby(["z","ppz"], as_index=False).mean()
        mean_c2g = mean_c2g[mean_c2g["ppz"] == ppz]
        

        
        best_deaths = res[(res["provider"] == provider) & (res["algorithm"]=="rnd")]
        best_deaths = best_deaths.sort_values("tot_deaths").groupby(["z","ppz"], as_index=False).first()
        best_deaths = best_deaths[best_deaths["ppz"] == ppz]
        
                
        det_alg = res[(res["provider"] == provider) & (res["ppz"] == ppz) & (res["algorithm"]!="rnd")]
        max_parking = det_alg[det_alg["algorithm"] == "max_parking"]
        max_avg_time = det_alg[det_alg["algorithm"] == "max_avg_time"]
        max_time = det_alg[det_alg["algorithm"] == "max_time"]
        
        ax = fig.gca()
        
        ax.set_title(provider + titles[column]+str(ppz), fontsize=48)
        
        df_dict={
                "mean_rnd": mean_c2g,
                "best_rnd":best_deaths,
                "max_parking":max_parking,
                "max_avg_time":max_avg_time,
                "max_time": max_time
                }

        ax.grid()
        if len(res['algorithm'].unique()) > 3 and column not in ["avg_bat_before", 'avg_bat-after'] and provider == 'car2go':
#            ax.plot(mean_c2g["z"], mean_c2g[column].div(div_facts[column]), color=colors["mean_rnd"], marker=markers["mean_rnd"], label=labels["mean_rnd"])
#            ax.plot(best_deaths["z"], best_deaths[column].div(div_facts[column]), color=colors["best_rnd"], marker=markers["best_rnd"], label=labels["best_rnd"])
#            ax.plot(max_parking["z"], max_parking[column].div(div_facts[column]), color=colors["max_parking"], marker=markers["max_parking"], label=labels["max_parking"])
#            ax.plot(max_avg_time["z"], max_avg_time[column].div(div_facts[column]), color=colors["max_avg_time"], marker=markers["max_avg_time"], label=labels["max_avg_time"])
#            ax.plot(max_time["z"], max_time[column].div(div_facts[column]), color=colors["max_time"], marker=markers["max_time"], label=labels["max_time"])
            print "ok"
            for alg in inputs:
                df_dict[alg]["z"]
                df_dict[alg][column]
                div_facts[column]
                colors[alg]
                markers[alg]
                labels[alg]
                ax.plot(df_dict[alg]["z"], df_dict[alg][column].div(div_facts[column]), color=colors[alg], marker=markers[alg], label=labels[alg])

            my_t = range( 10, 175, 10)
            my_ticks = [str(("{0:.2f}".format(x/noz))) for x in my_t ]
            labels = [""] * len(my_t)
            for i in range(0,len(labels)):
                    labels[i] = int(float(my_ticks[i])*100)
            
            plt.xticks(my_t, labels)
            plt.yticks([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8])

            
        elif len(res['algorithm'].unique()) > 3 and column not in ["avg_bat_before", 'avg_bat-after'] and provider == 'enjoy':
            ax.plot(max_parking["z"], max_parking[column].div(div_facts[column]), color=colors["max_parking"], marker=markers["max_parking"], label=labels["max_parking"])
            ax.plot(max_avg_time["z"], max_avg_time[column].div(div_facts[column]), color=colors["max_avg_time"], marker=markers["max_avg_time"], label=labels["max_avg_time"])
            ax.plot(max_time["z"], max_time[column].div(div_facts[column]), color=colors["max_time"], marker=markers["max_time"], label=labels["max_time"])
            my_t = range( 10, 175, 10)
            my_ticks = [str(("{0:.2f}".format(x/noz))) for x in my_t ]
            labels = [""] * len(my_t)
            for i in range(0,len(labels)):
                    labels[i] = int(float(my_ticks[i])*100)
            
            plt.xticks(my_t, labels)

        
        elif len(res['algorithm'].unique()) == 3 and column not in ["avg_bat_before", 'avg_bat-after']: 
            print "2"
            ax.plot(max_parking["z"], max_parking[column].div(div_facts[column]), color=colors["max_parking"], marker=markers["max_parking"], label=labels["max_parking"])
            ax.plot(max_avg_time["z"], max_avg_time[column].div(div_facts[column]), color=colors["max_avg_time"], marker=markers["max_avg_time"], label=labels["max_avg_time"])
            ax.plot(max_time["z"], max_time[column].div(div_facts[column]), color=colors["max_time"], marker=markers["max_time"], label=labels["max_time"])
            my_t = range( 10, 175, 10)
            my_ticks = [str(("{0:.2f}".format(x/noz))) for x in my_t ]
            labels = [""] * len(my_t)
            for i in range(0,len(labels)):
#                if i%2 == 0:
#                    labels[i] == ""
#                else:
                    labels[i] = int(float(my_ticks[i])*100)
            
            plt.xticks(my_t, labels)

        elif column  in ["avg_bat_before", "avg_bat_after"]:
            print column
#            ax.plot(mean_c2g["z"], mean_c2g[column].div(div_facts[column]), color=colors["mean_rnd"], marker=markers["mean_rnd"], label=labels["mean_rnd"])
#            
#            ax.plot(best_deaths["z"], best_deaths[column].div(div_facts[column]), color=colors["best_rnd"], marker=markers["best_rnd"], label=labels["best_rnd"])
            
            ax.plot(max_parking["z"], max_parking[column].div(div_facts[column]), color=colors["max_parking"], marker=markers["max_parking"], label=labels["max_parking"])
            
            ax.plot(max_avg_time["z"], max_avg_time[column].div(div_facts[column]), color=colors["max_avg_time"], marker=markers["max_avg_time"], label=labels["max_avg_time"])
            
            ax.plot(max_time["z"], max_time[column].div(div_facts[column]), color=colors["max_time"], marker=markers["max_time"], label=labels["max_time"])
#            cstm_t = [30,60,90,120,150,180,210,238]
            my_t = [30,60,90,120,150,180,210]
            if provider == 'car2go':
                my_t.append(238)
#            print noz, my_t
            my_ticks = [str(("{0:.2f}".format(x/noz))) for x in my_t ]
#            print my_ticks
            labels = [""] * len(my_t)
            for i in range(0,len(labels)):
#                if i%2 == 0:
#                    labels[i] == ""
#                else:
                labels[i] = int(float(my_ticks[i])*100)
            plt.xticks(my_t, labels)

        
        else:
            print "error"
            return
        
            plt.xticks(my_t, labels)

        for tick in ax.xaxis.get_major_ticks():
                tick.label.set_fontsize(36) 
                
        for tick in ax.yaxis.get_major_ticks():
                tick.label.set_fontsize(36) 
        
        ax.set_xlabel("Zones coverage(%)", fontsize=48)
        ax.set_ylabel(y_labels[column], fontsize=48)
        plt.legend(fontsize=36)
        
#        column = 'tot_deaths'
#        ppz = 6
#        provider = 'car2go'
#        dir_name  = {"tot_deaths": "bat_exaust/",
#           "avg_bat_before": "soc_before/", 
#           "avg_bat_after": "soc_after/", 
#           "pieni": "charging_prob/"}
#        saving_name  = {"tot_deaths": "bat_exaust_",
#           "avg_bat_before": "SoC_Before_", 
#           "avg_bat_after": "SoC_After_", 
#           "pieni": "charging_"}
        my_path="/home/mc/Immagini/pres_im/pzz_alg_"+str(len(inputs))
        plt.savefig(my_path, bbox_inches = 'tight')

#        plt.show()
        
        
        
        


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
     
#    print "END"
    ## rebuilding the resutls
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
        
    bat = pd.DataFrame()
    myDir ="sym_res_bat/"
    for j in range(0,3):
        bat = bat.append(pd.read_pickle(root+myDir+name+"bat_"+str(j)), ignore_index=True)
    
        

    plot_from_df(res2, torino, "car2go", 6, "tot_deaths", ["mean_rnd"])
    plot_from_df(res2, torino, "car2go", 6, "tot_deaths", ["mean_rnd","best_rnd"])
    plot_from_df(res2, torino, "car2go", 6, "tot_deaths", ["mean_rnd","best_rnd","max_avg_time"])
    plot_from_df(res2, torino, "car2go", 6, "tot_deaths", ["mean_rnd","best_rnd","max_avg_time","max_parking"])
    plot_from_df(res2, torino, "car2go", 6, "tot_deaths", ["max_time", "mean_rnd","best_rnd","max_avg_time","max_parking"])
    
#    plot_from_df(res2, torino, "car2go", 4, "tot_deaths")
#    plot_from_df(res2, torino, "car2go", 6, "tot_deaths")
#    plot_from_df(res2, torino, "car2go", 8, "tot_deaths")

#    plot_from_df(res2, torino, "enjoy", 2, "tot_deaths")
#    plot_from_df(res2, torino, "enjoy", 4, "tot_deaths")
#    plot_from_df(res2, torino, "enjoy", 6, "tot_deaths")
#    plot_from_df(res2, torino, "enjoy", 8, "tot_deaths")

#    plot_from_df(bat, torino, "car2go", 2, "avg_bat_before")
#    plot_from_df(bat, torino, "car2go", 4, "avg_bat_before")
#    plot_from_df(bat, torino, "car2go", 6, "avg_bat_before")
#    plot_from_df(bat, torino, "car2go", 6, "avg_bat_before")
#    plot_from_df(bat, torino, "car2go", 8, "avg_bat_before")

#    plot_from_df(bat, torino, "car2go", 2, "avg_bat_before")
#    plot_from_df(bat, torino, "car2go", 4, "avg_bat_before")
#    plot_from_df(bat, torino, "car2go", 6, "avg_bat_before")
#    plot_from_df(bat, torino, "car2go", 8, "avg_bat_before")

#    plot_from_df(bat, torino, "enjoy", 2, "avg_bat_before")
#    plot_from_df(bat, torino, "enjoy", 4, "avg_bat_before")
#    plot_from_df(bat, torino, "enjoy", 6, "avg_bat_before")
#    plot_from_df(bat, torino, "enjoy", 8, "avg_bat_before")
#
#    plot_from_df(res2, torino, "car2go", 2, "avg_bat_after")
#    plot_from_df(res2, torino, "car2go", 4, "avg_bat_after")
#    plot_from_df(res2, torino, "car2go", 6, "avg_bat_after")
#    plot_from_df(res2, torino, "car2go", 8, "avg_bat_after")

#    plot_from_df(res2, torino, "enjoy", 2, "avg_bat_after")
#    plot_from_df(res2, torino, "enjoy", 4, "avg_bat_after")
#    plot_from_df(res2, torino, "enjoy", 6, "avg_bat_after")
#    plot_from_df(res2, torino, "enjoy", 8, "avg_bat_after")

#    plot_from_df(res2, torino, "car2go", 2, "pieni")
#    plot_from_df(res2, torino, "car2go", 4, "pieni")
#    plot_from_df(res2, torino, "car2go", 6, "pieni")
#    plot_from_df(res2, torino, "car2go", 8, "pieni")

#    plot_from_df(res2, torino, "enjoy", 2, "pieni")
#    plot_from_df(res2, torino, "enjoy", 4, "pieni")
#    plot_from_df(res2, torino, "enjoy", 6, "pieni")
#    plot_from_df(res2, torino, "enjoy", 8, "pieni")

    
    
#    fig = plt.figure(figsize=(30,10))
#    ax = fig.gca()
#    ax.set_title("car2go" + " - Solution Improving", fontsize=36)
#    ax.grid()
##    ax.plot(df_to_plot.index, df_to_plot.min_no_deaths.div(len(torino.car2go)), color='blue', label="Min number of deaths")
#    ax.plot(df_to_plot.index, df_to_plot.min_no_deaths.div(len(torino.car2go)), color='blue', label="Min number of deaths")
#
#    ax.legend()
#    for tick in ax.xaxis.get_major_ticks():
#            tick.label.set_fontsize(27) 
#            
#    for tick in ax.yaxis.get_major_ticks():
#            tick.label.set_fontsize(27) 
#    
#    ax.set_xlabel("No. of run", fontsize=36)
#    ax.set_ylabel("Deaths (%)", fontsize=36)
        
        

    
#    zzz = res[res["algorithm"] == "duration_per_zone"]
#    plot_from_df(res, torino, "car2go", ['max_parking', 'max_avg_time' ,'max_time'], 4, "tot" )
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
    
    
#    plot_clorophlet_colorbar_solutions(torino.car2go_parkings_analysis, "car2go", "avg_duration_per_zone")
#    
#    z = 60
#    ppz = 6
#    res = res2
#    provider = 'car2go'
#    
#    mean_c2g = res[(res["provider"] == provider) & (res["algorithm"]=="rnd")]
#
#    mean_c2g = res[(res["provider"] == provider) & (res["algorithm"]=="rnd")]
#    mean_c2g = mean_c2g.groupby(["z","ppz"], as_index=False).mean()
#    mean_c2g['tot_deaths'] = mean_c2g['tot_deaths'].div(len(torino.car2go)).mul(100)
#    mean_c2g = mean_c2g[mean_c2g['ppz']==6]
#
##    mean_c2g = mean_c2g[mean_c2g['z']==z]
#
#    mean_c2g['tot_deaths'] = mean_c2g['tot_deaths'].div(len(torino.car2go)).mul(100)
#    
#    best_deaths = res[(res["provider"] == provider) & (res["algorithm"]=="rnd")]
#    best_deaths = best_deaths.sort_values("tot_deaths").groupby(["z","ppz"], as_index=False).first()
#    best_deaths['tot_deaths'] = best_deaths['tot_deaths'].div(len(torino.car2go)).mul(100)
#    best_deaths = best_deaths[best_deaths['ppz']==6]
#
#    best_deaths = best_deaths[best_deaths['z']==z]


#    best_deaths = best_deaths[best_deaths["ppz"] == ppz]
#    plot_clorophlet_colorbar_solutions(torino, "car2go", "max_parking", z, ppz)
#    plot_clorophlet_colorbar_solutions(torino, "car2go", "max_time", z, ppz)
#    plot_clorophlet_colorbar_solutions(torino, "car2go", "max_avg_time", z, ppz)
#    plot_clorophlet_colorbar_solutions(torino, "car2go", "rnd", z, ppz) 
    
#    plot_clorophlet_colorbar_solutions(torino, "enjoy", "max_parking", z, ppz)
#    plot_clorophlet_colorbar_solutions(torino, "enjoy", "max_time", z, ppz)
#    plot_clorophlet_colorbar_solutions(torino, "enjoy", "max_avg_time", z, ppz)
#    plot_clorophlet_colorbar_solutions(torino, "enjoy", "rnd", z, ppz) 


    


