#python ray tracing implementation challenge
#shawn / Aug 2017
#-------------------------
#Some stuff can be easily missing:
#1. keep in mind when using tan/cos/sin, use radians not degrees
#2. scene unit: cm

#-------------------------
import sys, math, multiprocessing, numpy
from PyQt5.QtWidgets import QApplication
#------------------------
from Geo.Vector import Vector
from Geo.Ray import Ray
from Geo.Sphere import Sphere
from Geo.Plane import Plane
from Geo.Triangle import Triangle
from Geo.Quad import Quad
from Geo.Disk import Disk
from Geo.Material import Material
from Geo.Geometry import Geometry

from Camera import Camera
from Light import PointLight, DiskLight
from Scene import Scene
from RenderWindow import RenderWindow


def main():
	renderApp = QApplication(sys.argv)
	renderView = RenderWindow() #All setting loaded from json file

	#--------------------Scene Modeling-------------------------------
	#Materials--------------------------------------------
	redLambert = Material(diffuseColor=Vector(0.9,0.1,0.1))
	blueLambert = Material(diffuseColor=Vector(0,0,0.9))
	greenLambert = Material(diffuseColor=Vector(0.1,0.9,0.1))
	whiteLambert = Material(diffuseColor=Vector(0.9,0.9,0.9))
	yellowLambert = Material(diffuseColor=Vector(0.95,0.4,0.0))
	lightBlueLambert = Material(diffuseColor=Vector(0.1,0.5,0.9))
	mirror = Material(reflectionColor=Vector(1,1,1),reflectionWeight=1)
	redMirror = Material(reflectionColor=Vector(0.9,0,0),reflectionWeight=1)
	emissive = Material(emissionAmount=500)
	glass = Material(refractionWeight=1,reflectionWeight=1)

	#Geometries----------------------------------------------
	#important! This is a right handed coordinate system! Scene unit: cm!!!
	sphere01 = Sphere(Vector(-15,-30,-136),20,material=whiteLambert)
	sphere02 = Sphere(Vector(10,-20,-146),30,material=mirror)
	sphere03 = Sphere(Vector(-25,-35,-115),15,material=glass)
	sphere04 = Sphere(Vector(25,-35,-100),15,material=whiteLambert)
	#plane01 = Plane(Vector(0,-50,-136),Vector(0,1,0),material=whiteLambert) #bottom wall
	#plane02 = Plane(Vector(-50,0,-136),Vector(1,0,0),material=redLambert) #left wall
	#plane03 = Plane(Vector(0,0,-186),Vector(0,0,1),material=whiteLambert) #back wall
	#plane04 = Plane(Vector(50,0,-136),Vector(-1,0,0),material=greenLambert) #right wall
	#plane05 = Plane(Vector(0,50,-136),Vector(0,-1,0),material=whiteLambert) #top wall
	tri01 = Triangle(Vector(30,40,-136),Vector(-10,20,-136),Vector(50,20,-156),material=glass)
	tri02 = Triangle(Vector(30,40,-146),Vector(50,20,-166),Vector(-10,20,-146),material=glass)
	disk01 = Disk(Vector(-30,30,-136),15,Vector(1,0,0),material=blueLambert)
	quad01 = Quad(Vector(-50,-50,-186),Vector(-50,-50,-76),Vector(50,-50,-76),Vector(50,-50,-186),material=whiteLambert) #bottom wall
	quad02 = Quad(Vector(-50,50,-76),Vector(-50,-50,-76),Vector(-50,-50,-186),Vector(-50,50,-186),material=yellowLambert) #left wall
	quad03 = Quad(Vector(-50,50,-186),Vector(-50,-50,-186),Vector(50,-50,-186),Vector(50,50,-186),material=whiteLambert)  #back wall
	quad04 = Quad(Vector(50,50,-186),Vector(50,-50,-186),Vector(50,-50,-76),Vector(50,50,-76),material=lightBlueLambert) #right wall
	quad05 = Quad(Vector(-50,50,-76),Vector(-50,50,-186),Vector(50,50,-186),Vector(50,50,-76),material=whiteLambert) #top wall
	quad06 = Quad(Vector(-50,20,-76),Vector(-50,20,-186),Vector(30,20,-186),Vector(30,20,-76),material=whiteLambert) #top matte

	#Lights-------------------------------------------------------
	light01 = DiskLight(Vector(0,48,-136),30,normal=Vector(0,-1,0),samples=1,isDoubleSided=True,visible=True) #light source on the top
	light02 = PointLight(Vector(-20,40,-120))
	light03 = PointLight(Vector(20,30,-90))

	newScene = Scene({"geometry":[quad01,quad02,quad03,quad04,quad05,sphere02,sphere03,sphere04],"light":[light01]})

	wideCam = Camera(Vector(0,0,0),Vector(0,0,1),32,aperture=2.8,focusDist=113,filmFit="Horizontal")
	teleCam = Camera(Vector(0,0,130),Vector(0,0,1),80,aperture=1.4,focusDist=243,filmFit="Horizontal")
	renderView.startRender(newScene,teleCam)

	sys.exit(renderApp.exec_())


if __name__ == "__main__":
	main()
