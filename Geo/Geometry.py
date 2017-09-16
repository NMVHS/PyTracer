from Material import Material

class Geomety:
    #This is a common attibute class, all geometris should inherit this class
    def __init__(self,objectId,material=Material()):
        #Object ID is an integer, and is unique
        self.objectId = 0
        self.material = material
