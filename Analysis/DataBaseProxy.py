from math import radians, cos, sin, asin, sqrt
def haversine(lon1, lat1, lon2, lat2):
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

import datetime
import pandas as pd
import numpy as np
#import recordFileds

from workalendar.europe import Italy

from pymongo import MongoClient
from bson.objectid import ObjectId

from sshtunnel import SSHTunnelForwarder

MONGO_HOST =  "bigdatadb.polito.it"#"REMOTE_IP_ADDRESS"
MONGO_DB = "carsharing" #"DATABASE_NAME"
MONGO_USER = "ict4transport"#"LOGIN"
MONGO_PASS = "pwd_ict4_2017"#"PASSWORD"
#server.stop()

class DataBaseProxy (object):
    
    def __init__ (self):
        server = SSHTunnelForwarder(
            MONGO_HOST,
            ssh_username=MONGO_USER,
            ssh_password=MONGO_PASS,
            remote_bind_address=('127.0.0.1', 27017)
        )
        server.start()
        client = MongoClient('127.0.0.1', server.local_bind_port)
        client.carsharing.authenticate('ictts', 'Ictts16!', mechanism= 'SCRAM-SHA-1')
        self.db = client[MONGO_DB]

    def query_bookings(self, vendor, city, start, end):
        if (vendor == "enjoy") :
            return self.db["enjoy_PermanentBookings"].find(
                    {'init_date':
                                   {
                                       '$gt': start,
                                       '$lt': end
                                   },
                    'city' : city
                    }).sort([("_id", 1)]) 
        elif (vendor == "car2go") :
            return self.db["PermanentBookings"].find(
                    {'init_date':
                                   {
                                       '$gt': start,
                                       '$lt': end
                                   },
                    'city' : city
                    }).sort([("_id", 1)]) 
        else:
            return "err"
        
    def query_bookings_df(self, vendor, city, start, end):
        books_cursor = self.query_bookings(vendor, city, start, end)
        if (books_cursor == "err" or books_cursor.count() == 0):
            return "err"
        else :
#            print books_cursor.count()
#            bookings_df = pd.DataFrame(columns = pd.Series(books_cursor.next()).index)
            bookings_df = pd.DataFrame(list(books_cursor))
            
            
            
            bookings_df['duration_dr'] = bookings_df.driving.apply(lambda x: float(x['duration']/60))
            bookings_df['distance_dr'] = bookings_df.driving.apply(lambda x: x['distance'])
            bookings_df = bookings_df.drop('driving',1)
            
            bookings_df['type'] = bookings_df.origin_destination.apply(lambda x : x['type'])
            bookings_df['coordinates'] = bookings_df.origin_destination.apply(lambda x : x['coordinates'])
            bookings_df = bookings_df.drop('origin_destination',1)
            
            bookings_df['start'] = bookings_df.coordinates.apply(lambda x : x[0])
            bookings_df['end'] = bookings_df.coordinates.apply(lambda x : x[1])
            bookings_df = bookings_df.drop('coordinates',1)
            
            bookings_df['start_lon'] = bookings_df.start.apply(lambda x : str(x[0]) )
            bookings_df['start_lat'] = bookings_df.start.apply(lambda x : str(x[1]) )
            bookings_df = bookings_df.drop('start',1)
            
            bookings_df['end_lon'] = bookings_df.end.apply(lambda x : str(x[0]) )
            bookings_df['end_lat'] = bookings_df.end.apply(lambda x : str(x[1]) )
            bookings_df = bookings_df.drop('end', 1)
            
            bookings_df['distance'] = bookings_df.apply(lambda x : haversine(
                    float(x['start_lon']),float(x['start_lat']),
                    float(x['end_lon']), float(x['end_lat'])), axis=1
            )
    
            bookings_df['duration'] = bookings_df.final_date - bookings_df.init_date 
            bookings_df['duration'] = bookings_df['duration'].apply(lambda x: x.days*24*60 + x.seconds/60)
            
            bookings_df['duration_pt'] = bookings_df.public_transport.apply(lambda x : x['duration'] )
            bookings_df['distance_pt'] = bookings_df.public_transport.apply(lambda x : x['distance'] )
            bookings_df['arrival_date_pt'] = bookings_df.public_transport.apply(lambda x : x['arrival_date'] )
            bookings_df['arrival_time_pt'] = bookings_df.public_transport.apply(lambda x : x['arrival_time'] )
            bookings_df = bookings_df.drop('public_transport',1)
            return bookings_df
        
    def get_provider(self, df):
        return df.iloc[0].vendor

    
    def query_parkings(self, vendor, city, start, end):
        if (vendor == "enjoy") :
            return self.db["enjoy_PermanentParkings"].find(
                    {'init_date':
                                   {
                                       '$gt': start,
                                       '$lt': end
                                   },
                    'city' : city
                    }).sort([("_id", 1)]) 
        elif (vendor == "car2go") :
            return self.db["PermanentParkings"].find(
                    {'init_date':
                                   {
                                       '$gt': start,
                                       '$lt': end
                                   },
                    'city' : city
                    }).sort([("_id", 1)]) 
        else:
            return "err"
        
    def query_parkings_df(self, vendor, city, start, end):
        parks_cursor = self.query_parkings(vendor, city, start, end)
        if (parks_cursor == "err" or parks_cursor.count() == 0):
            return  parks_cursor.count()
        else :
