#!/usr/bin/python
import time
import math
import numpy as np
import cv2
from dataTypes import *
from position_vector import PositionVector

''''
Class with various helper methods
'''

# crop an image at a specific location.  Center is the center of the image, size is width/height, origin is the upper left of the image
def roi(img,center,size):

    #full image
    (height, width) = img.shape

    #crop image
    x0 = max(center.x - size.x/2,0)
    x1 = min(center.x + size.x/2,width)
    y0 = max(center.y - size.y/2,0)
    y1 = min(center.y + size.y/2,height)

    roi = img[y0:y1, x0:x1]
    origin = Point(center.x-size.x/2,center.y-size.y/2)

    return roi, origin

#balance - improve contrast and adjust brightness in image
#Created By: Tobias Shapinsky
def balance(orig,min_range,res_reduction):

    img = np.copy(orig)
    #get min, max and range of image
    min_v = np.percentile(img,5)
    max_v = np.percentile(img,95)

    #clip extremes
    img.clip(min_v,max_v, img)

    #scale image so that brightest pixel is 255 and darkest is 0
    range_v = max_v - min_v
    if(range_v > min_range):
        img -= min_v
        img *= (255.0/(range_v))
        '''
        img /= res_reduction
        img *= res_reduction
        '''
        return img
    else:
        return np.zeros((img.shape[0],img.shape[1]), np.uint8)

def auto_canny(image, sigma=0.33):
    # compute the median of the single channel pixel intensities
    v = np.median(image)

    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)

    # return the edged image
    return edged

#add_stats - adds a text to the image
def add_stats(img, text,x0,y0):

    font = cv2.FONT_HERSHEY_SIMPLEX
    dy = 15
    for i, line in enumerate(text.split('\n')):
        y = y0 + i*dy
        cv2.putText(img,line,(x0,y), font, 0.45,(255,255,255),1)
    return img

# pip - picture in picture. Specify location/corner and size/scale
def pip(main, sub, location = None, size = None, scale = None, corner = None):
    pass
