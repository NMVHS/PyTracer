import multiprocessing, math, random, numpy
from Geo.Vector import Vector
from Geo.Ray import Ray
from Scene import Scene


class RenderProcess(multiprocessing.Process):
	def __init__(self,outputQ,order,width,height,startLine,bucketHeight,scene,cam):
		multiprocessing.Process.__init__(self)
		self.outputQ = outputQ
		self.order = order
		self.width = width
		self.height = height
		self.startLine = startLine
		self.bucketHeight = bucketHeight
		self.scene = scene #includes geometries and lights
		self.cam = cam
		#QImage pickling is not supported at the moment. PIL doesn't support 32 bit RGB.

	def run(self):
		#bucket rendered color data is stored in an array
		bucketArray = numpy.ndarray(shape=(self.bucketHeight,self.width,3),dtype = numpy.uint8)

		#----shoot rays-------
		for j in range(self.startLine,self.startLine + self.bucketHeight):
			for i in range(0,self.width):
				#shoot 4 rays each pixel for anti-aliasing
				col = Vector(0,0,0)
				AAsample = 1
				for k in range(0,AAsample):
					rayDir = Vector(i + random.random() - self.width/2, -j - random.random() + self.height/2,
									-0.5*self.width/math.tan(math.radians(self.cam.angle/2))) #Warning!!!!! Convert to radian!!!!!!!
					ray = Ray(self.cam.pos,rayDir)

					#----check intersections with spheres----
					#hitResult is a list storing calculated data [hit_t, hit_pos,hit_normal]
					hitResult = []
					hitBool = self.scene.getClosestIntersection(ray,hitResult)

					col = col + self.getColor(hitBool,hitResult)

				averageCol = self.clampColor(self.gammaCorrect(col / AAsample))
				bucketArray[j%self.bucketHeight,i] = [int(averageCol.x*255),int(averageCol.y*255),int(averageCol.z*255)]

		self.outputQ.put((self.order,bucketArray))
		print("Bucket Finished - " + multiprocessing.current_process().name)

	def getColor(self,hit,hitResult):
		#hit is bool,
		if hit:
			return self.directLighting(hitResult)

		else:
			return Vector(0,0,0)

	def directLighting(self,hitResult):
		litColor = Vector(0,0,0) #color accumulated after being lit
		#iterate through all the lights using shadow ray, check if object is in shadow

		for eachLight in self.scene.lights:
			shadowRayDir = eachLight.pos - hitResult[1]
 			#lambert is the cosine
			lambert = hitResult[2].dot(shadowRayDir.normalized())
			lambert = max(lambert,0) #clamp the values below 0
			offsetOrigin = hitResult[1] + shadowRayDir.normalized() * 0.0001 #slightly offset the ray start point because the origin itself is a root
			shadowRay = Ray(offsetOrigin,shadowRayDir)
			temp_t = shadowRayDir.length() #length form hit point to light
			shadowRayResult = [temp_t]
			shadowBool = self.scene.getClosestIntersection(shadowRay,shadowRayResult)
			if not shadowBool:
				litColor = litColor + eachLight.color * (eachLight.intensity * lambert / (4*math.pi*math.pow(temp_t,2)))


		return litColor


	def gammaCorrect(self,color):
		#apply a 2.2 gamma correction
		gamma = 2.2
		return Vector(math.pow(color.x,1/2.2),math.pow(color.y,1/2.2),math.pow(color.z,1/2.2))

	def clampColor(self,color):
		#clamp the color below (0,0,0) and above(1,1,1), only for saving 8 bit images
		r = max(min(color.x,1),0)
		g = max(min(color.y,1),0)
		b = max(min(color.z,1),0)
		return Vector(r,g,b)
