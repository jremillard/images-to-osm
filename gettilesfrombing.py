# for each feature in osm/baseball directory, get each point and make sure we have the 
# tile for that point in the tile cache. 

import requests
import os
import os.path
import csv
import QuadKey.quadkey as quadkey
import shutil
import imagestoosm.config as cfg
import imagestoosm.secrets as secrets
from random import random
from time import sleep

# MS doesn't want you hardcoding the URLs to the tile server. This request asks for the Aerial
# url template. Replace {quadkey}, and {subdomain}
response = requests.get("https://dev.virtualearth.net/REST/V1/Imagery/Metadata/Aerial?key=%s" % (secrets.bingKey))

data = response.json()

# grabs the data we need from the response.
tileUrlTemplate = data['resourceSets'][0]['resources'][0]['imageUrl']
imageDomains = data['resourceSets'][0]['resources'][0]['imageUrlSubdomains']

if ( os.path.exists(cfg.rootTileDir) == False) :
    os.mkdir(cfg.rootTileDir)

bingTilesDir = os.path.join( cfg.rootTileDir,"bing_z" + str( cfg.tileZoom))

if ( os.path.exists(bingTilesDir) == False) :
    os.mkdir(bingTilesDir)

for classDir in os.listdir(cfg.rootOsmDir) :
    classDirFull = os.path.join( cfg.rootOsmDir,classDir)
    for fileName in os.listdir(classDirFull) :
        fullPath = os.path.join( cfg.rootOsmDir,classDir,fileName)
        with open(fullPath, "rt") as csvfile:
            csveader = csv.reader(csvfile, delimiter='\t')
            print("%s " % (fullPath),end='')

            neededTile = False
            for row in csveader:

                tilePixel = quadkey.TileSystem.geo_to_pixel((float(row[0]),float(row[1])), cfg.tileZoom)

                for x in range(-2,3) :
                    for y in range(-2,3) :
                        pixel = ( tilePixel[0] + 256*x, tilePixel[1]+256*y)
                        geo = quadkey.TileSystem.pixel_to_geo(pixel, cfg.tileZoom)
                        qk = quadkey.from_geo(geo,cfg.tileZoom)

                        qkStr = str(qk)

                        tileCacheDir = os.path.join(bingTilesDir,qkStr[-3:])
                    
                        if ( os.path.exists(tileCacheDir) == False) :
                            os.mkdir( tileCacheDir)

                        tileFileName = "%s/%s.jpg" % (tileCacheDir, qkStr)

                        if ( os.path.exists(tileFileName) ) :                            
                            # already downloaded
                            ok = 1; 
                        else :
                            print("T",end='')
                            url = tileUrlTemplate.replace("{subdomain}",imageDomains[0])
                            url = url.replace("{quadkey}",qkStr)
                            url = "%s&key=%s" % (url,secrets.bingKey)

                            response = requests.get(url,stream=True)
                            
                            with open(tileFileName,'wb') as out_file:
                                shutil.copyfileobj(response.raw, out_file)

                            del response
                            neededTile = True
                    
            print("")
            
            if ( neededTile ):
                sleep(random()*3)


