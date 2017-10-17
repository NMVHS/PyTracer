import random, math
from Geo.Vector import Vector

class Camera:
	def __init__(self,pos,direction,focalLength,filmH=36,filmV=36,filmFit="Horizontal",
				exposure=1,aperture=4,focusDist=136):
		self.pos = pos
		self.dir = direction
		self.focalLength = focalLength #unit mm
		self.filmH = filmH
		self.filmV = filmV
		self.angleOfViewH = 2 * math.atan(filmH/(2*self.focalLength)) #angle of view , in radians
		self.angleOfViewV = 2 * math.atan(filmV/(2*self.focalLength))
		self.filmFit = filmFit #Options: Horizontal,Vertical, Fill
		self.exposure = exposure
		self.aperture = aperture #Aperture is the f-number 1.4,2.8 etc
		self.focusDist = focusDist
		self.pupilDiameter = self.focalLength / self.aperture

	def getRandomPointOnLens(self):
		theta = random.random() * 2 * math.pi #[0,2pi)
		multiplier =  1 - random.random()  #range (0,1]
		randPointOnLens =self.pos +  Vector(math.cos(theta) * self.pupilDiameter* 0.5 * multiplier,math.sin(theta) * self.pupilDiameter * 0.5 * multiplier,0)

		return randPointOnLens
