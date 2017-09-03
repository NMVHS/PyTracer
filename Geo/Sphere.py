import math
from Ray import Ray
from Vector import Vector

class Sphere:
	def __init__(self,pos,radius):
		self.pos = pos #pos is a vector
		self.radius = float(radius) #radius is a scalar

	def type(self):
		return "Sphere"

	def getIntersection(self,ray,closestHit,result):
		#result is a list storing calculated data [hit_t, hit_pos,hit_normal]

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

			if t0>0 and t1>0:
				if t0 < t1: #Important!!!! We need the closest t, means the smallest t!!!!!!!!!!!!!
					t = t0
				else:
					t = t1

			if t >= closestHit: #check if this t is behind the closest t detected so far
				return False

			hitPos = ray.origin + ray.dir*t
			hitNormal = (hitPos - self.pos).normalized()

			result.extend([t,hitPos,hitNormal])
			return True