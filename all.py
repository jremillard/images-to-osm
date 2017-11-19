import os

os.system("python getdatafromosm.py")
os.system("python gettilesfrombing.py")
os.system("python maketrainingimages.py")
os.system("python train.py")
