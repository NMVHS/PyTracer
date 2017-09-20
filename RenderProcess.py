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

		#shoot multiple rays each pixel for anti-aliasing
		AAsample = 4
		#--deconstruct AAsample---------
		AAxSubstep = int(math.floor(math.sqrt(AAsample)))
		AAxSubstepLen = 1.0 / AAxSubstep
		AAySubstep = int(AAsample / AAxSubstep)
		AAySubstepLen = 1.0 /AAySubstep

		#----shoot rays-------
		for j in range(self.startLine,self.startLine + self.bucketHeight):
			#----Each line of pixels level--------------
			for i in range(0,self.width):
				#--------Each pixel level--------------------
				col = Vector(0,0,0)

				for AAy in range(0,AAySubstep):
					for AAx in range(0,AAxSubstep):
						rayDir = Vector(i + AAx * AAxSubstepLen + AAxSubstepLen/2 - self.width/2,
										-j - AAy * AAySubstepLen - AAySubstepLen/2 + self.height/2,
										-0.5*self.width/math.tan(math.radians(self.cam.angle/2))) #Warning!!!!! Convert to radian!!!!!!!
						ray = Ray(self.cam.pos,rayDir)

						#----check intersections with spheres----
						#hitResult is a list storing calculated data [hit_t, hit_pos,hit_normal,objectId]
						hitResult = []
						hitBool = self.scene.getClosestIntersection(ray,hitResult)

						col = col + self.getColor(hitBool,hitResult)

				averageCol = self.clampColor(self.gammaCorrect(col / AAsample))
				bucketArray[j%self.bucketHeight,i] = [int(averageCol.x*255),int(averageCol.y*255),int(averageCol.z*255)]

		self.outputQ.put((self.order,bucketArray))
		print("Bucket Finished - " + multiprocessing.current_process().name)

	def getColor(self,hit,hitResult):
		if hit:
			hitPointColor = Vector(0,0,0)
			hitPointColor = hitPointColor + self.getHitPointColor(hitResult)

			#Recurvsive path tracing--------------------
			#Generation random derections


			return hitPointColor
		else:
			#Alpha black
			return Vector(0,0,0)

	def getRandomDirection(self):
		#Generate random direction based on a unit hemisphere in Cartesian System
		theta = ramdom.random()
		phi = random.random()

	def getHitPointColor(self,hitResult):
		litColor = Vector(0,0,0) #color accumulated after being lit
		#iterate through all the lights using shadow ray, check if object is in shadow

		for eachLight in self.scene.lights:
			for i in range(eachLight.samples):
				if eachLight.type == 'Area':
					shadowRayDir = eachLight.getRandomSample() - hitResult[1]
				else:
					shadowRayDir = eachLight.pos - hitResult[1]
	 			#lambert is the cosine
				lambert = hitResult[2].dot(shadowRayDir.normalized())
				if lambert > 0:
					offsetOrigin = hitResult[1] + shadowRayDir.normalized() * 0.0001 #slightly offset the ray start point because the origin itself is a root
					shadowRay = Ray(offsetOrigin,shadowRayDir)
					temp_t = shadowRayDir.length() #length form hit point to light
					shadowRayResult = [temp_t]
					inShadow = self.scene.getClosestIntersection(shadowRay,shadowRayResult)
					if not inShadow:
						litColor = litColor + eachLight.color * (eachLight.intensity * lambert / (4*math.pi*math.pow(temp_t,2)))

			litColorAvg = litColor / eachLight.samples * 2 * math.pi

		matColor = self.scene.getObjectById(hitResult[3]).material.diffuseColor

		return Vector(matColor.x * litColorAvg.x, matColor.y * litColorAvg.y,matColor.z * litColorAvg.z)



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
