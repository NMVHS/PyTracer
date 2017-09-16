import math
from Geometry import Geometry

class Plane(Geometry):
	def __init__(self,pos,size,normal):
		Geometry.__init__(self)
		self.pos = pos
		self.size = size
		self.normal = normal
		self.epsilon = 0.0001

	def type(self):
		return "Plane"

	def getIntersection(self,ray,closestHit,result):
		#t = (anyplanePoint - ray.origin).dot(plane.normal) / (ray.dir.dot(plane.normal))
		if ray.dir.dot(self.normal) >= 0: #ray hits the back side of the plane/ parallel
			return False

		t = (self.pos - ray.origin).dot(self.normal) / (ray.dir.dot(self.normal))

		if t < 0 or t >= closestHit:
			return False

		hitPos = ray.origin + ray.dir*t
		hitNormal = self.normal

		result.extend([t,hitPos,hitNormal])

		return True
