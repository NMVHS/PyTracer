#python ray tracing implementation challenge
#shawn / Aug 2017
#-------------------------
#Some stuff can be easily missing:
#1. keep in mind when using tan/cos/sin, use radians not degrees

#-------------------------

import sys, math, random, multiprocessing, numpy
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

class Plane:
	def __init__(self,pos,size,normal):
		self.pos = pos
		self.size = size
		self.normal = normal

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

class ObjectList:
	def __init__(self,objects):
		self.objects = objects #a list of objects, can include spheres, planes, and others

	def getClosestIntersection(self,ray,result):
		hitBool = False
		closestHit = 1000000000000
		closestHitResult = []
		for obj in self.objects:
			if obj.getIntersection(ray,closestHit,result):
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


class RenderProcess(multiprocessing.Process):
	#setPixSignal = pyqtSignal(list) #set pixel signal to UI

	def __init__(self,outputQ,order,width,height,startLine,bucketHeight,objects,cam):
		multiprocessing.Process.__init__(self)
		self.outputQ = outputQ
		self.order = order
		self.width = width
		self.height = height
		self.startLine = startLine
		self.bucketHeight = bucketHeight
		self.objects = objects
		self.cam = cam
		#QImage pickling is not supported at the moment. PIL doesn't support 32 bit RGB.
		
	def run(self):
		bucketArray = numpy.ndarray(shape=(self.bucketHeight,self.width,3),dtype = numpy.uint8)
		#----shoot rays-------
		for j in range(self.startLine,self.startLine + self.bucketHeight):
			for i in range(0,self.width):
				#shoot 4 rays each pixel for anti-aliasing
				col = Vector(0,0,0)
				AAsample = 4
				for k in range(0,AAsample):
					rayDir = Vector(i + random.random() - self.width/2, -j - random.random() + self.height/2, 
									-0.5*self.width/math.tan(math.radians(self.cam.angle/2))) #Warning!!!!! Convert to radian!!!!!!!
					ray = Ray(self.cam.pos,rayDir)

					#----check intersections with spheres----
					hitResult = [] #stores a list of data of intersections
					hitBool = self.objects.getClosestIntersection(ray,hitResult)

					col = col + self.getColor(hitBool,hitResult)

				averageCol = col / AAsample
				bucketArray[j%self.bucketHeight,i] = [int(averageCol.x),int(averageCol.y),int(averageCol.z)]

		self.outputQ.put((self.order,bucketArray))
		print("Bucket Finished - " + multiprocessing.current_process().name)

	def getColor(self,hit,hitResult):
		#hit is bool,
		if hit == True:
			remapHitNormal = (hitResult[2]+Vector(1,1,1))*0.5
			return Vector(255*remapHitNormal.x,255*remapHitNormal.y,255*remapHitNormal.z)
		else:
			return Vector(0,0,0)

class RenderWindow:
	def __init__(self,width,height):
		#-------ui initialization-------
		self.app = QApplication(sys.argv)
		self.window = QWidget()
		self.window.setFixedSize(width,height)
		self.window.move(50,50)
		self.window.setWindowTitle('PyTracer')
		self.width = width
		self.height = height

		#-----initialize a QImage, so we can maniputalte the pixels
		self.renderImage = QImage(width,height,4) #QImage.Format_RGB32
		self.graphic = QGraphicsScene(0,0,width,height,self.window)
		
		self.pixmap = QPixmap().fromImage(self.renderImage)
		self.graphicItem = self.graphic.addPixmap(self.pixmap)

		self.graphicView = QGraphicsView(self.graphic,self.window)
		self.window.show()


	def setPixel(self,x,y,color):
		self.renderImage.setPixel(x,y,QColor(color.x,color.y,color.z).rgba())

	def getBucket(self,processCnt):
		#input the process count, return the starting point of each bucket
		startLine = []
		bucketHeight = int(self.height / processCnt)
		for i in range(0,processCnt):
			startLine.append(bucketHeight * i)

		return startLine, bucketHeight

	def startRender(self,objects,cam):
		#start render in a new thread
		processCnt = multiprocessing.cpu_count()
		startLine,bucketHeight = self.getBucket(processCnt)
		jobs = []
		jobsQueue = multiprocessing.Queue()
		for i in range(processCnt):
			job = RenderProcess(jobsQueue,i,self.width,self.height,startLine[i],bucketHeight,objects,cam)
			jobs.append(job)
			
		for each in jobs: 
			each.start()

		bucketArrays = [jobsQueue.get() for each in jobs]

		# for each in self.jobs: #This has to be after Queue.get() or simply don't join
		# 	each.join()

		bucketArrays.sort(key = self.getOrderKey)
		bucketArrays = [r[1] for r in bucketArrays]

		#merge the arrays into one
		mergedArrays = numpy.vstack(bucketArrays) #merged along second axis
		#numpy.require(mergedArrays,numpy.float32,"C")
		
		#convert array to QImage
		newImage = QImage(mergedArrays.data,self.width,self.height,mergedArrays.strides[0],QImage.Format_RGB888)

		self.update(newImage)

	def getOrderKey(self,elem):
		return elem[0]

	def update(self,image):
		#update the render view, note the render is in another thread
		self.pixmap = QPixmap().fromImage(image)
		self.graphicItem.setPixmap(self.pixmap)
		image.save("test.png")
		print("Render finished")

	def getPixColor(self,pixData):
		#get the signal from the render thread
		self.setPixel(pixData[0],pixData[1],pixData[2])
		#print("Pixel set successfully----------")
		

def main():
	#-------canvas size-----
	width = 600
	height = 600

	renderView = RenderWindow(width,height)

	#-------Scene--------
	#important! This is a right handed coordinate system!
	sphere01 = Sphere(Vector(-15,-30,-136),20)
	sphere02 = Sphere(Vector(10,-20,-136),30)
	plane01 = Plane(Vector(0,-50,-136),10,Vector(0,1,0))
	plane02 = Plane(Vector(-50,0,-136),10,Vector(1,0,0))
	plane03 = Plane(Vector(0,0,-186),10,Vector(0,0,1))
	plane04 = Plane(Vector(50,0,-136),10,Vector(-1,0,0))
	plane05 = Plane(Vector(0,50,-136),10,Vector(0,-1,0))
	objects = ObjectList([sphere01,sphere02,plane01,plane02,plane03,plane04,plane05])
	cam = Camera(Vector(0,0,0),Vector(0,0,1),60)

	renderView.startRender(objects,cam)
	
	
	sys.exit(renderView.app.exec_())




if __name__ == "__main__":
	main()