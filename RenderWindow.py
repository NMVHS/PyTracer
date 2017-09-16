import sys,multiprocessing,numpy
from PyQt5.QtWidgets import QApplication, QWidget, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem
from PyQt5.QtGui import QImage, QPixmap, QColor
from RenderProcess import RenderProcess


class RenderWindow:
	def __init__(self,width,height):
		#-------ui initialization-------
		self.app = QApplication(sys.argv)
		self.window = QWidget()
		self.window.setFixedSize(width,height)
		self.window.move(50,50)
		self.window.setWindowTitle('PyTracer')
		self.width = width
		self.height = height

		#-----initialize a QImage, so we can maniputalte the pixels
		self.renderImage = QImage(width,height,4) #QImage.Format_RGB32
		self.graphic = QGraphicsScene(0,0,width,height,self.window)

		self.pixmap = QPixmap().fromImage(self.renderImage)
		self.graphicItem = self.graphic.addPixmap(self.pixmap)

		self.graphicView = QGraphicsView(self.graphic,self.window)
		self.window.show()


	def setPixel(self,x,y,color):
		self.renderImage.setPixel(x,y,QColor(color.x,color.y,color.z).rgba())

	def getBucket(self,processCnt):
		#input the process count, return the starting point of each bucket
		startLine = []
		bucketHeight = int(self.height / processCnt)
		for i in range(0,processCnt):
			startLine.append(bucketHeight * i)

		return startLine, bucketHeight

	def startRender(self,scene,cam):
		#start render in a new thread
		processCnt = multiprocessing.cpu_count()
		startLine,bucketHeight = self.getBucket(processCnt)
		jobs = []
		jobsQueue = multiprocessing.Queue()
		for i in range(processCnt):
			job = RenderProcess(jobsQueue,i,self.width,self.height,startLine[i],bucketHeight,scene,cam)
			jobs.append(job)

		for each in jobs:
			each.start()

		bucketArrays = [jobsQueue.get() for each in jobs]

		# for each in self.jobs: #This has to be after Queue.get() or simply don't join
		# 	each.join()

		bucketArrays.sort(key = self.getOrderKey)
		bucketArrays = [r[1] for r in bucketArrays]

		#merge the arrays into one
		mergedArrays = numpy.vstack(bucketArrays) #merged along second axis
		#numpy.require(mergedArrays,numpy.float32,"C")

		#convert array to QImage
		newImage = QImage(mergedArrays.data,self.width,self.height,mergedArrays.strides[0],QImage.Format_RGB888)

		self.update(newImage)

	def getOrderKey(self,elem):
		return elem[0]

	def update(self,image):
		#update the render view, note the render is in another thread
		self.pixmap = QPixmap().fromImage(image)
		self.graphicItem.setPixmap(self.pixmap)
		image.save("test.png")
		print("Render finished")

	def getPixColor(self,pixData):
		#get the signal from the render thread
		self.setPixel(pixData[0],pixData[1],pixData[2])
		#print("Pixel set successfully----------")
