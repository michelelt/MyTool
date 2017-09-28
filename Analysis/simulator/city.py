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
from shapely.geometry import Point, Polygon
from station import Station
import threading
from multiprocessing import Process
import matplotlib.pyplot as plt
from matplotlib import colors



util = Utility()

def pointfy (lon, lat):
    return pd.Series(Point(float(lon), float(lat)))


class City (object):
    def __init__(self, name, start, end):
        self.name = name
        self.start = start
        self.end = end
        self.days = (end-start).days + 1
        self.crs = {"init": "epsg:4326"}
        self.turin = gpd.read_file("../../SHAPE/grid500.dbf").to_crs(self.crs)
        self.stations={}


        return
        
    def parkings_analysis(self, df, days=0):
        g = pd.DataFrame(df.groupby("zone").count()["plate"]).rename(columns={"plate":"parking_per_zone"})
        g = g[g["parking_per_zone"] >= days]
        g["duration_per_zone"] = df.groupby("zone").sum()
        g["avg_duration_per_zone"] = 1.0* g["duration_per_zone"] /60/g["parking_per_zone"]
        g.index = g.index.astype(int)
        g["geometry"] = self.turin["geometry"]
        out = gpd.GeoDataFrame(g)
        return out
        
    
    def load_parkings(self, provider):
        if provider == "car2go":
            if os.path.exists(paths.car2go_parkings_pickle_path_zoned):
                self.car2go_parkings = pd.read_pickle(paths.car2go_parkings_pickle_path_zoned)
                self.car2go_parkings = self.car2go_parkings.sort_values("init_time").dropna()
            else :
                df1 = self.car2go
                self.car2go_parkings = pd.DataFrame(columns = ["plate", "city", "geometry", "init_time", "final_time", "duration", "zone"])
                row =0
                for plate in set(df1.plate):
                    car_bookings = df1[df1["plate"] == plate].sort_values("init_time").reset_index()
                    for i in range(len(car_bookings)-1) :
                        b2 = car_bookings.loc[i+1]
                        b1 = car_bookings.loc[i]
                        s = pd.Series()
                        s = b1[["plate", "city", "geometry"]]
                        s["init_time"]= b1["final_time"]
                        s["final_time"] = b2["init_time"]
                        s["duration"] = float(b2["init_time"] - b1["final_time"]) / 60
                        s["zone"] = b1["final_zone"]
                        self.car2go_parkings.loc[row] = s
                        row +=1
                self.car2go_parkings.to_pickle(paths.car2go_parkings_pickle_path_zoned).sort_values("init_time").dropna()
                return


        if provider == "enjoy":
            if os.path.exists(paths.enjoy_parkings_pickle_path_zoned):
                self.enjoy_parkings = pd.read_pickle(paths.enjoy_parkings_pickle_path_zoned)
                self.enjoy_parkings = self.enjoy_parkings.sort_values("init_time").dropna()
            else :
                df1 = self.enjoy
                self.enjoy_parkings = pd.DataFrame(columns = ["plate", "city", "geometry", "init_time", "final_time", "duration", "zone"])
                row =0
                for plate in list(set(df1.plate)):
                    car_bookings = df1[df1["plate"] == plate].sort_values("init_time").reset_index()
                    for i in range(len(car_bookings)-1) :
                        b2 = car_bookings.loc[i+1]
                        b1 = car_bookings.loc[i]
                        s = pd.Series()
                        s = b1[["plate", "city", "geometry"]]
                        s["init_time"]= b1["final_time"]
                        s["final_time"] = b2["init_time"]
                        s["duration"] = float(b2["init_time"] - b1["final_time"]) / 60
                        s["zone"] = b1["final_zone"]
                        self.enjoy_parkings.loc[row] = s
                        row +=1
                        if row % 1000 ==0:
                            print row
                self.enjoy_parkings.to_pickle(paths.enjoy_parkings_pickle_path_zoned).sort_values("init_time").dropna()
                return
                        

    
    def set_c2g_datasets(self, from_pickle=True):
        if from_pickle == True:
            df = pd.read_pickle(paths.car2go_bookings_pickle_path, None)
            df = df[(df["duration"] <= 120) &(df["distance"] >= 20)]
            self.car2go = gpd.GeoDataFrame(df, crs=self.crs)
            self.assign_zone_numbers("car2go")
        else:
            dbp = DataBaseProxy()
            df = dbp.query_bookings_df("car2go",self.name, self.start, self.end)
            df.to_pickle(paths.car2go_bookings_pickle_path, None)
            df = df[(df["duration"] <= 120) &(df["distance"] >= 20)]
            self.car2go = gpd.GeoDataFrame(df, crs=self.crs)
            self.assign_zone_numbers("car2go")
        
        self.car2go = self.car2go.dropna(axis=0).sort_values("init_time")
        self.load_parkings("car2go")
        self.car2go_parkings_analysis = self.parkings_analysis(self.car2go_parkings, days=self.days)
        self.car2go_stations_mp = self.car2go_parkings_analysis.sort_values("parking_per_zone", ascending=False)
        self.car2go_stations_mat = self.car2go_parkings_analysis.sort_values("avg_duration_per_zone", ascending=False)



    
    def set_enj_datasets(self, from_pickle=True):
        if from_pickle == True:
            df = pd.read_pickle(paths.enjoy_bookings_pickle_path, None)
            df = df[(df["duration"] <= 120) &(df["distance"] >= 20)]
            self.enjoy = gpd.GeoDataFrame(df, crs=self.crs)
            self.assign_zone_numbers("enjoy")
        else:
            dbp = DataBaseProxy()
            df = dbp.query_bookings_df("enjoy",self.name, self.start, self.end)
            df.to_pickle(paths.enjoy_bookings_pickle_path, None)
            df = df[(df["duration"] <= 120) &(df["distance"] >= 20)]
            self.enjoy = gpd.GeoDataFrame(df, crs=self.crs)
            self.assign_zone_numbers("enjoy")
            
        self.load_parkings("enjoy")
        self.enjoy = self.enjoy.dropna(axis=0).sort_values("init_time")
        self.enjoy_parkings_analysis = self.parkings_analysis(self.enjoy_parkings, days=self.days)
        self.enjoy_stations_mp = self.enjoy_parkings_analysis.sort_values("parking_per_zone", ascending=False)
        self.enjoy_stations_mat = self.enjoy_parkings_analysis.sort_values("avg_duration_per_zone", ascending=False)


    
    def get_fleet(self, provider):
        if provider == 'car2go':
            self.c2g_fleet = util.get_fleet(self.car2go, 
                          util.get_valid_days(self.car2go, self.start, self.end)["valid_days"])
            self.c2g_fleet = self.c2g_fleet[self.c2g_fleet["bookings_per_car"] >= self.days]
        else :
            self.enj_fleet = util.get_fleet(self.enjoy, 
                          util.get_valid_days(self.enjoy, self.start, self.end)["valid_days"])
            self.enj_fleet = self.enj_fleet[self.enj_fleet["bookings_per_car"] >= self.days]
            
    def assign_zone_numbers(self, provider):
        if provider == "car2go":
            if os.path.exists(paths.car2go_bookings_picke_path_zoned):
                self.car2go =  pd.read_pickle(paths.car2go_bookings_picke_path_zoned, None)
            else :
                self.car2go['geometry'] = self.car2go.apply(
                        lambda row: pointfy(row['start_lon'], row['start_lat']), axis = 1)
                self.car2go = gpd.sjoin(self.car2go, self.turin, how='inner', op='within')
                self.car2go.rename(columns={"FID": "init_zone"}, inplace=True)
                self.car2go.drop("index_right", axis=1, inplace=True)
                
                self.car2go['geometry'] = self.car2go.apply(
                        lambda row: pointfy(row['end_lon'], row['end_lat']), axis = 1)
                c2g2 = gpd.sjoin(self.car2go, self.turin, how='inner', op='within')
                c2g2.rename(columns={"FID": "final_zone"}, inplace=True)
                c2g2.drop("index_right", axis=1, inplace=True)
                self.car2go["final_zone"] = c2g2["final_zone"]
                del c2g2
                
                self.car2go.to_pickle(paths.car2go_bookings_picke_path_zoned, None)
        else :
            if os.path.exists(paths.enjoy_bookings_picke_path_zoned):
                self.enjoy =  pd.read_pickle(paths.enjoy_bookings_picke_path_zoned, None)
            else :
                self.enjoy['geometry'] = self.enjoy.apply(
                lambda row: pointfy(row['start_lon'], row['start_lat']), axis = 1)
                self.enjoy = gpd.sjoin(self.enjoy, self.turin, how='inner', op='within')
                self.enjoy.rename(columns={"FID": "init_zone"}, inplace=True)
                self.enjoy.drop("index_right", axis=1, inplace=True)
                
                self.enjoy['geometry'] = self.enjoy.apply(
                        lambda row: pointfy(row['end_lon'], row['end_lat']), axis = 1)
                c2g2 = gpd.sjoin(self.enjoy, self.turin, how='inner', op='within')
                c2g2.rename(columns={"FID": "final_zone"}, inplace=True)
                c2g2.drop("index_right", axis=1, inplace=True)
                self.enjoy["final_zone"] = c2g2["final_zone"]
                
                self.enjoy.to_pickle(paths.enjoy_bookings_picke_path_zoned, None)
                

                
    def create_c2g_cars_collections(self):
        self.cars_c2g={}
        for plate in self.car2go["plate"].unique():
            self.cars_c2g[plate] = Car(plate,"car2go",self.car2go.iloc[0])  
        return self.cars_c2g
    
    def create_enj_cars_collections(self):
        self.cars_enj={}
        for plate in self.enjoy["plate"].unique():
            self.cars_enj[plate] = Car(plate,"enjoy",self.enjoy.iloc[0]) 
        return self.cars_enj
    
    def place_stations(self, no_ps, no_ps_per_station, provider, algorithm="rnd", station_type=1):
        no_ps = int(no_ps)
        no_ps_per_station = int(no_ps_per_station)
        
        if provider == "car2go":
            df = self.car2go_parkings_analysis
        else:
            df = self.enjoy_parkings_analysis
        
        if no_ps % no_ps_per_station == 0:
            max_stat = no_ps / no_ps_per_station
        else:
            max_stat = (no_ps/no_ps_per_station)+1
        
        stations={}
        self.stations = stations
            
        if algorithm == "max_parking":
            zones = df.sort_values("parking_per_zone", ascending=False).head(max_stat)
            for i in range(0,len(zones)):
                zone = zones.iloc[[i]].index.get_values()[0]
                stations[zone] = Station(zone, no_ps_per_station,0, station_type)
