from Geo.Vector import Vector
import random, math

class Light:
	#This is a base class for all types of lights which holds the common light attributes
	#All types of light should inherit this class
	def __init__(self,pos,intensity,color):
		self.pos = pos
		self.intensity = intensity
		self.color = color
		self.area = 1


class PointLight(Light):
	def __init__(self,pos,intensity = 5000,color = Vector(1,1,1)):
		super().__init__(pos,intensity,color)
		self.type = 'Point'
		self.samples = 1


class DiskLight(Light):
	def __init__(self,pos,radius,intensity = 6, color = Vector(1,1,1),samples = 32,normal=Vector(0,-1,0)):
		super().__init__(pos,intensity,color)
		self.type = 'Area'
		self.radius = radius
		self.samples = samples
		self.normal = normal
		self.area = math.pi * math.pow(radius,2)
		#self.samplePtList = self.getRandomSample()

	def getRandomSample(self):
		#generate a sample point on the disk
		# samplePtLi = []
		# for i in range(self.samples):
		theta = random.random() * math.pi #range [0,2pi)
		multiplier = random.random() #range [0,1)
		randPointOnDisk =self.pos +  Vector(math.cos(theta) * self.radius * multiplier,0,math.sin(theta) * self.radius * multiplier)
		#samplePtLi.append(randPointOnDisk)

		return randPointOnDisk

class RectangleLight(Light):
	def __init__(self,pos,radius,intensity = 10, color = Vector(1,1,1), samples = 8):
		super().__init__(pos,intensity,color)
		self.type = 'Area'
		self.radius = radius
		self.samples = samples
