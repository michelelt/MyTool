import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
import datetime
import matplotlib.pyplot as plt
import paths as p
from util import Utility
import paths as paths
import thread


u = Utility()


turin_df = gpd.read_file("../SHAPE/Zonizzazione.dbf").to_crs({"init": "epsg:4326"})
grid_df = gpd.read_file("../SHAPE/grid.dbf").to_crs({"init": "epsg:4326"})

def pointfy (lon, lat):
    return Point(float(lon), float(lat))



pa_enjoy = pd.read_pickle(p.enjoy_parkings_pickle_path_zoned, None)
pa_car2go = pd.read_pickle(p.car2go_parkings_pickle_path_zoned, None)


def parkings_per_zone(df_in):
#    turin = gpd.read_file("../SHAPE/Zonizzazione.dbf").to_crs({"init": "epsg:4326"})
    
    turin = gpd.read_file("../SHAPE/grid500.dbf").to_crs({"init": "epsg:4326"})
    
#    df_in = df_in[df_in.duration > 20]
#    df_in['geometry'] = df_in.apply(lambda row: pointfy(row['lon'], row['lat']), axis = 1)
#    df_in ['geometry'] = pointfy(df_in["lon"],df_in["lat"])

    crs = {"init": "epsg:4326"}
    df_in = gpd.GeoDataFrame(df_in, crs=crs)
    
    turin['zone_id'] = turin.index
    df = gpd.sjoin(df_in, turin, how='right', op='within')
    df2 = df.groupby('zone_id').count()
#    df3 = pd.DataFrame(df.groupby('zone_id')['duration', 'zone_name'].sum())
    df3 = pd.DataFrame(df.groupby('zone_id')['duration'].sum())

    turin['count']  = df2[df2.columns[0]]
    turin['duration'] = (df3['duration'])
    turin_out = turin.dropna()
    
    
        ##total duration per zone /60 -> total duration in hours (a)
        ##(a)/ #parkings per zone -> hour of stop i each zone
    turin_out['max_avg_time'] = turin_out['duration']/60.0/turin_out['count']
    turin_out["max_parking"] = turin_out["count"]
    turin_out["max_time"] = turin_out["duration"]/60.0
    del turin
    return turin_out, df


#turin_c2g.to_csv("my_gdf_def.csv")
#turin_c2g.to_file('MyGeometries.shp', driver='ESRI Shapefile')


def plot_clorophlet_colorbar (gdf, column, filtered, vmin, vmax, provider, path):
    fig, ax = plt.subplots(1, 1, figsize=(10,10))
    gdf.plot(column=column, cmap='jet', ax=ax, linewidth=0.1)
    
    titles = { "max_time": provider + " - Whole parking time" + filtered,
              "max_avg_time" : provider + " - Avg. parking time"+ filtered,
              "max_parking" : provider + " - Parkings number"+ filtered
            }
    
    labels = { "max_time": "Cumulative parking time sum [h]",
              "max_avg_time" : "Average parking time [h]",
              "max_parking" : "Max. number of parkings"
            }
    plt.title(titles[column], fontsize = 36)
    ax.grid(linestyle='-', linewidth=1.0)
    plt.xticks([])
    plt.yticks([])
