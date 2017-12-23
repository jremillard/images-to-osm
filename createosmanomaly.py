import sys
sys.path.append("Mask_RCNN")

import os
import sys
import glob
import osmmodelconfig
import skimage
import math
import imagestoosm.config as osmcfg
import model as modellib
import visualize as vis
import numpy as np
import csv
import QuadKey.quadkey as quadkey
import shapely.geometry as geometry
import shapely.affinity as affinity
import matplotlib.pyplot as plt
import cv2
import scipy.optimize 
import time
from skimage import draw
from skimage import io

showFigures = False

def toDegrees(rad):
  return rad * 180/math.pi

def writeOSM( osmFileName,featureName, simpleContour,tilePixel, qkRoot) :
    with open(osmFileName,"wt",encoding="ascii") as f: 
        f.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
        f.write("<osm version=\"0.6\">\n")
        id = -1
        for pt in simpleContour :
            geo = quadkey.TileSystem.pixel_to_geo( (pt[0,0]+tilePixel[0],pt[0,1]+tilePixel[1]),qkRoot.level)
            f.write("  <node id=\"{}\" lat=\"{}\" lon=\"{}\" />\n".format(id,geo[0],geo[1]))
            id -= 1

        f.write("  <way id=\"{}\" visible=\"true\">\n".format(id))
        id = -1
        for pt in simpleContour :
            f.write("    <nd ref=\"{}\" />\n".format(id))
            id -= 1
        f.write("    <nd ref=\"{}\" />\n".format(-1))
        f.write("    <tag k=\"{}\" v=\"{}\" />\n".format("leisure","pitch"))
        f.write("    <tag k=\"{}\" v=\"{}\" />\n".format("sport",featureName))
        f.write("  </way>\n")

        f.write("</osm>\n")   
        f.close             

def writeShape(wayNumber, finalShape, image, bbTop,bbHeight,bbLeft,bbWidth) :
    nPts = int(finalShape.length)
    if ( nPts > 5000) :
        nPts = 5000
    fitContour = np.zeros((nPts,1,2), dtype=np.int32)

    if ( nPts > 3):

        for t in range(0,nPts) :
            pt = finalShape.interpolate(t)
            fitContour[t,0,0] = pt.x
            fitContour[t,0,1] = pt.y
            
        fitContour = [ fitContour ]
        fitContour = [ cv2.approxPolyDP(cnt,2,True) for cnt in fitContour]
                        
        image = np.copy(imageNoMasks)
        cv2.drawContours(image, fitContour,-1, (0,255,0), 2)
        if ( showFigures ):
            fig.add_subplot(2,2,3)
            plt.title(featureName + " " + str(r['scores'][i]) + " Fit")
            plt.imshow(image[bbTop:bbTop+bbHeight,bbLeft:bbLeft+bbWidth])

        while ( os.path.exists( "anomaly/add/{0:06d}.osm".format(wayNumber) )) :
            wayNumber += 1

        debugFileName = os.path.join( inference_config.ROOT_DIR, "anomaly","add","{0:06d}.jpg".format(wayNumber))
        io.imsave(debugFileName,image[bbTop:bbTop+bbHeight,bbLeft:bbLeft+bbWidth],quality=100)

        osmFileName = os.path.join( inference_config.ROOT_DIR, "anomaly","add","{0:06d}.osm".format(wayNumber))
        writeOSM( osmFileName,featureName, fitContour[0],tilePixel, qkRoot)

    if (showFigures ):
        plt.show(block=False)
        plt.pause(0.05)

    return wayNumber
    


ROOT_DIR_ = os.path.dirname(os.path.realpath(sys.argv[0]))
MODEL_DIR = os.path.join(ROOT_DIR_, "logs")

class InferenceConfig(osmmodelconfig.OsmModelConfig):
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1
    ROOT_DIR = ROOT_DIR_

inference_config = InferenceConfig()

fullTrainingDir = os.path.join( ROOT_DIR_, osmcfg.trainDir,"*")
fullImageList = []
for imageDir in glob.glob(fullTrainingDir): 
    if ( os.path.isdir( os.path.join( fullTrainingDir, imageDir) )):
        id = os.path.split(imageDir)[1]
        fullImageList.append( id)

# Training dataset
dataset_full =  osmmodelconfig.OsmImagesDataset(ROOT_DIR_)
dataset_full.load(fullImageList, inference_config.IMAGE_SHAPE[0], inference_config.IMAGE_SHAPE[1])
dataset_full.prepare()

inference_config.display()

# Recreate the model in inference mode
model = modellib.MaskRCNN(mode="inference", 
                          config=inference_config,
                          model_dir=MODEL_DIR)

