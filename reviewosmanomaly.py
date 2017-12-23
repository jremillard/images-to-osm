import os
import sys
import glob
import imagestoosm.config as osmcfg
import xml.etree.ElementTree as ET
import QuadKey.quadkey as quadkey
import shapely.geometry as geometry
import matplotlib.pyplot as plt
import skimage.io
import shutil

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


addDirectory = os.path.join( "anomaly","add","*.osm")
anomalyStatusFile = os.path.join( "anomaly","status.csv")

# read in OSM files, convert to pixels z18, make them shapely polygons

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
if ( os.path.exists(anomalyStatusFile)):
    with open(anomalyStatusFile,"rt",encoding="ascii") as f: 
        for line in f:
            (status,osmFileName) =  line.split(',')
            osmFileName = osmFileName.strip()
            newWays[osmFileName]['status'] = status

fig = plt.figure()

for wayKey in sorted(newWays):
    # if reviewed skip
    way = newWays[wayKey]

    if ( len(way['status']) == 0 ) :

        # for each way, check for overlap, same tags, add to review cluster, handle more ways than maxSubPlots
        subPlotCols = 2
        subPlotRows = 2
        maxSubPlots = subPlotCols*subPlotRows

        reviewSet = [way]
        for otherKey in sorted(newWays):
            other = newWays[otherKey]
            if ( other != way and len(other['status']) == 0 and way['tags'] == other['tags'] and other['geometry'].intersects( way['geometry'])):
                reviewSet.append(other)

        for wayIndex in range(len(reviewSet)):
            other = reviewSet[wayIndex]
            other['status'] = 'rejected'

        acceptedWay = {}
        viewSet = []
        for wayIndex in range(len(reviewSet)):
            viewSet.append(reviewSet[wayIndex])

            if ( len(viewSet) == maxSubPlots or wayIndex+1 >= len(reviewSet)):

                for plotIndex in range(maxSubPlots):
                    sb = fig.add_subplot(subPlotRows,subPlotCols,plotIndex+1)
                    sb.cla()

                for wayIndex in range(len(viewSet)):
                    fig.add_subplot(subPlotRows,subPlotCols,wayIndex+1)
                    plt.title("{} {}".format(wayIndex+1,viewSet[wayIndex]['osmFile']))
                    image = skimage.io.imread( viewSet[wayIndex]['imageName'])
                    plt.imshow(image)

                plt.show(block=False)
                plt.pause(0.05)

                goodInput = False
                while goodInput  == False:
                    print("{} - q to quit, 0 to reject all, to except use sub plot index".format(way['osmFile']))
                    c = getch()

                    try:
                        index = int(c)
                        if ( index > 0):
                            acceptedWay = viewSet[index-1 ]
                            viewSet = [acceptedWay]
                            print("selected {} {}".format(acceptedWay['osmFile'],index))
                            goodInput = True
                        if ( index == 0):
                            viewSet = [reviewSet[0]]
                            acceptedWay = {}
                            print("reject all")
                            goodInput = True
                                                    
                    except:
                        if ( c == "q"):
                            sys.exit(0)
                        print("what??")

        if ( bool(acceptedWay) ) :
            acceptedWay['status'] = 'accepted'
            print("accepted {}".format(acceptedWay['osmFile']))
        
        if ( os.path.exists(anomalyStatusFile+".1")):
            shutil.copy(anomalyStatusFile+".1",anomalyStatusFile+".2" )
        if ( os.path.exists(anomalyStatusFile)):
            shutil.copy(anomalyStatusFile,anomalyStatusFile+".1" )

        with open(anomalyStatusFile,"wt",encoding="ascii") as f: 
            for otherKey in sorted(newWays):
                other = newWays[otherKey]
                if ( len(other['status']) > 0 ):
                    f.write("{},{}\n".format(other['status'],other['osmFile']))

