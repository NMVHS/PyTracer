from Geo.Vector import Vector

class Camera:
	def __init__(self,pos,direction,angle,exposure=1):
		self.pos = pos
		self.dir = direction
		self.angle = float(angle)#angle of view , input is degree, convert to radians while using
		self.exposure = exposure
