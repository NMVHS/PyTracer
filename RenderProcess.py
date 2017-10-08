import multiprocessing, math, random, numpy, sys, json
from datetime import datetime
import time
from Geo.Vector import Vector
from Geo.Ray import Ray
from Scene import Scene

class RenderProcess(multiprocessing.Process):
	#Render process class is the core of the tracer
	#each RenderProcess class instances calculates render bucketss, all the magic is here
	def __init__(self,outputQ,width,height,bucketPosData,bucketCnt,bucketCntLock,bucketSize,scene,cam):
		multiprocessing.Process.__init__(self)
		processSettings = self.loadSettings()
		self.outputQ = outputQ
		self.width = width #image width
		self.height = height
		self.bucketPosData = bucketPosData #manager.list of position data of each bucket
		self.bucketCnt = bucketCnt #shared counter among all processes
		self.bucketCntLock = bucketCntLock #lock for safely accessing shared variable
		self.bucketSize = bucketSize
		self.scene = scene #includes geometries and lights
		self.cam = cam
		self.bias = processSettings["Bias"]
		self.indirectSamples = processSettings["IndirectSamples"]
		self.indirectDepthLimit = processSettings["IndirectDepth"]
		self.AAsamples = processSettings["AAsamples"]
		self.reflectionMaxDepth = processSettings["ReflectionMaxDepth"]
		#QImage pickling is not supported at the moment. PIL doesn't support 32 bit RGB.

	def loadSettings(self):
		with open("RenderSettings.json") as settingsData:
			renderSettings = json.load(settingsData)

		return renderSettings["RenderProcess"]

	def run(self):
		#bucket rendered color data is stored in an array
		bucketArray = numpy.ndarray(shape=(self.bucketSize,self.bucketSize,3),dtype = numpy.float)
		bucketArray.fill(0) #Very import need to set default color

		#shoot multiple rays each pixel for anti-aliasing
		#--deconstruct self.AAsamples---------
		AAxSubstep = int(math.floor(math.sqrt(self.AAsamples)))
		AAxSubstepLen = 1.0 / AAxSubstep
		AAySubstep = int(self.AAsamples / AAxSubstep)
		AAySubstepLen = 1.0 / AAySubstep

		AAsampleGrid = []
		for AAy in range(0,AAySubstep):
			for AAx in range(0,AAxSubstep):
				AAsingleOffset = [AAx * AAxSubstepLen + AAxSubstepLen/2,AAy * AAySubstepLen + AAySubstepLen/2]
				AAsampleGrid.append(AAsingleOffset)

		timerStart = datetime.now()

		#-------Process keeps getting new bucket-------------------------
		while True:
			with self.bucketCntLock:
				#access shared variable with lock, get the next bucket id
				#print(self.bucketCnt.value,multiprocessing.current_process().name)
				if self.bucketCnt.value <= len(self.bucketPosData) * self.AAsamples -1:
					thisBucketId = self.bucketCnt.value % len(self.bucketPosData)
					thisAAoffset = math.floor(self.bucketCnt.value / len(self.bucketPosData))
					self.bucketCnt.value += 1
				else:
					break

			bucketX = self.bucketPosData[thisBucketId][0]
			bucketY = self.bucketPosData[thisBucketId][1]

			#-------------shoot rays---------------------------------------
			#----Each bucket level--------------
			for j in range(bucketY,bucketY + self.bucketSize):
				#----Each line of pixels level--------------
				for i in range(bucketX,bucketX + self.bucketSize):
					#--------Each pixel level--------------------
					col = Vector(0,0,0)

					rayDir = Vector(i + AAsampleGrid[thisAAoffset][0] - self.width/2,
									-j - AAsampleGrid[thisAAoffset][1] + self.height/2,
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
							reflectHitResult = []
							reflectionHitBool = self.getMirrorReflectionHit(self.cam.pos,hitResult,reflectHitResult)
							if reflectionHitBool:
								col = col + self.getColor(reflectHitResult,self.cam.pos).colorMult(currObj.material.reflectionColor)
						else:
							#diffuse material
							col = col + self.getColor(hitResult,self.cam.pos)

					bucketArray[j%self.bucketSize,i%self.bucketSize] = [col.x,col.y,col.z]

			print("bucket" + str(bucketX) + ":" + str(bucketY) + " Rendered by " + multiprocessing.current_process().name)
			self.outputQ.put([bucketX,bucketY,bucketArray,thisAAoffset+1])


		self.outputQ.put("Done")

		timerEnd = datetime.now()
		processRenderTime = timerEnd - timerStart
		print("Process Finished - " + multiprocessing.current_process().name + " Render time: " + str(processRenderTime))
		sys.stdout.flush()

	def getMirrorReflectionHit(self,prevHitPos,hitResult,reflectHitResult):
		incomingVec = (prevHitPos-hitResult[1]).normalized()
		reflectRayDir = incomingVec.rot("A",math.radians(180),hitResult[2])
		biasedOrigin = hitResult[1] + reflectRayDir * self.bias
		reflectionRay = Ray(biasedOrigin,reflectRayDir)
		reflectionHitBool = self.scene.getClosestIntersection(reflectionRay,reflectHitResult)
		return reflectionHitBool

	def getColor(self,hitResult,prevHitPos,currDepth=0):
		resursiveCnt = currDepth

		hitPointColor = Vector(0,0,0)
		hitPointColor = hitPointColor + self.getHitPointColor(hitResult)
		#Recurvsive path tracing--------------------

		if resursiveCnt < self.indirectDepthLimit:
			resursiveCnt += 1

			if resursiveCnt == 1:
				incomingRayDir = hitResult[1] - self.cam.pos #This has to be changed during recursive
			else:
				incomingRayDir = hitResult[1] - prevHitPos

			tangentAxis = incomingRayDir.cross(hitResult[2]).normalized()
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
					mirrorReflectHit = False
					indirectHitObj = self.scene.getObjectById(indirectHitResult[3])
					incomingHitPos = prevHitPos
					#Check if the indirect ray hits a mirror object
					mirrorDepthCnt = 0
					while indirectHitObj.material.reflectionWeight == 1 and mirrorDepthCnt < self.reflectionMaxDepth:
						mirrorHitResult = []
						mirrorHitBool = self.getMirrorReflectionHit(incomingHitPos,indirectHitResult,mirrorHitResult)
						if mirrorHitBool:
							incomingHitPos = indirectHitResult[1]
							indirectHitResult = mirrorHitResult
							indirectHitObj = self.scene.getObjectById(mirrorHitResult[3])
							mirrorReflectHit = True
							mirrorDepthCnt += 1
						else:
							mirrorReflectHit = False
							break

					if mirrorReflectHit:
						indirectHitPColor = self.getColor(indirectHitResult,hitResult[1],resursiveCnt) #get the indirect color
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
