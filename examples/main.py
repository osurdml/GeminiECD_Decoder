#Author: Robert DeBortoli, Oregon State University, debortor@oregonstate.edu

import sys
from read_ecd import ecdReader
from csv_to_jpg import build_jpgs

NUM_FRAMES_TO_PROCESS=1000

if __name__ == '__main__':
 	ecd_filename=str(sys.argv[1])

	if(len(sys.argv)==3):
		csv_filename=str(sys.argv[2])
		ecdReader(ecd_filename,csv_filename,NUM_FRAMES_TO_PROCESS)
		build_jpgs(csv_filename)

	elif(len(sys.argv)>3):
		csv_filename=str(sys.argv[2])
		num_frames=int(str(sys.argv[3]))
		ecdReader(ecd_filename,csv_filename,num_frames)
		build_jpgs(csv_filename)

	else:
		ecdReader(ecd_filename,'sonar_csv.csv',NUM_FRAMES_TO_PROCESS)
		csv_filename='sonar_csv.csv'
		build_jpgs(csv_filename)