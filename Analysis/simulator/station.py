import pandas as pd
import geopands as gpd



class Station (object):
    
    def __init__ (self, s_id, max_cars, cars):
        self.s_id = s_id
        self.max_cars = max_cars
        self.cars = cars
        return
    
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

    
    