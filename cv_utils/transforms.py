#!/usr/bin/python
import time
import math

''''
Class with various transformation methods
'''

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

# earthframe_rad_to_relative_home - take an earth frame angle to target(gimbal mounted camera) and turn it into meters from home
def earthframe_rad_to_relative_home(ef_angle_to_target,location,home,alt_above_terrain = None):

	home_pos = PositionVector().get_from_location(home)
	veh_pos = PositionVector().get_from_location(location)

    #get current altitude (constrained to no lower than 50cm)
	if alt_above_terrain is None:
        alt_above_terrain = location.alt
	alt = max(alt_above_terrain, 0.5)

    #convert earth-frame angles to earth-frame position offset
	x = alt*math.tan(ef_angle_to_target.x) #meters
	y = alt*math.tan(ef_angle_to_target.y)
	z = 0  #not used
	target_pos = PositionVector(x,y,z)

	#put in reference to home
	target_pos_relative = target_pos + veh_pos - home_pos

	return target_pos_relative


# earthframe_rad_relative_copter - take an earth frame angle to target(gimbal mounted camera) and turn it into meters from the copter
def earthframe_rad_to_relative_copter(ef_angle_to_target, location, alt_above_terrain = None):

	veh_pos = PositionVector().get_from_location(location)

    #get current altitude (constrained to no lower than 50cm)
	if alt_above_terrain is None:
        alt_above_terrain = location.alt
	alt = max(alt_above_terrain, 0.5)

    #convert earth-frame angles to earth-frame position offset
	x = alt*math.tan(ef_angle_to_target.x) #meters
	y = alt*math.tan(ef_angle_to_target.y)
	z = 0  #not used
	target_pos = PositionVector(x,y,z)

	return target_pos


# earthframe_rad_to_global - take an earth frame angle to target(gimbal mounted camera) and turn it into a lat lon point
def earthframe_rad_to_global(ef_angle_to_target, location, alt_above_terrain = None):

	veh_pos = PositionVector().get_from_location(location)

    #get current altitude (constrained to no lower than 50cm)
    if alt_above_terrain is None:
        alt_above_terrain = location.alt
	alt = max(alt_above_terrain, 0.5)


    #convert earth-frame angles to earth-frame position offset
	x = alt*math.tan(ef_angle_to_target.x) #meters
	y = alt*math.tan(ef_angle_to_target.y)
	z = 0  #not used
	target_pos = PositionVector(x,y,z)

	#put in reference to home
	target_pos_relative = target_pos + veh_pos
	target_pos_relative.z = 0

	return target_pos_relative.get_location()


# adjust a hardmount angle for tilt and heading of the vehicle body
def bodyframe_to_earthframe(self,angular_offset, attitude, ignore_tilt = False):

    x_rad = angular_offset.x
    y_rad = -angular_offset.y

    if not ignore_tilt:
        x_rad -= attitude.roll #radians
        y_rad += attitude.pitch

    #rotate to earth-frame angles
    x_ef = y_rad*math.cos(attitude.yaw) - x_rad*math.sin(attitude.yaw) #radians
    y_ef = y_rad*math.sin(attitude.yaw) + x_rad*math.cos(attitude.yaw)
    ef_angle_to_target = (x_ef,y_ef)

    return ef_angle_to_target
