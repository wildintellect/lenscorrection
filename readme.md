#Lens Correction 
#####(aka Zap-distortion)

A Python script to batch correct photo distortion for a GoPro Hero2 using the Lenfun database. 

Should be adaptable for any camera in the lensfun db.

##Requirements
* Python 2.7
* OpenCV 2.4.x (with Python bindings)
* Lensfun 2.8+

See pre.sh for more details.

Example![Compare before and after photos](overview.png  "Before and After")

##Usage
1. Install the prequisites
1. Download the undistort.py
1. Open a terminal in the directory where you have photos.
1. Run the code
	python /path/to/undistort.py
1. Results will be filename_fix.jpg