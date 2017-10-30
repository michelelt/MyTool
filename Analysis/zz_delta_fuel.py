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
        (enj_bookings["distance"] >=20)
        ]
enj_bookings["delta_fuel"] = enj_bookings["final_fuel"].sub(enj_bookings["init_fuel"])

c2g_bookings = c2g_bookings[
        (c2g_bookings["duration"] <= 120) & 
        (c2g_bookings["distance"] >=20) 
        ]
c2g_bookings["delta_fuel"] = c2g_bookings["final_fuel"].sub(c2g_bookings["init_fuel"])




def plot_bookig_per_car_cdf(df1, provider, column, path):
    if provider == 'car2go':
        color = 'blue'
    else:
        color = 'red'
    
    title = provider + " - Final fuel minus Init fuel"
    xlabel = "fuel difference"
    
    
    fig = plt.figure(figsize=(10,10))
    ax = fig.gca()
    ax.set_title(title, fontsize=36)
    ax.grid()

    
    values = [df1[column].quantile(0.25), 
              df1[column].quantile(0.50), 
              df1[column].quantile(0.75), 
              df1[column].quantile(0.9), 
              df1[column].quantile(0.99), 
              df1[column].mean(),
              df1[column].median(),
              df1[column].std()
              ]
    print provider
    print values
    print
    ax.hist(df1[column], cumulative=True, normed=True, bins=100, color=color)
    
#    for i in range(len(values)):
#        ax.axhline(percen[i], color='black',linewidth=3)
    
    for tick in ax.xaxis.get_major_ticks():
         tick.label.set_fontsize(20) 
#    y_ticks = [0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 0.95, 0.99]
#    ax.set_yticks(y_ticks)            
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(20) 

    if len(path) > 0 :
        plt.savefig(path,
                    bbox_inches = 'tight',pad_inches = 0.25)
        
    ax.set_xlabel(xlabel, fontsize=36)
    ax.set_ylabel("ECDF", fontsize=36)

    plt.show()
    


dir_= "04_data_analysis"
name= "cdf"

column = "delta_fuel"

provider = 'enjoy'
path = "/home/mc/Scrivania/Tesi/Writing/figures/"+dir_+"/"+provider+"_"+column+"_"+name
plot_bookig_per_car_cdf(enj_bookings, "enjoy", column, "")


provider = 'car2go'
path = "/home/mc/Scrivania/Tesi/Writing/figures/"+dir_+"/"+provider+"_"+column+"_"+name
plot_bookig_per_car_cdf(c2g_bookings, "car2go", column, "")
#
















