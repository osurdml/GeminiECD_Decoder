#Authors: Robert DeBortoli, Oregon State University, debortor@oregonstate.edu
#		  Veronica Gruning, Oregon State University, REU student


import numpy as np
import time
import matplotlib.pyplot as plt
import cv2
import sys
import struct


##################################
# Converts a hex string to ints
##################################
def hexListToInt(hlist,printVals=False):
	res=0
	i=0
	for val in hlist:
		if(len(val)==4):
			res+=int(val[2],16)*16**(i+1)
			res+=int(val[3],16)*16**(i)
		else:
			res+=int(val[2],16)*16**(i)
		i+=2
	return res



##################################
# The supports the below function in taking a 
# string of hex digits and converting them to floats
##################################
def signExponentMantissaToFloat(sign,exponent,mantissa):
	if(int(sign)==0):
		res_sign=1
	else:
		print "error occured"
		raw_input()

	res_exponent=0
	for i in range(len(exponent)):
		# print i
		if(int(exponent[len(exponent)-i-1])==1):
			res_exponent+=2**i
	res_exponent-=1023

	res_mantissa=1.
	for i in range(len(mantissa)):
		if(int(mantissa[i])==1):
			res_mantissa+=(1./(2**(i+1)))

	return res_sign*2**(res_exponent)*res_mantissa+315964800-86400*5



##################################
# This converts a string of hex digits to 
# a float
##################################
def hexListToFloat(hlist,printVals=False):
	res=""
	i=0
	for val in hlist:
		if(len(val)==4):
			res=val[2]+val[3]+res
		else:
			res='0'+val[2]+res
		i+=2
	#now that we have the hex string, we have to convert it to binary 
	binary = lambda x: " ".join(reversed( [i+j for i,j in zip( *[ ["{0:04b}".format(int(c,16)) for c in reversed("0"+x)][n::2] for n in [1,0] ] ) ] ))
	binary_res= binary(res).replace(" ","")
	sign=binary_res[0]
	exponent=binary_res[1:12]
	mantissa=binary_res[12:]
	res=signExponentMantissaToFloat(sign,exponent,mantissa)

	return res

##################################
# Converts decompressed hex data (now in string format)
# to integers, using the entire string (its not hex digit by)
# digit.
##################################
def dDataToInt(dData):
	res=[]
	i=0
	for val in dData:
		val=str(val)
		if(len(val)==2):
			res.append((int(val[0],16)*16**(1))+(int(val[1],16)*16**(0)))
		elif(len(val)==1):
			res.append(int(val[0],16)*16**(0))
		else:
			print "ERROR OCURRED"
	return res

##################################
# Converts the compressed data in hex format in cData to
# decompressed data (in dData)
##################################
def uncompress(dData, cData, size, m_dataSize):
	cDataSize = 0
	uSize = 0
	nZeros = 0
	cPtr = 0
	uPtr = 0

	while (cDataSize < size and uSize <m_dataSize):
		if (int(str(hex(ord(cData[cPtr])))[2:],16)==0 and cDataSize < (size-1)):
			cPtr+=1;
			cDataSize+=1  
			nZeros=int(str(hex(ord(cData[cPtr])))[2:],16)  
			cPtr+=1
			cDataSize+=1  
			if(nZeros==255 and int(str(hex(ord(cData[cPtr])))[2:],16)==255): 
				
				cPtr+=1
				cDataSize+=1

			while (nZeros and uSize<m_dataSize):
				dData[uPtr]=str(0)
				uPtr+=1
				uSize+=1
				nZeros-=1

		elif(cData[cPtr]==1):    
			cPtr+=1
			cData+=1
			dData[uPtr]=str(0)
			uPtr+=1
			uSize+=1 

		else:    
			dData[uPtr]=str(hex(ord(cData[cPtr])))[2:]
			uPtr+=1
			cPtr+=1
			uSize+=1
			cDataSize+=1



##################################
# The main workhorse for reading and the 
# converting the data in the proper order
# byte by byte. Because the data must be read in a seuqential manner,
# all of the data is read, even if it is not utilized. 
#
# Input: an ECD filename to process, a csv filename to put the pixel data and a number of sonar frames to process
##################################

