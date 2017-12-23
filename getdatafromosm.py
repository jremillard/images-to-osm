import sys
import overpy
import imagestoosm.config as cfg
import os

api = overpy.Overpass()

summary = {}

def saveOsmData(query) :

    result = api.query(query)

    for way in result.ways:

        # "leisure=pitch,sport=" , don't use "-" char" in featureDirectoryName
        featureDirectoryName = way.tags.get("sport")

        csvDirectoryName = os.path.join(cfg.rootOsmDir,featureDirectoryName)
        if ( os.path.exists(csvDirectoryName) == False):
            os.mkdir( csvDirectoryName)

        if ( (featureDirectoryName in summary) == False) :
            summary[featureDirectoryName]  = 1
        else:     
            summary[featureDirectoryName] += 1
        
        csvFilename = os.path.join(cfg.rootOsmDir,featureDirectoryName,str(way.id))

        print("Name: %d %s %s" % ( way.id ,way.tags.get("name", ""),csvFilename))

        with open("%s.csv" % (csvFilename), "wt") as text_file:
            for node in way.nodes:
                text_file.write("%0.7f\t%0.7f\n" % (node.lat, node.lon))
    

# fetch all ways and nodes
queryMA = """[timeout:125];
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
saveOsmData(queryMA)
    
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