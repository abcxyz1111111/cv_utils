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
    Initialise the output video
"""

'''
TODO:
Fix camera distortion stuff: How to pass in distortion matrix and image size????
'''


class Video:

    def __init__(self,index = 0,background_cap = False):

        # get which camera we will use
        self.camera_index = index
        '''
        #get camera distortion matrix and intrinsics. Defaults: logitech c920
        mtx = np.array([[ 614.01269552,0,315.00073982],
                        [ 0,614.43556296,237.14926858],
                        [ 0,0,1.0]])
        dist = np.array([0.12269303, -0.26618881,0.00129035, 0.00081791,0.17005303])

        self.matrix  = VN_config.get_array('camera','matrix', mtx)
        self.distortion = VN_config.get_array('camera', 'distortion', dist)

        self.newcameramtx, self.roi=cv2.getOptimalNewCameraMatrix(self.matrix,self.distortion,(self.img_width,self.img_height),1,(self.img_width,self.img_height))
        '''

        #create a camera object
        self.camera = None

        #does the user want to capture images in the background
        self.background_capture = background_cap

        # background image processing variables
        self.proc = None              # background process object
        self.parent_conn = None       # parent end of communicatoin pipe
        self.is_backgroundCap = False #state variable for background capture



    # get_camera - initialises camera and returns VideoCapture object
    def get_camera(self,index=0):
        if self.camera is not None:
            return self.camera
        else:
            #generic video capture device
            self.camera = cv2.VideoCapture(index)

            if not self.camera.isOpened():
                print "failed to open camera, exiting!"
                sys.exit(0)
            return self.camera

    # set_camera - use an already existing camera or non-opencv source for the image
    def set_camera(self,cam):
        self.camera = cam
        if not self.camera.isOpened():
            print "failed to open camera, exiting!"
            sys.exit(0)


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
            # check if the parent wants kill the process
            if imgcap_connection.poll():
                recv_obj = imgcap_connection.recv()
                # if -1 is received we exit
                if recv_obj == -1:
                    break

            # constantly get the image from the webcam
            imgcap_connection.send(self.camera.read())

        # release camera when exiting
        self.camera.release()


    def stop_capture(self):
        #Clean up when exitting background capture
        if(self.is_backgroundCap):
            # send exit command to image capture process
            self.parent_conn.send(-1)

            # join process
            self.proc.join()
        #no clean up required with regular capture

    def start_capture(self,index = 0):
        #make sure a camera is intialized
        if self.camera is None:
            print "Opening Camera"
            self.get_camera(index)
        print "Camera open!"

        #background capture is desired
        if self.background_capture:
            #if we have more than one core available, then start background capture
            if(self.cores_available > 1):

                # create pipe
                self.parent_conn, imgcap_conn = multiprocessing.Pipe()

                # create and start the sub process and pass it it's end of the pipe
                self.proc = multiprocessing.Process(target=self.image_capture_background, args=(imgcap_conn,))
                self.proc.daemon = True
                self.proc.start()

                #Mark that we are in background capture mode
                self.is_backgroundCap = True
        else:
            #Not enough cores for background capture or just doing regular capture
            self.is_backgroundCap = False


    # get_image - returns latest image from the camera captured from the background process
    def get_image(self):

        #grab image from pipe of background capture
        if(self.is_backgroundCap):
            # return immediately if pipe is not initialised
            if self.parent_conn == None:
                return None

            if self.is_image_available():
                # grab image
                return self.parent_conn.recv()
            else:
                return False, None

        #use standard image cap
        return self.camera.read()

    # is_image_available - Return if an image is ready from background capture
    def is_image_available(self):
        if self.background_capture:
            #check to see if a process has finished and sent data
		    return self.parent_conn.poll()
        return True

    #undisort_image- removes any distortion caused by the camera lense
    def undisort_image(self,frame):
        #undistort
        dst = cv2.undistort(frame, self.matrix, self.distortion, None, self.newcameramtx)

        # crop the image
        x,y,w,h = self.roi
        dst = dst[y:y+h, x:x+w]

        return dst

    # main - tests SmartCameraVideo class
    def main(self):
        #open a camera
        #self.get_camera(0)

        # start background process
        self.start_capture(self.camera_index)

        #did we start background capture
        print 'Background capture {0}'.format(self.is_backgroundCap)

        while True:
            # send request to image capture for image
            img = self.get_image()

            #undistort image
            #img = self.undisort_image(img)

            # check image is valid
            if not img is None:
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
