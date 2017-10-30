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


from DataBaseProxy import DataBaseProxy
dbp = DataBaseProxy()
util = Utility()

year = 2017
month = 5
day = 6

#km macchine per enjoy e car2go in una settimana
start = datetime.datetime(year, month, day, 0, 0, 0)
end = datetime.datetime(year, month, day, 23, 59, 0)

#enjoy = dbp.query_bookings_df("enjoy","Torino", start, end)
#car2go = dbp.query_bookings_df("car2go","Torino", start, end)

'''
loading data from pickles
'''
enj_bookings = pd.read_pickle(paths.enjoy_bookings_pickle_path, None)
c2g_bookings = pd.read_pickle(paths.car2go_bookings_pickle_path, None)

#enj_parkings = pd.read_pickle(paths.enjoy_parkings_pickle_path, None)
#c2g_parkings = pd.read_pickle(paths.car2go_parkings_pickle_path, None)

#fig = plt.figure(figsize=(10,10))
#ax = fig.gca()
#c2g_bookings = c2g_bookings[c2g_bookings.start_lat > 0]
#caselle = c2g_bookings[c2g_bookings["init_address"].str.contains("Caselle")]
#c2g_bookings = c2g_bookings[c2g_bookings["start_lat"] < 45.17]
#ax.scatter(c2g_bookings["start_lon"], c2g_bookings["start_lat"], color='blue', s=0.1)
#ax.scatter(caselle["start_lon"], caselle["start_lat"], color='blue', s=50)
#plt.show()

def operative_area(df, provider, path):
    df = df[df["start_lat"] > 0 ]
    df = df[df["start_lon"] > 0 ]

    if provider == 'car2go':
        color= 'blue'
    else:
        color = 'red'
        
    fig = plt.figure(figsize=(10,10))
    ax = fig.gca()
#    ax.set_xticks([])
#    ax.set_yticks([])
    ax.set_title(provider + " - Operative area", fontsize=36)
    ax.set_xlabel("Longitude [$^\circ$]", fontsize=36)
    ax.set_ylabel("Latitude [$^\circ$]", fontsize=36)
    ax.grid()
    
    df = df[df.start_lat > 0]
    caselle = df[df["init_address"].str.contains("Caselle")]
    df = df[df["start_lat"] < 45.17]
    ax.scatter(df["start_lon"], df["start_lat"], color=color, s=0.1)
    ax.scatter(caselle["start_lon"], caselle["start_lat"], color=color, s=50)
    
    for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(24) 
            
    for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(24)     
    
    if len(path) > 0:
        plt.savefig("/home/mc/Scrivania/Tesi/toptesi/figures/03_data_charact/"+provider+"_operative")
    
    plt.show()
    
operative_area(c2g_bookings, 'car2go', "yes")
operative_area(enj_bookings, 'enjoy',"yes")


#