# Get path to saved weights
# Either set a specific path or find last trained weights
# model_path = os.path.join(ROOT_DIR, ".h5 file name here")
model_path = model.find_last()[1]
print(model_path)

# Load trained weights (fill in path to trained weights here)
assert model_path != "", "Provide path to trained weights"
print("Loading weights from ", model_path)
model.load_weights(model_path, by_name=True)


print("Reading in OSM data")
# load up the OSM features into hash of arrays of polygons, in pixels
features = {}

for classDir in os.listdir(osmcfg.rootOsmDir) :
    classDirFull = os.path.join( osmcfg.rootOsmDir,classDir)
    for fileName in os.listdir(classDirFull) :
        fullPath = os.path.join( osmcfg.rootOsmDir,classDir,fileName)
        with open(fullPath, "rt") as csvfile:
            csveader = csv.reader(csvfile, delimiter='\t')

            pts = []
            for row in csveader:
                latLot = (float(row[0]),float(row[1]))
                pixel = quadkey.TileSystem.geo_to_pixel(latLot,osmcfg.tileZoom)

                pts.append(pixel)

            feature = {
                "geometry" : geometry.Polygon(pts),
                "filename" : fullPath
            }


            if ( (classDir in features) == False) :
                features[classDir] = []

            features[classDir].append( feature )


# make the output dirs, a fresh start is possible just by deleting anomaly
if ( not os.path.isdir("anomaly")) :
    os.mkdir("anomaly")
if ( not os.path.isdir("anomaly/add")) :
    os.mkdir("anomaly/add")
if ( not os.path.isdir("anomaly/replace")) :
    os.mkdir("anomaly/replace")
if ( not os.path.isdir("anomaly/overlap")) :
    os.mkdir("anomaly/overlap")

fig = {}
if ( showFigures):
    fig = plt.figure()

wayNumber = 0

startTime = time.time()