def ecdReader(ecd_filename,csv_filename='sonar_csv.csv',number_of_frames=7000):
	framenumber=0
	number_of_bytes=50000000
	
	csv_file= open(csv_filename,'w')
	num_skipped_frames=0
	with open(ecd_filename, "rb") as f:
		prev_byte=10000
		curr_byte=9
		i=0

		#header information printed but not saved
		print "version: ",hex(ord(f.read(1))),hex(ord(f.read(1)))
		print "version2: ",hex(ord(f.read(1))),hex(ord(f.read(1)))
		print "enc_inf: ",hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1)))
		print "msg1: ",hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1)))
		print "msg2: ",hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1)))
		print "enc_inf2: ",hex(ord(f.read(1))),hex(ord(f.read(1)))


		while (curr_byte != "" and framenumber<number_of_frames and i<number_of_bytes):	
			curr_byte = f.read(1)
			f.read(1)
			if(hex(ord(curr_byte))=='0x1'):#if its a sensor record,skip over it
				#We skip over a frame by reading bytes until we get the "end of message" byte
				for j in range(100000):
					prev_byte=curr_byte
					curr_byte=f.read(1)
					if((hex(ord(curr_byte))=='0xde' and curr_byte==prev_byte)):
						num_skipped_frames+=1
						break

			#now we start to decode the header of the frame
			if(hex(ord(curr_byte))=='0x2'):
				print "FRAMENUM: ",framenumber
				framenumber+=1

				#we now decode a series of constants and parameters for further processing
				hex(ord(f.read(1))),hex(ord(f.read(1)))
				hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1)))
				hex(ord(f.read(1))),hex(ord(f.read(1)))
				hex(ord(f.read(1))),hex(ord(f.read(1)))
				
				hex(ord(f.read(1))),hex(ord(f.read(1))) #End of Log Header Record
				hex(ord(f.read(1))),hex(ord(f.read(1))) #From CPing-Version number
				hex(ord(f.read(1)))# (01)
				hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1)))
				hex(ord(f.read(1))) #optimum transmit pulse length for a given range
				hex(ord(f.read(1)))
				hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))) # (~1483.2)
				hex(ord(f.read(1))),hex(ord(f.read(1)))
				hex(ord(f.read(1))),hex(ord(f.read(1))) # (1000)
				hex(ord(f.read(1))),hex(ord(f.read(1)))
				hex(ord(f.read(1))),hex(ord(f.read(1)))
				hex(ord(f.read(1))),hex(ord(f.read(1))) #specifies spreading gain (500)
				hex(ord(f.read(1))),hex(ord(f.read(1))) #specifies absorption gain
				hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1)))
				hex(ord(f.read(1))),hex(ord(f.read(1)))
				numberOfBeamsForAperture =hexListToInt([hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1)))]) # (120.000)
				hex(ord(f.read(1))),hex(ord(f.read(1)))
				hex(ord(f.read(1))),hex(ord(f.read(1)))
				hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1)))
				hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1)))
				hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))) #modulation frequency of the sonar in Hz (90422)
				numberOfBeams=hexListToInt([hex(ord(f.read(1))),hex(ord(f.read(1)))])
				hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))) # (~1483.2)
				hex(ord(f.read(1))), hex(ord(f.read(1)))
				hex(ord(f.read(1))), hex(ord(f.read(1)))
				hex(ord(f.read(1))), hex(ord(f.read(1)))
				hex(ord(f.read(1))),hex(ord(f.read(1)))
				hex(ord(f.read(1)))
				hex(ord(f.read(1)))
				hex(ord(f.read(1)))
				hexListToInt([hex(ord(f.read(1)))])#End of data from CPing


				hex(ord(f.read(1))),hex(ord(f.read(1)))#From CTgtRec
				hex(ord(f.read(1))),hex(ord(f.read(1)))
					
				#timestamps for sonar frames, please note the timestamps use GPS time. 
				timeOfTransmit=hexListToFloat([hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),
					hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1)))],True) # (~1116790948)

				timeOfLastRecord=hexListToFloat([hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),
						hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1)))])

				hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1)))
				hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))) #End of data from CTgtRec (1500.00)
				hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))) #From CTgtImg (12)
				

				bytesPerPixel=hexListToInt([hex(ord(f.read(1)))]) # (1)
				numberOfRanges = hexListToInt([hex(ord(f.read(1))), hex(ord(f.read(1))),hex(ord(f.read(1))), hex(ord(f.read(1)))]) # the number of range buckets on a single beam
				startBearing= hexListToInt([hex(ord(f.read(1))), hex(ord(f.read(1))),hex(ord(f.read(1))), hex(ord(f.read(1)))])
				endBearing = hexListToInt([hex(ord(f.read(1))), hex(ord(f.read(1))),hex(ord(f.read(1))), hex(ord(f.read(1)))]) # (256)
				startRange = hexListToInt([hex(ord(f.read(1))), hex(ord(f.read(1))),hex(ord(f.read(1))), hex(ord(f.read(1)))])
				endRange = hexListToInt([hex(ord(f.read(1))), hex(ord(f.read(1))),hex(ord(f.read(1))), hex(ord(f.read(1)))]) # (549)
				RXdual = hexListToInt([hex(ord(f.read(1))), hex(ord(f.read(1))),hex(ord(f.read(1))), hex(ord(f.read(1)))])
				numberOfBearings = hexListToInt([hex(ord(f.read(1))), hex(ord(f.read(1))),hex(ord(f.read(1))), hex(ord(f.read(1)))]) # number of beams sent out


				for i in range(numberOfBeams):
					hex(ord(f.read(1)))
					hex(ord(f.read(1)))
					hex(ord(f.read(1)))
					hex(ord(f.read(1)))
					hex(ord(f.read(1)))
					hex(ord(f.read(1)))
					hex(ord(f.read(1)))
					hex(ord(f.read(1)))
				numberOfBearings2 = hexListToInt([hex(ord(f.read(1))),hex(ord(f.read(1)))])

				f.read(1)
				f.read(1)

				#size of a frame
				cDataSize=hexListToInt([hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1)))])
				cData=[]

				#building of a compressed frame
				for i in range(cDataSize):
					cData.append(f.read(1))
				
				#dData is where the uncompressed data will go.
				dData=[0]*(numberOfBearings*numberOfRanges*bytesPerPixel)
				uncompress(dData, cData, cDataSize, numberOfBearings*numberOfRanges*bytesPerPixel)
				dDataNew=dDataToInt(dData)

				csv_file.write(str(timeOfTransmit)+',')

				#writing of the uncompressed frame to a csv file
				for i in range(numberOfBearings*numberOfRanges*bytesPerPixel):
					csv_file.write(str(dDataNew[i])+',')
				csv_file.write('\n')

				hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1)))
				hex(ord(f.read(1))),hex(ord(f.read(1)))

				#Process the ping tail of every record
				hex(ord(f.read(1))),hex(ord(f.read(1)))
				hex(ord(f.read(1))),hex(ord(f.read(1)))
				hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1)))
				hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1)))
				hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1)))

				#number of generally meaningless hex bytes at the end to read (so that the next frame starts st the right location in memory)
				numberOfClinex= hexListToInt([hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1)))])
				hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1))),hex(ord(f.read(1)))
				hex(ord(f.read(1))),hex(ord(f.read(1)))
				hex(ord(f.read(1))),hex(ord(f.read(1)))
				hex(ord(f.read(1))),hex(ord(f.read(1)))
				hex(ord(f.read(1))),hex(ord(f.read(1)))

				#clear the rest of the meaningless data
				for i in range(numberOfClinex):
					hex(ord(f.read(1)))
					hex(ord(f.read(1)))
					hex(ord(f.read(1)))
					hex(ord(f.read(1)))

				hex(ord(f.read(1))),hex(ord(f.read(1)))
				

		i+=	1
		csv_file.close()

if __name__ == '__main__':
  filename=str(sys.argv[1])
  ecdReader(filename)
