# Images to OSM
<<<<<<< HEAD
This project uses the Mask R-CNN algorithm to detect features in satellite images. The goal is to test the Mask R-CNN algorithm and improve OpenStreetMap, by adding high quality baseball, soccer, tennis, football, and basketball fields to the map.

The [Mask R-CNN]([https://arxiv.org/abs/1703.06870) was published March 2017, by the [Facebook AI Research (FAIR)](https://research.fb.com/category/facebook-ai-research-fair/). 

This paper claims state of the art performance for detecting instance segmentation masks. The paper is an exciting result because "Solving" the instance segmentation mask problem will benefit numerious practical applications outside of Facebook. 

Using Mask R-CNN successfully on a new data set would be a good indication that the algorithm is generic enough to be applicable on many problems. However, the number of publicly available data sets with enough images to train this algorithm are limited, because collecting and annotating data for 50,000+ images is expensive and time consuming. 

Microsoft's Bing tiles, combined with the OpenStreetMap data, is a good source of segmentation mask data. The opportunity of working with cutting edge AI algorithms and doing my favorite hobby, was too much to pass up. The OpenStreetMap project can come to the rescue. 
=======
This project uses the Mask R-CNN algorithm to detect features in satellite images. The goal is to test the Mask R-CNN algorithm and improve OpenStreetMap by adding many high quality baseball, soccer, tennis, football, and basketball fields to the map.

The [Mask R-CNN]([https://arxiv.org/abs/1703.06870) was published March 2017 by the [Facebook AI Research (FAIR)](https://research.fb.com/category/facebook-ai-research-fair/). 

The paper claimed state of the art performance for detecting instance segmentation masks. The paper is an exciting result because "Solving" the instance segmentation mask problem will benefit many applications outside of Facebook. 

Using Mask R-CNN successfully on a new data set would be a good indication that the algorithm is generic enough to be applicable on many problems. However, the number of publicly available data sets with enough images to train this algorithm are limited because collecting and annotating data for 50,000+ images is expensive and time consuming. 

Microsoft's Bing tiles combined with the OpenStreetMap data is a good source of segmentation mask data. The opportunity of working with cutting edge AI algorithms and my favorite hobby was too much to pass up. The OpenStreetMap project can come to the rescue. 
>>>>>>> 164438af2d762a9932100dcebc35a277be1004d9

## Samples Images

Mask R-CNN finding baseball, basketball, and tennis fields in Bing images.

![OSM Mask R-CNN sample 1](/sample-images/sample1.png)
![OSM Mask R-CNN sample 2](/sample-images/sample2.png)
![OSM Mask R-CNN sample 3](/sample-images/sample3.png)

## Mask R-CNN Implementation

<<<<<<< HEAD
At this time (end of 2017), Facebook AI research has not yet released their implementation. [Matterport, Inc](https://matterport.com/) has graciously released a very nice python [implementation of Mask R-CNN](https://github.com/matterport/Mask_RCNN) on github using Keras and TensorFlow. 

## Why Sports Fields

Sport fields are a good fit for the Mask R-CNN algorithm. 

- They are visible in the satellite images regardless of the tree cover, unlike, say, buildings. 
- They are "blob" shape and not a line shape, like a roads.
- If successful, they are easy to conflate and import back into OSM, because they are isolated features.

## Training with OSM

The stretch goal for this project is to train a network at human level performance and to completely map the sports fields in Massachusetts in OSM. The problem is that the existing data in OSM is not of high enough quality to train any algorithm to human level performance.  The plan is to iteratively train, feed corrections back to OSM, and re-train, bootstrapping the algorithm and OSM together. Hopefully a virtuous circle between OSM and the algorithm will form.

## Workflow
=======
At this time (end of 2017), Facebook AI research has not yet released their implementation. [Matterport, Inc](https://matterport.com/) has graciously released an very nice python [implementation of Mask R-CNN](https://github.com/matterport/Mask_RCNN) on github using Keras and TensorFlow. 

## Why Sports Fields

Sport fields are a good fit for the Mask R-CNN algorithm. 

- They are visible in the satellite images regardless of the tree cover, unlike say buildings. 
- They are "blob" shape and not a line shape like a roads.
- If successful, they are easy to conflate and import back into OSM because they are isolated features.

## Training with OSM

The stretch goal for this project is to train a network at human level performance and to completely map the sports fields in Massachusetts in OSM. The problem is that the existing data in OSM is not of high enough quality to train any algorithm to human level performance.  The plan is to iteratively train, feed corrections back to OSM, and re-train, bootstrapping the algorithm and OSM together. Hopefully a virtuous circle between OSM and the algorithm will form.
>>>>>>> 164438af2d762a9932100dcebc35a277be1004d9

The entire training workflow is in the trainall.py script, which calls the following scripts in sequence.

<<<<<<< HEAD
1. getdatafromosm.py uses overpass to download the data for the sports fields.
2. gettilesfrombing.py uses the OSM data to download the required Bing tiles. Expect around 2 days to run the first time.
3. maketrainingimages.py collects the OSM data, and the Bing tiles into a set of training images and masks. Expect 12 hours to run each time.
4. train.py actually runs training for the Mask R-CNN algorithm. Expect that this will take 3 or 4 days to run on single GTX 1080 with 8GB of memory.
=======
The entire training workflow is in the trainall.py script, which calls the following scripts in sequence.

1. getdatafromosm.py uses overpass to download the data for the sports fields.
2. gettilesfrombing.py uses the downloaded osm data, and matching bing tiles.
3. maketrainingimages.py collects the osm data, and the bing tiles into a collection of training images and masks.
4. train.py actually runs training for the Mask R-CNN algorithm.

Note if you want to run this yourself. I am using a GeForce GTX 1080 with 8GB of memory. It takes 4 days to do a "light" training using the existing weights from Matterport. 
>>>>>>> 164438af2d762a9932100dcebc35a277be1004d9

## Convert Results to OSM File

5. createosmanomaly.py, runs the trained network and suggests changes to OSM. The script generates final OSM ways using the masks. 
   It fits perfect rectangles for non baseball fields and wedge shapes for baseball fields. This script is
   slow because of the shape fitting and requires that it be run over 35+ hour period.
6. The reviewosmanomaly.py is run next to visually approve or reject the changes suggested in the anomaly directory. Note this is 
    the only script that requires user interaction. For every cluster of features. the user must inspect the image and 
    approve or reject changes suggested by createosmanomaly.py. 
7. The createfinalosm.py creates the final osm files from the anomaly review done by reviewosmanomaly.py.

## Configuration 

- Ubuntu 17.10
- A Bing key, create a secrets.py file, add in bingKey ="your key"
- Create a virtual environment python 3.6 
- In the virtual environment, run "pip install -r requirements.txt"
- TensorFlow 1.3+ 
- Keras 2.0.8+.

