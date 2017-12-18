import imagestoosm.config as cfg
import os
import QuadKey.quadkey as quadkey
import numpy as np
import shapely.geometry as geometry
from skimage import draw
from skimage import io
import csv


# load up the OSM features into hash of arrays of polygons, in pixels

for classDir in os.listdir(cfg.rootOsmDir) :
    if ( classDir == 'baseball') :
        classDirFull = os.path.join( cfg.rootOsmDir,classDir)
        for fileName in os.listdir(classDirFull) :
            fullPath = os.path.join( cfg.rootOsmDir,classDir,fileName)
            with open(fullPath, "rt") as csvfile:
                csveader = csv.reader(csvfile, delimiter='\t')

                pts = []
                for row in csveader:
                    latLot = (float(row[0]),float(row[1]))
                    pixel = quadkey.TileSystem.geo_to_pixel(latLot,cfg.tileZoom)

                    pts.append(pixel)

                poly = geometry.Polygon(pts);

                areaMeters = poly.area * 0.596 *0.596;

                print("{}\t{}".format(fileName,areaMeters))








