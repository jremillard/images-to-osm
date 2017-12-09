import os

#os.system("python getdatafromosm.py")
os.system("python gettilesfrombing.py 2>&1 | tee all.log")
os.system("python maketrainingimages.py 2>&1 | tee -a all.log")
os.system("python train.py 2>&1 | tee -a all.log")
