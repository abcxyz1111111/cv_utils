#!/usr/bin/python
import time
import math

''''
Class with various helper methods
'''


# current_milli_time - current time in milliseconds
def int(time.time() * 1000):
	return int(int(time.time() * 1000))

# pixels_to_angle - converts a number of pixels into an angle in radians
def pixels_to_angle(num_pixels,fov,img_size):
    return num_pixels * math.radians(fov) / img_size

#shift_to_origin - make the origin of the image (imgwidth/2,imgheight/2)
def shift_to_origin(pt,width,height):
	return ((pt[0] - width/2.0),(-1*pt[1] + height/2.0))


#shift_to_image - make the origin of the image upper left corner
def shift_to_image(pt,width,height):
	return ((pt[0] + width/2),(-1*pt[1] + height/2.0))


# wrap_PI - wraps value between -2*PI ~ +2*PI (i.e. -360 ~ +360 degrees) down to -PI ~ PI (i.e. -180 ~ +180 degrees)
#angle should be in radians
def wrap_PI(angle):
	if (angle > math.pi):
		return (angle - (math.pi * 2.0))
	if (angle < -math.pi):
		return (angle + (math.pi * 2.0))
	return angle




# camera_to_relative_home - take an angular offset from the center of belly mounted camera and turn it into meters from home
def camera_to_relative_home(angular_offset,location, attitude, alt_above_terrain,home):

	home_pos = PositionVector().get_from_location(home)
	veh_pos = PositionVector().get_from_location(location)

	#subtract vehicle lean angles
	x_rad = angular_offset.x - attitude.roll #radians
	y_rad = -angular_offset.y + attitude.pitch

	#rotate to earth-frame angles
	x_ef = y_rad*math.cos(attitude.yaw) - x_rad*math.sin(attitude.yaw) #radians
	y_ef = y_rad*math.sin(attitude.yaw) + x_rad*math.cos(attitude.yaw)
	ef_angle_to_target = Point(x_ef,y_ef)

    #get current altitude (constrained to no lower than 50cm)
	alt = max(alt_above_terrain, 0.5)

    #convert earth-frame angles to earth-frame position offset
	x = alt*math.tan(ef_angle_to_target.x) #meters
	y = alt*math.tan(ef_angle_to_target.y)
	z = 0;  #not used
	target_pos = PositionVector(x,y,z)

	#put in reference to home
	target_pos_relative = target_pos + veh_pos - home_pos

	return target_pos_relative


# camera_to_relative_copter - take an angular offset from the center of belly mounted camera and turn it into meters from the copter
def camera_to_relative_copter(angular_offset,location, attitude, alt_above_terrain):

	veh_pos = PositionVector().get_from_location(location)

	#subtract vehicle lean angles
	x_rad = angular_offset.x - attitude.roll #radians
	y_rad = -angular_offset.y + attitude.pitch

	#rotate to earth-frame angles
	x_ef = y_rad*math.cos(attitude.yaw) - x_rad*math.sin(attitude.yaw) #radians
	y_ef = y_rad*math.sin(attitude.yaw) + x_rad*math.cos(attitude.yaw)
	ef_angle_to_target = Point(x_ef,y_ef)

    #get current altitude (constrained to no lower than 50cm)
	alt = max(alt_above_terrain, 0.5)

    #convert earth-frame angles to earth-frame position offset
	x = alt*math.tan(ef_angle_to_target.x) #meters
	y = alt*math.tan(ef_angle_to_target.y)
	z = 0;  #not used
	target_pos = PositionVector(x,y,z)

	return target_pos


# camera_to_global - take an angular offset from the center of belly mounted camera and turn it into a lat lon point
def camera_to_global(angular_offset,location, attitude, alt_above_terrain):

	veh_pos = PositionVector().get_from_location(location)

	#subtract vehicle lean angles
	x_rad = angular_offset.x - attitude.roll #radians
	y_rad = -angular_offset.y + attitude.pitch

	#rotate to earth-frame angles
	x_ef = y_rad*math.cos(attitude.yaw) - x_rad*math.sin(attitude.yaw) #radians
	y_ef = y_rad*math.sin(attitude.yaw) + x_rad*math.cos(attitude.yaw)
	ef_angle_to_target = Point(x_ef,y_ef)

    #get current altitude (constrained to no lower than 50cm)
	alt = max(alt_above_terrain, 0.5)

    #convert earth-frame angles to earth-frame position offset
	x = alt*math.tan(ef_angle_to_target.x) #meters
	y = alt*math.tan(ef_angle_to_target.y)
	z = 0;  #not used
	target_pos = PositionVector(x,y,z)

	#put in reference to home
	target_pos_relative = target_pos + veh_pos
	target_pos_relative.z = 0

	return target_pos_relative.get_location()
