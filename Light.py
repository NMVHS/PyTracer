from Geo.Vector import Vector

class Light:
	#by default, this is a disk light
	def __init__(self,pos,radius,intensity = 3000, color = Vector(1,1,1)):
		self.pos = pos
		self.radius = float(radius)
		self.intensity = intensity
		self.color = color

	def getIntersection(self,ray,closestHit,result):
		pass
