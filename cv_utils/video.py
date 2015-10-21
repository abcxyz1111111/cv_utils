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
        '''
        #get camera distortion matrix and intrinsics. Defaults: logitech c920
        mtx = np.array([[ 614.01269552,0,315.00073982],
                        [ 0,614.43556296,237.14926858],
                        [ 0,0,1.0]])
        dist = np.array([0.12269303, -0.26618881,0.00129035, 0.00081791,0.17005303])

        self.matrix  = VN_config.get_array('camera','matrix', mtx)
        self.distortion = VN_config.get_array('camera', 'distortion', dist)


        '''
        self.img_width = 1280
        self.img_height= 720

        self.matrix = np.array([[764.17228563, 0.0, 676.22364905],
                         [0.0, 766.63752673, 349.10277454],
                         [0.0, 0.0, 1.0]])
        self.distortion = np.array([[-0.26516979,  0.00344694,  0.00081852, -0.00055108,  0.1954367 ]])

        self.newcameramtx, self.roi=cv2.getOptimalNewCameraMatrix(self.matrix,self.distortion,(self.img_width,self.img_height),1,(self.img_width,self.img_height))


        #create a camera object
        self.camera = None

        # background image processing variables
        self.background_capture = background_cap #does the user want to capture images in the background
        self.proc = None              # background process object
        self.parent_conn = None       # parent end of communicatoin pipe



    # get_camera - initialises camera and returns VideoCapture object
    def get_camera(self,src="0"):
        if self.camera is not None:
            return self.camera
        else:
            print 'Starting Camera....'

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
        self.start_capture()

        #did we start background capture
        print 'Background capture {0}'.format(self.background_capture)

        while True:
            # send request to image capture for image
            ret, img = self.get_image()
            # check image is valid
            if img is not None:
                #undistort image
                img = self.undisort_image(img)
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
