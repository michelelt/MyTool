import pandas as pd
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
end = datetime.datetime(year, month +2, day, 23, 59, 0)
end2 = datetime.datetime(year, month, day, 23,59,0)

'''
loading data from pickles
'''
#enj_bookings = pd.read_pickle(paths.enjoy_pickle_path, None)
#c2g_bookings = pd.read_pickle(paths.car2go_pickle_path, None)
#enj_parkings = pd.read_pickle(paths.enjoy_parkings_pickle_path, None)
#c2g_parkings = pd.read_pickle(paths.car2go_parkings_pickle_path, None)

'''
statistics on bookigns
-avg distnaces per car
-avg duration per car
'''

## fleet size ##
c2g_fleet = util.get_fleet(c2g_bookings, len(util.get_valid_days(c2g_bookings, start, end)["df"]))
enj_fleet = util.get_fleet(enj_bookings, len(util.get_valid_days(enj_bookings, start, end)["df"]))


## filtering ##
c2g_bookings_filtered = c2g_bookings[
    (c2g_bookings["distance"]> 500)]

c2g_bookings_filtered = c2g_bookings[
    (c2g_bookings["duration"]  > 5) &
    (c2g_bookings["duration"] < 120)
    ]

print c2g_bookings.loc[0, "init_date"].date()

c2g_bookings_filtered["day"] = c2g_bookings_filtered["init_date"].apply(lambda x : x.date())
c2g_bf = pd.DataFrame(c2g_bookings_filtered.groupby("day").count()["_id"]).rename(columns={"_id":"count"})
