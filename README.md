# GeminiECD_Decoder
A Python script for decoding the Tritech Gemini Sonar ECD data format to .CSV format, which can be used for image processing, etc.

The resulting CSV file containes rows of pixel values which can be reshaped into images. 

For example, if a frame is 10x5 pixels, one row would contain a frame number, timestamp, and 50 pixel values

This was designed to work with Application version 1.17.00

To run the code:
	python main.py ecd-filename [csv-filename] [number-of-frames-to-process]