#            print zones.index
        
        elif algorithm == "max_avg_time" :
            zones = df.sort_values("avg_duration_per_zone", ascending=False).head(max_stat)
            for i in range(0,len(zones)):
                zone = zones.iloc[[i]].index.get_values()[0]
#                print zone
                stations[zone] = Station(zone, no_ps_per_station,0, station_type) 
#            print zones.index


        elif algorithm == "max_time":
            zones = df.sort_values("duration_per_zone", ascending=False).head(max_stat)
            for i in range(0,len(zones)):
                zone = zones.iloc[[i]].index.get_values()[0]
                stations[zone] = Station(zone, no_ps_per_station,0, station_type)
#            print zones.index


        elif algorithm == "rnd": 
            seed = random.randint(1, 1e6)  % random.randint(1, 1e6) 
            zones = df.sample(n=max_stat, random_state=seed)
            for i in range(0,len(zones)):
                zone = zones.iloc[[i]].index.get_values()[0]
                stations[zone] = Station(zone, no_ps_per_station,0, station_type)
#            print stations.keys()[0:10]
        else:
            print "error dionace"
            return
        
        self.stations = stations
        
        return stations
                
        
                
    def run(self, provider, threshold):
#        print "running..."
        if provider == "car2go":
            df = self.car2go
            cars = self.create_c2g_cars_collections()
            corrective_factor = 1.82

            
        if provider == "enjoy":
            df = self.enjoy
            cars = self.create_enj_cars_collections()
            corrective_factor = 1.82
        
        stations = self.stations
        
        refused_bookings = 0
        s = time.time()
