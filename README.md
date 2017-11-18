# Images to OSM
This project uses the Mask R-CNN algorithm to detect features in satellite images.

The goal of the project is to have fun, be educational, and if successful add 
a bunch of missing baseball, soccer, tennis, football, and basketball fields to OSM.

## Why Sports Fields
- Sport fields are a good fit for the Mask R-CNN algorithm that I want to explore. 
Something like roads that are lines won't work well.
- They are visible in the satellite images regardless of the tree cover, unlike say buildings. 
- If successful, they are easy to conflate and import back into OSM because they are isolated features.

## Training

The training/truth data is derived from the existing fields in OSM and Bing satellite tiles. The data in OSM is 
used to create pixel masks and bounding boxes over the Bing tiles to create training data.  

## Running

TODO

## Convert Results to OSM File

TODO

## Configuration 

1. Ubuntu 17.10
2. A Bing key, create a secrets.py file, add in bingKey ="your key"
3. create a virtual environment python 3.6 
4. in the virtual environment, run "pip install -r requirements.txt"
5. TensorFlow 1.3+ 
6. Keras 2.0.8+.

