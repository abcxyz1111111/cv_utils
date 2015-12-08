#!/usr/bin/python
#SYSTEM IMPORTS
import sys
from os.path import expanduser
import time
import math
import multiprocessing
import cv2
import numpy as np


"""
video.py
This file includes functions to:
    Initialise the camera
"""

'''
TODO:
Fix camera distortion stuff: How to pass in distortion matrix and image size????
'''


class Video:

    def __init__(self,source = "0",background_cap = False):

        # get which camera we will use
        self.camera_source = source

        #create a camera object
        self.camera = None

        # background image processing variables
        self.background_capture = background_cap #does the user want to capture images in the background
        self.proc = None              # background process object
        self.parent_conn = None       # parent end of communicatoin pipe



    # get_camera - initialises camera and returns VideoCapture object
    def get_camera(self,src="0"):
        print 'Starting Camera:', src

        if self.camera is not None:
            return self.camera
        else:
            #setup generic video capture device
            try:
                self.camera = cv2.VideoCapture(int(src))
            except ValueError:
                self.camera = cv2.VideoCapture(src)

            # check we can connect to camera
            if not self.camera.isOpened():
                print "failed to open camera, exiting!"
                sys.exit(0)

            print 'Camera Open!'

            return self.camera

    # set_camera - use non_opencv video device
    def set_camera(self,camera):
        # check we can connect to camera
        if not camera.isOpened():
            print "failed to open camera, exiting!"
            sys.exit(0)
        else:
            self.camera = camera
        print 'Camera Open!'

    #
    # background image processing routines
    #

    # image_capture_background - captures all images from the camera in the background and returning the latest image via the pipe when the parent requests it
    def image_capture_background(self, imgcap_connection):
        # exit immediately if imgcap_connection is invalid
        if imgcap_connection is None:
            print "image_capture failed because pipe is uninitialised"
            return

        # clear latest image
        latest_image = None

        while True:
            # constantly get the image from the webcam
            success_flag, image=self.camera.read()

            # if successful overwrite our latest image
            if success_flag:
                latest_image = image

            # check if the parent wants the image
            if imgcap_connection.poll():
                recv_obj = imgcap_connection.recv()
                # if -1 is received we exit
                if recv_obj == -1:
                    break

                # otherwise we return the latest image
                imgcap_connection.send((success_flag,latest_image))

        # release camera when exiting
        self.camera.release()


    def stop_capture(self):
        #Clean up when exitting background capture
        if(self.background_capture):
            # send exit command to image capture process
            self.parent_conn.send(-1)

            # join process
            self.proc.join()
        #no clean up required with regular capture

    def start_capture(self):
        #make sure a camera is intialized
        if self.camera is None:
            self.get_camera(self.camera_source)

        #background capture is desired
        if self.background_capture:

            # create pipe
            self.parent_conn, imgcap_conn = multiprocessing.Pipe()

            # create and start the sub process and pass it it's end of the pipe
            self.proc = multiprocessing.Process(target=self.image_capture_background, args=(imgcap_conn,))
            self.proc.daemon = True
            self.proc.start()


    # get_image - returns latest image from the camera captured from the background process
    def get_image(self):
        #grab image from pipe of background capture
        if(self.background_capture):
            # return immediately if pipe is not initialised
            if self.parent_conn == None:
                return None

            # send request to image capture for image
            self.parent_conn.send(0)

            # wait endlessly until image is returned
            success_flag, img = self.parent_conn.recv()

        #use standard image cap
        else:
            #Grab an image
            success_flag, img = self.camera.read()

        # return image to caller
        return success_flag,img

    # main - tests SmartCameraVideo class
    def main(self):

        self.start_capture()

        #did we start background capture
        print 'Background capture {0}'.format(self.background_capture)

        while True:
            # send request to image capture for image
            ret, img = self.get_image()
            # check image is valid
            if img is not None:
                # display image
                cv2.imshow ('image_display', img)
            else:
                print "no image"

            # check for ESC key being pressed
            k = cv2.waitKey(5) & 0xFF
            if k == 27:
                break

            # take a rest for a bit
            time.sleep(0.1)

        # send exit command to image capture process
        self.stop_capture()

if __name__ == "__main__":
    video = Video()
    video.main()
