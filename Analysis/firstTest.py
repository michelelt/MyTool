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
day = 5

#km macchine per enjoy e car2go in una settimana
start = datetime.datetime(year, month, day, 0, 0, 0)
end = datetime.datetime(year, month+2, day, 23, 59, 0)

#
#enjoy = dbp.query_bookings_df("enjoy","Torino", start, end)
#enjoy_p = dbp.query_parkings_df("enjoy", "Torino", start,end)
##enjoy_2 = enjoy[enjoy["duration"]< 120]
##enjoy_2.duration.hist(bins=50, color='red')
#car2go = dbp.query_bookings_df("car2go","Torino", start, end)
#car2go_p = dbp.query_parkings_df("car2go","Torino", start, end)

#enjoy.to_pickle(paths.enjoy_bookings_pickle_path, None)
#car2go.to_pickle(paths.car2go_bookings_pickle_path, None)
#
#enjoy_p.to_pickle(paths.enjoy_parkings_pickle_path, None)
#car2go_p.to_pickle(paths.car2go_parkings_pickle_path, None)

def clean_distances(df):
    df = df[df.distance >1]
    df = df[df.distance < df.distance.quantile(0.95)]
    df = df[df.distance > df.distance.quantile(0.05)]
    return df


def distances_per_car(df):
    out_df= pd.DataFrame()
    out_df["plate"]  = df.plate
    out_df['distance']  = df.distance
    out_df['duration'] = df.duration
    distaces_per_car = out_df.groupby('plate', as_index = False).sum()
    distaces_per_car['distance'] = distaces_per_car.distance.apply(lambda x : x/1000)
    freq_per_car = out_df.groupby('plate', as_index=False).count()
    distaces_per_car['freq'] = freq_per_car['distance']
    return distaces_per_car

def total_dist_per_car(df):
#    df = clean_distances(df)
    dist_per_car = distances_per_car(df)
    provider = util.get_provider(df)
    
    color = util.get_color(df)
    fig, ax = plt.subplots(1, 1, figsize=(20,10))
    my_xticks = dist_per_car.plate
    plt.xticks(dist_per_car.index, my_xticks, rotation=45)
#    plt.set_xticklabels(my_xticks, rotation=45)
    plt.plot(dist_per_car.index, dist_per_car.distance, linestyle='-', marker='x',
             color=color)
    plt.title("km per car - " + provider)
    plt.ylabel("km")
    plt.xlabel("plates")
#    plt.savefig(paths.plots_path+provider+"_dist_per_car.png")
#    plt.savefig(paths.plots_path2+provider+"_dist_per_car.png")
    plt.show()
    return dist_per_car
        
def total_dist_per_car_no_outliers (df):
    df = clean_distances(df)
    dist_per_car = distances_per_car(df)
    
    fig, ax = plt.subplots(1, 1, figsize=(20,10))
    provider = util.get_provider(df)
    color = util.get_color(df)

    std = dist_per_car['distance'].std()
    avg = dist_per_car['distance'].mean()
    normalized_distance = dist_per_car[(dist_per_car['distance'] >= (avg-std)) &
                                       (dist_per_car['distance'] <= (avg+std))]
    
    my_xticks = normalized_distance.plate
    plt.xticks(normalized_distance.index, my_xticks, rotation=45)
    plt.plot(normalized_distance.index, normalized_distance.distance, 
             linestyle='-', marker='x', color=color)
    plt.title("km per car normalized - " + provider)
    plt.ylabel("Km")
    plt.xlabel("plates")
#    plt.savefig(paths.plots_path+provider+"_dist_per_car_no_out.png")
#    plt.savefig(paths.plots_path2+provider+"_dist_per_car_no_out.png")
    plt.show()
    return
    
def fuel_behavior_max_distnace(df):
    provider = util.get_provider(df)
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
    plt.title("Fuel consuption, big dist - " + provider)
    plt.legend()
    plt.ylabel("Fuel level")
    plt.xlabel("Chrological rent ID")
#    plt.savefig(paths.plots_path+provider+"_fuel_behav_max_dist.png")
#    plt.savefig(paths.plots_path2+provider+"_fuel_behav_max_dist.png")
    plt.show()

    return fuel_cons
    
