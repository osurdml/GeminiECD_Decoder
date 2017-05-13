import sys

if __name__ == '__main__':
 	ecd_filename=str(sys.argv[1])

	if(len(sys.argv)==2):
		csv_filename=str(sys.argv[2])
		ecdReader(filename,csv_filename)

	elif(len(sys.argv)>2):
		num_frames=int(str(sys.argv[3]))
		ecdReader(filename,csv_filename,num_frames)

	else:
		ecdReader(filename)