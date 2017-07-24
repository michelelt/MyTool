import pandas as pd
import datetime
import matplotlib.pyplot as plt
import matplotlib
from math import *
import numpy as np
import paths as paths


from DataBaseProxy import DataBaseProxy
dbp = DataBaseProxy()

year = 2017
month = 5
day = 17

#car2go_pickle_path = "/home/mc/Scrivania/Tesi/MyTool/car2go_p"
#enjoy_pickle_path = "/home/mc/Scrivania/Tesi/MyTool/enjoy_p"
#plots_path= "/home/mc/Scrivania/Tesi/MyTool/plots/01/"

#km macchine per enjoy e car2go in una settimana
start = datetime.datetime(year, month, day, 0, 0, 0)
end = datetime.datetime(year, month +1, day, 23, 59, 0)
end2 = datetime.datetime(year, 7, 23, 23,59,0)

#
#enjoy = dbp.query_bookings_df("enjoy","Torino", start, end)
#car2go = dbp.query_bookings_df("car2go","Torino", start, end)
#enjoy.to_pickle(paths.enjoy_pickle_path, None)
#car2go.to_pickle(paths.car2go_pickle_path, None)

def clean_distances(df):
    df = df[df.distance >1]
    df = df[df.distance < df.distance.quantile(0.95)]
    df = df[df.distance > df.distance.quantile(0.05)]
    return df


def distances_per_car(df):
    out_df= pd.DataFrame()
    out_df["plate"]  = df.plate
    out_df['distance']  = df.distance
    distaces_per_car = out_df.groupby('plate', as_index = False).sum()
    distaces_per_car['distance'] = distaces_per_car.distance.apply(lambda x : x/1000)
    freq_per_car = out_df.groupby('plate', as_index=False).count()
    distaces_per_car['freq'] = freq_per_car['distance']
    return distaces_per_car

def total_dist_per_car(df):
    df = clean_distances(df)
    dist_per_car = distances_per_car(df)
    provider = dbp.get_provider(df)
    
    color = dbp.get_color(dbp.get_provider(df))
    fig, ax = plt.subplots(1, 1, figsize=(20,10))
    my_xticks = dist_per_car.plate
    plt.xticks(dist_per_car.index, my_xticks, rotation=45)
#    plt.set_xticklabels(my_xticks, rotation=45)
    plt.plot(dist_per_car.index, dist_per_car.distance, linestyle='-', marker='x',
             color=color)
    plt.title("km per car - " + dbp.get_provider(df))
    plt.ylabel("km")
    plt.xlabel("plates")
    plt.savefig(paths.plots_path+provider+"_dist_per_car.png")
    plt.show()
    return dist_per_car
        
def total_dist_per_car_no_outliers (df):
    df = clean_distances(df)
    dist_per_car = distances_per_car(df)
    
    fig, ax = plt.subplots(1, 1, figsize=(20,10))
    provider = dbp.get_provider(df)
    color = dbp.get_color(dbp.get_provider(df))

    std = dist_per_car['distance'].std()
    avg = dist_per_car['distance'].mean()
    normalized_distance = dist_per_car[(dist_per_car['distance'] >= (avg-std)) &
                                       (dist_per_car['distance'] <= (avg+std))]
    
    my_xticks = normalized_distance.plate
    plt.xticks(normalized_distance.index, my_xticks, rotation=45)
    plt.plot(normalized_distance.index, normalized_distance.distance, 
             linestyle='-', marker='x', color=color)
    plt.title("km per car normalized - " + dbp.get_provider(df))
    plt.ylabel("Km")
    plt.xlabel("plates")
    plt.savefig(paths.plots_path+provider+"_dist_per_car_no_out.png")
    plt.show()
    return
    
def fuel_behavior_max_distnace(df):
    provider = dbp.get_provider(df)
    df2 = clean_distances(df)
    dist_per_car = distances_per_car(df2)
    
    
    id_max = dist_per_car.distance.idxmax(1) 
    row = dist_per_car.loc[id_max]
    plate = row['plate']
    
    fuel_cons = df[df.plate == plate]
#    fuel_cons = fuel_cons[fuel_cons.distance_dr != -1]
    x = range(0,len(fuel_cons.index))
    fig, ax = plt.subplots(1, 1, figsize=(9,10))

    ax.plot(x, fuel_cons.init_fuel, 'bs', label='init fuel')
    ax.plot(x, fuel_cons.final_fuel,'r^', label='final fuel', alpha = 0.5)
    plt.title("Fuel consuption, big dist - " + dbp.get_provider(df))
    plt.legend()
    plt.ylabel("Fuel level")
    plt.xlabel("Chrological rent ID")
    plt.savefig(paths.plots_path+provider+"_fuel_behav_max_dist.png")
    plt.show()

    return fuel_cons
    
