import random
import pandas as pd

class Car (object):

    def __init__ (self, plate, provider,last_booking):
        self.plate = plate
        self.last_booking = last_booking
        self.capacity  = self.parameter(provider)["capacity"]
        self.consumption = self.parameter(provider)["cons"]
        self.current_capacity = self.capacity
        self.in_charge = False
        self.deaths = 0 
        return 
    
    def __repr__(self):
        string = "plate: " + self.plate + "\n"
        string += "capacity: " + str(self.capacity) + "\n"
        string += "curr_cap: " + str(self.current_capacity) + "\n"
        string += "charging: " + str(self.in_charge) + "\n"
        string += "deaths:   " + str(self.deaths) + "\n"
        return string
    
    def parameter(self, provider):
        if provider == 'car2go':
            capacity = 17.6
            kwh_km = 0.13
        else:
            capacity = 25.2
            kwh_km = 0.188
        
        res = {'capacity': capacity, 'cons': kwh_km}
        return res
    
    def compute_consuption(self, distance):
        dist_km = self.m2km(distance)
        dc = dist_km * self.consumption
        self.current_capacity = self.current_capacity - dc
        if self.current_capacity <= 0:
            self.deaths = self.deaths + 1
            self.current_capacity = 0
        return dc
    
    def compute_recharge(self, station, cb):
        duration = (cb["init_time"] - self.last_booking["final_time"])/60/60 #in hour
        delta_c = duration * station.kw
        if (self.current_capacity <= self.capacity):
            self.current_capacity = self.current_capacity + delta_c
        else:
            self.current_capacity = self.capacity
        return delta_c
        
    
    def last_final_zone(self):
        return int(self.last_booking["final_zone"])

    
    def assign_last_booking(self, new_booking):
        self.last_booking = new_booking
        return
    
    def m2km(self, distance):
        return distance/1000
    
    def random_refil (self):
        self.current_capacity = random.random()
        
    def set_in_charge(self):
        self.in_charge=True
    
    def set_not_in_charge(self):
        self.in_charge=False
        
    def car2df(self):
        df = pd.Series()
        df["plate"] = self.plate
        df["capacity"] = self.capacity
        df["cc"] = self.current_capacity
        df["deaths"] = self.deaths
        return df
    
    def to_dict(self):
        d = {}
        d["capacity"] = self.capacity
        d["current_capacity"]  = self.current_capacity
        d["charging"] = self.in_charge
        d["deaths"] = self.deaths
        return d
        
        
    
    
"http://it.smart.com/it/it/index/smart-fortwo-electric-drive-453/technical-data.html"
"https://www.fiatusa.com/en/500e/"    
        