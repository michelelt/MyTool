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

enj_data = util.get_valid_days(enj_bookings, start,end)
c2g_data = util.get_valid_days(c2g_bookings, start, end)

enj_data_b = util.get_valid_days(enj_parkings, start,end)
c2g_data_b = util.get_valid_days(c2g_parkings, start, end)



#enj_cars = len(enj_bookings.plate.unique())
#enj_bookings_len = len(pd.read_pickle(paths.enjoy_bookings_pickle_path))
#enj_parkings_len = len(pd.read_pickle(paths.enjoy_parkings_pickle_path))
#
#enj_days = float(enj_data["valid_days"])
#
#print "enj B/D " + str(enj_bookings_len/enj_days)
#print "enj_B/D/C " + str(enj_bookings_len/enj_days/enj_cars)
#print "enj P/D " + str(enj_parkings_len/enj_days)
#print "enj P/D/C " + str(enj_parkings_len/enj_days/enj_cars)
#print
#
#c2g_cars = len(c2g_bookings.plate.unique())
#c2g_bookings_len = len(pd.read_pickle(paths.car2go_bookings_pickle_path))
#c2g_parkings_len = len(pd.read_pickle(paths.car2go_parkings_pickle_path))
#c2g_days = float(c2g_data["valid_days"])
#
#print "c2g B/D " + str(c2g_bookings_len/c2g_days)
#print "c2g B/D/C " + str(c2g_bookings_len/c2g_days/c2g_cars)
#print "c2g P/D " + str(c2g_parkings_len/c2g_days)
#print "c2g P/D/C " + str(c2g_parkings_len/c2g_days/c2g_cars)



def plot_valid_days(df1, provider, path):
    if provider == 'car2go':
        color = 'blue'
    else:
        color = 'red'
        
    months_dict = {"mag": "May", "giu": "Jun", "lug":"Jul"}
    
    fig = plt.figure(figsize=(30,10))
    
    ax = fig.gca()
    ax.set_title(provider + " - Valid Days", fontsize=36)
    ax.grid()
    
    width=0.5
    ind = np.arange(len(df1.index))
    ax.bar(ind, df1["entries"], width, color=color)
    
    ax.set_ylabel("Entries per day", fontsize=36)
    
    ticks = [datetime.date.today()]*len(df1.index)
    ticks[0:len(df1.index):5] = df1.index[range(0,len(ind),5)]
    for i in range(len(ticks)):
        if i % 5 == 0 :
            t = ticks[i]
            date = t.strftime("%d %b %Y").split(" ")
            date[1] = months_dict[date[1]]
            ticks[i] = str(date[0]) + " " + str(date[1]) + " " + str(date[2])
            
        else:
            ticks[i] = ""

    ax.set_xticks(ind + width /32)
    ax.set_xticklabels(ticks, rotation=30)
#    
    for tick in ax.xaxis.get_major_ticks():
         tick.label.set_fontsize(20)
                
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(20) 

    fig.autofmt_xdate()
    plt.savefig(path,
                bbox_inches = 'tight')

    plt.show()
    
#plot_valid_days(enj_data['df'], 'enjoy')
#plot_valid_days(c2g_data['df'], 'car2go')

#enj_bookings = enj_bookings[
#        (enj_bookings["duration"] <= 120) & 
#        (enj_bookings["distance"] >=20)
#        ]
#
#c2g_bookings = c2g_bookings[
#        (c2g_bookings["duration"] <= 120) & 
#        (c2g_bookings["distance"] >=20)
#        ]



dir_= "03_data_charact/"
name= "valid_days"

provider = 'enjoy'
path = "/home/mc/Scrivania/Tesi/toptesi/figures/" + dir_ +provider+"_"+name
enj_data = util.get_valid_days(enj_bookings, start,end)
plot_valid_days(enj_data['df'], 'enjoy', path)
enj_data["filtered_fleet"] = util.get_fleet(enj_bookings, 61)

provider = 'car2go'
path = "/home/mc/Scrivania/Tesi/toptesi/figures/" + dir_ + provider+"_"+name
c2g_data = util.get_valid_days(c2g_bookings, start,end)
plot_valid_days(c2g_data['df'], 'car2go', path)
c2g_data["filtered_fleet"] = util.get_fleet(c2g_bookings, 61)