#    plt.xlabel("Latitude", fontproperties=font)
#    plt.ylabel("Longitude", fontproperties=font)
    

    cax = fig.add_axes([0.9, 0.1, 0.03, 0.8,])
    sm_ = plt.cm.ScalarMappable(cmap='jet',
                                norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm_._A = []
#    fig.colorbar(sm_, cax=cax)
    cbar = plt.colorbar(sm_, cax=cax)
    cbar.ax.tick_params(labelsize=20)
    cbar.set_label(labels[column], rotation=270, fontsize=20, labelpad=30)
#    gdf.apply(lambda x: ax.annotate(s=x.N, xy=(x.geometry.centroid.x, x.geometry.centroid.y), ha='center'),axis=1)
    
    fig.savefig(path, bbox_inches='tight')
    plt.show()
    
    return


def gloabl_function (df_parking, provider, ub, lb, column, path):
    parkings_filtered = df_parking[
        (df_parking["duration"] <= ub) & 
        (df_parking["duration"] >= lb )
        ]
    turin_df, parkings = parkings_per_zone(parkings_filtered) 
    parkings = parkings.dropna()
    
    df = turin_df  
    maxs =   { "max_time": 4500,
              "max_avg_time" : 25,
              "max_parking" : 1506}
    my_min = 0
    my_max = maxs[column]
    if lb > 0:
        title = ""
    else :
        title= ""
    print provider, column, my_min, my_max
    if "car2go" in path:
        df.loc[426,'max_time'] = 4500
    plot_clorophlet_colorbar(df, column, title,my_min,my_max, provider, path)
    return df
    
def duration_cdf (df, provider, path):
    if provider == 'car2go':
        color = 'blue'
    else:
        color = 'red'
    
    column='duration'
    df[column] = df[column].div(60.0)
    
    fig = plt.figure(figsize=(10,10))
    ax = fig.gca()
    ax.set_title(provider + " - Parking duration", fontsize=36)
    ax.grid()
    
    df1=df
    column='duration'
    values = [df1[column].quantile(0.25), 
              df1[column].quantile(0.50), 
              df1[column].quantile(0.75), 
              df1[column].quantile(0.99), 
              df1[column].mean(),
              df1[column].median(),
              df1[column].std()
              ]
    print provider, column
    print values
    print
    
    ax.hist(df["duration"], bins=100, cumulative=True, normed=True, color=color)    
    
    ax.set_ylabel("ECDF", fontsize=36)
    ax.set_xlabel("Duration [h]", fontsize=36)
    
    for tick in ax.xaxis.get_major_ticks():
         tick.label.set_fontsize(27) 
                
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(27)    
    
    if  len(path) > 0:
        plt.savefig(path,bbox_inches = 'tight',pad_inches = 0.25)
        print "salva"

      
'''
c2g - avg time per park in zone
'''

#q=0.01
#ub_c2g = pa_car2go["duration"].quantile(1-q/10)
#lb_c2g = pa_car2go["duration"].quantile(q*9)
#
#q=0.01
#ub_enj = pa_car2go["duration"].quantile(1-q/10)
#lb_enj = pa_car2go["duration"].quantile(q*9)

#provider = 'car2go'
#path = "/home/mc/Scrivania/Tesi/Writing/figures/04_data_analysis/parkings/"+provider
#column = 'max_time'
#gloabl_function(pa_car2go, provider, ub_c2g, lb_c2g, column, path+"_"+column+"_f")
#zzz = gloabl_function(pa_car2go, provider, max(pa_car2go["duration"]), 0, column, path+"_"+column)

#column = 'max_avg_time'
#gloabl_function(pa_car2go, provider, ub_c2g, lb_c2g, column, path+"_"+column+"_f") 
#gloabl_function(pa_car2go, provider, max(pa_car2go["duration"]), 0, column, path+"_"+column)

column = 'max_parking'
#gloabl_function(pa_car2go, provider, pa_car2go["duration"].quantile(0.95), 20, column, path+"_"+column+"_f")
#gloabl_function(pa_car2go, provider, max(pa_car2go["duration"]), 0, column, path+"_"+column)

#provider='enjoy'
#path = "/home/mc/Scrivania/Tesi/Writing/figures/04_data_analysis/parkings/"+provider
column = 'max_time'
#gloabl_function(pa_enjoy, provider, ub_enj, lb_enj, column, path+"_"+column+"_f")
#zzz2 = gloabl_function(pa_enjoy, provider, max(pa_enjoy["duration"]), 0, column, path+"_"+column)

#column = 'max_avg_time'
#gloabl_function(pa_enjoy, provider, ub_enj, lb_enj, column, path+"_"+column+"") ### THE OBLY ONE FILTERED! ####
#gloabl_function(pa_enjoy, provider, max(pa_enjoy["duration"]), 0, column, path+"_"+column)

#column = 'max_parking'
#gloabl_function(pa_enjoy, provider, lb_enj, 20, column, path+"_"+column+"_f")
#gloabl_function(pa_enjoy, provider, max(pa_enjoy["duration"]), 0, column, path+"_"+column)


provider = 'car2go'
path = "/home/mc/Scrivania/Tesi/toptesi/figures/04_data_analysis/parkings/"+provider
q=0.01
ub = pa_car2go["duration"].quantile(1-q/10)
lb = pa_car2go["duration"].quantile(q*9)
df1 = pa_car2go[
        (pa_car2go["duration"] <= ub) & 
        (pa_car2go["duration"] >= lb )
        ]
duration_cdf(df1, 'car2go', path+"_pd_cdf")

provider = 'enjoy'
path = "/home/mc/Scrivania/Tesi/toptesi/figures/04_data_analysis/parkings/"+provider
q=0.01
up = pa_car2go["duration"].quantile(1-q/10)
lb = pa_car2go["duration"].quantile(q*9)
df2 = pa_enjoy[
        (pa_enjoy["duration"] <= ub) & 
        (pa_enjoy["duration"] >= lb)
        ]
duration_cdf(df2, 'enjoy', path+"_pd_cdf")




def cdf_pdf_parking_time_per_zone(df_parkings,bins):

    color = u.get_color(df_parkings)
    provider = u.get_provider(df_parkings)
    
    check_big_zones = df_parkings.groupby("zone_id").count()
    zones = []
    zones = check_big_zones.index
#    path = paths.plots_path4+"/"+provider+"_zones/"+ str(zones[0])
#    print path
    for i in range (1, len(zones)) :
        df = df_parkings[df_parkings["zone_id"] == zones[i]]
    
        title1 = "zone "+str(zones[i]) + " - cdf, total element " + str(len(df))
        title2 = "zone "+str(zones[i]) + " - pdf, total element " + str(len(df))
        path = paths.plots_path4+"/"+provider+"_zones/"+ str(zones[i])
        print path
        
        fig, ax= plt.subplots(1,2, figsize=(20,10))
        
        ax1 = ax[0]
        ax2 = ax[1]
        df["duration"].hist(ax=ax1, bins=bins, cumulative=True, normed=True, color=color)
        ax1.set_title(title1)
        ax1.set_xlabel("minutes")
        
        df["duration"].hist(ax=ax2, bins=bins, normed=True , color=color)
        ax2.set_title(title2)
        ax2.set_xlabel("minutes")
        plt.ioff()
#        fig.savefig(paths.plots_path4+"/"+provider+"_zones50/"+ str(zones[i]), bbox_inches='tight')
        plt.close(fig)
