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


def plot_from_df (df, torino, provider, ppz, column):
        fig = plt.figure(figsize=(30,10))
        
        if provider == "car2go":
            nob = float(len(torino.car2go))
            noz = float(len(torino.car2go_parkings_analysis))
            noc = float(len(torino.c2g_fleet))
            cap = 17.6
        else:
            nob = len(torino.enjoy)
            noz = float(len(torino.enjoy_parkings_analysis))

        colors = {"max_avg_time":"red", "max_parking":"blue", "max_time": "black", "best_rnd": "gray", "mean_rnd":"green"}
        markers = {"max_avg_time":"o", "max_parking":"x", "max_time": "^", "best_rnd": "d", "mean_rnd":"+"}
        labels = {"max_avg_time":"max average parking time", "max_parking":"max number of parking", "max_time": "max parking time", "best_rnd": "best random", "mean_rnd":" average random"}
        div_facts = {"tot_deaths":nob,  "avg_bat_before": cap, "avg_bat_after": cap, "pieni": nob}
        
        titles  = {"tot_deaths": " - Battery expir. prob. vs Zone coverage - ppz=",
                   "avg_bat_before": " - Avg. beofre charingig Soc vs Zone coverage - ppz=", 
                   "avg_bat_after": " - Aveg. after charingig Soc vs Zone coverage - ppz=", 
                   "pieni": " - Charging probability vs Zone Coverage - ppz="}
        
        y_labels  = {"tot_deaths": "Battery exausted(%)",
                   "avg_bat_before": "Avg. SoC - Before charging(%)", 
                   "avg_bat_after": "Avg. SoC - After charging(%)", 
                   "pieni": "Charging probability(%)"}
        
        saving_name  = {"tot_deaths": "bat_exaust_",
                   "avg_bat_before": "SoC_Before_", 
                   "avg_bat_after": "Soc_After_", 
                   "pieni": "charging_"}

#        res = df[(df["z"]>=80) & (df["z"]<=100)]
        res = df
        mean_c2g = res[(res["provider"] == provider) & (res["algorithm"]=="rnd")]
        mean_c2g = mean_c2g.groupby(["z","ppz"], as_index=False).mean()
        mean_c2g = mean_c2g[mean_c2g["ppz"] == ppz]
        
        best_deaths = res[(res["provider"] == provider) & (res["algorithm"]=="rnd")]
        best_deaths = best_deaths.sort_values("tot_deaths").groupby(["z","ppz"], as_index=False).first()
        best_deaths = best_deaths[best_deaths["ppz"] == ppz]
        
        det_alg = res[(res["provider"] == provider) & (res["ppz"] == ppz) & (res["algorithm"]!="rnd")]
        algs = det_alg["algorithm"].unique().astype(str)
        max_parking = det_alg[det_alg["algorithm"] == str(algs[0])]
        max_avg_time = det_alg[det_alg["algorithm"] == algs[1]]
        max_time = det_alg[det_alg["algorithm"] == algs[2]]
        
        ax = fig.gca()
        
        ax.set_title(provider + titles[column]+str(ppz), fontsize=36)

        ax.grid()
        if len(res['algorithm'].unique()) >3:
            ax.plot(mean_c2g["z"], mean_c2g[column].div(div_facts[column]), color=colors["mean_rnd"], marker=markers["mean_rnd"], label=labels["mean_rnd"])
            ax.plot(best_deaths["z"], best_deaths[column].div(div_facts[column]), color=colors["best_rnd"], marker=markers["best_rnd"], label=labels["best_rnd"])
            ax.plot(max_parking["z"], max_parking[column].div(div_facts[column]), color=colors["max_parking"], marker=markers["max_parking"], label=labels["max_parking"])
            ax.plot(max_avg_time["z"], max_avg_time[column].div(div_facts[column]), color=colors["max_avg_time"], marker=markers["max_avg_time"], label=labels["max_avg_time"])
            ax.plot(max_time["z"], max_time[column].div(div_facts[column]), color=colors["max_time"], marker=markers["max_time"], label=labels["max_time"])
            my_t = range( 10, 175, 10)
            my_ticks = [str(("{0:.2f}".format(x/noz))) for x in my_t ]
            labels = [""] * len(my_t)
            for i in range(0,len(labels)):
                if i%2 == 0:
                    labels[i] == ""
                else:
                    labels[i] = my_ticks[i]
            
            plt.xticks(my_t, labels)

        else :
            ax.plot(max_parking["z"], max_parking[column].div(div_facts[column]), color=colors["max_parking"], marker=markers["max_parking"], label=labels["max_parking"])
            ax.plot(max_avg_time["z"], max_avg_time[column].div(div_facts[column]), color=colors["max_avg_time"], marker=markers["max_avg_time"], label=labels["max_avg_time"])
            ax.plot(max_time["z"], max_time[column].div(div_facts[column]), color=colors["max_time"], marker=markers["max_time"], label=labels["max_time"])
            my_t = [30,60,90,120,150,180,210,238]
            my_ticks = [str(("{0:.2f}".format(x/noz))) for x in my_t ]
            labels = [""] * len(my_t)
            for i in range(0,len(labels)):
                labels[i] = my_ticks[i]
            
            plt.xticks(my_t, labels)

                
