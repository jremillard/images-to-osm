
# coding: utf-8

# # Mask R-CNN - Train on Shapes Dataset
# 
# 
# This notebook shows how to train Mask R-CNN on your own dataset. To keep things simple we use a synthetic dataset of shapes (squares, triangles, and circles) which enables fast training. You'd still need a GPU, though, because the network backbone is a Resnet101, which would be too slow to train on a CPU. On a GPU, you can start to get okay-ish results in a few minutes, and good results in less than an hour.
# 
# The code of the *Shapes* dataset is included below. It generates images on the fly, so it doesn't require downloading any data. And it can generate images of any size, so we pick a small image size to train faster. 

# In[1]:

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
import matplotlib.pyplot as plt

from config import Config
import imagestoosm.config as osmcfg
import utils
import model as modellib
import visualize
from model import log

# Root directory of the project
#ROOT_DIR = os.getcwd()
ROOT_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))

# Directory to save logs and trained model
MODEL_DIR = os.path.join(ROOT_DIR, "logs")

# Path to COCO trained weights
COCO_MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco.h5")

featureNames = {
    "baseball":1,
    "american_football":2,
    "basketball":3,
    "soccer":4,
    "tennis":5
}

# ## Configurations

class OsmImagesConfig(Config):
    """Configuration for training on the toy shapes dataset.
    Derives from the base Config class and overrides values specific
    to the toy shapes dataset.
    """
    # Give the configuration a recognizable name
    NAME = "OSM Images"

    # Batch size is (GPUs * images/GPU).
    GPU_COUNT = 1
    IMAGES_PER_GPU = 2

    STEPS_PER_EPOCH = 1000 // IMAGES_PER_GPU

    # Number of classes (including background)
    NUM_CLASSES = 1 + len(featureNames)  # background + featureType's

    # Each tile is 256 pixels across, training data is 3x3 tiles
    TILES=3
    IMAGE_MIN_DIM = 256*TILES
    IMAGE_MAX_DIM = 256*TILES

    # Reduce training ROIs per image because the images are small and have
    # few objects. Aim to allow ROI sampling to pick 33% positive ROIs.
    TRAIN_ROIS_PER_IMAGE = 64
    DETECTION_MAX_INSTANCES = 64

    
config = OsmImagesConfig()
config.display()

# ## Dataset
# * load_mask()

class OsmImagesDataset(utils.Dataset):

    def load(self, imageDirs, height, width):
        """Generate the requested number of synthetic images.
        count: number of images to generate.
        height, width: the size of the generated images.
        """

        for feature in featureNames:
            self.add_class("osm", featureNames[feature],feature)

            # Add images
        for i in range(len(imageDirs)):
            imgPath = os.path.join( ROOT_DIR, osmcfg.trainDir,imageDirs[i],imageDirs[i] + ".jpg")
            self.add_image("osm", image_id=imageDirs[i], path=imgPath, width=width, height=height)

    def load_mask(self, image_id):
        """Generate instance masks for shapes of the given image ID.
        """
        info = self.image_info[image_id]

        imgDir = os.path.join( ROOT_DIR, osmcfg.trainDir,"%05d" % (image_id))
        wildcard = os.path.join( imgDir,"*.png")

        # 00015-american_football-0.png  00015-baseball-0.png  00015-baseball-1.png  00015-baseball-2.png  00015-baseball-3.png  00015-basketball-0.png  00015-basketball-1.png  00015.jpg  00015.txt

        maskCount = 0
        for filePath in glob.glob(wildcard): 
            filename = os.path.split(filePath)[1] 
            parts = filename.split( "-")
            if ( len(parts) == 3) : 
                maskCount += 1

        mask = np.zeros([info['height'], info['width'], maskCount], dtype=np.uint8)
        class_ids = np.zeros((maskCount), np.int32)
 
        count = 0
        for filePath in glob.glob(wildcard): 
            filename = os.path.split(filePath)[1] 
            parts = filename.split( "-")
            if ( len(parts) == 3) : 
                imgPath = filePath
                mask[:, :, count] = skimage.io.imread(filePath)
                class_ids[count] = featureNames[parts[1]]
                count += 1            
                
        return mask, class_ids

fullTrainingDir = os.path.join( ROOT_DIR, osmcfg.trainDir,"*")
fullImageList = []
for imageDir in glob.glob(fullTrainingDir): 
    if ( os.path.isdir( os.path.join( fullTrainingDir, imageDir) )):
        id = os.path.split(imageDir)[1]
        fullImageList.append( id)

random.shuffle(fullImageList)

cutoffIndex = int(len(fullImageList)*.75)
trainingImages = fullImageList[0:cutoffIndex ]
validationImages = fullImageList[cutoffIndex:-1 ]

# Training dataset
dataset_train = OsmImagesDataset()
dataset_train.load(trainingImages, config.IMAGE_SHAPE[0], config.IMAGE_SHAPE[1])
dataset_train.prepare()

# Validation dataset
dataset_val = OsmImagesDataset()
dataset_val.load(validationImages, config.IMAGE_SHAPE[0], config.IMAGE_SHAPE[1])
dataset_val.prepare()


# Create model in training mode
model = modellib.MaskRCNN(mode="training", config=config,
                          model_dir=MODEL_DIR)


# Which weights to start with?
init_with = "coco"  # imagenet, coco, or last

if init_with == "imagenet":
    model.load_weights(model.get_imagenet_weights(), by_name=True)
elif init_with == "coco":
    # Load weights trained on MS COCO, but skip layers that
    # are different due to the different number of classes
    # See README for instructions to download the COCO weights
    model.load_weights(COCO_MODEL_PATH, by_name=True,
                       exclude=["mrcnn_class_logits", "mrcnn_bbox_fc", 
                                "mrcnn_bbox", "mrcnn_mask"])
elif init_with == "last":
    # Load the last model you trained and continue training
    model.load_weights(model.find_last()[1], by_name=True)


# Training - Stage 1
# Adjust epochs and layers as needed
print("Training network heads")
model.train(dataset_train, dataset_val,
            learning_rate=config.LEARNING_RATE,
            epochs=4,
            layers='heads')

# Training - Stage 2
# Finetune layers from ResNet stage 4 and up
print("Training Resnet layer 4+")
model.train(dataset_train, dataset_val,
            learning_rate=config.LEARNING_RATE / 10,
            epochs=20,
            layers='4+')

# Training - Stage 3
# Finetune layers from ResNet stage 3 and up
print("Training Resnet layer 3+")
model.train(dataset_train, dataset_val,
            learning_rate=config.LEARNING_RATE / 100,
            epochs=50,
            layers='all')
            

# Fine tune all layers
# Passing layers="all" trains all layers. You can also 
# pass a regular expression to select which layers to
# train by name pattern.
#model.train(dataset_train, dataset_val, 
#            learning_rate=config.LEARNING_RATE / 10,
#            epochs=2, 
#            layers="all")


# Save weights
# Typically not needed because callbacks save after every epoch
# Uncomment to save manually
# model_path = os.path.join(MODEL_DIR, "mask_rcnn_shapes.h5")
# model.keras_model.save_weights(model_path)


