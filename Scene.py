class Scene:
	def __init__(self,objects):
		self.geo = objects['geometry'] #a list of objects, can include spheres, planes, and others
		self.shuffleObjectId()
		self.lights = objects['light']

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

	def getObjectById(self,id):
		return self.geo[id]

	def getClosestIntersection(self,ray,result):
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
					break

		result.extend(closestHitResult)
		return hitBool
