import os
import sys
import glob
import imagestoosm.config as osmcfg
import xml.etree.ElementTree as ET
import QuadKey.quadkey as quadkey
import shapely.geometry as geometry
import matplotlib.pyplot as plt
import skimage.io

def _find_getch():
    try:
        import termios
    except ImportError:
        # Non-POSIX. Return msvcrt's (Windows') getch.
        import msvcrt
        return msvcrt.getch

    # POSIX system. Create and return a getch that manipulates the tty.
    import sys, tty
    def _getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    return _getch

getch = _find_getch()


# read in OSM files, convert to pixels z18, make them shapely polygons

addDirectory = os.path.join( "anomaly","add","*.osm")

newWays = {}
for osmFileName in glob.glob(addDirectory): 

    (path,filename) = os.path.split(osmFileName);
    wayNumber = os.path.splitext(filename)[0]

    newEntry = { 
        "imageName" : os.path.join( path,str(wayNumber) + ".jpg") ,
        "osmFile" : osmFileName,
        "tags" : {},
        "status" : ""
    }

    tree = ET.parse(osmFileName)
    root = tree.getroot()

    for tag in root.findall('./way/tag'):
        key = tag.attrib["k"]
        val = tag.attrib["v"]
        
        newEntry['tags'][key] = val

    pts =[]
    for node in root.iter('node'):
        pt = ( float(node.attrib['lat']),float(node.attrib['lon']))
        pixel = quadkey.TileSystem.geo_to_pixel(pt,osmcfg.tileZoom)
        pts.append(pixel)

    if ( len(pts ) > 2 ):
        newEntry["geometry"] = geometry.Polygon(pts)
        #print(newEntry )
        newWays[osmFileName] = newEntry

# read in review file, file status (accepted or rejected), path to osm 

# for each add way that 

fig = plt.figure()


for wayKey in sorted(newWays):
    # if reviewed skip
    way = newWays[wayKey]

    if ( len(way['status']) == 0 ) :

        # for each way, check for overlap, same tags, add to review cluster 
        subPlotCols = 2
        subPlotRows = 1
        maxSubPlots = subPlotCols*subPlotRows

        reviewSet = [way]
        for otherKey in sorted(newWays):
            other = newWays[otherKey]
            if ( other != way and len(other['status']) == 0 and way['tags'] == other['tags'] and other['geometry'].intersects( way['geometry'])):
                reviewSet.append(other)

        viewSet = []
        for wayIndex in range(len(reviewSet)):
            viewSet.append(reviewSet[wayIndex])

            if ( len(viewSet) == maxSubPlots or wayIndex+1 >= len(reviewSet)):

                for plotIndex in range(maxSubPlots):
                    sb = fig.add_subplot(subPlotRows,subPlotCols,plotIndex+1)
                    sb.cla()

                for wayIndex in range(len(viewSet)):
                    fig.add_subplot(subPlotRows,subPlotCols,wayIndex+1)
                    plt.title(viewSet[wayIndex]['osmFile'])
                    image = skimage.io.imread( viewSet[wayIndex]['imageName'])
                    plt.imshow(image)
                    viewSet[wayIndex]['status'] = 'rejected'

                plt.show(block=False)
                plt.pause(0.05)

                getch()

                viewSet = [ reviewSet[0] ]
        

  # read in diagnostic images from review cluster
  # display up to 9 images 
  # get choice (r reject call, 1-9 to accept, ask again if other, q quit)
  #  if > 9 images and an image was selected bring it forward, keep looping
  # update review file, reject and accept flags for each way in review cluster





