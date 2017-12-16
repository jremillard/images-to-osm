import sys
sys.path.append("Mask_RCNN")

import os
import sys
import glob
import osmmodelconfig
import skimage
import imagestoosm.config as osmcfg
import model as modellib
import visualize as vis
from skimage import io
import numpy as np

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

print(dataset_full.image_ids)

count = 0

for image_index in dataset_full.image_ids :

    image, image_meta, gt_class_id, gt_bbox, gt_mask = modellib.load_image_gt(dataset_full, inference_config,image_index, use_mini_mask=False)

    info = dataset_full.image_info[image_index]

    imgDir = os.path.join( inference_config.ROOT_DIR, osmcfg.trainDir,info['id'])
    imgDir = os.path.join( inference_config.ROOT_DIR, "temp" )
    outputFile = os.path.join( imgDir,info['id'] + "-output.png")

    print(outputFile)

    results = model.detect([image], verbose=0)

    r = results[0]
  
    for i in range( len(r['class_ids']))  :
        if ( r['scores'][i] > 0.95 ) :

            mask = r['masks'][:,:,i]
            edgePixels = 20
            outside = np.sum( mask[0:edgePixels,:]) + np.sum( mask[-edgePixels:-1,:]) + np.sum( mask[:,0:edgePixels]) + np.sum( mask[:,-edgePixels:-1])
            if ( outside == 0 ) :
                if ( r['class_ids'][i] == 1):
                    vis.apply_mask(image,mask,[0.5,0,0])
                if (  r['class_ids'][i] == 2):
                    vis.apply_mask(image,mask,[0.5,0.5,0])
                if (  r['class_ids'][i] == 3):
                    vis.apply_mask(image,mask,[0.0,0,0.5])

            # for each osm object
                # make osm mask
                # ignore if on border
                # see if nn overlaps, draw green, draw thick red and write out image
                # save mask

            # for each nn mask
                # ignore if on border, bad score
                # fill in normal color
                # see if osm mask does not overlaps, draw thick red line and write out image


    io.imsave(outputFile,image)

    count += 1

    if ( count >1000):
        break

 
    
