import os, sys
import ogr
from math import ceil, cos,sin, sqrt, degrees, radians
from util import Utility
import paths as paths


def griding(outputGridfn,xmin,xmax,ymin,ymax,gridHeight,gridWidth):

    # convert sys.argv to float
    xmin = float(xmin)
    xmax = float(xmax)
    ymin = float(ymin)
    ymax = float(ymax)
    gridWidth = float(gridWidth)
    gridHeight = float(gridHeight)

    # get rows
    rows = ceil((ymax-ymin)/gridHeight)
    # get columns
    cols = ceil((xmax-xmin)/gridWidth)

    # start grid cell envelope
    ringXleftOrigin = xmin
    ringXrightOrigin = xmin + gridWidth
    ringYtopOrigin = ymax
    ringYbottomOrigin = ymax-gridHeight

    # create output file
    outDriver = ogr.GetDriverByName('ESRI Shapefile')
    if os.path.exists(outputGridfn):
        os.remove(outputGridfn)
    outDataSource = outDriver.CreateDataSource(outputGridfn)
    outLayer = outDataSource.CreateLayer(outputGridfn,geom_type=ogr.wkbPolygon )
    featureDefn = outLayer.GetLayerDefn()
    print "cols " + str(cols)
    print "rows " + str(rows)
    # create grid cells
    countcols = 0
    while countcols < cols:
        countcols += 1

        # reset envelope for rows
        ringYtop = ringYtopOrigin
        ringYbottom =ringYbottomOrigin
        countrows = 0

        while countrows < rows:
            print   "C: " + str(countcols) + " R: " + str(countrows)
            countrows += 1
            ring = ogr.Geometry(ogr.wkbLinearRing)
            ring.AddPoint(ringXleftOrigin, ringYtop)
            ring.AddPoint(ringXrightOrigin, ringYtop)
            ring.AddPoint(ringXrightOrigin, ringYbottom)
            ring.AddPoint(ringXleftOrigin, ringYbottom)
            ring.AddPoint(ringXleftOrigin, ringYtop)
            poly = ogr.Geometry(ogr.wkbPolygon)
            poly.AddGeometry(ring)

            # add new geom to layer
            outFeature = ogr.Feature(featureDefn)
            outFeature.SetGeometry(poly)
            outLayer.CreateFeature(outFeature)
            outFeature.Destroy

            # new envelope for next poly
            ringYtop = ringYtop - gridHeight
            ringYbottom = ringYbottom - gridHeight

        # new envelope for next poly
        ringXleftOrigin = ringXleftOrigin + gridWidth
        ringXrightOrigin = ringXrightOrigin + gridWidth

    # Close DataSources
    outDataSource.Destroy()
    
#50m in decimal degree 0.0045
def convert_geo2cart(lat, lon, high):
    phi = radians(lat)
    lam = radians(lon)
    a = 6378137
    alfa = 1/298.257223563
    C = a*(1-alfa)
    e2 = (a*a - C*C)/(a*a)
    fact = e2*(sin(phi)*sin(phi))
    w = sqrt(1-fact)
    res = {
        "x" : ((a/w)+high) * cos(phi) * cos(lam),
        "y" : ((a/w)+high) * cos(phi) * sin(lam),
        "z" : ((a/w)*(1-e2)+high) * sin(phi)
        }
    
    return res

high_left = {
        "lat" : 45.20,
        "lon" : 7.4,
        "h": 300
        }
bottom_right = {
        "lat" : 44.85,
        "lon" : 7.9,
        "h": 300
        }

x = []
y = []
x.append(convert_geo2cart(high_left["lat"], high_left["lon"], high_left["h"])["x"])
y.append(convert_geo2cart(high_left["lat"], high_left["lon"], high_left["h"])["y"])
x.append(convert_geo2cart(bottom_right["lat"], bottom_right["lon"], bottom_right["h"])["x"])
y.append(convert_geo2cart(bottom_right["lat"], bottom_right["lon"], bottom_right["h"])["y"])

griding(paths.grid_path, 
        min(x), max(x), 
        min(y), max(y), 
        40000/50, 
        40000/50 )
