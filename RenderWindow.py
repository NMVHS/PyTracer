import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem
from PyQt5.QtGui import QImage, QPixmap, QColor
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
		self.renderImage = QImage(width,height,4) #QImage.Format_RGB32
		self.graphic = QGraphicsScene(0,0,width,height,self.window)

		self.pixmap = QPixmap().fromImage(self.renderImage)
		self.graphicItem = self.graphic.addPixmap(self.pixmap)

		self.graphicView = QGraphicsView(self.graphic,self.window)
		self.window.show()

	def setPixel(self,x,y,color):
		self.renderImage.setPixel(x,y,QColor(color.x,color.y,color.z).rgba())

	def startRender(self,scene,cam):
		#start render in a new thread
		self.renderTask = RenderThread(self.width,self.height,scene,cam)
		#self.renderTask.finished.connect(self.update)
		self.renderTask.updateImgSignal.connect(self.update)
		self.renderTask.start()

	def update(self,image):
		#update the render view, note the render is in another thread
		self.pixmap = QPixmap().fromImage(image)
		self.graphicItem.setPixmap(self.pixmap)

		print("Render Window Updated")
