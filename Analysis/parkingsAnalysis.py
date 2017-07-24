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
day = 17

c2g_fleet = 395
enj_fleet = 315

start = datetime.datetime(year, month, day, 0, 0, 0)
end = datetime.datetime(year, month+1, day, 23, 59, 0)

def clean_durations(df):
    df = df[df.duration < df.duration.quantile(0.99)]
    df = df[df.duration > df.duration.quantile(0.01)]
    return df

def duration_per_car(df) :
    out_df= pd.DataFrame()
    out_df["plate"]  = df.plate
    out_df['duration']  = df.duration
    dur_per_car = out_df.groupby('plate', as_index = False).sum()
    return dur_per_car

def bookings_per_car(df):
    df_freq = df.groupby('plate', as_index=True).count()
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
    provider = dbp.get_provider(df)
    color = dbp.get_color(provider)
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
    provider = dbp.get_provider(df)
    color = dbp.get_color(provider)
    df = clean_durations(df)
    dur_per_car = duration_per_car(df)
    
    std = dur_per_car['duration'].std()
    avg = dur_per_car['duration'].median()
    normalized_durations = dur_per_car[(dur_per_car['duration'] >= (avg-std)) &
                                       (dur_per_car['duration'] <= (avg+std))]
    
    fig, ax = plt.subplots(1, 1, figsize=(9,10))
    my_xticks = normalized_durations.plate
#    print len(my_xticks)
#    plt.xticks(normalized_durations.index, my_xticks)
    plt.plot(normalized_durations.index, normalized_durations['duration'], linestyle='-', marker='x',color=color)
    ax.set_title("min per car in std - " + provider)
    ax.set_xlabel("Plate")
    ax.set_ylabel("Total minutes")
    plt.show()
    
def hist_dur_freq(df, df_source):
    provider = dbp.get_provider(df_source)
    color = dbp.get_color(provider)
        
    provider = dbp.get_provider(df_source)
    color = dbp.get_color(provider)
    
    fig, ax = plt.subplots(2, 2, figsize=(9,10))
    fig.suptitle('distributions - ' + provider)
#    fig.set_title("distances - " + provider)
    ax[0,0].hist(df.duration, 50, facecolor=color, alpha=0.75, cumulative=True, normed=True)
    ax[0,0].set_title("CDF - durations")
    ax[0,1].hist(df.duration, 50, facecolor=color, alpha=0.75)
    ax[0,1].set_title("PDF - durations")

#    ax[1].set_title("distances filtered- " + provider)
#    df_source = df_source[df_source['duration'] > 90]
    df = df[df.freq > 30]
    ax[1,0].hist(df.duration, 50, facecolor=color, alpha=0.75, cumulative=True, normed=True)
    ax[1,0].set_title("filtered CDF - durations")
    ax[1,1].hist(df.duration, 50, facecolor=color, alpha=0.75)
    ax[1,1].set_title("filtered PDF - durations")
    return df

    
enjoy_parkings = dbp.query_parkings_df('enjoy','Torino', start, end)
car2go_parkings = dbp.query_parkings_df('car2go','Torino', start, end)
enjoy_parkings.to_pickle(paths.enjoy_parkings_pickle_path, None)
car2go_parkings.to_pickle(paths.car2go_parkings_pickle_path, None)

enjoy = pd.read_pickle(paths.enjoy_pickle_path, None)
car2go = pd.read_pickle(paths.car2go_pickle_path, None)


enjoy_parkings = pd.read_pickle(paths.enjoy_parkings_pickle_path, None)
car2go_parkings = pd.read_pickle(paths.car2go_parkings_pickle_path, None)


enjoy_parkings_duration = duration_per_car(enjoy_parkings)
enj_park_duration_freq = total_dur_per_car(enjoy_parkings, enjoy)
total_dist_per_car_no_outliers(enjoy)
enj_clean = hist_dur_freq(enj_park_duration_freq, enjoy)

car2go_parkings_duration = duration_per_car(car2go_parkings)
car2go_park_duration_freq = total_dur_per_car(car2go_parkings, car2go)
total_dist_per_car_no_outliers(car2go)
c2g_clean = hist_dur_freq(car2go_park_duration_freq, car2go)

"""
Avg parking time per car (valid days)
"""
enj_park_days= util.get_valid_days(enjoy,start,end)
valid_days = enj_park_days[enj_park_days.entries > 0]
enj_clean["duration_per_day"] = enj_park_duration_freq["duration"]/len(valid_days)
enj_clean["freq_per_day"] = enj_park_duration_freq["freq"]/len(valid_days)


c2g_park_days= util.get_valid_days(car2go,start,end)
valid_days = c2g_park_days[c2g_park_days.entries > 0]
c2g_clean["duration_per_day"] = car2go_park_duration_freq["duration"]/len(valid_days)
c2g_clean["freq_per_day"] = car2go_park_duration_freq["freq"]/len(valid_days)


fig,ax =plt.subplots(1, 1, figsize=(9,10))
enj_clean.hist(ax=ax, color=util.get_color(enjoy))
fig2,ax2 = plt.subplots(1, 1, figsize=(9,10))
c2g_clean.hist(ax=ax2, color=util.get_color(car2go))




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



