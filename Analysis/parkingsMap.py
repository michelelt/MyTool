import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
import datetime
import matplotlib.pyplot as plt
import paths as p
from util import Utility

u = Utility()



turin = gpd.read_file("../SHAPE/Zonizzazione.dbf").to_crs({"init": "epsg:4326"})

def pointfy (lon, lat):
    return Point(float(lon), float(lat))

year = 2017
month = 5
day = 17
start = datetime.datetime(year, month, day, 0, 0, 0)
end = datetime.datetime(year, month +1, day, 23, 59, 0)
enjoy = pd.read_pickle(p.enjoy_parkings_pickle_path, None)
car2go = pd.read_pickle(p.car2go_parkings_pickle_path, None)
#v_enj = u.get_valid_days(enjoy, start,end)
#v_enj = v_enj[v_enj["entries"]>0]
#print len(v_enj), "enjoy"
#v_enj = u.get_valid_days(car2go, start,end)
#v_enj = v_enj[v_enj["entries"]>0]
#print len(v_enj), "car2go"


def parkings_per_zone(df_in, valid_days, fleet):
    df_in = df_in[df_in.duration > 20]
    df_in ['geometry'] = df_in.apply(lambda row: pointfy(row['lon'], row['lat']), axis = 1)
    crs = {"init": "epsg:4326"}
    df_in = gpd.GeoDataFrame(df_in, crs=crs)
    
    turin['zone_id'] = turin.index
    df = gpd.sjoin(df_in, turin, how='right', op='within')
    df2 = df.groupby('zone_id').count()
    df3 = pd.DataFrame(df.groupby('zone_id')['duration', 'zone_name'].sum())
    turin['count']  = df2['_id']
    turin['duration'] = (df3['duration'])
    turin_out = turin.dropna()
    turin_out = turin_out[turin_out['count'] > 90]
    turin_out['factor'] = turin_out['duration']/60/turin_out['count']
    return turin_out

#turin_c2g.to_csv("my_gdf_def.csv")
#turin_c2g.to_file('MyGeometries.shp', driver='ESRI Shapefile')


def plot_clorophlet_colorbar (gdf, column, title, vmin, vmax, provider):
    
    fig, ax = plt.subplots(1, 1, figsize=(9,10))
    gdf.plot(column=column, cmap='jet', ax=ax)
    plt.title(title)
    plt.xticks([])
    plt.yticks([])
#    plt.xlabel("Latitude", fontproperties=font)
#    plt.ylabel("Longitude", fontproperties=font)

    cax = fig.add_axes([0.9, 0.1, 0.03, 0.8])
    sm_ = plt.cm.ScalarMappable(cmap='jet', 
                                norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm_._A = []
    fig.colorbar(sm_, cax=cax)
#    fig.savefig(plots_path+provider+"_parkings_amp.png")
    plt.show()
#    plt.savefig("clorophlet_" + str(column) + "_" + str(slot) + ".pdf", format="pdf")
    
    return


#turin_c2g = parkings_per_zone(car2go, u.c2g_valid_days, u.c2g_fleet)    
#my_min = turin_c2g['factor'].min()
#my_max = turin_c2g['factor'].max()
#plot_clorophlet_colorbar(turin_c2g, 'factor', "parkings per zone - car2go",my_min,my_max, "car2go")
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


turin_enj = parkings_per_zone(enjoy, u.enj_valid_days, u.enj_fleet)
my_min = turin_enj['factor'].min()
my_max = turin_enj['factor'].max()
plot_clorophlet_colorbar(turin_enj, 'factor', "parkings per zone - enjoy",my_min,my_max,"enjoy")