#            print books_cursor.count()
#            bookings_df = pd.DataFrame(columns = pd.Series(books_cursor.next()).index)
            parkings_df = pd.DataFrame(list(parks_cursor))
            
            parkings_df['type'] = parkings_df['loc'].apply(lambda x : x['type'])
            parkings_df['coordinates'] = parkings_df['loc'].apply(lambda x : x['coordinates'])
            parkings_df = parkings_df.drop('loc',1)
            
            parkings_df['lon'] = parkings_df.coordinates.apply(lambda x : str(x[0]))
            parkings_df['lat'] = parkings_df.coordinates.apply(lambda x : str(x[1]))
            parkings_df = parkings_df.drop('coordinates',1)
            
            parkings_df['duration'] =parkings_df.final_date - parkings_df.init_date 
            parkings_df['duration'] = parkings_df['duration'].apply(lambda x: x.days*24*60 + x.seconds/60)

            return parkings_df
        
    def get_color (self, provider):
        if isinstance(provider, pd.DataFrame):
            provider = self.get_provider(provider)
            if (provider == "enjoy"):
                return "red"
            else:
                return "blue"
        
        if provider == 'enjoy':
            return "red"
        elif provider == 'car2go':
            return "blue"
           
        
    def query_car_per_plate_df(self, vendor, plate, start, end):
        if vendor == 'car2go' :
            cursor = self.db["PermanentBookings"].find(
                        {'init_date':
                                       {
                                           '$gt': start,
                                           '$lt': end
                                       },
                        'plate' : {'$in': [plate]}
                        }).sort([("_id", 1)]) 
            
        if vendor == 'enjoy' :
            cursor = self.db["enjoy_PermanentBookings"].find(
                        {'init_date':
                                       {
                                           '$gt': start,
                                           '$lt': end
                                       },
                        'plate' : {'$in': plate}
                        })                   
        
        df = pd.DataFrame(list(cursor))
        return df
    
    def query_car_per_plate_active_df(self, vendor, plate, start, end):
        if vendor == 'car2go' :
            cursor = self.db["ActiveBookings"].find(
                        {'init_date':
                                       {
                                           '$gt': start,
                                           '$lt': end
                                       },
                        'plate' : {'$in': [plate]}
                        }).sort([("_id", 1)]) 
            
        if vendor == 'enjoy' :
            cursor = self.db["enjoy_ActiveBookings"].find(
                        {'init_date':
                                       {
                                           '$gt': start,
                                           '$lt': end
                                       },
                        'plate' : {'$in': plate}
                        })                   
        
        df = pd.DataFrame(list(cursor))
        return df
    
    
        

