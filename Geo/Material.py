from Geo.Vector import Vector

class Material:
    def __init__(self,diffuseColor=Vector(0.18,0.18,0.18),diffuseWeight = 1.0,
                reflectionColor=Vector(0,0,0),reflectionWeight = 0):
        #Default material values
        self.diffuseColor = diffuseColor
        self.diffuseWeight = diffuseWeight
        self.reflectionColor = reflectionColor
        self.reflectionWeight = reflectionWeight
