# Images to OSM
This project uses the Mask R-CNN algorithm to detect features in satellite images. The goal is to test the Mask R-CNN neural network algorithm and improve OpenStreetMap by adding high quality baseball, soccer, tennis, football, and basketball fields to the map.

The [Mask R-CNN]([https://arxiv.org/abs/1703.06870) was published March 2017, by the [Facebook AI Research (FAIR)](https://research.fb.com/category/facebook-ai-research-fair/). 

This paper claims state of the art performance for detecting instance segmentation masks. The paper is an exciting result because "Solving" the instance segmentation mask problem will benefit numerious practical applications outside of Facebook and OpenStreetMap.

Using Mask R-CNN successfully on a new data set would be a good indication that the algorithm is generic enough to be applicable on many problems. However, the number of publicly available data sets with enough images to train this algorithm are limited because collecting and annotating data for 50,000+ images is expensive and time consuming. 

Microsoft's Bing satellite tiles, combined with the OpenStreetMap data, is a good source of segmentation mask data. The opportunity of working with a cutting edge AI algorithms and doing my favorite hobby was too much to pass up. The OpenStreetMap project can come to the rescue. 

## Samples Images

Mask R-CNN finding baseball, basketball, and tennis fields in Bing images.

![OSM Mask R-CNN sample 1](/sample-images/sample1.png)
![OSM Mask R-CNN sample 2](/sample-images/sample2.png)
![OSM Mask R-CNN sample 3](/sample-images/sample3.png)

## Mask R-CNN Implementation

At this time (end of 2017), Facebook AI research has not yet released their implementation. [Matterport, Inc](https://matterport.com/) has graciously released a very nice python [implementation of Mask R-CNN](https://github.com/matterport/Mask_RCNN) on github using Keras and TensorFlow. 

## Why Sports Fields

Sport fields are a good fit for the Mask R-CNN algorithm. 

- They are visible in the satellite images regardless of the tree cover, unlike, say, buildings. 
- They are "blob" shape and not a line shape, like a roads.
- If successful, they are easy to conflate and import back into OSM, because they are isolated features.

## Training with OSM

The stretch goal for this project is to train a neural network at human level performance and to completely map the sports fields in Massachusetts in OSM. The problem is that the existing data in OSM is not of high enough quality to train any algorithm to human level performance.  The plan is to iteratively train, feed corrections back to OSM, and re-train, bootstrapping the algorithm and OSM together. Hopefully a virtuous circle between OSM and the algorithm will form until the algorithm is good as a human mapper.

## Workflow

The training workflow is in the trainall.py script, which calls the following scripts in sequence.

1. getdatafromosm.py uses overpass to download the data for the sports fields.
2. gettilesfrombing.py uses the OSM data to download the required Bing tiles. Expect around 2 days to run the first time.
3. maketrainingimages.py collects the OSM data, and the Bing tiles into a set of training images and masks. Expect 12 hours to run each time.
4. train.py actually runs training for the Mask R-CNN algorithm. Expect that this will take 3 or 4 days to run on single GTX 1080 with 8GB of memory.

## Convert Results to OSM File

5. createosmanomaly.py runs the neural network over the training image set and suggests changes to OSM. 

   This script converts the neural network output masks into the candidate OSM ways. It does this by fitting perfect rectangles to tennis and basketball mask boundaries. For baseball fields, the osm ways are a fitted 90 degree wedges and the simplified masks boundary. The mask fitting is a nonlinear optimization problem and it is performed with a simplex optimizer using a robust Huber cost function. The simplex optimizer was used because I was too lazy code a partial derivative function. The boundary being fit is not a gaussian process, therefor the Huber cost function is a better choice than a standard least squared cost function. The unknown rotation of the features causes the fitting optimization to be highly non-convex. In English, the optimization gets stuck in local valleys if it is started far away from the optimal solution. This is handled by simply seeding the optimizer at several rotations and emitting all the high quality fits. A human using the reviewosmanomaly.py script sorts out which rotation is the right one. Hopefully as the neural network performance on baseball fields improves the alternate rotations can be removed.

   In order to hit the stretch goal, the training data from OSM will need to be pristine. The script will need to be extended to identify incorrectly tagged fields and fields that are poorly traced. For now, it simply identifies fields that are missing from OSM.

6. The reviewosmanomaly.py is run next to visually approve or reject the changes suggested in the anomaly directory. 

    Note this is the only script that requires user interaction. The script clusters together suggestions from 
    createosmanomaly.py and presents an gallery options. The the user visually inspect the image gallery and approves or reject changes suggested by createosmanomaly.py. The images shown are of the final way geometry over the Bing satellite images.

7. The createfinalosm.py creates the final .osm files from the anomaly review done by reviewosmanomaly.py. It breaks up the files so that the final OSM file size is under the 10,000 element limit of the OSM sdk.

## Phase 1 - Notes ##

Phase 1 of the project is training the neural network directly off of the unimproved OSM data, and importing 
missing fields from the training images back into OSM. 2,800 high quality fields were found.

For tennis and basketball courts the performance is quite good. The masks are rectangles with few
false positives. Like a human mapper it has no problem handling clusters of tennis and basketball courts, rotations, occultations from trees, and different colored pavement. It is close, but not quite at to human performance. After the 2,800 missing fields are put into OSM, hopefully it will reach human level performance. 

The good news/bad news are the baseball fields. They are much more challenging and interesting than the tennis and basketball courts. First off, they have a large variation in scale. A baseball field for very small children is 5x to 6x smaller than a full sized field for adults. The primary feature to identify a baseball field is the infield diamond, but the infield is only a small part of the actual full baseball field. To map a baseball field, the large featureless grassy outfield must be included. The outfields have to be extrapolated out from the infield. In cases where there is a outfield fence, the neural network does quite well at terminating the outfield at the fence. But most baseball fields don't have an outfield fence or even a painted line. The outfields stretch out until they "bump" into something else, a tree line, a road, another field while maintaining its wedge shape. Also complicating the situation, is that like the neural network, the OSM human mappers are also confused about how to map the outfields without a fence. About 10% of the mapped baseball fields are just the infields. These tiny baseball fields were excluded from the training set, but because they are still in the training images and not mapped, they are still causing performance problems. 

In the 2,800 missing fields, only the baseball fields with really good outfields were included. The phase 1 neural network had no trouble identifying the infields, but it was struggling with outfields without fences. Many missing baseball fields had to be skipped because of poor outfield marking. Hopefully the additional high quality outfield data imported into OSM will improve its performance in this challenging area on the next phase. 

## Configuration 

- Ubuntu 17.10
- A Bing key, create a secrets.py file, add in bingKey ="your key"
- Create a virtual environment python 3.6 
- In the virtual environment, run "pip install -r requirements.txt"
- TensorFlow 1.3+ 
- Keras 2.0.8+.

