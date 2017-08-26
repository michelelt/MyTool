import pandas as pd
import geopandas as gpd
import sys
sys.path.insert(0, '/home/mc/Scrivania/Tesi/MyTool/Analysis/')
import datetime
import paths as paths
sys.path.insert(0, '/home/mc/Scrivania/Tesi/MyTool/Analysis/simulator')
from util import Utility
from car import Car


## time interval ##
year = 2017
month = 5
day = 6
start = datetime.datetime(year, month, day, 0, 0, 0)
end = datetime.datetime(year, month +2, day, 23, 59, 0)

## data loading ##
enj_bookings = pd.read_pickle(paths.enjoy_pickle_path, None)
c2g_bookings = pd.read_pickle(paths.car2go_pickle_path, None)

enj_parkings = pd.read_pickle(paths.enjoy_parkings_pickle_path, None)
c2g_parkings = pd.read_pickle(paths.car2go_parkings_pickle_path, None)


## data cleaning ##
q = 0.025
c2g_bookings_filtered = c2g_bookings[
        (c2g_bookings["duration"] <= c2g_bookings["duration"].quantile(1-q)) &
        (c2g_bookings["duration"] >= c2g_bookings["duration"].quantile(q) ) &
        (c2g_bookings["distance"] >= 20)
        ]
#q=q*10
enj_bookings_filtered = enj_bookings[
        (enj_bookings["duration"] <= enj_bookings["duration"].quantile(1-q)) &        
        (enj_bookings["duration"] >= enj_bookings["duration"].quantile(q) ) &
        (enj_bookings["distance"] >= 20)
        ]

###should be unuseful, i can extract per index -> cronologically distributed
### init temporal index  - iti ##
#c2g_bookings_filtered["iti"] = c2g_bookings_filtered.init_date.apply(lambda x : x.strftime("%Y-%m-%d %H:%M"))
#enj_bookings_filtered["iti"] = enj_bookings_filtered.init_date.apply(lambda x : x.strftime("%Y-%m-%d %H:%M"))
#
### final temporal index - fti ##
#c2g_bookings_filtered["fti"] = c2g_bookings_filtered.init_date.apply(lambda x : x.strftime("%Y-%m-%d %H:%M"))
#enj_bookings_filtered["fti"] = enj_bookings_filtered.init_date.apply(lambda x : x.strftime("%Y-%m-%d %H:%M"))


## fleet acquiring ##
util = Utility()
c2g_fleet = util.get_fleet(c2g_bookings_filtered, 
                           util.get_valid_days(c2g_bookings_filtered, start, end)["valid_days"])

enj_fleet = util.get_fleet(enj_bookings_filtered, 
                           util.get_valid_days(enj_bookings_filtered, start, end)["valid_days"])

cars_c2g={}
cars_enj={}

#cars creations
c2g_plates = c2g_fleet.index
enj_plates = enj_fleet.index

for plate in c2g_plates:
    cars_c2g[plate] = Car(plate,"car2go","")
    
    
for plate in enj_plates:
    cars_enj[plate] = Car(plate,"enjoy","")


    





