#        print my_ticks, len(my_ticks)
        
#        ax.set_xticklabels(labels)
        for tick in ax.xaxis.get_major_ticks():
                tick.label.set_fontsize(27) 
                
        for tick in ax.yaxis.get_major_ticks():
                tick.label.set_fontsize(27) 
        
        ax.set_xlabel("Zones coverage(%)", fontsize=36)
        ax.set_ylabel(y_labels[column], fontsize=36)
        

 
        plt.legend(fontsize=18)
        plt.savefig(paths.plots_path9+provider+"_"+saving_name[column]+str(ppz), bbox_inches = 'tight',pad_inches = 0.25)
        plt.show()
        
        
def plot_from_df_algorithm (df, torino, provider, column):
        colors = {2:"red", 4:"blue", 6: "black", 8: "gray"}
        markers = {2:"o", 4:"x", 6: "^", 8: "d"}
        labels = {2:"ppz = 2", 4:"ppz = 4", 6: "ppz = 6", 8:"ppz = 8",}
        alg_names = {"max_avg_time":"Max average parking time", "max_parking":"Max number of parking", "max_time": "Max parking time", "best_rnd": "Best random", "mean_rnd":" Average random(209 run)"}
    
        fig = plt.figure(figsize=(30,10))
        ax = fig.gca()
        ax.set_title(provider + " - " + alg_names[column] + " performances", fontsize=36)
        ax.grid()
        
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
            
        df2 = df[(df["algorithm"] == column) & (df["ppz"] ==2)]
        df4 = df[(df["algorithm"] == column) & (df["ppz"] ==4)]
        df6 = df[(df["algorithm"] == column) & (df["ppz"] ==6)]
        df8 = df[(df["algorithm"] == column) & (df["ppz"] ==8)]
            
        ax.plot(df2["z"], df2["tot_deaths"].div(nob), color=colors[2], marker=markers[2], label=labels[2])
        ax.plot(df4["z"], df4["tot_deaths"].div(nob), color=colors[4], marker=markers[4], label=labels[4])
        ax.plot(df6["z"], df6["tot_deaths"].div(nob), color=colors[6], marker=markers[6], label=labels[6])
        ax.plot(df8["z"], df8["tot_deaths"].div(nob), color=colors[8], marker=markers[8], label=labels[8])

        my_t = range( 10, 175, 10)
#        print my_ticks, len(my_ticks)
        my_ticks = [str(("{0:.2f}".format(x/noz))) for x in my_t ]
        print my_ticks
        labels = [""] * 17
        for i in range(0,len(labels)):
            if i%2 == 0:
                labels[i] == ""
            else:
                labels[i] = my_ticks[i]
        
        plt.xticks(my_t, labels)
#        ax.set_xticklabels(labels)
        for tick in ax.xaxis.get_major_ticks():
                tick.label.set_fontsize(27) 
                
        for tick in ax.yaxis.get_major_ticks():
                tick.label.set_fontsize(27) 
        
        ax.set_xlabel("Zones(%)", fontsize=36)
        ax.set_ylabel("Battery exausted(%)", fontsize=36)
        

 
        plt.legend(fontsize=18)
#        plt.savefig(paths.plots_path9+provider+"_"+column+"_performances", bbox_inches = 'tight',pad_inches = 0.25)
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
#    
    print len(torino.car2go_parkings_analysis)

 
