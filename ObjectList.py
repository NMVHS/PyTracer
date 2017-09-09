class ObjectList:
	def __init__(self,objects):
		self.geo = objects['geometry'] #a list of objects, can include spheres, planes, and others
		self.lights = objects['light']

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