#'''
#statistics on bookigns
#-avg distnaces per car
#-avg duration per car
#'''
#
### filtering ##
#
#c2g_bookings_filtered = c2g_bookings[
#        (c2g_bookings["duration"] <= 120) &
#        (c2g_bookings["distance"] >= 20)
#        ]
#
#enj_bookings_filtered = enj_bookings[
#        (enj_bookings["duration"] <= 120) &        
#        (enj_bookings["distance"] >= 20)
#        ]
#
#
#
### fleet size ##
#c2g_fleet = util.get_fleet(c2g_bookings_filtered, 
#                           util.get_valid_days(c2g_bookings_filtered, start, end)["valid_days"])
#
#enj_fleet = util.get_fleet(enj_bookings_filtered, 
#                           util.get_valid_days(enj_bookings_filtered, start, end)["valid_days"])
#
#
### entries per day ##
#c2g_bookings_filtered["day"] = c2g_bookings_filtered["init_date"].apply(lambda x : x.date())
#c2g_bf = pd.DataFrame(c2g_bookings_filtered.groupby("day").count()["_id"]).rename(columns={"_id":"entry_per_day"})
#
#enj_bookings_filtered["day"] = enj_bookings_filtered["init_date"].apply(lambda x : x.date())
#enj_bf = pd.DataFrame(enj_bookings_filtered.groupby("day").count()["_id"]).rename(columns={"_id":"entry_per_day"})
#
### avg freq per car - smaller than data in reports ##
#c2g_avg_freq = float(
#            float(len(c2g_bookings_filtered))/
#            float(len(c2g_fleet))/
#            float(util.get_valid_days(c2g_bookings_filtered, start, end)["valid_days"])
#            )
#
#enj_avg_freq = float(
#            float(len(enj_bookings_filtered))/
#            float(len(enj_fleet))/
#            float(util.get_valid_days(enj_bookings_filtered, start, end)["valid_days"])
#            )
#print 
#print "c2g - freq per car " + str(c2g_avg_freq)
#print "enj - freq per car " + str(enj_avg_freq)
#print
#
### duration per booking ##
## removing the big quantiles -> outliers #
#
#print "Car2go - Duration Per Trip"
#print " mean[min]: " + str(float(sum(c2g_bookings_filtered.duration))/ float(len(c2g_bookings_filtered)))
#print " median[min]: " + str(c2g_bookings_filtered.duration.median())
#print " std[min]: " + str(c2g_bookings_filtered.duration.std())
#print
#print "Car2go - Trip duration per day"
#print " mean[min]: " + str(float(sum(c2g_bookings_filtered.duration)*c2g_avg_freq)/ float(len(c2g_bookings_filtered)))
#print " median[min]: " + str(c2g_bookings_filtered.duration.median()*c2g_avg_freq)
#print
#print "Enjoy - Duration Per Trip"
#print " mean[min]: " + str(float(sum(enj_bookings_filtered.duration))/ float(len(enj_bookings_filtered)))
#print " median[min]: " + str(enj_bookings_filtered.duration.median())
#print " std[min]: " + str(enj_bookings_filtered.duration.std())
#print
#print "Enjoy - Trip duration per day"
#print " mean[min]: " + str(float(sum(c2g_bookings_filtered.duration)*enj_avg_freq)/ float(len(c2g_bookings_filtered)))
#print " median[min]: " + str(c2g_bookings_filtered.duration.median()*enj_avg_freq)
#print
#
### factor correction between gd/ed ##
#c2g_dist = c2g_bookings_filtered[
#        (c2g_bookings_filtered["distance"] > 0) &
#        (c2g_bookings_filtered["distance_dr"] > 0)
#        ]
#c2g_dist["ed_over_gd"] = c2g_dist["distance_dr"] / c2g_dist["distance"]
#c2g_dist = c2g_dist[
#        c2g_dist["ed_over_gd"] < 7
#         ]
#
#enj_dist = enj_bookings_filtered[
#        (enj_bookings_filtered["distance"] > 0) &
#        (enj_bookings_filtered["distance_dr"] > 0)
#        ]
#enj_dist["ed_over_gd"] = enj_dist["distance_dr"] / enj_dist["distance"]
#enj_dist = enj_dist[
#        enj_dist["ed_over_gd"] < 7
#         ]

