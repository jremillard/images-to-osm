# Images to OSM
This project uses the Mask R-CNN algorithm to detect features in satellite images. The goal is to test the Mask R-CNN algorithm and improve OpenStreetMap by adding many high quality baseball, soccer, tennis, football, and basketball fields to the map.

The [Mask R-CNN]([https://arxiv.org/abs/1703.06870) was published March 2017 by the [Facebook AI Research (FAIR)](https://research.fb.com/category/facebook-ai-research-fair/). 

The paper claimed state of the art performance for detecting instance segmentation masks. The paper is an exciting result because "Solving" the instance segmentation mask problem will benefit many applications outside of Facebook. 

Using Mask R-CNN successfully on a new data set would be a good indication that the algorithm is generic enough to be applicable on many problems. However, the number of publicly available data sets with enough images to train this algorithm are limited because collecting and annotating data for 50,000+ images is expensive and time consuming. 

The opportunity of working with cutting edge AI algorithms and my favorite hobby was too much to pass up. The OpenStreetMap project can come to the rescue. Microsoft's Bing tiles combined with the OpenStreetMap data is a good source of segmentation mask data!

## Samples Images

Mask R-CNN finding baseballs, basketball, and tennis fields in Bing images.

![OSM Mask R-CNN sample 1](/sample-images/sample1.png)
![OSM Mask R-CNN sample 2](/sample-images/sample2.png)
![OSM Mask R-CNN sample 3](/sample-images/sample3.png)

## Mask R-CNN Implementation

At this time (end of 2017), Facebook AI research has not yet released their implementation. [Matterport, Inc](https://matterport.com/) has graciously released an very nice python [implementation of Mask R-CNN](https://github.com/matterport/Mask_RCNN) on github using Keras and TensorFlow. 

## Why Sports Fields

Sport fields are a good fit for the Mask R-CNN algorithm. 

- They are visible in the satellite images regardless of the tree cover, unlike say buildings. 
- They are "blob" shape and not a line shape like a roads.
- If successful, they are easy to conflate and import back into OSM because they are isolated features.

## Training with OSM

The stretch goal for this project is to train a network that is at or past human level performance and to completely map the sports fields in Massachusetts in OSM. The problem is that the existing data in OSM is not of high enough quality to train any algorithm to human level performance.  The plan is to iteratively train, feed corrections back to OSM, and re-train, bootstrapping the algorithm and OSM together. Hopefully a virtuous circle between OSM and the algorithm will form.

## Running

The entire training workflow is in the trainall.py script, which calls the following scripts in 
sequence.

1. getdatafromosm.py uses overpass to download the data for the sports fields.
2. gettilesfrombing.py uses the downloaded osm data, and matching bing tiles.
3. maketrainingimages.py collects the osm data, and the bing tiles into a collection of training images and masks.
4. train.py actually runs training for the Mask R-CNN algorithm.

Note if you want to run this yourself. I am using a GeForce GTX 1080 with 8GB of memory. It takes 4 days to do a "light" training using the existing weights from Matterport.

## Convert Results to OSM File

TODO

## Configuration 

1. Ubuntu 17.10
2. A Bing key, create a secrets.py file, add in bingKey ="your key"
3. create a virtual environment python 3.6 
4. in the virtual environment, run "pip install -r requirements.txt"
5. TensorFlow 1.3+ 
6. Keras 2.0.8+.

