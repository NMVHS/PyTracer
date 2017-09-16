#python ray tracing implementation challenge
#shawn / Aug 2017
#-------------------------
#Some stuff can be easily missing:
#1. keep in mind when using tan/cos/sin, use radians not degrees

#-------------------------

import sys, math, random, multiprocessing, numpy


#------------------------
from Geo.Vector import Vector
from Geo.Ray import Ray
from Geo.Sphere import Sphere
from Geo.Plane import Plane
from Geo.Material import Material
from Geo.Geometry import Geometry

from Camera import Camera
from Light import Light
from Scene import Scene
from RenderWindow import RenderWindow
from RenderProcess import RenderProcess


def main():
	#-------canvas size-----
	width = 600
	height = 600

	renderView = RenderWindow(width,height)

	redLambert = Material(diffuseColor=Vector(1,0,0))
	blueLambert = Material(diffuseColor=Vector(0,0,1))
	#-------Scene--------
	#important! This is a right handed coordinate system!
	sphere01 = Sphere(Vector(-15,-30,-136),20)
	sphere02 = Sphere(Vector(10,-20,-136),30)
	plane01 = Plane(Vector(0,-50,-136),10,Vector(0,1,0)) #bottom wall
	plane02 = Plane(Vector(-50,0,-136),10,Vector(1,0,0),redLambert) #left wall
	plane03 = Plane(Vector(0,0,-186),10,Vector(0,0,1)) #back wall
	plane04 = Plane(Vector(50,0,-136),10,Vector(-1,0,0),blueLambert) #right wall
	plane05 = Plane(Vector(0,50,-136),10,Vector(0,-1,0)) #top wall
	light01 = Light(Vector(0,40,-136),5) #light source on the top
	light02 = Light(Vector(-20,40,-100),5)

	newScene = Scene({"geometry":[sphere01,sphere02,plane01,plane02,plane03,plane04,plane05],"light":[light01,light02]})

	cam = Camera(Vector(0,0,0),Vector(0,0,1),60)

	renderView.startRender(newScene,cam)


	sys.exit(renderView.app.exec_())


if __name__ == "__main__":
	main()
