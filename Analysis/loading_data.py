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

start = datetime.datetime(year, month, day, 0, 0, 0)
end = datetime.datetime(year, month +2 , day, 23, 59, 0)

## bookings ##
c2g_bookings = dbp.query_bookings_df("car2go","Torino", start, end)
c2g_bookings.to_pickle(paths.car2go_booking_pickle_path)

enj_bookings = dbp.query_bookings_df("enjoy","Torino", start, end)
enj_bookings.to_pickle(paths.enjoy_booking_pickle_path)


##parkings
c2g_parkings = dbp.query_parkings_df("car2go","Torino", start, end)
c2g_parkings.to_pickle(paths.car2go_parkings_pickle_path)

enj_parkings = dbp.query_parkings_df("enjoy","Torino", start, end)
enj_parkings.to_pickle(paths.enjoy_parkings_pickle_path)