#    print "END"
    ## rebuilding the resutls
    res2 = pd.DataFrame()
    root = "/home/mc/Scrivania/Tesi/MyTool/pickles/"
    myDir = "sym_res_rnd/"
    name = "rnd_"
    for j in range(0,56):
        res2= res2.append(pd.read_pickle(root+myDir+name+str(j)), ignore_index=True)
    
    myDir = "sym_res_rnd_c2g/"
    name = "res_rnd"
    for j in range(0,200):
        res2 = res2.append(pd.read_pickle(root+myDir+name+str(j)), ignore_index=True)
        
    myDir = "sym_res_3_alg_no_rand_final/"
    name = "sym_res_3_alg_no_rand_final3_alg_fin_"
    for j in range(0,24):
        res2 = res2.append(pd.read_pickle(root+myDir+name+str(j)), ignore_index=True)
    
    res3 = pd.DataFrame()
    myDir = "sym_res_200_ppz_8/"
    name = "final_df"
    res3 = res3.append(pd.read_pickle(root+myDir+name), ignore_index=True)
    
    res4 = pd.DataFrame()
    myDir = "sym_res_final_3A_209_9_rnd/"
    name = "209_c2g_9_enj"
    res4 = res3.append(pd.read_pickle(root+myDir+name), ignore_index=True)
    
    df_to_plot=pd.DataFrame(columns=["min_no_deaths"])
    for i, row in res3.iterrows():
        df = res3.head(n=i+1)
#        df_to_plot.loc[i,"n_run"] = i
        df_to_plot.loc[i+1,"min_no_deaths"] = min(df["tot_deaths"])
    
    '''
    200 random ppz=4 zones = 60 per veere come migliora il rnd
    '''
    res5 = pd.DataFrame()
    for i in range(0,200):
        res5 = res5.append(pd.read_pickle(paths.sym_path_rnd_200_ppz_4+str(i)), ignore_index=True)
    
    df_to_plot2=pd.DataFrame(columns=["min_no_deaths"])
    for i, row in res5.iterrows():
        df = res5.head(n=i+1)
#        df_to_plot.loc[i,"n_run"] = i
        df_to_plot2.loc[i+1,"min_no_deaths"] = min(df["tot_deaths"])/float(len(torino.car2go))
    
    '''
    SOC study
    '''
    res6 = pd.DataFrame()
    for i in range (0,3):
        res6 = res6.append(pd.read_pickle(paths.sym_path_SOC+str(i)), ignore_index=True)
        

        
#    plot_from_df(res4, torino, "car2go", 2, "avg_bat_after")
#    plot_from_df(res4, torino, "car2go", 4, "avg_bat_after")
#    plot_from_df(res4, torino, "car2go", 6, "avg_bat_after")
#    plot_from_df(res4, torino, "car2go", 8, "avg_bat_after")

    plot_from_df(res6, torino, "car2go", 4, "avg_bat_before")
    plot_from_df(res6, torino, "car2go", 4, "avg_bat_after")

    
#    plot_from_df_algorithm (res4, torino, "car2go", "max_parking") 
#    plot_from_df_algorithm (res4, torino, "car2go", "max_time") 
#    plot_from_df_algorithm (res4, torino, "car2go", "max_avg_time") 
#    plot_from_df_algorithm (res4, torino, "car2go", "best_rnd") 
#    plot_from_df_algorithm (res4, torino, "car2go", "mean_rnd") 
    
    
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
        
        
        
        
    
    
#    plot_from_df(res, torino, 'car2go', 2)
#    plot_from_df(res, torino, 'car2go', 4)
#    plot_from_df(res, torino, 'car2go', 6)
#    plot_from_df(res, torino, 'car2go', 8)

#    plot_from_df(res, torino, 'enjoy', 2)
#    plot_from_df(res, torino, 'enjoy', 4)
#    plot_from_df(res, torino, 'enjoy', 6)
#    plot_from_df(res, torino, 'enjoy', 8) 

    
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
    
    

#    plot_clorophlet_colorbar_solutions(torino.car2go_parkings_analysis, "car2go", "duration_per_zone")
#    plot_clorophlet_colorbar_solutions(torino.car2go_parkings_analysis, "car2go", "avg_duration_per_zone")
#    
#    plot_clorophlet_colorbar_solutions(torino.enjoy_parkings_analysis, "enjoy", "parking_per_zone")
#    plot_clorophlet_colorbar_solutions(torino.enjoy_parkings_analysis, "enjoy", "duration_per_zone")
#    plot_clorophlet_colorbar_solutions(torino.enjoy_parkings_analysis, "enjoy", "avg_duration_per_zone") 

    
    

    


