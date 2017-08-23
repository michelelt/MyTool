from fiona.crs import from_epsg
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
import paths as paths
#grid creation

#coordinates of turin (all area)
start_x = 7.58257
final_x = 7.7320933
step_x = 0.00064 * 5 #50m
start_y = 45.009132
final_y = 45.20
step_y = 0.00045 * 5 #50m

x = start_x
y= start_y
newdata = gpd.GeoDataFrame()
newdata.crs = from_epsg(4326)
newdata['geometry'] = None
gdf_row = 0
while x <= final_x:
    y = start_y
    while y <= final_y:
        p1 = (x,y)
        p2 = (x+step_x,y)
        p3 = (x+step_x, y+step_y)
        p4 = (x, y+step_y)
        q= Polygon([p1,p2,p3,p4])
        newdata.loc[gdf_row, 'geometry'] = q
        gdf_row = gdf_row + 1
        y = y + step_y
    
    x = x + step_x

outfp = r"/home/mc/Scrivania/Tesi/MyTool/SHAPE/grid250.shp"
newdata.to_file(outfp)