def fuel_behavior_max_booked(df):   
    provider = util.get_provider(df)
    count_df = df.groupby('plate', as_index = True).count()
    id_max = count_df.distance.idxmax(1) 
    #row = count_df.loc[id_max]
    plate = id_max
    fuel_cons = df[df.plate == plate]
    
    fig, ax = plt.subplots(1, 1, figsize=(9,10))
    x = range(0,len(fuel_cons.index))
    ax.plot(x, fuel_cons.init_fuel, 'bs', label='init fuel')
    ax.plot(x, fuel_cons.final_fuel,'r^', label= 'end fuel', alpha = 0.5)
    plt.title("Fuel consuption, most booked- " + util.get_provider(df))
    plt.legend()
    plt.ylabel("Fuel level")
    plt.xlabel("Chrological rent ID")
#    plt.savefig(paths.plots_path+provider+"_fuel_behav_most_booked.png")
#    plt.savefig(paths.plots_path2+provider+"_fuel_behav_most_booked.png")
    plt.show()
    return fuel_cons
    
def hist_cdf_pdf(df_source, df_dist, column, valid_days, valid_days_clnd):
    provider = util.get_provider(df_source)
    color = util.get_color(df_source)
    if column == "distance" :
        xlabel = "km"
    elif column == "duration" :
        xlabel = "min"
    else:
        xlabel = ""
        
    res = {}
    
    fig, ax = plt.subplots(2, 4, figsize=(20,10))
    fig.suptitle("Bookings " + column  + " - " + provider)
    
    ## dirty ##
    ax[0,0].hist(df_dist[column], 50, facecolor=color, alpha=0.75, cumulative=True, normed=True)
    ax[0,0].set_title("CDF - " + column)
    ax[0,0].set_xlabel(xlabel)
    
    ax[1,0].hist(df_dist[column], 50, facecolor=color, alpha=0.75)
    ax[1,0].set_title("PDF - " + column)
    ax[1,0].set_xlabel(xlabel)
    
    res[column+"_mean"] = df_dist[column].mean()
    res[column+"_median"] = df_dist[column].median()
    res[column+"_std"] = df_dist[column].std()

    ## filtering ##
    df_dist2 = util.clean_df(df_dist, column, df_dist[column].median(), df_dist[column].std())
    
    ax[0,1].hist(df_dist2[column], 50, facecolor=color, alpha=0.75, cumulative=True, normed=True)
    ax[0,1].set_title("filtered (med;std) CDF - " + column)
    ax[0,1].set_xlabel(xlabel)
    
    ax[1,1].hist(df_dist2[column], 50, facecolor=color, alpha=0.75)
    ax[1,1].set_title("filtered (med;std) PDF - " + column)
    ax[1,1].set_xlabel(xlabel)
    
    res[column+"_mean_flt"] = df_dist2[column].mean()
    res[column+"_median_flt"] = df_dist2[column].median()
    res[column+"_std_flt"] = df_dist2[column].std()
    

    ## per day ##
    ax[0,2].hist(df_dist2[column]/valid_days, 50, facecolor=color, alpha=0.75, cumulative=True, normed=True)
    ax[0,2].set_title("filtered CDF per day - " + column)
    ax[0,2].set_xlabel(xlabel)
    
    ax[1,2].hist(df_dist2[column]/valid_days, 50, facecolor=color, alpha=0.75)
    ax[1,2].set_title("filtered PDF per day - " + column)
    ax[1,2].set_xlabel(xlabel)
    
    res[column+"_mean_flt_per_day"] = (df_dist2[column]/valid_days).mean()
    res[column+"_median_flt_per_day"] = (df_dist2[column]/valid_days).median()
    res[column+"_std_flt_per_day"] = (df_dist2[column]/valid_days).std()
    
    ## per day clnd ##
    ax[0,3].hist(df_dist2[column]/valid_days_clnd, 50, facecolor=color, alpha=0.75, cumulative=True, normed=True)
    ax[0,3].set_title("filtered CDF per day clnd - " + column)
    ax[0,3].set_xlabel(xlabel)
    
    ax[1,3].hist(df_dist2[column]/valid_days_clnd, 50, facecolor=color, alpha=0.75)
    ax[1,3].set_title("filtered PDF per day clnd - " + column)
    ax[1,3].set_xlabel(xlabel)
    
    res[column+"_mean_flt_per_day_clnd"] = (df_dist2[column]/valid_days_clnd).mean()
    res[column+"_median_flt_per_day_clnd"] = (df_dist2[column]/valid_days_clnd).median()
    res[column+"_std_flt_per_day_clnd"] = (df_dist2[column]/valid_days_clnd).std()
    

#    plt.savefig(paths.plots_path+provider+"_PDF_CDF.png")
#    plt.savefig(paths.plots_path2+provider+"_PDF_CDF.png")
    fig.savefig(paths.plots_path3+"_"+provider+"_"+column+"_books_tats.png", bbox_inches='tight')

    plt.show()
    return res

