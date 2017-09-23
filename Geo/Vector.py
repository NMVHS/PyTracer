import math
import numpy as np

class Vector:

	def __init__(self,x,y,z):
		self.x = float(x)
		self.y = float(y)
		self.z = float(z)
		self.value = (self.x,self.y,self.z)

	def __str__(self):
		return 'Vector'+str(self.value)

	def __add__(self,other):
		return Vector(self.x + other.x,self.y + other.y,self.z + other.z)

	def __sub__(self,other):
		return Vector(self.x - other.x,self.y - other.y,self.z - other.z)

	def __mul__(self,other):
		return Vector(self.x * float(other),self.y * float(other), self.z * float(other))

	def __truediv__(self,other):
		return Vector(self.x /other, self.y/other, self.z/other)

	def length(self):
		return math.sqrt(math.pow(self.x,2) + math.pow(self.y,2) + math.pow(self.z,2))

	def normalized(self):
		return self/self.length()

	def dot(self,other):
		return self.x * other.x + self.y * other.y + self.z * other.z

	def cross(self,other):
		return Vector(self.y*other.z - self.z*other.y,
					  self.z*other.x - self.x*other.z,
					  self.x*other.y - self.y*other.x)

	def sqr(self):
		return self.dot(self)

	def colorMult(self,other):
		return Vector(self.x * other.x, self.y * other.y, self.z * other.z)

	def rot(self,axis,angle,axisVec=None):
		#input angle is in radians, axisVec has to be a unit vector
		vectorArray = np.array([self.x,self.y,self.z])

		cosA = math.cos(angle)
		sinA = math.sin(angle)


		if axisVec == None:
			rotXMatrix = np.array([[1,0,0],
								  [0,cosA,sinA],
								  [0,-sinA,cosA]])

			rotYMatrix = np.array([[cosA,0,-sinA],
								  [0,1,0],
								  [sinA,0,cosA]])

			rotZMatrix = np.array([[cosA,sinA,0],
								  [-sinA,cosA,0],
								  [0,0,1]])

			rotMatrix = {"X":rotXMatrix,"Z":rotZMatrix,"Y":rotYMatrix}
			result = vectorArray.dot(rotMatrix[axis])

		else:
			Vx = axisVec.x
			Vy = axisVec.y
			Vz = axisVec.z
		    #arbitrary
			rotAMatrix = np.array([[cosA+math.pow(Vx,2)*(1-cosA),Vx*Vy*(1-cosA)+Vz*sinA,Vx*Vz*(1-cosA)-Vy*sinA],
									[Vy*Vx*(1-cosA)-Vz*sinA,cosA+math.pow(Vy,2)*(1-cosA),Vy*Vz*(1-cosA)+Vx*sinA],
									[Vz*Vx*(1-cosA)+Vy*sinA,Vz*Vy*(1-cosA)-Vx*sinA,cosA+math.pow(Vz,2)*(1-cosA)]])

			result = vectorArray.dot(rotAMatrix)


		return Vector(result[0],result[1],result[2])
