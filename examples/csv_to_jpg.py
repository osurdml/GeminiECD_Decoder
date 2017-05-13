#Author: Robert DeBortoli, Oregon State University, debortor@oregonstate.edu

import csv
import sys
import cv2
import matplotlib.pyplot as plt
import numpy as np
import math

# Please note this uses OpenCV just to write the image files


NUM_BEAMS=256

# Input: a csv containing pixel values 
# Output: a folder full of jpgs
def build_jpgs(csv_file):
	with open(csv_file) as f:
		reader = csv.reader(f)
		for count,row in enumerate(reader):

			row=row[1:len(row)-1]
			row=np.asarray(row,dtype=np.int64)
			num_range_buckets=len(row)/NUM_BEAMS
			img=np.reshape(row,((num_range_buckets,NUM_BEAMS)))	
			cv2.imwrite("../data/jpgs/im"+str(count)+".jpg",img)

			if(count%200==0):
				print count
		f.close()


if __name__ == '__main__':
	build_jpgs(sys.argv[1])	
