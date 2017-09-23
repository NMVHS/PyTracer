import multiprocessing, math, random, numpy
from datetime import datetime
from Geo.Vector import Vector
from Geo.Ray import Ray
from Scene import Scene

class RenderProcess(multiprocessing.Process):
	def __init__(self,outputQ,width,height,bucketX,bucketY,bucketHeight,scene,cam):
		multiprocessing.Process.__init__(self)
		self.outputQ = outputQ
		self.width = width #image width
		self.height = height
		self.bucketX = bucketX #X coord of of bucket
		self.bucketY = bucketY #Y coord of the bucket
		self.bucketHeight = bucketHeight
		self.scene = scene #includes geometries and lights
		self.cam = cam
		self.bias = 0.0001
		self.indirectSamples = 8
		self.indirectDepthLimit = 0
		#QImage pickling is not supported at the moment. PIL doesn't support 32 bit RGB.

	def run(self):
		#bucket rendered color data is stored in an array
		bucketArray = numpy.ndarray(shape=(self.bucketHeight,self.width,3),dtype = numpy.float)

		#shoot multiple rays each pixel for anti-aliasing
		AAsample = 4
		#--deconstruct AAsample---------
		AAxSubstep = int(math.floor(math.sqrt(AAsample)))
		AAxSubstepLen = 1.0 / AAxSubstep
		AAySubstep = int(AAsample / AAxSubstep)
		AAySubstepLen = 1.0 /AAySubstep

		timerStart = datetime.now()
		#----shoot rays-------
		for AAy in range(0,AAySubstep):
			for AAx in range(0,AAxSubstep):
				for j in range(self.bucketY,self.bucketY + self.bucketHeight):
					#----Each line of pixels level--------------
					for i in range(0,self.width):
						#--------Each pixel level--------------------
						col = Vector(0,0,0)

						rayDir = Vector(i + AAx * AAxSubstepLen + AAxSubstepLen/2 - self.width/2,
										-j - AAy * AAySubstepLen - AAySubstepLen/2 + self.height/2,
										-0.5*self.width/math.tan(math.radians(self.cam.angle/2))) #Warning!!!!! Convert to radian!!!!!!!
						camRay = Ray(self.cam.pos,rayDir)

						#----check intersections with spheres----
						#hitResult is a list storing calculated data [hit_t, hit_pos,hit_normal,objectId]
						hitResult = []
						hitBool = self.scene.getClosestIntersection(camRay,hitResult)

						if hitBool:
							currObj = self.scene.getObjectById(hitResult[3])
							if currObj.material.reflectionWeight == 1:
								#If this object's material is perfect mirror
								incomingVec = (self.cam.pos-hitResult[1]).normalized()
								reflectRayDir = incomingVec.rot("A",math.radians(180),hitResult[2])
								biasedOrigin = hitResult[1] + reflectRayDir * self.bias
								reflectionRay = Ray(biasedOrigin,reflectRayDir)
								reflectHitResult = []
								reflectionHitBool = self.scene.getClosestIntersection(reflectionRay,reflectHitResult)

								if reflectionHitBool:
									col = col + self.getColor(reflectHitResult).colorMult(currObj.material.reflectionColor)

							else:
								#diffuse material
								col = col + self.getColor(hitResult)

						bucketArray[j%self.bucketHeight,i] = [col.x,col.y,col.z]

		bucketArray /= AAsample
		numpy.clip(bucketArray,0,1)
		self.outputQ.put([self.bucketX,self.bucketY,bucketArray])

		timerEnd = datetime.now()
		bucketRenderTime = timerEnd - timerStart
		print("Bucket Finished - " + multiprocessing.current_process().name + " Render time: " + str(bucketRenderTime))

	def getColor(self,hitResult,currDepth=0):
		resursiveCnt = currDepth

		hitPointColor = Vector(0,0,0)
		hitPointColor = hitPointColor + self.getHitPointColor(hitResult)
		#Recurvsive path tracing--------------------

		if resursiveCnt < self.indirectDepthLimit:
			resursiveCnt += 1

			camRayDir = hitResult[1] - self.cam.pos #This has to be changed during recursive
			tangentAxis = camRayDir.cross(hitResult[2]).normalized()
			biTangentAxis = hitResult[2].cross(tangentAxis).normalized()

			indirectColor = Vector(0,0,0)
			currentObj = self.scene.getObjectById(hitResult[3])

			for i in range(self.indirectSamples):
				tangentRotAmount = (random.random()-0.5)*math.pi
				biTrangentRotAmount = (random.random()-0.5)*math.pi
				indirectRayDir = hitResult[2].rot("A",tangentRotAmount,tangentAxis).rot("A",biTrangentRotAmount,biTangentAxis)
				biasedOrigin = hitResult[1] + indirectRayDir * self.bias
				indirectRay = Ray(biasedOrigin,indirectRayDir)

				indirectHitResult = []
				indirectHitBool = self.scene.getClosestIntersection(indirectRay,indirectHitResult)
				if indirectHitBool:
					indirectHitPColor = self.getColor(indirectHitResult,resursiveCnt)
					lambert = hitResult[2].dot(indirectRayDir)
					indirectPointDist = (indirectHitResult[1] - hitResult[1]).length()
					indirectLitColor = indirectHitPColor * lambert  #/ (2*math.pi*math.pow(indirectPointDist,2))
					indirectColor = indirectColor + indirectLitColor

			indirectColor = indirectColor / self.indirectSamples * 2 * math.pi
			matColor = currentObj.material.diffuseColor
			hitPointColor = hitPointColor + indirectColor.colorMult(matColor)


		#Generation random derections

		return hitPointColor


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
					# if shadowRayDir.normalized().dot(eachLight.normal) > 0: #single side area light
					# 	continue
				else:
					shadowRayDir = eachLight.pos - hitResult[1]
	 			#lambert is the cosine
				lambert = hitResult[2].dot(shadowRayDir.normalized())
				if lambert > 0:
					offsetOrigin = hitResult[1] + shadowRayDir.normalized() * self.bias #slightly offset the ray start point because the origin itself is a root
					shadowRay = Ray(offsetOrigin,shadowRayDir)
					temp_t = shadowRayDir.length() #length form hit point to light
					shadowRayResult = [temp_t]
					inShadow = self.scene.getClosestIntersection(shadowRay,shadowRayResult)
					if not inShadow:
						litColor = litColor + eachLight.color * (eachLight.intensity * lambert / (4*math.pi*math.pow(temp_t,2)))

			litColorAvg = litColor / eachLight.samples * eachLight.area

		matColor = self.scene.getObjectById(hitResult[3]).material.diffuseColor

		return Vector(matColor.x * litColorAvg.x, matColor.y * litColorAvg.y,matColor.z * litColorAvg.z)
