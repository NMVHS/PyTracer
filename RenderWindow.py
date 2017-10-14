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

		#-----initialize a QImage, so we can maniputalte the pixels
		self.bgImage = QImage(self.width,self.height,4) #QImage.Format_RGB32
		self.bgImage.fill(QColor(0,0,0)) # important, give canvas a default color

		self.graphic = QGraphicsScene(0,0,self.width,self.height,self)
		self.pixmap = QPixmap().fromImage(self.bgImage)
		self.graphicItem = self.graphic.addPixmap(self.pixmap)
		self.painter = QPainter(self.pixmap)

		self.graphicView = QGraphicsView(self.graphic,self)
		self.show()

	def loadSettings(self):
		with open("RenderSettings.json") as settingsData:
			renderSettings = json.load(settingsData)

		return renderSettings["RenderWindow"]

	def keyPressEvent(self,event):
		if event.key() == Qt.Key_S:
			self.saveImage()
		elif event.key() == Qt.Key_B:
			print("Show Buckets")

	def startRender(self,scene,cam):
		#start render in a new thread
		self.renderTask = RenderThread(self.width,self.height,scene,cam,)
		self.renderTask.finished.connect(self.saveImage)
		self.renderTask.updateImgSignal.connect(self.update)
		self.renderTask.start()

	def update(self,bucketDataList):
		#update the render view, note the render is in another thread]
		#use QPainter to stamp the image to canvas
		self.painter.drawImage(bucketDataList[0],bucketDataList[1],bucketDataList[2])
		self.graphicItem.setPixmap(self.pixmap)

		#print("Bucket "+ str(bucketDataList[0]) +":"+ str(bucketDataList[1])+" Updated")

	def saveImage(self):
		self.pixmap.save("test.png")
		print("Image Saved")
