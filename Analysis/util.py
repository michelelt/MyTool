import pandas as pd
import datetime
import matplotlib.pyplot as plt
from time import gmtime, strftime
from fiona.crs import from_epsg
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
from math import radians,degrees, cos, sin, asin, sqrt, acos
import matplotlib.pyplot as plt


class Utility (object):

    def __init__ (self):
        return
        
        
    def get_color(self, df):
        provider = self.get_provider(df)
        if provider == "enjoy" :
            return "red"
        else:
            return "blue"
        
    def get_provider(self, df):
        return df.iloc[0].vendor
    
    #return a df with the valid date with entries and #parkings/#bookings
    def get_valid_days(self,df,start,end):
        year = start.year
        month = start.month
        day = start.day
        
        delta = end - start
        
        df = pd.DataFrame(df['init_date'])
        df['date'] = df.init_date.apply(lambda x : x.date())
        df = df.groupby('date').count()
        
        datelist = pd.date_range(pd.datetime(year,month,day), periods=delta.days).tolist()
        dfdays = pd.DataFrame(datelist)
        dfdays['count'] = [0]*len(datelist)
        dfdays.set_index(0, inplace=True)
        df2= dfdays['count'] +  df['init_date']
        df2 = pd.DataFrame(df2)
        df2.fillna(0, inplace=True)
        df2 = df2.rename(columns={0:'entries'})
        
        df2["date"] = df2.index
        df2["date"] = df2.date.apply(lambda x: x.strftime("%A"))
        
        res={}
        res["df"] = df2
        res["valid_days"] = len(df2[df2["entries"]>0])
        tmp = df2[df2["entries"] > 0]
        res["mean"] = tmp.entries.mean()
        res["std"] = tmp.entries.std()
        res["median"]  = tmp.entries.median()
        
        tmp = tmp[(tmp.entries >= res["median"] - res["std"]) &
                  (tmp.entries <= res["median"] + res["std"])
                 ]
        res["cleaned_valid_days"] =len(tmp)

        return res
    
    def clean_df (self, df, column, median, std):
        tmp = df[(df[column] >= median - std) &
                 (df[column] <= median + std)
                ]
        return tmp
    
    def haversine(self, lon1, lat1, lon2, lat2):
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians 
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        # haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        km = 6367 * c
        return int(km*1000)
    
    def step_x(self, meters):
        phi1 = radians(7)
        R = 6367.0
        
        a = radians(float(meters)/(2*R))
        numeratore = 2*(sin(a)*sin((a)))
        denominatore = (cos(phi1)*cos(phi1))
        fract = numeratore/denominatore
        step = acos(1-fract)
        return step
    
    def step_y(self, meters):
        return
    
    def grid_df (self, xmin, xmax, ymin, ymax, s_x, s_y):
        start_x = xmin
        final_x = xmax
        step_x = s_x 
        start_y = ymin
        final_y = ymax
        step_y = s_y
        
        x = start_x
        y= start_y
        newdata = gpd.GeoDataFrame()
        newdata.crs = from_epsg(4326)
        newdata['geometry'] = None
        gdf_row = 0
        while x <= final_x:
            y = start_y
            while y <= final_y:
                p1 = (x,y)
                p2 = (x+step_x,y)
                p3 = (x+step_x, y+step_y)
                p4 = (x, y+step_y)
                q= Polygon([p1,p2,p3,p4])
                newdata.loc[gdf_row, 'geometry'] = q
                gdf_row = gdf_row + 1
                y = y + step_y
            
            x = x + step_x
        
        outfp = r"/home/mc/Scrivania/Tesi/MyTool/SHAPE/grid.shp"
        newdata.to_file(outfp)
        
    def get_fleet(self, df, days):
        df = pd.DataFrame(df.groupby("plate").count()["_id"]).rename(columns={"_id":"bookings_per_car"})
        df = df[df["bookings_per_car"] > days]
        return df        
                    


#meters = 50.0
#phi1 = radians(7)
#R = 6367.0*1000.0
#
#a = radians(meters/(2*R))
#numeratore = 2*(sin(a)*sin((a)))
#denominatore = (cos(phi1)*cos(phi1))
#fract = numeratore/denominatore
#step = acos(1-fract)
#
#u = Utility()
#my_test_m = []
#distances = []
#for test_m in range(0,100000):
#    my_test_m.append(test_m)
#    distances.append(u.haversine(7.0, 45, 7.0+u.step_x(test_m), 45.0))
##print u.step_x(test_m)
##print u.haversine(7.0, 45, 7.0+u.step_x(test_m), 45.0)
#
#df = pd.DataFrame()
#df["distances"] = distances
#df["my_test_m"] = my_test_m
#
#df.plot()
#plt.show()













