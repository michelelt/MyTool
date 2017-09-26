import pandas as pd
import geopandas as gpd



class Station (object):
    
    def __init__ (self, s_id, max_cars, cars, s_type=1):
        self.s_id = s_id
        self.max_cars = max_cars
        self.cars = cars
        self.set_station_profile(s_type)
        return
    
    def __repr__(self):
        string  = "id: " + str(self.s_id) + "\n" 
        string += "max cars:" + str(self.max_cars) + "\n"
        string += "cars: " + str(self.cars) + "\n"
        string += "s_type: " + str(self.s_type) +"\n\n"
        return string
    
    def increase_supplied_cars(self):
        if self.cars <= self.max_cars :
            self.cars = self.cars + 1
        return
    
    def decrease_supplied_cars(self):
        if self.cars >= 1 :
            self.cars = self.cars -1
        return
    
    def compute_centroid (self, geometry):
        self.lat = geometry.centroid.y
        self.lon = geometry.centroid.x
        return
    
    def set_station_profile(self, s_type):
        #data from paper A
        if s_type == 1:
            self.s_type = 1
            self.kw = 1.92
        elif s_type == 2:
            self.s_type = 2
            self.kw = 19.2 #or 2.5
        else :
            self.s_type =3
            self.kw = 240.0
    