def valid_days(df):
    provider = util.get_provider(df)
    color = util.get_color(df)
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
#    fig.savefig(paths.plots_path+provider+"_valid_days.png")
#    fig.savefig(paths.plots_path2+provider+"_valid_days.png")

    return

def gd_vs_ed_hist(df_dist, provider, color):
    fig, ax = plt.subplots(1,1,figsize=(9,10))
    ax.axhline(0.9, color='black', linestyle='-')
    ax.axhline(0.95, color='black', linestyle='-')
    ax.axhline(0.99, color='black', linestyle='-')
    ax.set_title(provider+" - Error google d. - Euclidean d.", fontsize=20)
    df_dist.dr_over_dist.hist(ax=ax, cumulative=True, color=color, normed=True, bins=500)
#    fig.savefig(paths.plots_path2+provider+"_errors_on_dist.png", bbox_inches='tight')
    fig.savefig(paths.plots_path3+provider+"_errors_on_dist.png", bbox_inches='tight')
    plt.show()
    return
    

enjoy = pd.read_pickle(paths.enjoy_bookings_pickle_path, None)
car2go = pd.read_pickle(paths.car2go_bookings_pickle_path, None)
enj_data = {}
c2g_data = {}
enj_data["general"] = util.get_valid_days(enjoy,start,end)
c2g_data["general"] = util.get_valid_days(car2go,start,end)

enj_bookings = len(pd.read_pickle(paths.enjoy_bookings_pickle_path))
enj_parkings = len(pd.read_pickle(paths.enjoy_parkings_pickle_path))
enj_cars = len(enjoy.plate.unique())
enj_days = 35.0

print "enj B/D " + str(enj_bookings/enj_days)
print "enj_B/D/C " + str(enj_bookings/enj_days/enj_cars)
print "enj P/D " + str(enj_parkings/enj_days)
print "enj P/D/C " + str(enj_parkings/enj_days/enj_cars)
print
c2g_bookings = len(pd.read_pickle(paths.car2go_bookings_pickle_path))
c2g_parkings = len(pd.read_pickle(paths.car2go_parkings_pickle_path))
c2g_cars = len(car2go.plate.unique())
c2g_days = 38.0

print "c2g B/D " + str(c2g_bookings/c2g_days)
print "c2g B/D/C " + str(c2g_bookings/c2g_days/c2g_cars)
print "c2g P/D " + str(c2g_parkings/c2g_days)
print "c2g P/D/C " + str(c2g_parkings/c2g_days/c2g_cars)




valid_days(enjoy)
valid_days(car2go)


enj_dist = distances_per_car(enjoy)
#total_dist_per_car_no_outliers(enjoy)
enj_data["distance"] = hist_cdf_pdf(
        enjoy, 
        enj_dist, 
        "distance", 
        enj_data["general"]["valid_days"], 
        enj_data["general"]["cleaned_valid_days"]
        )
enj_data["duration"] = hist_cdf_pdf(
        enjoy, 
        enj_dist, 
        "duration", 
        enj_data["general"]["valid_days"], 
        enj_data["general"]["cleaned_valid_days"]
        )


##fuel_behavior_max_distnace(enjoy)
##fuel_cons = fuel_behavior_max_booked(enjoy)
#
#c2g_dist = total_dist_per_car(car2go)
##total_dist_per_car_no_outliers(car2go)
#c2g_data["distance"] = hist_cdf_pdf(
#        car2go, 
#        c2g_dist, 
#        "distance", 
#        c2g_data["general"]["valid_days"], 
#        c2g_data["general"]["cleaned_valid_days"]
#        )
#c2g_data["duration"] = hist_cdf_pdf(
#        car2go, 
#        c2g_dist, 
#        "duration", 
#        c2g_data["general"]["valid_days"], 
#        c2g_data["general"]["cleaned_valid_days"]
#        )

#fuel_cons  = fuel_behavior_max_distnace(car2go)
#fuel_behavior_max_booked(car2go)

'''
cerco macchine con cuty sbagliata
'''

#enj_dist_ok = enj_dist[(enj_dist["distance"] > 30)]
#enj_dist_not_ok = enj_dist[~enj_dist.isin(enj_dist_ok)].dropna()
#
#plates = enj_dist_not_ok['plate'].tolist()
#print len(plates)
#for pos in range(0, len(plates)):
#    plates[pos] = str(plates[pos])
#
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
#
#car_per_city = grouped.groupby('city').count()
#car_per_city["log"] = np.log10(car_per_city["bookings_per_car"])
#car_per_city.bookings_per_car.plot(color=dbp.get_color(enjoy), marker='o', linewidth=0)

