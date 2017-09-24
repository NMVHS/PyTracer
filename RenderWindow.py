import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem
from PyQt5.QtGui import QPainter, QImage, QPixmap, QColor
from RenderThread import RenderThread

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
		self.bgImage = QImage(width,height,4) #QImage.Format_RGB32
		self.bgImage.fill(QColor(0,0,0)) # important, give canvas a default color

		self.graphic = QGraphicsScene(0,0,width,height,self.window)
		self.pixmap = QPixmap().fromImage(self.bgImage)
		self.graphicItem = self.graphic.addPixmap(self.pixmap)
		self.painter = QPainter(self.pixmap)

		self.graphicView = QGraphicsView(self.graphic,self.window)
		self.window.show()

	def startRender(self,scene,cam):
		#start render in a new thread
		self.renderTask = RenderThread(self.width,self.height,scene,cam)
		self.renderTask.finished.connect(self.saveImage)
		self.renderTask.updateImgSignal.connect(self.update)
		self.renderTask.start()

	def update(self,bucketDataList):
		#update the render view, note the render is in another thread]
		#use QPainter to stamp the image to canvas
		self.painter.drawImage(bucketDataList[0],bucketDataList[1],bucketDataList[2])
		self.graphicItem.setPixmap(self.pixmap)

		print("Bucket "+ str(bucketDataList[0]) +":"+ str(bucketDataList[1])+" Updated")

	def saveImage(self):
		self.pixmap.save("test.png")
		print("Image Saved")
