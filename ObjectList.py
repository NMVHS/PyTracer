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