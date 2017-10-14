from Geo.Plane import Plane
from Geo.Vector import Vector
from Geo.Material import Material
from Geo.Vector import Vector

class Disk(Plane):
    def __init__(self,pos,radius,normal,material=Material()):
        self.pos = pos
        self.radius = radius
        self.normal = normal

        super().__init__(self.pos,self.normal)
        self.material = material
        self.type = "Disk"

    def getIntersection(self,ray,closestHit,result):
        if Plane.getIntersection(self,ray,closestHit,result):
            #Check if this point is within the radius
            distToCenter = (result[1] - self.pos).length()

            if distToCenter <= self.radius:
                return True
            else:
                result.clear()
                return False
        else:
            result.clear()
            return False
