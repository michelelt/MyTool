import pandas as pd
import geopandas as gpd
import numpy as np
import datetime
import time
import random
import sys
import os.path
sys.path.insert(0, '/home/mc/Scrivania/Tesi/MyTool/Analysis/')
import paths as paths
from DataBaseProxy import DataBaseProxy
sys.path.insert(0, '/home/mc/Scrivania/Tesi/MyTool/Analysis/simulator')
from util import Utility
from car import Car
from shapely.geometry import Point, Polygon
from station import Station
import threading

def main(args): 
    a = int(args[0])
    time.sleep(a)
    print a
    

if __name__ == '__main__':
  main()