def fuel_behavior_max_booked(df):   
    provider = dbp.get_provider(df)
    count_df = df.groupby('plate', as_index = True).count()
    id_max = count_df.distance.idxmax(1) 
    #row = count_df.loc[id_max]
    plate = id_max
    fuel_cons = df[df.plate == plate]
    
    fig, ax = plt.subplots(1, 1, figsize=(9,10))
    x = range(0,len(fuel_cons.index))
    ax.plot(x, fuel_cons.init_fuel, 'bs', label='init fuel')
    ax.plot(x, fuel_cons.final_fuel,'r^', label= 'end fuel', alpha = 0.5)
    plt.title("Fuel consuption, most booked- " + dbp.get_provider(df))
    plt.legend()
    plt.ylabel("Fuel level")
    plt.xlabel("Chrological rent ID")
    plt.savefig(paths.plots_path+provider+"_fuel_behav_most_booked.png")
    plt.show()
    return fuel_cons
    
def pdf_distance(df_source, df_dist):
    provider = dbp.get_provider(df_source)
    color = dbp.get_color(provider)
    fig, ax = plt.subplots(2, 2, figsize=(9,10))
    fig.suptitle("bookings duration - " + provider)
    ax[0,0].hist(df_dist.distance, 50, facecolor=color, alpha=0.75, cumulative=True, normed=True)
    ax[0,0].set_title("CDF - durations")
    ax[0,1].hist(df_dist.distance, 50, facecolor=color, alpha=0.75)
    ax[0,1].set_title("PDF - durations")
#    ax[1].set_title("distances filtered- " + provider)
    df_dist = df_dist[df_dist['distance'] > 30]
    df_dist = df_dist[df_dist.freq > 0]
    ax[1,0].hist(df_dist.distance, 50, facecolor=color, alpha=0.75, cumulative=True, normed=True)
    ax[1,0].set_title("filtered CDF - durations")
    ax[1,1].hist(df_dist.distance, 50, facecolor=color, alpha=0.75)
    ax[1,0].set_title("filtered PDF - durations")

    plt.savefig(paths.plots_path+provider+"_PDF_CDF.png")
    plt.show()
    return 

def valid_days(df):
    provider = dbp.get_provider(df)
    color = dbp.get_color(provider)
    df = pd.DataFrame(df['init_date'])
    df['date'] = df.init_date.apply(lambda x : x.date())
    df = df.groupby('date').count()
    
    datelist = pd.date_range(pd.datetime(year,month,day), periods=32).tolist()
    dfdays = pd.DataFrame(datelist)
    dfdays['count'] = [0]*len(datelist)
    dfdays.set_index(0, inplace=True)
    df2= dfdays['count'] +  df['init_date']
    df2.fillna(0, inplace=True)
    
    fig, ax = plt.subplots(1, 1, figsize=(9,10))
    plt.title("Entry per days - " + provider)
    df2.plot(color=color)
    fig.savefig(paths.plots_path+provider+"_valid_days.png")
    return
    


enjoy = pd.read_pickle(paths.enjoy_pickle_path, None)
car2go = pd.read_pickle(paths.car2go_pickle_path, None)


valid_days(enjoy)
valid_days(car2go)

enj_dist = total_dist_per_car(enjoy)
total_dist_per_car_no_outliers(enjoy)
pdf_distance(enjoy, enj_dist)
fuel_behavior_max_distnace(enjoy)
fuel_cons = fuel_behavior_max_booked(enjoy)

c2g_dist = total_dist_per_car(car2go)
total_dist_per_car_no_outliers(car2go)
pdf_distance(car2go, c2g_dist)
fuel_cons  = fuel_behavior_max_distnace(car2go)
fuel_behavior_max_booked(car2go)

fuel_cons['diff'] = fuel_cons['init_fuel'] - fuel_cons['final_fuel']


'''
cerco macchine che hanno poche prenotazioni nell'active booking
'''
#enj_dist_not_ok = enj_dist[~enj_dist.isin(enj_dist_ok)].dropna()
#plates = enj_dist_not_ok['plate'].tolist()
#for pos in range(0, len(plates)):
#    plates[pos] = str(plates[pos])
#disappeared_cars = dbp.query_car_per_plate_df("enjoy", plates, start,end)
#disappeared_cars.to_pickle(paths.enjoy_disap_pickle_path, None)
#grouped = pd.DataFrame(disappeared_cars.groupby(["plate", "city"]).size())
#grouped = grouped.rename(columns={0 : "bookings_per_car"})
#zzz = grouped.index
#zzz = list(zzz)
#grouped["temp"] = zzz
#grouped["plate_col"] = grouped.temp.apply(lambda row: row[0])
#grouped["city_col"] = grouped.temp.apply(lambda row: row[1])
#del grouped["temp"]
#car_per_city = grouped.groupby('city').sum()
#car_per_city["log"] = np.log10(car_per_city["bookings_per_car"])
#car_per_city.bookings_per_car.plot(color=dbp.get_color(enjoy), marker='o', linewidth=0)












