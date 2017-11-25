import sys
sys.path.append("Mask_RCNN")

import os
import random
import math
import re
import time
import numpy as np
import cv2
import matplotlib
import random
import glob
import skimage

from config import Config
import imagestoosm.config as osmcfg
import utils
import model as modellib
import visualize
from model import log

featureNames = {
#    "baseball":1,
#    "american_football":2,
    "basketball":1,
#    "soccer":4,
    "tennis":2
}

class OsmModelConfig(Config):
    """Configuration for training on the toy shapes dataset.
    Derives from the base Config class and overrides values specific
    to the toy shapes dataset.
    """
    # Give the configuration a recognizable name
    NAME = "OSM Images BB TN"

    # Batch size is (GPUs * images/GPU).
    GPU_COUNT = 1
    IMAGES_PER_GPU = 2
    LEARNING_RATE = 2e-4

    # 2 minutes
    #STEPS_PER_EPOCH = 100 // IMAGES_PER_GPU

    # 1 hour epoch
    STEPS_PER_EPOCH = 12000 // IMAGES_PER_GPU

    # Number of classes (including background)
    NUM_CLASSES = 1 + len(featureNames)  # background + featureType's

    # Each tile is 256 pixels across, training data is 3x3 tiles
    TILES=3
    IMAGE_MIN_DIM = 256*TILES
    IMAGE_MAX_DIM = 256*TILES

    # Reduce training ROIs per image because the images are small and have
    # few objects. Aim to allow ROI sampling to pick 33% positive ROIs.
    #TRAIN_ROIS_PER_IMAGE = 64
    #DETECTION_MAX_INSTANCES = 64

    VALIDATION_STEPS = 100

class OsmImagesDataset(utils.Dataset):

    def __init__(self, rootDir):
        utils.Dataset.__init__(self)
        self.ROOT_DIR = rootDir

    def load(self, imageDirs, height, width):
        """Generate the requested number of synthetic images.
        count: number of images to generate.
        height, width: the size of the generated images.
        """

        for feature in featureNames:
            self.add_class("osm", featureNames[feature],feature)

            # Add images
        for i in range(len(imageDirs)):
            imgPath = os.path.join( self.ROOT_DIR, osmcfg.trainDir,imageDirs[i],imageDirs[i] + ".jpg")
            self.add_image("osm", image_id=imageDirs[i], path=imgPath, width=width, height=height)

    def load_mask(self, image_id):
        """Generate instance masks for shapes of the given image ID.
        """
        info = self.image_info[image_id]

        imgDir = os.path.join( self.ROOT_DIR, osmcfg.trainDir,"%05d" % (image_id))
        wildcard = os.path.join( imgDir,"*.png")

        # 00015-american_football-0.png  00015-baseball-0.png  00015-baseball-1.png  00015-baseball-2.png  00015-baseball-3.png  00015-basketball-0.png  00015-basketball-1.png  00015.jpg  00015.txt

        maskCount = 0
        for filePath in glob.glob(wildcard): 
            filename = os.path.split(filePath)[1] 
            parts = filename.split( "-")
            if ( len(parts) == 3) and parts[1] in featureNames: 
                maskCount += 1

        mask = np.zeros([info['height'], info['width'], maskCount], dtype=np.uint8)
        class_ids = np.zeros((maskCount), np.int32)
 
        count = 0
        for filePath in glob.glob(wildcard): 
            filename = os.path.split(filePath)[1] 
            parts = filename.split( "-")
            if ( len(parts) == 3) and parts[1] in featureNames: 
                imgPath = filePath
                mask[:, :, count] = skimage.io.imread(filePath)
                class_ids[count] = featureNames[parts[1]]
                count += 1            
                
        return mask, class_ids
