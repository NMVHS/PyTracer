import math
from Geo.Geometry import Geometry
from Geo.Material import Material

class Sphere(Geometry):
	def __init__(self,pos,radius,material=Material()):
		super().__init__(material)
		self.pos = pos #pos is a vector
		self.radius = float(radius) #radius is a scalar
		self.epsilon = 0.0001

	def type(self):
		return "Sphere"

	def getIntersection(self,ray,closestHit,result):
		#result is a list storing calculated data [hit_t, hit_pos,hit_normal]
		#the input result might already contain a hit_t

		#testing delta ----- b^2 - 4ac >=0
		a = 1 #ray.dir.dot(ray.dir)
		b = 2*ray.dir.dot(ray.origin - self.pos)
		c = (ray.origin - self.pos).sqr() - math.pow(self.radius,2)

		delta = b*b - 4*a*c

		if delta < 0:
			return False
		else:
			t0 = (-b + math.sqrt(delta)) / (2*a)
			t1 = (-b - math.sqrt(delta)) / (2*a)

			if t0>0 and t1>0: #root has to be positive, otherwise it's behind the ray origin
				if t0 < t1: #Important!!!! We need the closest t, means the smallest t!!!!!!!!!!!!!
					t = t0
				else:
					t = t1

				if t >= closestHit: #check if this t is behind the closest t detected so far
					return False
			elif t0 > 0 and t1 <= 0:
				t = t0
			elif t1 > 0 and t0 <= 0:
				t = t1
			else:
				return False


			hitPos = ray.origin + ray.dir*t
			hitNormal = (hitPos - self.pos).normalized()

			result.extend([t,hitPos,hitNormal,self.objectId])
			return True
