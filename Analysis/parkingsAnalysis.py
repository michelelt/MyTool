#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import paths as paths

from DataBaseProxy import DataBaseProxy
from util import Utility
util = Utility()
dbp = DataBaseProxy()


year = 2017
month = 5
day = 6

#km macchine per enjoy e car2go in una settimana
start = datetime.datetime(year, month, day, 0, 0, 0)
end = datetime.datetime(year, month +2, day, 23, 59, 0)
end2 = datetime.datetime(year, month, day, 23,59,0)

def clean_durations(df):
    df = df[df.duration < df.duration.quantile(0.99)]
    df = df[df.duration > df.duration.quantile(0.01)]
    return df

def duration_per_car(df) :
    out_df= pd.DataFrame()
    out_df["plate"]  = df.plate
    out_df['duration']  = df.duration
    dur_per_car = out_df.groupby('plate',  as_index = False).sum()
    return dur_per_car

def bookings_per_car(df):
    df_freq = df.groupby('plate').count()
    df_freq = df_freq[['_id']].copy()
    df_freq = df_freq.rename(columns={'_id': 'freq'})
    return df_freq

def parkings_per_car(df) :
    out_df= pd.DataFrame()
    out_df["plate"]  = df.plate
    out_df['number_of_parkings']  = df.duration
    dur_per_car = out_df.groupby('plate', as_index = False).count()
    
    return dur_per_car

def total_dur_per_car(df, df2):
    provider = util.get_provider(df)
    color = util.get_color(df)
    df = clean_durations(df)
    dur_per_car = duration_per_car(df)
    freq_per_car = bookings_per_car(df2)
    

    fig, ax = plt.subplots(1, 1, figsize=(9,10))
    my_xticks = dur_per_car.plate
#    print len(my_xticks)
    ax.plot(dur_per_car.index, dur_per_car.duration, linestyle='-', marker='x',color=color)
#    ax.set_xticks(my_xticks)
    ax.set_title("min per car - " + provider)
    ax.set_xlabel("Plate")
    ax.set_ylabel("Total minutes")
    plt.show()
    dur_per_car.set_index('plate', inplace=True)
    dur_per_car['freq'] = freq_per_car['freq']
    dur_per_car.dropna()
    return dur_per_car
    
def total_dist_per_car_no_outliers (df):
    provider = util.get_provider(df)
    color = util.get_color(df)
    df = clean_durations(df)
    dur_per_car = duration_per_car(df)
    
    std = dur_per_car['duration'].std()
    avg = dur_per_car['duration'].median()
    normalized_durations = dur_per_car[(dur_per_car['duration'] >= (avg-std)) &
                                       (dur_per_car['duration'] <= (avg+std))]
    
    fig, ax = plt.subplots(1, 1, figsize=(9,10))
#    my_xticks = normalized_durations.plate
#    print len(my_xticks)
#    plt.xticks(normalized_durations.index, my_xticks)
    plt.plot(normalized_durations.index, normalized_durations['duration'], linestyle='-', marker='x',color=color)
    ax.set_title("min per car in std - " + provider)
    ax.set_xlabel("Plate")
    ax.set_ylabel("Total minutes")
    plt.show()
    
def hist_dur_freq(column, df, df_source, data):
    provider = util.get_provider(df_source)
    color = util.get_color(df_source)

    if column == "duration":
        xlabel = "min"
    else :
        xlabel = ""
    
    if column == "freq":
        df = df.dropna()
        
    fig, ax = plt.subplots(2, 4, figsize=(20,10))
    fig.suptitle(provider + ' - ' + column + ' distributions')
    
    #uncleaned data
    ax[0,0].hist(df[column], 50, facecolor=color, alpha=0.75, cumulative=True, normed=True)
    ax[0,0].set_title("CDF - " + column)
    ax[0,0].set_xlabel(xlabel)
    
    ax[1,0].hist(df[column], 50, facecolor=color, alpha=0.75)
    ax[1,0].set_title("PDF - " + column)
    ax[1,0].set_xlabel(xlabel)
        
    #filtering - only cars with at least 3 parkings at day
    df = df[df.freq > 30]
    ax[0,1].hist(df[column], 50, facecolor=color, alpha=0.75, cumulative=True, normed=True)
    ax[0,1].set_title("filtered CDF - " + column)
    ax[0,1].set_xlabel(xlabel)
    
    ax[1,1].hist(df[column], 50, facecolor=color, alpha=0.75)
    ax[1,1].set_title("filtered PDF - " + column)
    ax[1,1].set_xlabel(xlabel)
    
    #divided per number of days
    ax[0,2].hist(df[column]/data["valid_days"], 50, facecolor=color, alpha=0.75, cumulative=True, normed=True)
    ax[0,2].set_title("filtered CDF per day - " + column)
    ax[0,2].set_xlabel(xlabel)
    
    ax[1,2].hist(df[column]/data["valid_days"], 50, facecolor=color, alpha=0.75)
    ax[1,2].set_title("filtered PDF per day - " + column)
    ax[1,2].set_xlabel(xlabel)
    
    #divided per number of days in interval
    ax[0,3].hist(df[column]/data["cleaned_valid_days"], 50, facecolor=color, alpha=0.75, cumulative=True, normed=True)
    ax[0,3].set_title("filtered CDF per day clnd - " + column)
    ax[0,3].set_xlabel(xlabel)
    
    ax[1,3].hist(df[column]/data["cleaned_valid_days"], 50, facecolor=color, alpha=0.75)
    ax[1,3].set_title("filtered PDF per day clnd - " + column)
    ax[1,3].set_xlabel(xlabel)
    
    res = {
            column+"_mean" : df[column].mean(),
            column+"_median": df[column].median(),
            column+"_std" : df[column].std(),
            column+"_mean_valid_days" : (df[column]/data["valid_days"]).mean(),
            column+"_median_valid_days": (df[column]/data["valid_days"]).median(),
            column+"_std_valid_days" : (df[column]/data["valid_days"]).std(),
            column+"_mean_valid_days_clnd" : (df[column]/data["cleaned_valid_days"]).mean(),
            column+"_median_valid_days_clnd": (df[column]/data["cleaned_valid_days"]).median(),
            column+"_std_valid_days_clnd" : (df[column]/data["cleaned_valid_days"]).std()
            }
    
    fig.savefig(paths.plots_path3+"_"+provider+"_"+column+"_parkings_tats.png", bbox_inches='tight')
    return df,res