#        for i in range (1, len(df)-1):
#        df.drop("geometry",axis=1, inplace=True)
#        df = pd.DataFrame(df)
#        self.avg_bat_before = 0
        self.avg_bat_after = 0
        self.avg_bat_before = 0
        pieni = 0 
        for index, row in df.iterrows() :
#            if i%10000 == 0:
#                print i
            c_booking = row
            c_plate = str(c_booking["plate"])
            c_car = cars[c_plate]
            old_cap = c_car.current_capacity
            
            self.avg_bat_before = self.avg_bat_before + c_car.current_capacity

            if c_car.in_charge == True :
                
                old_cap = c_car.current_capacity
                rech_z = c_car.last_final_zone()                
                stations[rech_z].decrease_supplied_cars()
                stations[rech_z].increase_recharged_counter(c_plate)
                c_car.compute_recharge(stations[rech_z], c_booking)
            

            if old_cap - c_car.current_capacity < 0:
                pieni = pieni + 1
                
                
#            fz = c_booking["final_zone"].astype(np.int64)
            fz = int(c_booking["final_zone"])

#            print c_car.current_capacuty, threshold
            if c_car.current_capacity >= threshold:
                c_car.compute_consuption(c_booking["distance"] * corrective_factor)
#                print  fz, type(fz), stations.keys()[3], type(stations.keys()[3]), fz==stations.keys()[3] 
#                if fz in stations.keys():
#                    print"o
                if fz in stations.keys() and stations[fz].cars < stations[fz].max_cars :
                    stations[fz].increase_supplied_cars()
                    c_car.set_in_charge()
                    c_car.assign_last_booking(c_booking)
                else:
                    c_car.set_not_in_charge()
                    c_car.assign_last_booking(c_booking)

            else:
                refused_bookings +=1
            self.avg_bat_after = self.avg_bat_after + c_car.current_capacity

        df = pd.DataFrame.from_records([cars[c].to_dict() for c in cars])
        self.avg_bat_after = self.avg_bat_after/len(df)
        self.avg_bat_before = self.avg_bat_before/len(df)

        self.et = time.time()-s
        self.pieni = pieni
        self.rech_cars = pd.DataFrame(columns=["disticint_cars_in_zone"])
        
        for zone_id in self.stations.keys() :
            self.rech_cars.loc[zone_id,"disticint_cars_in_zone"] = len(self.stations[zone_id].charged_cars)
        stats = pd.DataFrame()
        for plate in cars :
            row = cars[plate].car2df()
            stats = stats.append(row, ignore_index=True)
        stats.set_index("plate", inplace =True)
        return stats
       
        


