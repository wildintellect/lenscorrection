#!/usr/bin/env python
# -*- coding: utf_8 -*
#
# A Script to batch correct photo distortion for a GoPro Hero2 using the Lenfun database. 
# Should be usable for any camera in the lensfun db.
# Alex Mandel 2014
# tech@wildintellect.com

from PIL import Image
from PIL.ExifTags import TAGS
import lensfunpy # Lensfun 
import cv2 # OpenCV library
import os
from multiprocessing import Pool
import timeit #Add a timer
import piexif

#Test image /Pictures/gopro/farm/color/3D_R0971.JPG
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
    except Exception as e:
        print(" ".join(["Something failed because of",str(e),fname]))
    return(ret)

def photolist(directory):
    '''get list of photos in the directory'''
    #TODO: support raw file sorting too instead and in addition to jpg
    extension = ".jpg"
    list_of_files = [filen for filen in os.listdir(directory) if filen.lower().endswith(extension)]
    return(list_of_files)

def process_photos(photos):
    ''' Single threaded iteration of photo list'''
    results = [correct_photo(photo) for photo in photos]
    return(results)

def multi_process(photos):
    ''' Multithreaded/Core variant that does multiple photos in parallel'''
    pool = Pool(processes=2) #2 is safe number of threads/cores, up the number if you have more
    pool.map(correct_photo, photos)
    pool.close()
    pool.join()
    return

def correct_photo(photo):
    '''Apply distortion correction'''

    #exif = get_exif_data(photo)
    #exif.get('Make')
    #exif.get('Model')

    #https://pypi.python.org/pypi/lensfunpy/0.12.0
    cam_maker="GoPro"
    cam_model="HD2"
    #lens="HD2 & Compatibles"
    
    #Set output filename
    fileName, fileExtension = os.path.splitext(photo)
    undistortedImagePath = "".join([fileName,"_fixN",fileExtension])
    
    #Query the Lensfun db for camera parameters
    db = lensfunpy.Database()
    cam = db.find_cameras(cam_maker, cam_model)[0]
    lens = db.find_lenses(cam)[0]

    #TODO: set camera parameters from exif data and lensfun
    focalLength = lens.min_focal #2.5
    aperture = 2.8
    distance = 0

    im = cv2.imread(photo)
    height, width = im.shape[0], im.shape[1]

    mod = lensfunpy.Modifier(lens, cam.crop_factor, width, height)
    mod.initialize(focalLength, aperture, distance)

    undistCoords = mod.apply_geometry_distortion()
    #imUndistorted = cv2.remap(im, undistCoords, None, cv2.INTER_LANCZOS4)
    imUndistorted = cv2.remap(im, undistCoords, None, cv2.INTER_NEAREST)
    #cv2.imwrite(undistortedImagePath, imUndistorted,[int(cv2.IMWRITE_JPEG_QUALITY), 95])
    
    #Change the order of colors to RGB for Pil (Pillow)
    cvRgbImage = cv2.cvtColor(imUndistorted, cv2.COLOR_BGR2RGB)
    pil_im = Image.fromarray(cvRgbImage)

    #update the metadata for the new files
    exif_dict = piexif.load(photo)
    #exif_dict = piexif.load(pil_im.info["exif"])
    
    exif_dict["0th"][piexif.ImageIFD.Model] = "HD2 U"
    exif_dict["0th"][piexif.ImageIFD.Make] = "GoPro"
    exif_dict["Exif"][piexif.ExifIFD.FocalLength] = (250,100)
    #it's actually 21.5 but exif barfs on float
    exif_dict["Exif"][piexif.ExifIFD.FocalLengthIn35mmFilm] = 21
    exif_bytes = piexif.dump(exif_dict)
    
    #Write the file with metadata, 100% or 95%
    pil_im.save(undistortedImagePath, "jpeg", quality=100,exif=exif_bytes)
    #pil_im.save(undistortedImagePath, "jpeg", quality=95)
    #piexif.insert(exif_bytes, undistortedImagePath)
      
def importexif():
    try:
        __import__(piexif)
    except ImportError:
        return False
    else:
        return True

#Import piexif if it's available, probably a better way to do this
#imexif = importexif()

if __name__ == '__main__':

    #sample = "/Pictures/gopro/farm/color/3D_R0971.JPG"
    #undistortedImagePath ="testoutput.JPG"
    #sample = "/redwood/Photos/kite/gopro/2013-06-01-cloverleaf/corrected/multi"
    #directory = "/home/madadh/Pictures/odm/checkercalibration/measure"

    directory = os.curdir
    try:
        os.chdir(directory)
        photos = photolist(directory)
        
        tic=timeit.default_timer()
        #result = process_photos(photos)
        multi_process(photos)
        toc=timeit.default_timer()
        #im = Image.open(sample)
        print(toc-tic)
        
    except Exception as e:
        print(" ".join(["Something failed because of",str(e)]))
