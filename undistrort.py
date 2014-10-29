#!/usr/bin/env python
# -*- coding: utf_8 -*
#
# A Script to batch correct photo distortion for a GoPro Hero2 using the Lenfun database. 
# Should be usable for any camera in the lensfun db.
# Alex Mandel 2014
# tech@wildintellect.com

from PIL import Image
from PIL.ExifTags import TAGS
import lensfunpy
import cv2 # OpenCV library


#Test image /home/madadh/Pictures/gopro/farm/color/3D_R0971.JPG
def get_exif_data(fname):
    """Get embedded EXIF data from image file.
    http://www.endlesslycurious.com/2011/05/11/extracting-image-exif-data-with-python/
    """
    ret = {}
    try:
        img = Image.open(fname)
        if hasattr( img, '_getexif' ):
            exifinfo = img._getexif()
            if exifinfo != None:
                for tag, value in exifinfo.items():
                    decoded = TAGS.get(tag, tag)
                    ret[decoded] = value
    except IOError:
        print 'IOERROR ' + fname
    return ret

sample = "/home/madadh/Pictures/gopro/farm/color/3D_R0971.JPG"
undistortedImagePath ="testoutput.JPG"

im = Image.open(sample)
exif = get_exif_data(im)

exif.get('Make')
exif.get('Model')

#https://pypi.python.org/pypi/lensfunpy/0.12.0
cam_maker="GoPro"
cam_model="HD2"
lens="HD2 & Compatibles"
db = lensfunpy.Database()
cam = db.find_cameras(cam_maker, cam_model)[0]
lens = db.find_lenses(cam)[0]

focalLength = 2.5
aperture = 2.8
distance = 0

im = cv2.imread(sample)
height, width = im.shape[0], im.shape[1]

mod = lensfunpy.Modifier(lens, cam.crop_factor, width, height)
mod.initialize(focalLength, aperture, distance)

undistCoords = mod.apply_geometry_distortion()
imUndistorted = cv2.remap(im, undistCoords, None, cv.INTER_LANCZOS4)
cv2.imwrite(undistortedImagePath, imUndistorted)