#enjoy_torino = dbp.query_bookings_df("enjoy","Torino", start, end)
#enjoy_milano = dbp.query_bookings_df("enjoy","Milano", start, end)
#enjoy_firenze = dbp.query_bookings_df("enjoy","Firenze", start, end)
#enjoy_roma = dbp.query_bookings_df("enjoy","Roma", start, end)
#enjoy_catania = dbp.query_bookings_df("enjoy"," Catania", start, end)

#enjoy = pd.DataFrame()
#enjoy.append([enjoy_torino, enjoy_firenze, enjoy_milano, enjoy_roma, enjoy_catania], ignore_index=True)

'''
prendo i rental (ed elimino anche le entry senza google distnace)
'''
#enjoy = enj_bookings_filtered
#enjoy_distances = enjoy[enjoy.distance>20] #macchine che si sono spostate
#enjoy_distances = enjoy_distances[enjoy_distances.distance_dr != -1] #cars with valid entry of google_dir
#enjoy_distances["dr_over_dist"] = enjoy_distances["distance_dr"] / enjoy_distances["distance"]
#enjoy_distances = enjoy_distances[
#        (enjoy_distances["dr_over_dist"] >= enjoy_distances["dr_over_dist"].quantile(0.01)) &
#        (enjoy_distances["dr_over_dist"] <= enjoy_distances["dr_over_dist"].quantile(0.99)) ]
##enjoy_distances.dr_minus_dist.hist(normed=True, cumulative=True,color="red", bins =500)
#gd_vs_ed_hist(enjoy_distances, util.get_provider(enjoy), util.get_color(enjoy))
#
#
#car2go = c2g_bookings_filtered     
#c2g_distances = car2go[car2go.distance>20] #macchine che si sono spostate
#c2g_distances = c2g_distances[c2g_distances.distance_dr!= -1] #cars with valid entry of google_dir
##c2g_invalid = c2g_distances[c2g_distances.distance_dr == -1] #cars with valid entry of google_dir
#c2g_distances["dr_over_dist"] = c2g_distances["distance_dr"] / c2g_distances["distance"]
#c2g_distances = c2g_distances[
#        (c2g_distances["dr_over_dist"] >= c2g_distances["dr_over_dist"].quantile(0.01)) &
#        (c2g_distances["dr_over_dist"] <= c2g_distances["dr_over_dist"].quantile(0.99)) ]
##c2g_distances.dr_minus_dist.hist(normed=True, cumulative=True, color="blue", bins=500)
#gd_vs_ed_hist(c2g_distances, util.get_provider(car2go), util.get_color(car2go))
#
#print "car2go" 
#print c2g_distances.dr_over_dist.quantile(0.9)
#print c2g_distances.dr_over_dist.quantile(0.95)
#print c2g_distances.dr_over_dist.quantile(0.99)
#print "enjoy"
#print enjoy_distances.dr_over_dist.quantile(0.9)
#print enjoy_distances.dr_over_dist.quantile(0.95)
#print enjoy_distances.dr_over_dist.quantile(0.99)

'''
fuel consuption vs distnace eucl
'''

#enjoy = enjoy [enjoy["distance"] > 500]
#enjoy["fuel_diff"] = enjoy["final_fuel"] - enjoy["init_fuel"]
#x=enjoy["distance"] * enjoy_distances["dr_over_dist"].quantile(0.9)
#y=enjoy["fuel_diff"]
#fig, [ax1,ax2] = plt.subplots(1,2,figsize=(18,10))
#ax1.scatter(x,y, color='red')
#ax1.set_title("enjoy - fuel cosnuption vs distance", fontsize=18)
#ax1.set_ylabel("Fuel difference")
#ax1.set_xlabel("Distance [m]")
#
#
#car2go = car2go [car2go["distance"] > 500]
#car2go["fuel_diff"] = car2go["final_fuel"] - car2go["init_fuel"]
#x=car2go["distance"] * c2g_distances["dr_over_dist"].quantile(0.9)
#y=car2go["fuel_diff"]
#ax2.scatter(x,y, color='blue')
#ax2.set_title("car2go - fuel cosnuption vs distance",fontsize=18)
#ax2.set_ylabel("Fuel difference")
#ax2.set_xlabel("Distance [m]")
#
#fig.savefig(paths.plots_path3+"_scatter_fuel_diff.png", bbox_inches='tight')
#fig.show()
















