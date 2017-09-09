class Light:
	#by default, this is a disk light
	def __init__(self,pos,radius):
		self.pos = pos
		self.radius = float(radius)

	def getIntersection(self,ray,closestHit,result):
		pass