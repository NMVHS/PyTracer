import math
from Geo.Geometry import Geometry
from Geo.Material import Material
from Geo.Vector import Vector

class Plane(Geometry):
	def __init__(self,pos,normal,w=None,h=None,material=Material()):
		super().__init__(material)
		self.type = "InfinitePlane"
		if w != None and h != None:
			#FinitePlane
			self.Type = "Plane"
			self.width = w
			self.height = h
			self.p0 = pos + Vector(w/2,0,h/2)
			self.p1 = pos + Vector(-w/2,0,h/2)
			self.p2 = pos + Vector(-w/2,0,-h/2)
			self.p3 = pos + Vector(w/2,0,-h/2)

		self.pos = pos
		self.normal = normal
		self.epsilon = 0.0001

	def type(self):
		return self.type

	def getIntersection(self,ray,closestHit,result):
		#t = (anyplanePoint - ray.origin).dot(plane.normal) / (ray.dir.dot(plane.normal))
		if ray.dir.dot(self.normal) >= 0: #ray hits the back side of the plane/ parallel
			return False

		t = (self.pos - ray.origin).dot(self.normal) / (ray.dir.dot(self.normal))

		if t < 0 or t >= closestHit:
			return False

		hitPos = ray.origin + ray.dir*t
		hitNormal = self.normal

		result.extend([t,hitPos,hitNormal,self.objectId])

		return True
