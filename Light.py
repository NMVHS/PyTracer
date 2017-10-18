from Geo.Vector import Vector
from Geo.Disk import Disk
import random, math

class Light:
	#This is a base class for all types of lights which holds the common light attributes
	#All types of light should inherit this class
	def __init__(self,pos,intensity,color):
		self.pos = pos
		self.intensity = intensity
		self.color = color
		self.area = 1
		self.type = "Light"

class PointLight(Light):
	def __init__(self,pos,intensity = 5000,color = Vector(1,1,1)):
		super().__init__(pos,intensity,color)
		self.type = "Point" + self.type
		self.samples = 1

class DiskLight(Light,Disk):
	def __init__(self,pos,radius,intensity = 6, color = Vector(1,1,1),samples = 8,normal=Vector(0,-1,0),isDoubleSided=False,visible=True):
		Disk.__init__(self,pos,radius,normal)
		Light.__init__(self,pos,intensity,color)
		self.type = "AreaLight_Disk"
		self.radius = radius
		self.samples = samples
		self.normal = normal
		self.isDoubleSided = isDoubleSided
		self.visible = visible
		self.area = math.pi * math.pow(radius,2)
		#self.samplePtList = self.getRandomSample()

	def getRandomSample(self):
		#generate a sample point on the disk
		# samplePtLi = []
		# for i in range(self.samples):
		theta = random.random() * 2 * math.pi #range [0,2pi)
		u = random.random() + random.random()
		#Better sampling method
		if u > 1:
			multiplier =  2 - u
		else:
			multiplier =  u
			
		randPointOnDisk =self.pos +  Vector(math.cos(theta) * self.radius * multiplier,0,math.sin(theta) * self.radius * multiplier)
		#samplePtLi.append(randPointOnDisk)

		return randPointOnDisk

class RectangleLight(Light):
	def __init__(self,pos,radius,intensity = 10, color = Vector(1,1,1), samples = 8):
		super().__init__(pos,intensity,color)
		self.type = "AreaLight_Rectangle"
		self.radius = radius
		self.samples = samples
