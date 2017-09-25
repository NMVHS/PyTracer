from Geo.Material import Material

class Geometry:
    #This is a common attibute class, all geometris should inherit this class
    def __init__(self,material,objectId=0):
        #Object ID is an integer, and is unique
        self.objectId = objectId
        self.material = material
        self.type = "Geometry"

    def getObjectId(self):
        return self.objectId

    def getType(self):
        return self.type
