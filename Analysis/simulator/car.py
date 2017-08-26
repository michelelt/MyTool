import random

class Car (object):

    def __init__ (self, plate, provider,last_booking):
        self.plate = plate
        self.last_booking = last_booking
        self.capacity, self.consumption = self.parameter(provider)
        self.current_capacity = self.capacity
        return
    
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
        return dc
    
    def compute_recharge(self, duration):
        return duration *0.1 ##da rivedere
    
    
    def assign_new_booking(self, new_booking):
        self.last_booking = new_booking
        return
    
    def m2km(self, distance):
        return distance/1000
    
    def random_refil (self):
        self.current_capacity = random.random()
    
"http://it.smart.com/it/it/index/smart-fortwo-electric-drive-453/technical-data.html"
"https://www.fiatusa.com/en/500e/"    
        