import math

class Point(object):
	def __init__(self, x = None, y = None, tup = None):
		if tup is not None:
			self.x = tup[0]
			self.y = tup[1]
		else:
			self.x = x
			self.y = y

	def distance_to(self,other):
		return math.sqrt(math.pow(self.x - other.x,2)+ math.pow(self.y - other.y,2))

	def angle_to(self,other):
		#image coordinates
		diff_x = other.x - self.x
		diff_y = self.y -other.y
		return math.atan2(diff_x,diff_y) #NED coordinates

	def tuple(self):
		return (self.x,self.y)

	def int(self):
		self.x = int(self.x)
		self.y = int(self.y)

	def float(self):
		self.x *= 1.0
		self.y *= 1.0

	def __add__(self,other):
		return Point(self.x + other.x, self.y + other.y)

	def __sub__(self,other):
		return Point(self.x - other.x, self.y - other.y)

	def __mul__(self,scalar):
		return Point(self.x * scalar, self.y * scalar)

	def __div__(self,scalar):
		return Point(self.x / scalar, self.y / scalar)

	def __getattr__(self,k):
		if k == 0:
			return x
		if k == 1:
			return y
		raise AttributeError


	def __str__(self):
		return "({0}, {1})".format(self.x,self.y)



class Point3(object):
	def __init__(self, x = None, y = None, z = None, tup = None):
		if tup is not None:
			self.x = tup[0]
			self.y = tup[1]
			self.z = tup[2]
		else:
			self.x = x
			self.y = y
			self.z = z

	def distance_to(self,other):
		return math.sqrt(math.pow(self.x - other.x,2)+ math.pow(self.y - other.y,2) + math.pow(self.z - other.z,2))

	def tuple(self):
		return (self.x,self.y,self.z)

	def __add__(self,other):
		return Point(self.x + other.x, self.y + other.y, self.z + other.z)

	def __sub__(self,other):
		return Point(self.x - other.x, self.y - other.y, self.z - other.z)

	def __getattr__(self,k):
		if k == 0:
			return x
		if k == 1:
			return y
		if k == 2:
			return z
		raise AttributeError

	def __str__(self):
		return "({0}, {1})".format(self.x,self.y)