#
#enjoy_parkings = dbp.query_parkings_df('enjoy','Torino', start, end)
#car2go_parkings = dbp.query_parkings_df('car2go','Torino', start, end)
#enjoy_parkings.to_pickle(paths.enjoy_parkings_pickle_path, None)
#car2go_parkings.to_pickle(paths.car2go_parkings_pickle_path, None)

enjoy = pd.read_pickle(paths.enjoy_pickle_path, None)
car2go = pd.read_pickle(paths.car2go_pickle_path, None)
enjoy_parkings = pd.read_pickle(paths.enjoy_parkings_pickle_path, None)
car2go_parkings = pd.read_pickle(paths.car2go_parkings_pickle_path, None)


#enj_data = util.get_valid_days(enjoy,start,end)
#c2g_data = util.get_valid_days(car2go,start,end)


#enjoy_parkings_duration = duration_per_car(enjoy_parkings)
#enj_park_duration_freq = total_dur_per_car(enjoy_parkings, enjoy)
#total_dist_per_car_no_outliers(enjoy)
#enj_clean, enj_data["park_stats_duration"]  = hist_dur_freq("duration", enj_park_duration_freq, enjoy, enj_data)
#enj_clean, enj_data["park_stats_freq"]  = hist_dur_freq("freq", enj_park_duration_freq, enjoy, enj_data)
#
#car2go_parkings_duration = duration_per_car(car2go_parkings)
#car2go_park_duration_freq = total_dur_per_car(car2go_parkings, car2go)
#total_dist_per_car_no_outliers(car2go)
#c2g_clean, c2g_data["park_stats_duration"] = hist_dur_freq("duration", car2go_park_duration_freq, car2go, c2g_data)
#c2g_clean, c2g_data["park_stats_freq"] = hist_dur_freq("freq", car2go_park_duration_freq, car2go, c2g_data)

"""
Avg parking time per car (valid days)
"""
#enj_clean["duration_per_day"] = enj_park_duration_freq["duration"]/(enj_data["cleaned_valid_days"])
#enj_clean["freq_per_day"] = enj_park_duration_freq["freq"]/(enj_data["cleaned_valid_days"])
#c2g_clean["duration_per_day"] = car2go_park_duration_freq["duration"]/(c2g_data["cleaned_valid_days"])
#c2g_clean["freq_per_day"] = car2go_park_duration_freq["freq"]/(enj_data["cleaned_valid_days"])
#
#
#fig,ax =plt.subplots(1, 1, figsize=(9,10))
#enj_clean.hist(ax=ax, color=util.get_color(enjoy))
#fig2,ax2 = plt.subplots(1, 1, figsize=(9,10))
#c2g_clean.hist(ax=ax2, color=util.get_color(car2go))

'''
come informazione ho il numero di minuti in cui è stata ferma la macchina, e il numero di prenotazioni che questa ha
ricevuto
'''
#total_dist_per_car_no_outliers(enjoy_parkings)

#dur_per_car['index']  = dur_per_car['index'] / (dur_per_car['index'].sum())
#dur_per_car.hist(bins=100, cumulative=True, normed=True)


#df2 = parkings_per_car(enjoy_parkings)
#enjoy_parkings_duration['count'] = df2['number_of_parkings']
#
#df = enjoy_parkings[
#                    (enjoy_parkings.plate == 'EZ049TY')
#                    ]


