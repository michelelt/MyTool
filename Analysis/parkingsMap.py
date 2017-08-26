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



pa_enjoy = pd.read_pickle(p.enjoy_parkings_pickle_path, None)
pa_car2go = pd.read_pickle(p.car2go_parkings_pickle_path, None)


def parkings_per_zone(df_in, valid_days, fleet, q):
#    turin = gpd.read_file("../SHAPE/Zonizzazione.dbf").to_crs({"init": "epsg:4326"})
    
    turin = gpd.read_file("../SHAPE/grid500.dbf").to_crs({"init": "epsg:4326"})
    
    df_in = df_in[df_in.duration > 20]
    df_in['geometry'] = df_in.apply(lambda row: pointfy(row['lon'], row['lat']), axis = 1)
#    df_in ['geometry'] = pointfy(df_in["lon"],df_in["lat"])

    crs = {"init": "epsg:4326"}
    df_in = gpd.GeoDataFrame(df_in, crs=crs)
    
    turin['zone_id'] = turin.index
    df = gpd.sjoin(df_in, turin, how='right', op='within')
    df2 = df.groupby('zone_id').count()
#    df3 = pd.DataFrame(df.groupby('zone_id')['duration', 'zone_name'].sum())
    df3 = pd.DataFrame(df.groupby('zone_id')['duration'].sum())

    turin['count']  = df2['_id']
    turin['duration'] = (df3['duration'])
    turin_out = turin.dropna()
#    turin_out = turin_out[
#            (turin_out['count'] >= turin_out['count'].quantile(q) ) &
#            (turin_out['count'] <= turin_out['count'].quantile(1-q))]

#    turin_out = turin_out[
#            (turin_out['count'] >= turin_out['count'].quantile(q))]


#    turin_out = turin_out[
#        (turin_out['count'] >= 1)]
    
    ##total duration per zone /60 -> total duration in hours (a)
    ##(a)/ #parkings per zone -> hour of stop i each zone
    turin_out['factor'] = turin_out['duration']/60/turin_out['count']
    del turin
    return turin_out, df


#turin_c2g.to_csv("my_gdf_def.csv")
#turin_c2g.to_file('MyGeometries.shp', driver='ESRI Shapefile')


def plot_clorophlet_colorbar (gdf, column, title, vmin, vmax, provider):
    fig, ax = plt.subplots(1, 1, figsize=(10,10))
    gdf.plot(column=column, cmap='jet', ax=ax, linewidth=0.1)
    plt.title(title, fontsize = 18)
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
    cbar.ax.tick_params(labelsize=14)
    cbar.set_label('Mean car parking time per hour', rotation=270, fontsize=18, labelpad=30)
#    gdf.apply(lambda x: ax.annotate(s=x.N, xy=(x.geometry.centroid.x, x.geometry.centroid.y), ha='center'),axis=1)
    
#    fig.savefig(paths.plots_path4+provider+"500x500_parkings_amp.png", bbox_inches='tight',dpi=250)
    plt.show()
#    plt.savefig("clorophlet_" + str(column) + "_" + str(slot) + ".pdf", format="pdf")
    
    return

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
        fig.savefig(paths.plots_path4+"/"+provider+"_zones50/"+ str(zones[i]), bbox_inches='tight')
        plt.close(fig)


#df_in = car2go
#
#df_in = df_in[df_in.duration > 20]
#df_in ['geometry'] = df_in.apply(lambda row: pointfy(row['lon'], row['lat']), axis = 1)
#crs = {"init": "epsg:4326"}
#df_in = gpd.GeoDataFrame(df_in, crs=crs)
#
#turin['zone_id'] = turin.index
#df = gpd.sjoin(df_in, turin, how='right', op='within')
#df2 = df.groupby('zone_id').count()
#df3 = pd.DataFrame(df.groupby('zone_id')['duration'].sum())
#turin['count']  = df2['_id']
#turin['duration'] = df3['duration']
#turin_out = turin.dropna()
#turin_out = turin_out[turin_out['count'] > 90]
#turin_out['factor'] = turin_out['count']*turin_out['duration']


   
   
'''
c2g - avg time per park in zone
'''
q=0.05
c2g_parkings_filtered = pa_car2go[
        (pa_car2go["duration"] <= pa_car2go["duration"].quantile(1-q)) & 
        (pa_car2go["duration"] >= 20 )
        ]
C2G_FLEET = 414
C2G_DAYS = 39
turin_c2g, car2go_parkings = parkings_per_zone(c2g_parkings_filtered, C2G_DAYS, C2G_FLEET, 0.01) 
car2go_parkings = car2go_parkings.dropna()
#cdf_pdf_parking_time_per_zone(car2go_parkings,50)
#q=0.05
#df = turin_c2g[
#        (turin_c2g['factor'] >= turin_c2g['factor'].quantile(q) ) &
#        (turin_c2g['factor'] <= turin_c2g['factor'].quantile(1-q))]
df = turin_c2g  
my_min = df['factor'].min()
my_max = df['factor'].max()
plot_clorophlet_colorbar(df, 'factor', "parkings per zone - car2go",my_min,my_max, "car2go")

#plt.scatter(turin_c2g.zone_id, turin_c2g.factor)
#plt.show()
#q=0.5
#df = turin_c2g[
#        (turin_c2g['factor'] >= turin_c2g['factor'].quantile(q) ) &
#        (turin_c2g['factor'] <= turin_c2g['factor'].quantile(1-q))]
#plt.scatter(df.zone_id, df.factor)
#plt.show()



'''
enjoy - avg time per park in zone
'''
#turin_enj, enjoy_parkings = parkings_per_zone(enjoy, u.enj_valid_days, u.enj_fleet, 0.01)
#enjoy_parkings = enjoy_parkings.dropna()
#cdf_pdf_parking_time_per_zone(enjoy_parkings,50)

#df = turin_enj[
#        (turin_enj['factor'] >= turin_enj['factor'].quantile(q) ) &
#        (turin_enj['factor'] <= turin_enj['factor'].quantile(1-q))]  
#my_min = df['factor'].min()
#my_max = df['factor'].max()
#plot_clorophlet_colorbar(df, 'factor', "parkings per zone - enjoy",my_min,my_max,"enjoy")

#out_csv=pd.DataFrame()
#out_csv["N"] = turin_df["N"]
#out_csv["Denom_GTT"] = turin_df["Denom_GTT"]
#out_csv["zone_name"] = turin_df["zone_name"]
#
#plt.ioff()
#fig, ax = plt.subplots(1, 1, figsize=(30,30))
#turin_df.apply(lambda x: ax.annotate(s=str(x.N) +"\n"+x.zone_name, xy=(x.geometry.centroid.x, x.geometry.centroid.y), ha='center'),axis=1)
#turin_df.plot(ax = ax)
#ax.grid(linestyle='-')
#ax.set_title("Zones with names", fontsize = 18)
#plt.show()
#ax.set_xticks([])
#ax.set_yticks([])
#plt.savefig(paths.plots_path3+"_all_zones_.png", bbox_inches='tight')
#plt.close(fig)

