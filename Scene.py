class Scene:
	def __init__(self,objects):
		#a list of objects, can include spheres, planes.... and area lights
		self.geo = objects['geometry']
		self.lights = objects['light']
		self.sortLights()
		self.shuffleObjectId()

	def sortLights(self):
		for eachLight in self.lights:
			if "AreaLight" in eachLight.type:
				#Add this light to the geo list
				self.geo.append(eachLight)

	def checkObjectId(self):
		for each in self.geo:
			print(each.objectId)

	def shuffleObjectId(self):
		objId = 0
		for eachObj in self.geo:
			eachObj.objectId = objId
			objId += 1

	def checkSceneMaterial(self):
		for each in self.geo:
			mat = each.material.diffuseColor
			print(mat)

	def checkLightIntensity(self):
		for each in self.lights:
			print(each.intensity)

	def getObjectById(self,id):
		return self.geo[id]

	def getClosestIntersection(self,ray,result,currLight=None):
		#when checking secondary intersections, eg shadow ray
		#the input variable result may not be empty
		#if it's not empty, it contains the current hit_t
		hitBool = False
		closestHit = 1000000000000
		isShadowRay = False
		if len(result) > 0:
			closestHit = result[0]
			isShadowRay = True

		closestHitResult = []

		for obj in self.geo:
			if obj.getIntersection(ray,closestHit,result):
				hitBool = True
				closestHit = result[0] #closest t
				closestHitResult.clear()
				closestHitResult.extend(result)
				result.clear()
				if isShadowRay:
					currHitObj = self.getObjectById(closestHitResult[3])
					if "AreaLight" in currHitObj.type:
						if currHitObj == currLight:
							#if this object is the area light shadow ray is checking
							hitBool = False
						else:
							if currHitObj.visible == False:
								#if this area light is invisible
								hitBool = False
					# else:
					# 	if currHitObj.material.refractionWeight < 1:
					# 		#if this object is not transparent
					# 		break
					# 	else:
					# 		hitBool = False

		result.extend(closestHitResult)
		return hitBool