#year = 2017
#month = 5
#day = 6
#start = datetime.datetime(year, month, day, 0, 0, 0)
#end = datetime.datetime(year, month +2, day, 23, 59, 0)
#torino = City("Torino", start,end)
#torino.set_c2g_datasets(from_pickle=True)
#torino.set_enj_datasets(from_pickle=True)
#torino.get_fleet("car2go")
#torino.get_fleet("enjoy")
##
##ms = time.time()
#print "max_parking ",
#print torino.place_stations(20,
#                      2,
#                      "car2go",
#                      "max_parking",
#                      station_type=1).keys()
#print
#
#print "max_avg_time"
#print torino.place_stations(20,
#                      2,
#                      "car2go",
#                      "max_avg_time",
#                      station_type=1).keys()
#print
#
#print "max_time "
#print torino.place_stations(20,
#                      2,
#                      "car2go",
#                      "max_time",
#                      station_type=1).keys()
#print
#
#zzz = torino.car2go_parkings_analysis
#zzz2 = torino.car2go_parkings_analysis

#print torino.run("car2go", 0)["deaths"].sum()
#print time.time() - ms

#zones = 17.0
#ppz = 4
#algs = 3
#prov = 2
#texec = 14
#print zones* ppz* algs* prov

    
#n_z = range(10,260, 50)
#n_ppz = [3,9]
#commands = {}
#j=0
#for cso in ["car2go", "enjoy"]:
#    for alg in ["max_parking", "rnd", "max_avg_time"] :
#        for ppz in n_ppz:
#            d = {}
#            d["alg"] = alg
#            d["ppz"] = ppz
#            d["out"] =  "/home/mc/Scrivania/Tesi/MyTool/pickles/sym_res/sym_res_"+str(j) 
#            d["cso"] = cso
#            commands[j] = d
#            j=j+1
#def return_path(cso, alg, ppz, z):
#    string = str(cso) +"_"+ str(alg) + "_" + str(ppz) + "_"+ str(z)
#    return string
#
#
#node_sim_list=[]
#process_list = []
#for i in commands.keys():
#    node_sim_list.append(commands[i])
#    
#    
#def worker(node):
#    resutls = pd.DataFrame()  
#    for z in n_z:
#        torino.place_stations(z * node["ppz"],
#                              node["ppz"],
#                              node["cso"],
#                              algorithm=node["alg"],
#                             station_type=1)
#        c2g_stats = torino.run(node["cso"], threshold=0)
#        row = pd.Series()
#        row["z"] = z
#        row["ppz"] = node["ppz"]
#        row["p"] = z*node["ppz"]
#        row["provider"] = node["cso"]
#        row["algorithm"] = node["alg"]
#        row["mean_dpc"] = c2g_stats["deaths"].mean()
#        row["median_dpc"] = c2g_stats["deaths"].median()
#        row["tot_deaths"] = c2g_stats["deaths"].sum()    
#        resutls = resutls.append(row, ignore_index=True)
#    resutls.to_pickle(node["out"])
#
#
#init_time = time.time()
#for node in node_sim_list:
#    p = Process(target=worker, args=(node,))
#    process_list.append(p)
#    p.start()
#
#for p in process_list:
#    p.join()
#    
#print time.time() - init_time
#
#res = pd.DataFrame()
#for node in node_sim_list:
#    res = res.append(pd.read_pickle(node["out"]), ignore_index=True)
#
#
#import matplotlib.pyplot as plt
#resutls = pd.read_pickle("/home/mc/Scrivania/Tesi/MyTool/pickles/sym_results2")
#def plot_from_df (df, provider, algorithm, ppz, parameter):
#    fig = plt.figure(figsize=(10,10))
#    colors = {"max_avg_time":"red", "max_parking":"blue", "rnd": "black"}
#
#    ax = fig.gca()
#    ax.set_title("Deaths vs Number of PS", fontsize=36)
#    for alg in algorithm:
#    
#        inside = df[
#            (df["provider"]==provider) &
#            (df["ppz"] == ppz) &
#            (df["algorithm"] == alg)]
#        if parameter == "median":
#            ax.plot(inside["p"], inside["median_dpc"], color=colors[alg], label=alg)
#            ax.set_ylabel("Median number of death per car")
#        else :
#            ax.plot(inside["p"], inside["tot_deaths"], color=colors[alg], label=alg)
#            ax.set_ylabel("Total number of deaths")
#    
#    ax.set_xlabel("Total number of power supply")
#    plt.legend(fontsize=18)
##    plt.savefig(paths.)
#    plt.show()
#
#plot_from_df(res, "car2go", ["max_avg_time", "rnd", "max_parking"], 3, "tot" )
#plot_from_df(res, "car2go", ["max_avg_time", "rnd", "max_parking"], 9, "tot" )



