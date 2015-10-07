#!/usr/bin/python
#SYSTEM IMPORTS
import logging
import sys
import os
import cv2
import time

#COMMOM IMPORTS
from config import config
from ImageRW import ImageWriter

#TODO allow images to be displayed over webserver and possibly print statements

#list of loggers open
loggers = []

#get an logger by name
def get_logger(name = None):
	#return first logger
	if name is None:
		return loggers[0]
	#return logger by name
	for loggr in loggers:
		if loggr.name == name:
			return loggr
	#no logger found
	return None


class Logger(object):

	#level enumerations: text
	#general - logs/prints inforamtion about program activities(starting processes, camera failure, mode change, errors)
	GENERAL = 'general'
	#aircraft - logs/prints information coming from autopilot
	AIRCRAFT = 'aircraft'
	#algorithm - logs/prints information returned by image processing algorithm
	ALGORITHM = 'algorithm'
	#performance - logs/prints performance of the program
	PERFORMANCE = 'performance'
	#debug - logs/prints temporary messages to be used while developing
	DEBUG = 'debug'

	#level enumeration: image
	#raw - record/display raw video from camera
	RAW = 'raw'
	#gui - record/display raw video overlayed with a gui
	GUI = 'gui'

	####Other enumerations made be added as necessary. These are just the defaults


	def __init__(self,name,location,width = 640, height=480):
		#create sub driectory for logs and videos

		self.location = location.replace("~/", "os.environ['HOME']")


		path = self.location + 'logs'
		if not os.path.exists(path):
		    os.makedirs(path)
		path = self.location + 'vids'
		if not os.path.exists(path):
		    os.makedirs(path)

		#set default startegy name
		self.name = name

		# get image resolution
		self.img_width = 640
		self.img_height = 480

		#####TEXT LOGGING######
		#levels = 'debug' , 'general' , 'aircraft' , 'algorithm' , ' performance'
		#multiple message levels can be selected by concatination strings i.e. 'debug, aircraft'
		#what type of messages we print to the terminal
		self.print_level = 'debug, general'
		#what type of messages we log to a file
		self.log_level = 'aircraft, algorithm, general'


		#####VIDEO RECORDING######
		#levels = 'frame' , 'gui'
		#multiple message levels can be selected at once by concatination strings i.e. 'frame, gui'
		#what type of images we display on the screen
		self.display_level =  'raw, gui'
		#what type of images we record
		self.record_level = 'raw'
		#Write a video or individual images
		self.record_type = 'video'

		#Note about useful logging practices:
			#Inorder to replay a flight through the program log_level must include 'aircraft' and 'algorithm'
			#record level must include 'frame'
			#all other logging levels are for user diagnostics

		#a list of video writers and their tag
		self.video_writers = []

		#text logger
		self.logger = None

		#append to list of loggers
		logger.append(self)

	#set_name - give the logger a name. Helps when creating and understanding file names
	def set_name(self, name):
		#define the name of the current strategy
		self.name = name

	def set_print_level(self,level):
		self.print_level = level

	def set_log_level(self,level):
		self.log_level = level

	def set_display_level(self,level):
		self.display_level = level

	def set_record_level(self,level):
		self.record_level = level

	def set_record_type(self,typ):
		self.record_type = typ


	#image - records/displays an image with the provided level
	def image(self, level, img):
		#display frame
		if(self.display_level.find(level) != -1):
			#show image
			cv2.imshow(level, img)
			#end program with esc key
			k = cv2.waitKey(1) & 0xFF
			if k == 27:
				cv2.destroyAllWindows()
				self.text(self.GENERAL, "User terminated Program")
				sys.exit(0)

		#record frame
		if(self.record_level.find(level) != -1):
			writer = self.get_video_writer(level)
			writer.write(img)


	#text - logs/prints a message with the provided level
	def text(self, level, msg):
		#print text
		if(self.print_level.find(level) != -1):
			print msg

		#log text
		if(self.log_level.find(level) != -1):

			#open a logger if necessary
			if(self.logger is None):
				self.open_text_logger()


			#log text
			self.logger.info(msg , extra={'type': level})



	#open_video_writer- opens a video writer with a filename that starts the tag. The rest of the file name is date-time
	def open_video_writer(self, tag):

		#define filename
		file_index = 0
		filename = self.location + 'vids/{0}-{1}-{2}'.format(self.name, tag,file_index)
		while os.path.exists(filename):
			file_index = file_index + 1
			filename = self.location + 'vids/{0}-{1}-{2}'.format(self.name, tag,file_index)


		# Define the codec and create VideoWriter object
		video_writer = None
		if self.record_type == "video":
			ex = int(cv2.cv.CV_FOURCC('M','J','P','G'))
			video_writer = cv2.VideoWriter(filename + '.avi', ex, 15, (self.img_width,self.img_height))
		elif self.record_type == 'image':
			video_writer = ImageWriter(filename)


		#add the video writer to a list of video writers
		self.video_writers.append((tag,video_writer))

		#return the writer
		return video_writer

	#get_video_writer- retreives a videowriter assocaited with a certain tag
	def get_video_writer(self,tag):
		#look for video writer
		for writer in self.video_writers:
			if(writer[0] == tag):
				return writer[1]

		#if it doesn't exist, open one
		return self.open_video_writer(tag)



	#open_text_logger - create an instance of 'logging' and
	def open_text_logger(self):

		#create logger
		self.logger = logging.getLogger('logger')
		self.logger.setLevel(logging.INFO)


		#define filename
		file_index = 0
		filename = self.location + 'logs/{0}-{1}.log'.format(self.name,file_index)
		while os.path.exists(filename):
			file_index = file_index + 1
			filename = self.location + 'logs/{0}-{1}.log'.format(self.name,file_index)

		# add a file handler
		fh = logging.FileHandler(filename)
		fh.setLevel(logging.INFO)
		# create a formatter and set the formatter for the handler.
		frmt = logging.Formatter('%(asctime)s - %(type)s - %(message)s')
		fh.setFormatter(frmt)
		# add the Handler to the logger
		self.logger.addHandler(fh)
		self.logger.propagate = False



if __name__ == '__main__':
	'''
	VN_logger.set_name('test')

	#test text logger
	VN_logger.text(VN_logger.DEBUG,"This is should appear in the terminal")
	VN_logger.text(VN_logger.AIRCRAFT, "This should appear in the file")
	VN_logger.text(VN_logger.GENERAL, "This should appear in both")
	VN_logger.text(VN_logger.PERFORMANCE, "This should not appear at all")

	#test video logger
	#create images
	import numpy as np
	green_image = np.zeros((VN_logger.img_height,VN_logger.img_width,3), np.uint8)
	green_image[:] = (0,255,0)
	blue_image = np.zeros((VN_logger.img_height,VN_logger.img_width,3), np.uint8)
	blue_image[:] = (255,0,0)


	for x in range(0, 45):
		time.sleep(66.6/1000)
		#Display a green and blue image for 3 seconds
		#Save a 3 second video of the blue image
		VN_logger.image(VN_logger.RAW, blue_image)
		VN_logger.image(VN_logger.GUI, green_image)
	'''
