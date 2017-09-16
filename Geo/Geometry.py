from Material import Material

class Geometry:
    #This is a common attibute class, all geometris should inherit this class
    def __init__(self,objectId=0,material=Material()):
        #Object ID is an integer, and is unique
        self.objectId = objectId
        self.material = material

    def getObjectId(self):
        return self.objectId
