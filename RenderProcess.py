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
		self.refractionMaxDepth = processSettings["RefractionMaxDepth"]
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
						prevHitPos = self.cam.pos
						col = col + self.getColor(hitResult,prevHitPos)

					bucketArray[j%self.bucketSize,i%self.bucketSize] = [col.x,col.y,col.z]

			print("bucket" + str(bucketX) + ":" + str(bucketY) + " Rendered by " + multiprocessing.current_process().name)
			self.outputQ.put([bucketX,bucketY,bucketArray,thisAAoffset+1])


		self.outputQ.put("Done")

		timerEnd = datetime.now()
		processRenderTime = timerEnd - timerStart
		print("Process Finished - " + multiprocessing.current_process().name + " Render time: " + str(processRenderTime))
		sys.stdout.flush()

	def getRefractionColor(self,currObj,prevHitPos,hitResult):
		refractDepthCnt = 0
		refractionCol = Vector(0,0,0)
		reflectionCol = Vector(0,0,0)
		fresnelCol = Vector(0,0,0)
		while currObj.material.refractionWeight == 1 and refractDepthCnt < self.refractionMaxDepth:
			#If this object's material is transparent
			incomingVec = (prevHitPos - hitResult[1]).normalized() #It's actually the inverse direction of incoming ray
			incomingCos = incomingVec.dot(hitResult[2])
			ior = self.scene.getObjectById(hitResult[3]).material.refractionIndex
			rotAxis = hitResult[2].cross(incomingVec).normalized()

			if incomingCos >= 0 and incomingCos < 1:
				#When ray is entering another medium
				refractAngle = math.asin(math.sqrt(1-math.pow(incomingCos,2))/ior)
				refractRayDir = (hitResult[2]*(-1)).rot("A",refractAngle,rotAxis)
				refractCos = math.cos(refractAngle)
			elif incomingCos > -1 and incomingCos < 0:
				#When ray is leaving the medium
				refractAngleMultIor = math.sqrt(1-math.pow(incomingCos,2))*ior
				if refractAngleMultIor  > 1:
					#Critical angle, total internal reflection
					refractRayDir = incomingVec.rot("A",math.radians(180),hitResult[2])
					refractCos = 0
				else:
					refractAngle = math.asin(refractAngleMultIor)
					refractRayDir = hitResult[2].rot("A",-refractAngle,rotAxis)
					refractCos = math.cos(refractAngle)
			else:
				#incoming ray is perpendicular to the surface
				refractCos = 1
				refractRayDir = incomingVec * (-1)

			biasedOrigin = hitResult[1] + refractRayDir * self.bias
			refractionRay = Ray(biasedOrigin,refractRayDir)
			refractHitResult = []
			refractionHitBool = self.scene.getClosestIntersection(refractionRay,refractHitResult)

			if refractDepthCnt == 0:
				#Calculate fresnel, but only the first refraction
				fresnelParallel = math.pow((ior*incomingCos - refractCos) / (ior*incomingCos + refractCos),2)
				fresnelPerpendicular = math.pow((refractCos - ior*incomingCos) / (ior*incomingCos + refractCos),2)
				fresnelReflect = 0.5 * (fresnelParallel + fresnelPerpendicular)
				fresnelRefract = 1 - fresnelReflect
				#Get the reflection color
				reflectionCol = reflectionCol + self.getMirrorReflectionColor(currObj,prevHitPos,hitResult)

			if refractionHitBool:
				currObj = self.scene.getObjectById(refractHitResult[3])
				prevHitPos = hitResult[1]
				hitResult = refractHitResult
				refractDepthCnt += 1
			else:
				break

		else:
			refractionCol = refractionCol + self.getColor(hitResult,prevHitPos,self.indirectDepthLimit)
			fresnelCol = fresnelCol + refractionCol * fresnelRefract + reflectionCol*fresnelReflect

		return fresnelCol

	def getMirrorReflectionColor(self,currObj,prevHitPos,hitResult):
		mirrorDepthCnt = 0
		reflectionCol = Vector(0,0,0)
		reflectObj = currObj
		while currObj.material.reflectionWeight == 1 and mirrorDepthCnt < self.reflectionMaxDepth:
			#If this object's material is perfect mirror, and maybe the reflected ray hits mirror again
			incomingVec = (prevHitPos-hitResult[1]).normalized()
			reflectRayDir = incomingVec.rot("A",math.radians(180),hitResult[2])
			biasedOrigin = hitResult[1] + reflectRayDir * self.bias
			reflectionRay = Ray(biasedOrigin,reflectRayDir)

			reflectHitResult = []
			reflectionHitBool = self.scene.getClosestIntersection(reflectionRay,reflectHitResult)

			if reflectionHitBool:
				currObj = self.scene.getObjectById(reflectHitResult[3])
				prevHitPos = hitResult[1]
				hitResult = reflectHitResult
				mirrorDepthCnt += 1
			else:
				#reflect ray doesn't hit anything
				break
		else:
			reflectionCol = reflectionCol + self.getColor(hitResult,prevHitPos,self.indirectDepthLimit).colorMult(reflectObj.material.reflectionColor)

		return reflectionCol

	def getColor(self,hitResult,prevHitPos,currDepth=0):
		#Important, when calculating refraction/mirror reflection, pass indirectDepthLimit to getColor to avoid infinite loop
		recursiveCnt = currDepth
		currObj = self.scene.getObjectById(hitResult[3])
		hitPointColor = Vector(0,0,0)

		if currObj.material.refractionWeight == 1 and currObj.material.reflectionWeight == 1:
			#if this object is glass
			hitPointColor = hitPointColor + self.getRefractionColor(currObj,prevHitPos,hitResult)
		elif currObj.material.refractionWeight != 1 and currObj.material.reflectionWeight == 1:
			#If this object is perfect mirror
			hitPointColor = hitPointColor + self.getMirrorReflectionColor(currObj,prevHitPos,hitResult)
		else:
			#Diffuse material
			hitPointColor = hitPointColor + self.getHitPointColor(hitResult)

			#Recurvsive path tracing, only for diffuse material--------------------
			if recursiveCnt < self.indirectDepthLimit:
				recursiveCnt += 1
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
						indirectHitPColor = self.getColor(indirectHitResult,hitResult[1],recursiveCnt) #get the indirect color
						lambert = hitResult[2].dot(indirectRayDir)
						indirectPointDist = (indirectHitResult[1] - hitResult[1]).length()
						indirectLitColor = indirectHitPColor * lambert  #/ (2*math.pi*math.pow(indirectPointDist,2))
						indirectColor = indirectColor + indirectLitColor

				indirectColor = indirectColor / self.indirectSamples * 2 * math.pi
				matColor = currentObj.material.diffuseColor
				hitPointColor = hitPointColor + indirectColor.colorMult(matColor)

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
