import sys
sys.path.append("Mask_RCNN")

import os
import sys
import glob
import osmmodelconfig
import skimage
import imagestoosm.config as osmcfg
import model as modellib

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

# Load trained weights (fill in path to trained weights here)
assert model_path != "", "Provide path to trained weights"
print("Loading weights from ", model_path)
model.load_weights(model_path, by_name=True)

for image_id in dataset_full.image_ids :

    image, image_meta, gt_class_id, gt_bbox, gt_mask = modellib.load_image_gt(dataset_full, inference_config,
                               image_id, use_mini_mask=False)

    results = model.detect([image], verbose=1)

    r = results[0]

    print(r)
    print(r['masks'])
    print(r['class_ids'])
    print(r['scores'])

    break    

    