#print "Car2go - Corrective factors "
#print " 0.90: " + str(c2g_dist.ed_over_gd.quantile(0.90))
#print " 0.95: " + str(c2g_dist.ed_over_gd.quantile(0.95))
#print " 0.99: " + str(c2g_dist.ed_over_gd.quantile(0.99))
#print
#print "Enjoy - Corrective factors "
#print " 0.90: " + str(enj_dist.ed_over_gd.quantile(0.90))
#print " 0.95: " + str(enj_dist.ed_over_gd.quantile(0.95))
#print " 0.99: " + str(enj_dist.ed_over_gd.quantile(0.99))
#print
#
### bookings distances ##
#print "Car2go distances"
#print " mean[km]: " + str(c2g_bookings_filtered.distance.mean()/1000)
#print " mean google[km]: " + str(c2g_dist.distance_dr.mean()/1000)
#print " mean * factor: " + str(c2g_bookings_filtered.distance.mean()*c2g_dist.ed_over_gd.quantile(0.90))
#
#print " median[km]: " + str(c2g_bookings_filtered.distance.median()/1000)
#print " median google[km]: " + str(c2g_dist.distance_dr.median()/1000)
#print " median * factor: " + str(c2g_bookings_filtered.distance.median()*c2g_dist.ed_over_gd.quantile(0.90))
#print
#
#print "Enjoy distances"
#print " mean[km]: " + str(enj_bookings_filtered.distance.mean()/1000)
#print " mean google[km]: " + str(enj_dist.distance_dr.mean()/1000)
#print " mean * factor: " + str(enj_bookings_filtered.distance.mean()*enj_dist.ed_over_gd.quantile(0.90))
#
#print " median[km]: " + str(enj_bookings_filtered.distance.median()/1000)
#print " median google[km]: " + str(enj_dist.distance_dr.median()/1000)
#print " median * factor: " + str(enj_bookings_filtered.distance.median()*enj_dist.ed_over_gd.quantile(0.90))
#print
#
#
#'''
#statistics on parkigns
#- duration
#'''
#
### Derivated analysis ##
#print "Car2go - parking duration from bookings"
#print  "mean[h]: " + str(24-(float(sum(c2g_bookings_filtered.duration)*c2g_avg_freq)/ float(60*len(c2g_bookings_filtered))))
#print " median[h]: " + str( 24 - (c2g_bookings_filtered.duration.median()*c2g_avg_freq/60))
#print
#print "Enjoy - parking duration from bookings"
#print  "mean[h]: " + str(24-(float(sum(enj_bookings_filtered.duration)*enj_avg_freq)/ float(60*len(enj_bookings_filtered))))
#print " median[h]: " + str( 24 - (enj_bookings_filtered.duration.median()*enj_avg_freq/60))
#print
#
### filtering ##
#q=0.01
#c2g_parkings_filtered = c2g_parkings[
#        (c2g_parkings["duration"] <= c2g_parkings["duration"].quantile(1-q)) & 
#        (c2g_parkings["duration"] >= 20 )
#        ]
#tail = c2g_parkings_filtered[
#        c2g_parkings_filtered["duration"] >= c2g_parkings["duration"].quantile(1-q)
#        ]
#len(tail)
#
#
#
#q=0.01
#enj_parkings_filtered = enj_parkings[
#        (enj_parkings["duration"] <= enj_parkings["duration"].quantile(1-q)) & 
#        (enj_parkings["duration"] >= enj_parkings["duration"].quantile(q))
#        ]
##enj_parkings_filtered.duration.hist(cumulative=True,bins=200)
#
#
#
#c2g_avg_freq2 = float(
#            float(len(c2g_parkings_filtered.duration))/
#            float(len(c2g_fleet))/
#            float(util.get_valid_days(c2g_parkings_filtered, start, end)["valid_days"])
#            )
#
#mean = float(
#            float(sum(c2g_parkings_filtered.duration))/
#            float(len(c2g_fleet))/
#            float(util.get_valid_days(c2g_parkings_filtered, start, end)["valid_days"])
#            )
#
#print "Car2go - parking duration from data"
#print " mean[h]: " + str(c2g_parkings_filtered["duration"].mean()*c2g_avg_freq2/60)
#print " median[h]: " + str(c2g_parkings_filtered["duration"].median()*c2g_avg_freq2/60)
#print " std[h]: " + str(c2g_parkings_filtered["duration"].std()/60)
#print
#
#print "Car2go - parking duration from data"
#print " mean[h]: " + str(c2g_parkings_filtered["duration"].mean()*c2g_avg_freq2/60)
#print " median[h]: " + str(c2g_parkings_filtered["duration"].median()*c2g_avg_freq2/60)
#print " std[h]: " + str(c2g_parkings_filtered["duration"].std()/60)
#print











 




































