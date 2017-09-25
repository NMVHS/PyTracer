from Geo.Triangle import Triangle
from Geo.Geometry import Geometry
from Geo.Material import Material

class Quad(Geometry):
    def __init__(self,p0,p1,p2,p3,material = Material()):
        #Quad is 2 triangles, define in a counter-clockwise order
        self.triList = [Triangle(p0,p1,p2),Triangle(p0,p2,p3)]
        self.material = material
        self.type = "Quad"

    def getIntersection(self,ray,closestHit,result):
        for eachTri in self.triList:
            if eachTri.getIntersection(ray,closestHit,result):
                #Important, overide object Id, otherwise the id of triangle will be returned, which is 0
                result[3] = self.objectId
                return True

        return False
