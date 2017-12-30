import os
import sys
import imagestoosm.config as osmcfg
import xml.etree.ElementTree as ET
import shapely.geometry as geometry

def makeOsmFileName( fileNumber):

    return os.path.join( "anomaly","reviewed_{:02d}.osm".format(fileNumber))

# clean out the old OSM files.
fileCount = 1
while (os.path.exists(makeOsmFileName(fileCount))):
    os.remove( makeOsmFileName(fileCount))
    fileCount += 1
fileCount = 1

# besides sticking the single accepted OSM files together, this script 
# also need to fix up the negative/placeholder ids to be unique in the 
# file.
startId = 0

anomalyStatusFile = os.path.join( "anomaly","status.csv")

osmTreeRoot = ET.Element('osm')
osmTreeRoot.attrib['version'] = "0.6"

if ( os.path.exists(anomalyStatusFile)):
    with open(anomalyStatusFile,"rt",encoding="ascii") as f: 
        for line in f:
            (status,osmFileName) =  line.split(',')                
            osmFileName = osmFileName.strip()

            if ( status == "accepted") :
                tree = ET.parse(osmFileName)
                root = tree.getroot()

                wayCount = 0
                for node in root.iter('node'):
                    node.attrib['id'] = "{0:d}".format(int(node.attrib['id'])-startId)
                    wayCount += 1
                    osmTreeRoot.append(node)
                
                for node in root.findall('./way/nd'):
                    node.attrib['ref'] = "{0:d}".format(int(node.attrib['ref'])-startId)

                for node in root.iter('way'):
                    node.attrib['id'] = "{0:d}".format(int(node.attrib['id'])-startId)
                    wayCount += 1
                    osmTreeRoot.append(node)

                startId += wayCount

                # only only allows 10,000 elements in a single change set upload, make different osm file
                # so they can be uploaded without blowing up.
                if ( startId > 9500) :
                    tree = ET.ElementTree(osmTreeRoot)
                    tree.write( makeOsmFileName(fileCount))
                    fileCount += 1

                    osmTreeRoot = ET.Element('osm')
                    osmTreeRoot.attrib['version'] = "0.6"
                    startId = 0

tree = ET.ElementTree(osmTreeRoot)
tree.write( makeOsmFileName(fileCount))


