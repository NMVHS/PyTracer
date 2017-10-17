import sys, json
from PyQt5.QtWidgets import QWidget, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem
from PyQt5.QtGui import QPainter, QImage, QPixmap, QColor
from PyQt5.QtCore import Qt
from RenderThread import RenderThread

class RenderWindow(QWidget):
	def __init__(self):
		#loadSettings from json file
		windowSettings = self.loadSettings()
		self.width = windowSettings["ImageWidth"]
		self.height = windowSettings["ImageHeight"]

		#-------ui initialization-------
		super().__init__()
		self.setFixedSize(self.width,self.height)
		self.move(50,50)
		self.setWindowTitle('PyTracer')
		self.showBuckets = True #show bucket switch

		#-----initialize a QImage, so we can maniputalte the pixels
		self.bgImage = QImage(self.width,self.height,4) #QImage.Format_RGB32
		self.bgImage.fill(QColor(0,0,0)) # important, give canvas a default color
		self.bucketLocator = QImage("bucketLocator.png") #Bucket Locator Image

		self.graphic = QGraphicsScene(0,0,self.width,self.height,self)

		#Canvas-----
		self.canvasPixmap = QPixmap().fromImage(self.bgImage)
		self.canvasPainter = QPainter(self.canvasPixmap)

		#Render image pixmap and painter
		self.renderImagePixmap = QPixmap().fromImage(self.bgImage)
		self.renderImagePainter = QPainter(self.renderImagePixmap)

		#BuckerLocators pixmap and painter
		self.locatorPixmap = QPixmap().fromImage(self.bgImage)
		self.locatorPainter = QPainter(self.locatorPixmap)

		self.graphicItem = self.graphic.addPixmap(self.canvasPixmap)
		self.graphicView = QGraphicsView(self.graphic,self)
		self.show()

	def loadSettings(self):
		with open("RenderSettings.json") as settingsData:
			renderSettings = json.load(settingsData)

		return renderSettings["RenderWindow"]

	def keyPressEvent(self,event):
		if event.key() == Qt.Key_S:
			self.saveImage()
		elif event.key() == Qt.Key_H:
			if self.showBuckets:
				self.showBuckets = False
				print("Hide Buckets")
			else:
				self.showBuckets = True
				print("Show Buckets")

			self.refreshCanvas()

	def startRender(self,scene,cam):
		#start render in a new thread
		self.renderTask = RenderThread(self.width,self.height,scene,cam)
		self.renderTask.updateImgSignal.connect(self.updateRenderImage)
		self.renderTask.bucketProgressSignal.connect(self.showBucketProgess)
		self.renderTask.finished.connect(self.cleanBucketLocators)
		self.renderTask.finished.connect(self.saveImage)
		self.renderTask.start()

	def cleanBucketLocators(self):
		self.locatorPainter.drawImage(0,0,self.bgImage)
		self.refreshCanvas()

	def showBucketProgess(self,bucketProgressPos):
		bucketSize = bucketProgressPos[2]
		if len(bucketProgressPos) > 3:
			blackPatch = QImage(bucketSize,bucketSize,4)
			blackPatch.fill(0)
			self.locatorPainter.drawImage(bucketProgressPos[3],bucketProgressPos[4],blackPatch)
		bucketLocImg = self.bucketLocator.scaled(bucketSize,bucketSize)
		self.locatorPainter.drawImage(bucketProgressPos[0],bucketProgressPos[1],bucketLocImg)
		self.refreshCanvas()

	def updateRenderImage(self,bucketDataList):
		#update the render view, note the render is in another thread]
		#use QPainter to stamp the image to canvas
		self.renderImagePainter.drawImage(bucketDataList[0],bucketDataList[1],bucketDataList[2])
		self.refreshCanvas()
		#print("Bucket "+ str(bucketDataList[0]) +":"+ str(bucketDataList[1])+" Updated")

	def refreshCanvas(self):
		self.canvasPainter.drawPixmap(0,0,self.renderImagePixmap)
		if self.showBuckets:
			self.canvasPainter.setCompositionMode(12) #plus locator layer on top
			self.canvasPainter.drawPixmap(0,0,self.locatorPixmap)
			self.canvasPainter.setCompositionMode(0) #set comp mode back to over
		self.graphicItem.setPixmap(self.canvasPixmap)

	def saveImage(self):
		self.canvasPixmap.save("test.png")
		print("Image Saved")
