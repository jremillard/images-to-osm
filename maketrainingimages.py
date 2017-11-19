import imagestoosm.config as cfg
import os
import QuadKey.quadkey as quadkey
import numpy as np
import shapely.geometry as geometry
from skimage import draw
from skimage import io
import csv

minFeatureClip = 0.3

# make the training data images

# construct index of osm data, each point
# for each tile
#   check for tiles east and south, and south/east to make 512x512 tile, if no skip
# bounding box for image
# write out image as png
# see what features overlap with image

# if more than >20%
# lit of augmentations (N +45,-45 degree), N offsets
#    emit mask for feature for current image.

# training will do flips, intensity, and color shifts if needed


os.system("rm -R " + cfg.trainDir)
os.mkdir(cfg.trainDir)

# load up the OSM features into hash of arrays of polygons, in pixels
features = {}

for classDir in os.listdir(cfg.rootOsmDir) :
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

            feature = {
                "geometry" : geometry.Polygon(pts),
                "filename" : fullPath
            }

            if ( (classDir in features) == False) :
                features[classDir] = []

            features[classDir].append( feature )

imageWriteCounter = 0
for root, subFolders, files in os.walk(cfg.rootTileDir):

    for file in files: 

        quadKeyStr = os.path.splitext(file)[0]

        qkRoot = quadkey.from_str(quadKeyStr)
        tilePixel = quadkey.TileSystem.geo_to_pixel(qkRoot.to_geo(), qkRoot.level)

        tileRootDir = os.path.split( root)[0]

        # stick the adjacent tiles together to make larger images up to max
        # image size.
        maxImageSize = 256*3
        maxTileCount = maxImageSize // 256
        count = 0
        image = np.zeros([maxImageSize,maxImageSize,3],dtype=np.uint8)
        for x in range(maxTileCount) :
            for y in range(maxTileCount) :
                pixel = ( tilePixel[0] + 256*x, tilePixel[1]+256*y)
                geo = quadkey.TileSystem.pixel_to_geo(pixel, qkRoot.level)
                qk = quadkey.from_geo(geo, qkRoot.level)

                qkStr = str(qk)

                tileCacheDir = os.path.join(tileRootDir,qkStr[-3:])

                tileFileName = "%s/%s.jpg" % (tileCacheDir, qkStr)

                if ( os.path.exists(tileFileName) ) :
                    image[ y*256 : (y+1)*256, x*256 : (x+1)*256,0:3 ] = io.imread(tileFileName )
                    count += 1


        pts = []
        pts.append( ( tilePixel[0]+0,tilePixel[1]+0 ) )
        pts.append( ( tilePixel[0]+0,tilePixel[1]+maxImageSize ) )
        pts.append( ( tilePixel[0]+maxImageSize,tilePixel[1]+maxImageSize ) )
        pts.append( ( tilePixel[0]+maxImageSize,tilePixel[1]+0 ) )
        
        imageBoundingBoxPoly = geometry.Polygon(pts)

        if (os.path.exists( "%s/%05d" % (cfg.trainDir,imageWriteCounter) ) == False) :
            os.mkdir( "%s/%05d" % (cfg.trainDir,imageWriteCounter) )

        featureMask = np.zeros((maxImageSize, maxImageSize), dtype=np.uint8)
        featureCountTotal = 0
        usedFileNames = []
        for featureType in features :
            featureCount = 0
            for feature in features[featureType] :
                if ( imageBoundingBoxPoly.intersects( feature['geometry']) ) :
                    area = feature['geometry'].area

                    xs, ys = feature['geometry'].exterior.coords.xy
                    xs = [ x-tilePixel[0] for x in xs]
                    ys = [ y-tilePixel[1] for y in ys]
    
                    xsClipped = [ min( max( x,0),maxImageSize) for x in xs]
                    ysClipped = [ min( max( y,0),maxImageSize) for y in ys]

                    pts2 = []
                    for i in range(len(xs)) :
                        pts2.append( (xsClipped[i],ysClipped[i] ) )

                    clippedPoly = geometry.Polygon(pts2)
                    newArea = clippedPoly.area

                    if ( newArea/area > minFeatureClip) :
                        featureMask.fill(0)
                        rr, cc = draw.polygon(xs,ys,(maxImageSize,maxImageSize))
                        featureMask[cc,rr] = 255
                        io.imsave("%s/%05d/%05d-%s-%d.png" % (cfg.trainDir,imageWriteCounter,imageWriteCounter,featureType,featureCount),featureMask)
                        usedFileNames.append( feature['filename'] )
                        featureCount += 1
                        featureCountTotal += 1

        if ( featureCountTotal > 0) :
            io.imsave("%s/%05d/%05d.jpg" % (cfg.trainDir,imageWriteCounter,imageWriteCounter),image,quality=100)
            
            with open("%s/%05d/%05d.txt" % (cfg.trainDir,imageWriteCounter,imageWriteCounter), "wt") as text_file:
                text_file.write( "%s\n" % (str(qkRoot)))
                text_file.write( "%0.8f,%0.8f\n" % qkRoot.to_geo())
                for f in usedFileNames :
                    text_file.write( "%s\n" % (f))
                    
            imageWriteCounter += 1

            print("%s - %s - tiles %d - features %d" % (os.path.join(root, file), quadKeyStr,count, featureCountTotal))





