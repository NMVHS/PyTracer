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
		self.filmFitOptions = {"Horizontal":self.width,"Vertical":self.height}
		#--------Render Process Settings------------------------
		self.kernel = processSettings["Kernel"]
		self.dof = processSettings["DOF"]
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

	def getNextBucket(self,bucketResult):
		with self.bucketCntLock:
			#access shared variable with lock, get the next bucket id
			#print(self.bucketCnt.value,multiprocessing.current_process().name)
			if self.bucketCnt.value <= len(self.bucketPosData) * self.AAsamples -1:
				thisBucketId = self.bucketCnt.value % len(self.bucketPosData)
				thisAAoffset = math.floor(self.bucketCnt.value / len(self.bucketPosData))
				self.bucketCnt.value += 1
				bucketX = self.bucketPosData[thisBucketId][0]
				bucketY = self.bucketPosData[thisBucketId][1]
				bucketResult.extend([bucketX,bucketY,thisAAoffset])
				return True
			else:
				return False

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

		#---------------------
		filmFitVal = self.filmFitOptions[self.cam.filmFit]
		focusRatio = self.cam.focusDist / (0.5*filmFitVal/math.tan(self.cam.angleOfViewH/2))
		#---------------------
		bucketResult = []
		#-------Process keeps getting new bucket-------------------------
		while self.getNextBucket(bucketResult):
			bucketX = bucketResult[0]
			bucketY = bucketResult[1]
			thisAAoffset = bucketResult[2]
			bucketResult.clear()
			#-------------shoot rays---------------------------------------
			#----Each bucket level--------------
			for j in range(bucketY,bucketY + self.bucketSize):
				#----Each line of pixels level--------------
				for i in range(bucketX,bucketX + self.bucketSize):
					#--------Each pixel level--------------------
					col = Vector(0,0,0)
					if self.dof == 1:
						camRayStart = self.cam.getRandomPointOnLens()
					else:
						camRayStart = self.cam.pos

					camRayEnd = self.cam.pos + Vector((i + AAsampleGrid[thisAAoffset][0] - self.width/2)*focusRatio,
									(-j - AAsampleGrid[thisAAoffset][1] + self.height/2)*focusRatio,
									-self.cam.focusDist) #Warning!!!!! Convert to radian!!!!!!!
					rayDir = camRayEnd - camRayStart
					camRay = Ray(camRayStart,rayDir)

					#hitResult is a list storing calculated data [hit_t, hit_pos,hit_normal,objectId]
					hitResult = []
					hitBool = self.scene.getClosestIntersection(camRay,hitResult)

					if hitBool:
						prevHitPos = camRayStart
						col = col + self.getColor(hitResult,prevHitPos)

					bucketArray[j%self.bucketSize,i%self.bucketSize] = [col.x,col.y,col.z]

			returnData = [bucketX,bucketY,bucketArray,thisAAoffset+1,self.AAsamples]
			#print("bucket" + str(bucketX) + ":" + str(bucketY) + " Rendered by " + multiprocessing.current_process().name)

			#----get the next bucket--------
			self.outputQ.put(returnData)

		self.outputQ.put("Done")

		timerEnd = datetime.now()
		processRenderTime = timerEnd - timerStart
		print("Process Finished - " + multiprocessing.current_process().name + " Render time: " + str(processRenderTime))
		sys.stdout.flush()

	def getRefractionColor(self,currObj,prevHitPos,hitResult,indirectDepth,refractDepth,reflectDepth,reflectDist):
		refractDepth += 1

		refractionCol = Vector(0,0,0)
		reflectionCol = Vector(0,0,0)
		fresnelCol = Vector(0,0,0)
		fresnelRefract = 1
		fresnelReflect = 0

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

		if refractDepth == 1:
			#Calculate fresnel, but only the first refraction
			fresnelS = math.pow((incomingCos - ior*refractCos) / (incomingCos + ior*refractCos),2)
			fresnelP = math.pow((refractCos - ior*incomingCos) / (ior*incomingCos + refractCos),2)
			fresnelReflect = 0.5 * (fresnelS + fresnelP)
			fresnelRefract = 1 - fresnelReflect
			#Get the reflection color
			reflectionCol = reflectionCol + self.getMirrorReflectionColor(currObj,prevHitPos,hitResult,indirectDepth,reflectDepth,reflectDist)

		if refractionHitBool:
			reflectDist = reflectDist + (refractHitResult[1] - hitResult[1]).length() #accumulation of distance of reflection
			prevHitPos = hitResult[1]
			hitResult = refractHitResult
			if refractDepth < self.refractionMaxDepth:
				refractionCol = refractionCol + self.getColor(hitResult,prevHitPos,indirectDepth=indirectDepth,refractDepth=refractDepth,reflectDist=reflectDist)
			else:
				refractionCol = refractionCol + self.getHitPointColor(hitResult)

			fresnelCol = fresnelCol + refractionCol * fresnelRefract + reflectionCol*fresnelReflect

		return fresnelCol

	def getMirrorReflectionColor(self,currObj,prevHitPos,hitResult,indirectDepth,reflectDepth,reflectDist):
		reflectionCol = Vector(0,0,0)
		reflectDepth += 1
		#If this object's material is perfect mirror, and maybe the reflected ray hits mirror again
		incomingVec = (prevHitPos-hitResult[1]).normalized()
		reflectRayDir = incomingVec.rot("A",math.radians(180),hitResult[2])
		biasedOrigin = hitResult[1] + reflectRayDir * self.bias
		reflectionRay = Ray(biasedOrigin,reflectRayDir)

		reflectHitResult = []
		reflectionHitBool = self.scene.getClosestIntersection(reflectionRay,reflectHitResult)

		if reflectionHitBool:
			reflectDist = reflectDist + (reflectHitResult[1] - hitResult[1]).length() #accumulation of distance of reflection
			prevHitPos = hitResult[1]
			hitResult = reflectHitResult
			if reflectDepth < self.reflectionMaxDepth:
				reflectionCol = reflectionCol + self.getColor(hitResult,prevHitPos,indirectDepth=indirectDepth,reflectDepth=reflectDepth,reflectDist=reflectDist).colorMult(currObj.material.reflectionColor)
			else:
				reflectionCol = reflectionCol + self.getHitPointColor(hitResult).colorMult(currObj.material.reflectionColor)

		return reflectionCol

	def getColor(self,hitResult,prevHitPos,indirectDepth=0,reflectDepth=0,refractDepth=0,reflectDist=0):
		#Important, when calculating refraction/mirror reflection, pass indirectDepthLimit to getColor to avoid infinite loop
		currObj = self.scene.getObjectById(hitResult[3])
		hitPointColor = Vector(0,0,0)

		if "AreaLight" in currObj.type:
			#if this object is AreaLight, return lightColor * lightIntensity
			if currObj.visible:
				#if hit a light, return color is attenuated. And will be clipped in renderThread
				if indirectDepth == 0:
					#camera ray, no attenuation
					litColor = currObj.color * currObj.intensity
				else:
					#indirect ray, return attenuated value
					litColor = currObj.color * currObj.intensity / (4*math.pi*math.pow(reflectDist,2))

				hitPointColor = hitPointColor + litColor
				return hitPointColor

		if currObj.material.refractionWeight == 1 and currObj.material.reflectionWeight == 1:
			#if this object is glass
			hitPointColor = hitPointColor + self.getRefractionColor(currObj,prevHitPos,hitResult,indirectDepth,refractDepth,reflectDepth,reflectDist)
		elif currObj.material.refractionWeight != 1 and currObj.material.reflectionWeight == 1:
			#If this object is perfect mirror
			hitPointColor = hitPointColor + self.getMirrorReflectionColor(currObj,prevHitPos,hitResult,indirectDepth,reflectDepth,reflectDist)
		else:
			#Diffuse material
			if self.kernel == 0:
				#DirectLighting Kernel
				hitPointColor = hitPointColor + self.getHitPointColor(hitResult)

			#Recurvsive path tracing, only for Diffuse material--------------------
			if indirectDepth < self.indirectDepthLimit:
				indirectDepth += 1
				incomingRayDir = hitResult[1] - prevHitPos

				tangentAxis = incomingRayDir.cross(hitResult[2]).normalized()
				biTangentAxis = hitResult[2].cross(tangentAxis).normalized()

				indirectColor = Vector(0,0,0)
				currentObj = self.scene.getObjectById(hitResult[3])

				for i in range(self.indirectSamples):
					tangentRotAmount = random.random()*0.5*math.pi #range: [0,0.5pi)
					biTrangentRotAmount = random.random()*2*math.pi #range: [0,2pi)
					indirectRayDir = hitResult[2].rot("A",tangentRotAmount,tangentAxis).rot("A",biTrangentRotAmount,hitResult[2])
					biasedOrigin = hitResult[1] + indirectRayDir * self.bias
					indirectRay = Ray(biasedOrigin,indirectRayDir)

					indirectHitResult = []
					indirectHitBool = self.scene.getClosestIntersection(indirectRay,indirectHitResult)

					if indirectHitBool:
						indirectPointDist = (indirectHitResult[1] - hitResult[1]).length()
						reflectDist = reflectDist + indirectPointDist
						indirectHitPColor = self.getColor(indirectHitResult,hitResult[1],indirectDepth,0,0,reflectDist) #get the indirect color
						lambert = hitResult[2].dot(indirectRayDir)

						indirectLitColor = indirectHitPColor * lambert  #/ (2*math.pi*math.pow(indirectPointDist,2))
						indirectColor = indirectColor + indirectLitColor

				indirectColor = indirectColor / self.indirectSamples * 2 * math.pi
				matColor = currentObj.material.diffuseColor
				hitPointColor = hitPointColor + indirectColor.colorMult(matColor) * 0.3  #arbitrary contribution multiplier

		return hitPointColor

	def getHitPointColor(self,hitResult):
		litColor = Vector(0,0,0) #color accumulated after being lit

		#iterate through all the lights using shadow ray, check if object is in shadow
		for eachLight in self.scene.lights:
			for i in range(eachLight.samples):
				if "AreaLight" in eachLight.type:
					shadowRayDir = eachLight.getRandomSample() - hitResult[1]
					if eachLight.isDoubleSided == False:
						#single side area light
						hitLightBack = shadowRayDir.normalized().dot(eachLight.normal)
						if hitLightBack > 0:
							break #this is a cheat, only works for disk of planeLight
							#continue
				else:
					shadowRayDir = eachLight.pos - hitResult[1]
	 			#lambert is the cosine
				lambert = hitResult[2].dot(shadowRayDir.normalized())
				facingCam = hitResult[2].dot((self.cam.pos - hitResult[1]).normalized())
				if lambert < 0 and facingCam < 0:
					#poly is not facing the light or cam
					lambert = abs(lambert)

				if lambert > 0:
					#poly is facing the light
					offsetOrigin = hitResult[1] + shadowRayDir.normalized() * self.bias #slightly offset the ray start point because the origin itself is a root
					shadowRay = Ray(offsetOrigin,shadowRayDir)
					temp_t = shadowRayDir.length() #length form hit point to light
					shadowRayResult = [temp_t]
					inShadow = self.scene.getClosestIntersection(shadowRay,shadowRayResult,eachLight)
					if not inShadow:
						litColor = litColor + eachLight.color * (eachLight.intensity * lambert / (4*math.pi*math.pow(temp_t,2)))

			litColorAvg = litColor / eachLight.samples * eachLight.area

		matColor = self.scene.getObjectById(hitResult[3]).material.diffuseColor

		return Vector(matColor.x * litColorAvg.x, matColor.y * litColorAvg.y,matColor.z * litColorAvg.z)
