import sys
import overpy
import imagestoosm.config as cfg
import os
import shapely.geometry
import shapely.wkt
import shapely.ops
import geojson

api = overpy.Overpass()

summary = {}

def saveOsmData(query) :

    result = api.query(query)

    for way in result.ways:

        # "leisure=pitch,sport=" , don't use "-" char" in featureDirectoryName
        featureDirectoryName = way.tags.get("sport")

        outputDirectoryName = os.path.join(cfg.rootOsmDir,featureDirectoryName)
        if ( os.path.exists(outputDirectoryName) == False):
            os.makedirs(outputDirectoryName)

        if ( (featureDirectoryName in summary) == False) :
            summary[featureDirectoryName]  = 1
        else:     
            summary[featureDirectoryName] += 1
        
        filenameBase= os.path.join(cfg.rootOsmDir,featureDirectoryName,str(way.id))

        #print("Name: %d %s %s" % ( way.id ,way.tags.get("name", ""),filenameBase))

        # leave the csv file for now, will delete when the script for the next
        # stage is rewritten.
        with open("%s.csv" % (filenameBase), "wt") as text_file:
            for node in way.nodes:
                text_file.write("%0.7f\t%0.7f\n" % (node.lat, node.lon))

        with open("%s.GeoJSON" % (filenameBase), "wt") as text_file:

            rawNodes = []
            for node in way.nodes:
                rawNodes.append( (node.lon, node.lat) )
            
            try:
                geom = shapely.geometry.Polygon(rawNodes)

                tags = way.tags
                tags['wayOSMId'] = way.id

                features =[]            
                features.append( geojson.Feature(geometry=geom, properties=tags))

                featureC = geojson.FeatureCollection(features)

                text_file.write(geojson.dumps(featureC))
            except Exception as e:
                print(e)
                    

queryFull = """[timeout:125];
    ( 
        area[admin_level=4][boundary=administrative][name="Massachusetts"];         
        area[admin_level=4][boundary=administrative][name="New York"];         
        area[admin_level=4][boundary=administrative][name="Connecticut"];         
        area[admin_level=4][boundary=administrative][name="Rhode Island"]; 
        area[admin_level=4][boundary=administrative][name="Pennsylvania"];                               
    )->.searchArea;
    (
    way["sport"="baseball"]["leisure"="pitch"](area.searchArea);
    way["sport"="tennis"]["leisure"="pitch"](area.searchArea);
    way["sport"="soccer"]["leisure"="pitch"](area.searchArea);
    way["sport"="american_football"]["leisure"="pitch"](area.searchArea);    
    way["sport"="basketball"]["leisure"="pitch"](area.searchArea);    
    );
    (._;>;);
    out body;
    """

# fetch all ways and nodes
queryMA = """[timeout:125];
    ( 
        area[admin_level=4][boundary=administrative][name="Massachusetts"];         
    )->.searchArea;
    (
    way["sport"="baseball"]["leisure"="pitch"](area.searchArea);
    way["sport"="tennis"]["leisure"="pitch"](area.searchArea);
    way["sport"="soccer"]["leisure"="pitch"](area.searchArea);
    way["sport"="american_football"]["leisure"="pitch"](area.searchArea);    
    way["sport"="basketball"]["leisure"="pitch"](area.searchArea);    
    );
    (._;>;);
    out body;
    """
saveOsmData(queryFull)
    
# Other possible data to query
#  - bridges
#  - solar panels farms
#  - wind turbines 
#  - railroad crossings. 
#  - active rail roads 
#  - water tanks
#  - wafer/lakes/rivers
#  - parking lots
#  - driveways 
#  - gas stations 
#  - building (Microsoft has already done this)
#  - Running track

print(summary)
