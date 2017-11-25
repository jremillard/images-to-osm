
# coding: utf-8

# # Mask R-CNN - Train on Shapes Dataset
# 
# 
# This notebook shows how to train Mask R-CNN on your own dataset. To keep things simple we use a synthetic dataset of shapes (squares, triangles, and circles) which enables fast training. You'd still need a GPU, though, because the network backbone is a Resnet101, which would be too slow to train on a CPU. On a GPU, you can start to get okay-ish results in a few minutes, and good results in less than an hour.
# 
# The code of the *Shapes* dataset is included below. It generates images on the fly, so it doesn't require downloading any data. And it can generate images of any size, so we pick a small image size to train faster. 


import sys
sys.path.append("Mask_RCNN")

import os
import random
import math
import time
import numpy as np
import random
import glob
import skimage
import osmmodelconfig

from config import Config
import imagestoosm.config as osmcfg
import utils
import model as modellib
from model import log

# Root directory of the project
#ROOT_DIR = os.getcwd()
ROOT_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))

# Directory to save logs and trained model
MODEL_DIR = os.path.join(ROOT_DIR, "logs")

# Path to COCO trained weights
COCO_MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco.h5")

config = osmmodelconfig.OsmModelConfig()
config.ROOT_DIR = ROOT_DIR
config.display()

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
dataset_train =  osmmodelconfig.OsmImagesDataset(ROOT_DIR)
dataset_train.load(trainingImages, config.IMAGE_SHAPE[0], config.IMAGE_SHAPE[1])
dataset_train.prepare()

# Validation dataset
dataset_val =  osmmodelconfig.OsmImagesDataset(ROOT_DIR)
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
    print(model.find_last()[1])
    model.load_weights(model.find_last()[1], by_name=True)

if ( init_with != "last") :
    # Training - Stage 1
    # Adjust epochs and layers as needed
    print("Training network heads")
    model.train(dataset_train, dataset_val,
                learning_rate=config.LEARNING_RATE,
                epochs=4,
                layers='heads')

# Training - Stage 2
# Finetune layers from ResNet stage 4 and up
print("Training Resnet layer 5+")
model.train(dataset_train, dataset_val,
            learning_rate=config.LEARNING_RATE/10,
            epochs=100,
            layers='5+')

# Training - Stage 3
# Finetune layers from ResNet stage 3 and up
print("Training all")
model.train(dataset_train, dataset_val,
            learning_rate=config.LEARNING_RATE / 100,
            epochs=1000,
            layers='all')
            
