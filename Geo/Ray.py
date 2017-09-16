
class Ray:

	def __init__(self,origin,dir):
		self.origin = origin
		self.dir = dir.normalized()

	def __str__(self):
		return "Ray"+ str(self.dir)