#    def query_fleet_by_day (self, provider, city, start, end):
#        
#        return self.db['fleet'].find \
#                           ({
#                               'day':
#                                   {
#                                       '$gt': start,
#                                       '$lt': end
#                                   },
#                               'provider': provider,
#                               'city':city
#                           }).sort([("_id", 1)])        
#                
#    def query_raw_by_time (self, provider, city, start, end):
#        
#        return self.db["snapshots"].find \
#                    ({"timestamp":
#                         {
#                             '$gte': start,
#                             '$lt': end
#                         },
#                     "provider":provider,
#                     "city":city
#                    }).sort([("_id", 1)])
#
#    def query_fleet (self, provider, city):
#
#        return self.db["fleet"].find \
#                    ({
#                     "provider":provider,
#                     "city":city
#                    }).sort([("_id", 1)])
#                        
#    def query_parks (self, provider, city, start, end):
#        
#        return self.db["parks"].find \
#                    ({"start":
#                         {
#                             '$gte': start,
#                             '$lt': end
#                         },
#                     "provider":provider,
#                     "city":city
#                     }).sort([("_id", 1)])
#
#    def query_books (self, provider, city, start, end):
#        
#        return self.db["books"].find \
#                    ({"start":
#                         {
#                             '$gte': start,
#                             '$lt': end
#                         },
#                     "provider":provider,
#                     "city":city
#                    }).sort([("_id", 1)])
#
#    def query_books_group (self, provider, city, start, end):
#        
#        return self.db["books_aggregated"].find \
#                    ({"day":
#                         {
#                             '$gt': start,
#                             '$lt': end
#                         },
#                     "provider":provider,
#                     "city":city
#                    }).sort([("_id", 1)])
#
#    def process_books_df (self, provider, books_df):
#
#        def riding_time (provider, df):    
#         
#            df["reservation_time"] = df["duration"] - df["duration_driving"]
#            df.loc[df.reservation_time < 0, "riding_time"] = df["duration"]
#            df.loc[df.reservation_time > 0, "riding_time"] = df["duration_driving"]
#            
#            return df        
#        
#        def get_bill (provider, df):
#            
#            if provider == "car2go":
#                free_reservation = 20
#                ticket = 0.24
#                extra_ticket = 0.24    
#            elif provider == "enjoy":
#                free_reservation = 15
#                ticket = 0.25
#                extra_ticket = 0.10    
#         
#            indexes = df.loc[df.reservation_time > free_reservation].index
#            extra_minutes = df.loc[indexes, 'reservation_time'] - free_reservation
#            df.loc[indexes,"min_bill"] = df.loc[indexes, 'riding_time'].apply(lambda x: x * ticket) + \
#                                                    extra_minutes.apply(lambda x: x * extra_ticket)                                            
#            df.loc[indexes,"max_bill"] = df.loc[indexes, 'duration'].apply(lambda x: x * ticket)
#                                                 
#            indexes = df.loc[(df.reservation_time <= free_reservation) & (df.reservation_time > 0)].index
#            df.loc[indexes,"min_bill"] = df.loc[indexes, 'riding_time'].apply(lambda x: x * ticket)                    
#            df.loc[indexes,"max_bill"] = df.loc[indexes, 'riding_time'].apply(lambda x: x * ticket)
#           
#            indexes = df.loc[df.reservation_time < 0].index
#            df.loc[indexes,"min_bill"] = df.loc[indexes, 'riding_time'].apply(lambda x: x * ticket)
#            df.loc[indexes,"max_bill"] = df.loc[indexes, 'riding_time'].apply(lambda x: x * ticket)        
#            
#            return df
#                       
#        books_df["duration"] = \
#            (books_df["end"] - books_df["start"])/np.timedelta64(1, 'm')
#        books_df["distance"] = books_df.apply\
#            (lambda row: haversine(row["start_lon"], row["start_lat"], 
#                                   row["end_lon"], row["end_lat"]), axis=1)
#        books_df["fuel_consumption"] = \
#            books_df["start_fuel"] - books_df["end_fuel"]
#
#        books_df = riding_time(provider, books_df)
#        books_df = get_bill(provider, books_df)
#
#        return books_df                         
#                        
#    def query_parks_df (self, provider, city, start, end):
#        
#        parks_cursor = self.query_parks(provider, city, start, end)
#        parks_df = pd.DataFrame(columns = pd.Series(parks_cursor.next()).index)
#        for doc in parks_cursor:
#            s = pd.Series(doc)
#            parks_df = pd.concat([parks_df, pd.DataFrame(s).T], ignore_index=True)    
#
#        parks_df["duration"] = \
#            (parks_df["end"] - parks_df["start"])/np.timedelta64(1, 'm')            
#            
#        return parks_df[parks_cols]
#                        
#    def query_books_df (self, provider, city, start, end):
#        
#        books_cursor = self.query_books(provider, city, start, end)    
#        books_df = pd.DataFrame(columns = pd.Series(books_cursor.next()).index)
#        for doc in books_cursor:
#            s = pd.Series(doc)
#            books_df = pd.concat([books_df, pd.DataFrame(s).T], ignore_index=True)           
#        
#        return self.process_books_df(provider, books_df)[books_cols].replace({None:np.NaN})
#
#    def query_parks_df_intervals (self, provider, city, dates_list):
#        
#        parks_cursor = self.query_parks_intervals(provider, city, dates_list)
#        parks_df = pd.DataFrame(columns = pd.Series(parks_cursor.next()).index)
#        for doc in parks_cursor:
#            s = pd.Series(doc)
#            parks_df = pd.concat([parks_df, pd.DataFrame(s).T], ignore_index=True)    
#
#        parks_df["duration"] = \
#            (parks_df["end"] - parks_df["start"])/np.timedelta64(1, 'm')            
#            
#        return parks_df[parks_cols]
#
#    def query_books_df_intervals (self, provider, city, dates_list):
#        
#        books_cursor = self.query_books_intervals(provider, city, dates_list)    
#        books_df = pd.DataFrame(columns = pd.Series(books_cursor.next()).index)
#        for doc in books_cursor:
#            s = pd.Series(doc)
#            books_df = pd.concat([books_df, pd.DataFrame(s).T], ignore_index=True)           
#        
#        return self.process_books_df(provider, books_df)[books_cols].replace({None:np.NaN})
#
#    def query_books_df_aggregated (self, provider, city, start, end):
#        
#        books_cursor = self.query_books_group(provider, city, start, end) 
#
#        books_df = pd.DataFrame()
#
#        for doc in books_cursor:
#  
#            s = pd.DataFrame(doc['books'])
#            books_df = pd.concat([books_df, s], ignore_index=True)           
#        
#        return self.process_books_df(provider, books_df)[books_cols].replace({None:np.NaN})
#
#    def filter_books_df_outliers (self, df):
#
#        df['reservations'] = df['distance'].apply(lambda w: (w == 0)) 
#        df['ride'] = df['distance'].apply(lambda w: (w > 0.05))
#        df['short_trips'] = df['duration'].apply(lambda w: (w < 40))
#        df['medium_trips'] = df['duration'].apply(lambda w: (w > 40) and (w < 120))
#        df['long_trips'] = df['duration'].apply(lambda w: (w > 120) and (w < 1440))
#        
#        return df
#                    
#    def filter_df_days (self, df, start, end):
#        
#        cal = Italy()
#        
#        holidays = []
#        pre_holidays = []
#       
#        #holidays collection creation
#        if start.year == end.year:
#            for h in cal.holidays(start.year):
#                holidays.append(h[0])
#        else:
#            for year in range (start.year, end.year+1):
#                for h in cal.holidays(year):
#                    holidays.append(h[0])
#                     
#        for d in holidays:
#            if (d - datetime.timedelta(days = 1)) not in holidays:
#                pre_holidays.append(d - datetime.timedelta(days = 1))
#                             
#        df['all'] = True                
#        df['week_day'] = df['start'].apply(lambda x: x.weekday())
#        df['business'] = df['week_day'].apply(lambda w: (0 <= w) and (w <= 4))
#        df['weekend'] = df['week_day'].apply(lambda w: (5 <= w) and (w <= 6))
#        df['holiday'] = df['start'].apply(lambda x: x.date()).isin(holidays)    
#        df['week'] = df['start'].apply(lambda x: x.week)
#
#        return df
#
#    def filter_date (self, start, end, day_type):
#        
#        cal = Italy()
#        
#        holidays = []
#        holidays_ = []
#        pre_holidays = []
#        pre_holidays_ = []
#        business = []
#        weekends = []
#       
#        #holidays collection creation
#        if start.year == end.year:
#            for h in cal.holidays(start.year):
#                holidays.append(h[0])
#        else:
#            for year in range (start.year, end.year+1):
#                for h in cal.holidays(year):
#                    holidays.append(h[0])
#                     
#        for d in holidays:
#            if (d - datetime.timedelta(days = 1)) not in holidays:
#                pre_holidays.append(d - datetime.timedelta(days = 1))
#
#        date_list = [end - datetime.timedelta(days=x) for x in range(0, (end-start).days+1)]
#
#        if day_type == "business":
#            for day in date_list:
#                if (day.weekday() >= 0) & (day.weekday() <= 4) & (day not in holidays):
#                    business.append(day)
#            return business
#
#        if day_type == "weekend":
#            for day in date_list:
#                if (day.weekday() >= 5) & (day.weekday() <= 6) & (day not in holidays):
#                    weekends.append(day)
#            return weekends
#
#        if day_type == "holiday":
#            for day in date_list:
#                if (day.date() in holidays):
#                    holidays_.append(day)
#            return holidays_
#
#        if day_type == "preholiday":
#            for day in date_list:
#                if (day.date() in holidays):
#                    pre_holidays_.append(day)
#            return pre_holidays_
#
#    def query_books_intervals(self, provider, city, dates_list):
#
#        query = []
#        for end_ in dates_list:
#            start_ = (end_ - datetime.timedelta(days = 1))
#            q = {'start': {
#                            '$gt': start_,
#                            '$lt': end_
#                            }
#                }
#            query.append(q)
#
#        return self.db['books'].find \
#                    ({ 
#                        '$or': query,
#                        'provider': provider,
#                        'city': city                      
#                    })
#
#    def query_parks_intervals(self, provider, city, dates_list):
#
#        query = []
#        for end_ in dates_list:
#            start_ = (end_ - datetime.timedelta(days = 1))
#            q = {'start': {
#                            '$gt': start_,
#                            '$lt': end_
#                            }
#                }
#            query.append(q)
#
#        return self.db['parks'].find \
#                    ({ 
#                        '$or': query,
#                        'provider': provider,
#                        'city': city                      
#                    })
#        
#    def query_books_df_filtered (self, provider, city, start, end):
#
#        books_df = self.query_books_df(provider, city, start, end)
#        return self.filter_books_df_outliers(self.filter_df_days(books_df, start, end))
#
#    def query_parks_df_filtered (self, provider, city, start, end):
#        
#        parks_df = self.query_parks_df(provider, city, start, end)
#        return self.filter_df_days(parks_df, start, end)
#
#    def query_books_df_filtered_v2 (self, provider, city, start, end, day_type):
#
#        if day_type == "full":
#            return self.query_books_df(provider, city, start, end)
#        else:
#            lista_date = self.filter_date(start, end, day_type)
#            return self.query_books_df_intervals(provider, city, lista_date)
#
#    def query_parks_df_filtered_v2 (self, provider, city, start, end, day_type):
#        
#        if day_type == "full":
#            return self.query_parks_df(provider, city, start, end)
#        else:
#            lista_date = self.filter_date(start, end, day_type)
#            return self.query_parks_df_intervals(provider, city, lista_date)
#
#    def query_books_df_filtered_v3 (self, provider, city, start, end):
#
#        books_df = self.query_books_df_aggregated(provider, city, start, end)
#        return self.filter_books_df_outliers(self.filter_df_days(books_df, start, end))
#
#    def query_fleetsize_series (self, provider, city):
#
#        cursor = self.db['fleet'].aggregate([
#                {"$match":{"provider":provider}}, 
#                {"$group":{"_id": "$day", "daysize": {"$sum": {"$size": "$fleet"}}}}
#            ])
#        return pd.Series({doc["_id"]: doc["daysize"] for doc in cursor})
#                         