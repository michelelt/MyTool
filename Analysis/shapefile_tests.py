import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
import datetime
import matplotlib.pyplot as plt
import paths as p
from util import Utility
import paths as paths
import thread

turin_df = gpd.read_file("/home/mc/Scrivania/taglio_fogli_di_carta_tecnica_1000_geo/taglio_fogli_di_carta_tecnica_1000_geo.dbf").to_crs({"init": "epsg:4326"})
turin_df.plot()
plt.show()