#python ray tracing implementation challenge
#shawn / Aug 2017
#-------------------------
#Some stuff can be easily missing:
#1. keep in mind when using tan/cos/sin, use radians not degrees

#-------------------------

import sys, math, random, multiprocessing, numpy


#------------------------
from Vector import Vector
from Ray import Ray
from Sphere import Sphere
from Plane import Plane
from Camera import Camera
from Light import Light
from ObjectList import ObjectList
from RenderWindow import RenderWindow
from RenderProcess import RenderProcess


def main():
	#-------canvas size-----
	width = 600
	height = 600

	renderView = RenderWindow(width,height)

	#-------Scene--------
	#important! This is a right handed coordinate system!
	sphere01 = Sphere(Vector(-15,-30,-136),20)
	sphere02 = Sphere(Vector(10,-20,-136),30)
	plane01 = Plane(Vector(0,-50,-136),10,Vector(0,1,0))
	plane02 = Plane(Vector(-50,0,-136),10,Vector(1,0,0))
	plane03 = Plane(Vector(0,0,-186),10,Vector(0,0,1))
	plane04 = Plane(Vector(50,0,-136),10,Vector(-1,0,0))
	plane05 = Plane(Vector(0,50,-136),10,Vector(0,-1,0))
	objects = ObjectList([sphere01,sphere02,plane01,plane02,plane03,plane04,plane05])
	cam = Camera(Vector(0,0,0),Vector(0,0,1),60)

	renderView.startRender(objects,cam)
	
	
	sys.exit(renderView.app.exec_())


if __name__ == "__main__":
	main()