count = 1
for image_index in dataset_full.image_ids :
    currentTime = time.time()
    howLong = currentTime-startTime
    secPerImage = howLong/count
    imagesLeft = len(dataset_full.image_ids)-count
    timeLeftHrs = (imagesLeft*secPerImage)/3600.0

    print("Processing {} of {} {:2.1f} hrs left".format(count,len(dataset_full.image_ids),timeLeftHrs))
    count += 1

    image, image_meta, gt_class_id, gt_bbox, gt_mask = modellib.load_image_gt(dataset_full, inference_config,image_index, use_mini_mask=False)
    info = dataset_full.image_info[image_index]

    # get the pixel location for this training image.
    metaFileName = os.path.join( inference_config.ROOT_DIR, osmcfg.trainDir,info['id'],info['id']+".txt")

    quadKeyStr = ""
    with open(metaFileName) as metafile:  
        quadKeyStr = metafile.readline()

    quadKeyStr = quadKeyStr.strip()
    qkRoot = quadkey.from_str(quadKeyStr)
    tilePixel = quadkey.TileSystem.geo_to_pixel(qkRoot.to_geo(), qkRoot.level)

    # run the network
    results = model.detect([image], verbose=0)
    r = results[0]

    maxImageSize = 256*3
    featureMask = np.zeros((maxImageSize, maxImageSize), dtype=np.uint8)

    pts = []
    pts.append( ( tilePixel[0]+0,tilePixel[1]+0 ) )
    pts.append( ( tilePixel[0]+0,tilePixel[1]+maxImageSize ) )
    pts.append( ( tilePixel[0]+maxImageSize,tilePixel[1]+maxImageSize ) )
    pts.append( ( tilePixel[0]+maxImageSize,tilePixel[1]+0 ) )
    
    imageBoundingBoxPoly = geometry.Polygon(pts)

    foundFeatures = {}

    for featureType in osmmodelconfig.featureNames.keys() :
        foundFeatures[featureType ] = []

        for feature in features[featureType] :            
            if ( imageBoundingBoxPoly.intersects( feature['geometry']) ) :

                xs, ys = feature['geometry'].exterior.coords.xy

                outOfRangeCount = len([ x for x in xs if x < tilePixel[0] or x >= tilePixel[0]+maxImageSize ])
                outOfRangeCount += len([ y for y in ys if y < tilePixel[1] or y >= tilePixel[1]+maxImageSize ])

                if ( outOfRangeCount == 0) :
                    foundFeatures[featureType ].append( feature)

    # draw black lines showing where osm data is
    for featureType in osmmodelconfig.featureNames.keys() :
        for feature in foundFeatures[featureType] :
            xs, ys = feature['geometry'].exterior.coords.xy

            xs = [ x-tilePixel[0] for x in xs]
            ys = [ y-tilePixel[1] for y in ys]

            rr, cc = draw.polygon_perimeter(xs,ys,(maxImageSize,maxImageSize))
            image[cc,rr] = 0

    imageNoMasks = np.copy(image)

    for i in range( len(r['class_ids']))  :
        mask = r['masks'][:,:,i]
        edgePixels = 15
        outside = np.sum( mask[0:edgePixels,:]) + np.sum( mask[-edgePixels:-1,:]) + np.sum( mask[:,0:edgePixels]) + np.sum( mask[:,-edgePixels:-1])

        image = np.copy(imageNoMasks)

        if ( r['scores'][i] > 0.98 and outside == 0 ) :
            featureFound = False
            for featureType in osmmodelconfig.featureNames.keys() :
                for feature in foundFeatures[featureType] :
                    classId = osmmodelconfig.featureNames[featureType]
                
                    if ( classId == r['class_ids'][i]  ) :

                        xs, ys = feature['geometry'].exterior.coords.xy

                        xs = [ x-tilePixel[0] for x in xs]
                        ys = [ y-tilePixel[1] for y in ys]
        
                        xsClipped = [ min( max( x,0),maxImageSize) for x in xs]
                        ysClipped = [ min( max( y,0),maxImageSize) for y in ys]

                        featureMask.fill(0)
                        rr, cc = draw.polygon(xs,ys,(maxImageSize,maxImageSize))
                        featureMask[cc,rr] = 1

                        maskAnd = featureMask * mask
                        overlap = np.sum(maskAnd )

                        if ( outside == 0 and overlap > 0) :
                            featureFound = True

            if ( featureFound == False) :
                weight = 0.25

                # get feature name
                featureName = ""
                for featureType in osmmodelconfig.featureNames.keys() :
                    if ( osmmodelconfig.featureNames[featureType] == r['class_ids'][i]  ) :
                        featureName = featureType

                #if ( r['class_ids'][i] == 1):
                #    vis.apply_mask(image,mask,[weight,0,0])
                #if (  r['class_ids'][i] == 2):
                #    vis.apply_mask(image,mask,[weight,weight,0])
                #if (  r['class_ids'][i] == 3):
                #    vis.apply_mask(image,mask,[0.0,0,weight])

                mask = mask.astype(np.uint8)
                mask = mask * 255
 
                ret,thresh = cv2.threshold(mask,127,255,0)
                im2, rawContours,h = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

                bbLeft,bbTop,bbWidth,bbHeight = cv2.boundingRect(rawContours[0])                
                
                bbBuffer = 75

                bbLeft = max(bbLeft-bbBuffer,0)
                bbRight = min(bbLeft+2*bbBuffer+bbWidth,maxImageSize)
                bbWidth = bbRight-bbLeft

                bbTop = max(bbTop-bbBuffer,0)
                bbBottom = min(bbTop+2*bbBuffer+bbHeight,maxImageSize-1)
                bbHeight = bbBottom-bbTop

                image = np.copy(imageNoMasks)
                cv2.drawContours(image, rawContours,-1, (0,255,0), 2)

                if ( showFigures ):
                    fig.add_subplot(2,2,1)
                    plt.title(featureName + " " + str(r['scores'][i]) + " Raw")
                    plt.imshow(image[bbTop:bbTop+bbHeight,bbLeft:bbLeft+bbWidth])
                
                simpleContour = [ cv2.approxPolyDP(cnt,5,True) for cnt in rawContours]
                image = np.copy(imageNoMasks)
                cv2.drawContours(image, simpleContour,-1, (0,255,0), 2)
                if ( showFigures ):
                    fig.add_subplot(2,2,2)
                    plt.title(featureName + " " + str(r['scores'][i]) + " Simplify")
                    plt.imshow(image[bbTop:bbTop+bbHeight,bbLeft:bbLeft+bbWidth])

                simpleContour = simpleContour[0]
                
                print("  {}".format(featureName))
                if ( featureName == "baseball" and isinstance(simpleContour,np.ndarray) ):
                    
                    while ( os.path.exists( "anomaly/add/{0:06d}.osm".format(wayNumber) )) :
                        wayNumber += 1

                    debugFileName = os.path.join( inference_config.ROOT_DIR, "anomaly","add","{0:06d}.jpg".format(wayNumber))
                    io.imsave(debugFileName,image[bbTop:bbTop+bbHeight,bbLeft:bbLeft+bbWidth],quality=100)

                    osmFileName = os.path.join( inference_config.ROOT_DIR, "anomaly","add","{0:06d}.osm".format(wayNumber))
                    writeOSM( osmFileName,featureName, simpleContour,tilePixel, qkRoot)

                fitContour = simpleContour

                if ( featureName == 'baseball' ) :

                    def makePie(paramsX):
                        centerX,centerY,width,angle = paramsX

                        pts = []

                        pts.append((0,0))
                        pts.append((width,0))

                        step =  math.pi/10
                        r = step
                        while r < math.pi/2:
                            x = math.cos(r)*width
                            y = math.sin(r)*width
                            pts.append( (x,y) )
                            r += step

                        pts.append( (0,width))
                        pts.append( (0,0))

                        fitShape = geometry.LineString(pts)

                        fitShape = affinity.translate(fitShape, -width/2,-width/2 )
                        fitShape = affinity.rotate(fitShape,angle )
                        fitShape = affinity.translate(fitShape, centerX,centerY )

                        return fitShape

                    def fitPie(paramsX):
                        fitShape = makePie(paramsX)

                        huberCutoff = 5

                        sum = 0
                        for cnt in rawContours:
                            for pt in cnt:
                                p = geometry.Point(pt[0])
                                d = p.distance(fitShape)

                                if ( d < huberCutoff) :
                                    sum += 0.5 * d * d
                                else:
                                    sum += huberCutoff*(math.fabs(d)-0.5*huberCutoff)

                        return sum
                    
                    cm = np.mean( rawContours[0],axis=0)

                    results = []
                    angleStepCount = 8
                    for angleI in range(angleStepCount):
                        
                        centerX = cm[0,0]
                        centerY = cm[0,1]
                        width = math.sqrt(cv2.contourArea(rawContours[0]))
                        angle = 360 * float(angleI)/angleStepCount
                        x0 = np.array([centerX,centerY,width,angle ])
                                                
                        resultR = scipy.optimize.minimize(fitPie, x0, method='nelder-mead', options={'xtol': 1e-6,'maxiter':50 })

                        results.append(resultR)

                    bestScore = 1e100
                    bestResult = {}
                    for result in results:
                        if result.fun < bestScore :
                            bestScore  = result.fun
                            bestResult = result

                    bestResult = scipy.optimize.minimize(fitPie, bestResult.x, method='nelder-mead', options={'xtol': 1e-6 })
                    finalShape = makePie(bestResult.x)
                    wayNumber = writeShape(wayNumber, finalShape, image, bbTop,bbHeight,bbLeft,bbWidth) 

                    for result in results:
                        angle = result.x[3]
                        angleDelta = int(math.fabs(result.x[3]-bestResult.x[3])) % 360
                        if result.fun < 1.2*bestScore and angleDelta > 45  :
                            result = scipy.optimize.minimize(fitPie, result.x, method='nelder-mead', options={'xtol': 1e-6 })
                            finalShape = makePie(result.x)
                            wayNumber = writeShape(wayNumber, finalShape, image, bbTop,bbHeight,bbLeft,bbWidth) 

                else:

                    def makeRect(paramsX):
                        centerX,centerY,width,height,angle = paramsX

                        pts = [ 
                            (-width/2,height/2),
                            (width/2,height/2),
                            (width/2,-height/2),
                            (-width/2,-height/2),
                            (-width/2,height/2)]

                        fitShape = geometry.LineString(pts)

                        fitShape = affinity.rotate(fitShape, angle,use_radians=True )
                        fitShape = affinity.translate(fitShape, centerX,centerY )

                        return fitShape

                    def fitRect(paramsX):
                        fitShape = makeRect(paramsX)

                        sum = 0

                        for cnt in rawContours:
                            for pt in cnt:
                                p = geometry.Point(pt[0])
                                d = p.distance(fitShape)
                                sum += d*d
                        return sum

                    cm = np.mean( rawContours[0],axis=0)

                    result = {}
                    angleStepCount = 8
                    for angleI in range(angleStepCount):

                        centerX = cm[0,0]
                        centerY = cm[0,1]
                        width = math.sqrt(cv2.contourArea(rawContours[0]))
                        height = width
                        angle = 2*math.pi * float(angleI)/angleStepCount
                        x0 = np.array([centerX,centerY,width,height,angle ])
                        resultR = scipy.optimize.minimize(fitRect, x0, method='nelder-mead', options={'xtol': 1e-6,'maxiter':50 })

                        if ( angleI == 0):                            
                            result = resultR

                        if ( resultR.fun < result.fun):
                            result = resultR
                        #print("{} {}".format(angle * 180.0 / math.pi,resultR.fun ))

                    resultR = scipy.optimize.minimize(fitRect, resultR.x, method='nelder-mead', options={'xtol': 1e-6 })

                    #print(result)
                    finalShape = makeRect(result.x)
                
                    wayNumber = writeShape(wayNumber, finalShape, image, bbTop,bbHeight,bbLeft,bbWidth) 



                
                


    

 
    
