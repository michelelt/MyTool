import pandas as pd
import warnings
warnings.filterwarnings('ignore')
import datetime
import matplotlib.pyplot as plt
import matplotlib
from math import *
import numpy as np
import paths as paths
from util import Utility
import time


from DataBaseProxy import DataBaseProxy
#dbp = DataBaseProxy()
util = Utility()

year = 2017
month = 5
day = 6

#km macchine per enjoy e car2go in una settimana
start = datetime.datetime(year, month, day, 0, 0, 0)
end = datetime.datetime(year, month +2, day, 23, 59, 0)

enj_bookings = pd.read_pickle(paths.enjoy_bookings_pickle_path, None)
c2g_bookings = pd.read_pickle(paths.car2go_bookings_pickle_path, None)

enj_parkings = pd.read_pickle(paths.enjoy_parkings_pickle_path, None)
c2g_parkings = pd.read_pickle(paths.car2go_parkings_pickle_path, None)

enj_bookings = enj_bookings[
        (enj_bookings["duration"] <= 120) & 
        (enj_bookings["distance"] >=20) &
        (enj_bookings["distance_dr"] != -1)
        ]
enj_bookings["corr_fact"] = enj_bookings["distance_dr"].div(enj_bookings["distance"])


c2g_bookings = c2g_bookings[
        (c2g_bookings["duration"] <= 120) & 
        (c2g_bookings["distance"] >=20) &
        (c2g_bookings["distance_dr"] != -1)
        ]
c2g_bookings["corr_fact"] = c2g_bookings["distance_dr"].div(c2g_bookings["distance"])




def plot_gd_vs_df(df1, provider, path):
    if provider == 'car2go':
        color = 'blue'
    else:
        color = 'red'
    
    fig = plt.figure(figsize=(10,10))
    ax = fig.gca()
    ax.set_title(provider + " - Google dist. over Eucl. dist.", fontsize=36)
    ax.grid()

    q=0.01
    df1 = df1[
        (df1["corr_fact"] <= df1["corr_fact"].quantile(1-q)) & 
        (df1["corr_fact"] >= df1["corr_fact"].quantile(q) )
        ]
    
    values = [df1["corr_fact"].quantile(0.9), df1["corr_fact"].quantile(0.95), df1["corr_fact"].quantile(0.99)]
    percen = [0.9, 0.95, 0.99]
    print provider
    print values
    print
    ax.hist(df1["corr_fact"], cumulative=True, normed=True, bins=100, color=color)
    
    for i in range(len(values)):
        ax.axhline(percen[i], color='black',linewidth=3)
    
    ax.set_xlabel("Google dist over Eucl.dist", fontsize=36)
    for tick in ax.xaxis.get_major_ticks():
         tick.label.set_fontsize(20) 
    y_ticks = [0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 0.95, 0.99]
    ax.set_yticks(y_ticks)            
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(20) 

    ax.set_ylabel("ECDF", fontsize=36)

    if len(path) > 0 :
        plt.savefig(path,
                    bbox_inches = 'tight')

    plt.show()
    


dir_= "04_data_analysis"
name= "correctvie_factor"

provider = 'enjoy'
path = "/home/mc/Scrivania/Tesi/Writing/figures/"+dir_+"/"+provider+"_"+name
plot_gd_vs_df(enj_bookings, "enjoy", path)


provider = 'car2go'
path = "/home/mc/Scrivania/Tesi/Writing/figures/"+dir_+"/"+provider+"_"+name
plot_gd_vs_df(c2g_bookings, "car2go", path)













