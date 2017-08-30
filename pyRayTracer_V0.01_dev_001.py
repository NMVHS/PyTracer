#python ray tracing implementation challenge
#written from scratch!
#shawn / Aug 2017
#-------------------------
#Some stuff can be easily missing:
#1. keep in mind when using tan/cos/sin, use radians not degrees

#-------------------------

import sys, math, random
from PyQt5.QtWidgets import QApplication, QWidget, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem
from PyQt5.QtGui import QImage, QPixmap, QColor

#------------------------
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

class Ray:

	def __init__(self,origin,dir):
		self.origin = origin 
		self.dir = dir.normalized()

	def __str__(self):
		return "Ray"+ str(self.dir)

class Sphere:
	def __init__(self,pos,radius):
		self.pos = pos #pos is a vector
		self.radius = float(radius) #radius is a scalar

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
				if t0>=t1:
					t = t0
				else:
					t = t1

			if t >= closestHit:
				return False

			hitPos = ray.origin + ray.dir*t
			hitNormal = (hitPos - self.pos).normalized()

			result.extend([t,hitPos,hitNormal])
			return True


class SphereList:
	def __init__(self,spheres):
		self.spheres = spheres #a list of spheres

	def getClosestIntersection(self,ray,result):
		hitBool = False
		closestHit = 1000000000000
		closestHitResult = []
		for i in range(0,len(self.spheres)):
			if self.spheres[i].getIntersection(ray,closestHit,result):
				hitBool = True
				closestHit = result[0] #closest t
				closestHitResult.clear()
				closestHitResult.extend(result)
				result.clear()

		result.extend(closestHitResult)
		return hitBool


class Camera:
	def __init__(self,pos,direction,angle):
		self.pos = pos
		self.dir = direction
		self.angle = float(angle)#angle of view , input is degree, convert to radians while using

class Light:
	#by default, this is a disk light
	def __init__(self,pos,radius):
		self.pos = pos
		self.radius = float(radius)

def getColor(hit,hitResult):
	#hit is bool,
	if hit == True:

		remapHitNormal = (hitResult[2]+Vector(1,1,1))*0.5
		return Vector(255*remapHitNormal.x,255*remapHitNormal.y,255*remapHitNormal.z)
	else:
		return Vector(0,0,0)
		
		
def main():
	#-------canvas size-----
	width = 600
	height = 600

	#-------ui initialization-------
	app = QApplication(sys.argv)

	window = QWidget()
	window.setFixedSize(width,height)
	window.move(50,50)
	window.setWindowTitle('PyTracer')
	
	#-----initialize a QImage, so we can maniputalte the pixels
	renderImage = QImage(width,height,4) #QImage.Format_RGB32
	graphic = QGraphicsScene(0,0,width,height,window)
	pixmap = QPixmap().fromImage(renderImage)
	graphicItem = graphic.addPixmap(pixmap)

	graphicView = QGraphicsView(graphic,window)
	window.show()

	#-------Scene--------
	#important! This is a right handed coordinate system!
	sphere01 = Sphere(Vector(-5,0,-30),5)
	sphere02 = Sphere(Vector(5,0,-20),7)
	spheres = SphereList([sphere01,sphere02])
	cam = Camera(Vector(0,0,0),Vector(0,0,1),50)

	#----shoot rays-------
	for j in range(0,height):
		for i in range(0,width):
			#shoot 4 rays each pixel for anti-aliasing
			col = Vector(0,0,0)
			AAsample = 4
			for k in range(0,AAsample):
				rayDir = Vector(i + random.random() - width/2, -j - random.random() + height/2, 
								-0.5*width/math.tan(math.radians(cam.angle/2))) #Warning!!!!! Convert to radian!!!!!!!
				ray = Ray(cam.pos,rayDir)

				#----check intersections with spheres----
				hitResult = [] #stores a list of data of intersections
				hitBool = spheres.getClosestIntersection(ray,hitResult)

				col = col + getColor(hitBool,hitResult)

			averageCol = col / AAsample
			renderImage.setPixel(i,j,QColor(averageCol.x,averageCol.y,averageCol.z).rgba())
	

	#update the render view
	pixmap2 = QPixmap().fromImage(renderImage)
	graphicItem.setPixmap(pixmap2)

	renderImage.save("test.png")
	
	
	sys.exit(app.exec_())




if __name__ == "__main__":
	main()