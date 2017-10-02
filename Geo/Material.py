from Geo.Vector import Vector

class Material:
    def __init__(self,diffuseColor=Vector(0.18,0.18,0.18),diffuseWeight = 1.0,
                reflectionColor=Vector(1,1,1),reflectionWeight = 0,reflectionRoughness=0,
                emissionColor=Vector(1,1,1),emissionAmount=0):
        #Default material values
        self.diffuseColor = diffuseColor
        self.diffuseWeight = diffuseWeight
        self.reflectionColor = reflectionColor
        self.reflectionWeight = reflectionWeight
        self.reflectionRoughness = reflectionRoughness
        self.emissionColor = emissionColor
        self.emissionAmount = emissionAmount
