import multiprocessing
import numpy as np
from datetime import datetime
from PyQt5.QtGui import QImage, QColor
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from RenderProcess import RenderProcess

class RenderThread(QThread):
	#This is a separate thread from UI, this thread will spawn tasks to multi processing
	#This thread itself will be rendering as well
	updateImgSignal =pyqtSignal(QImage)

	def __init__(self,width,height,scene,cam):
		QThread.__init__(self)
		self.width = width
		self.height = height
		self.scene = scene
		self.cam = cam
		self.canvas = np.ndarray(shape=(self.height,self.width,3),dtype = np.float)

	def getBucket(self,processCnt):
		#input the process count, return the starting point of each bucket
		startLine = []
		bucketHeight = int(self.height / processCnt)
		for i in range(0,processCnt):
			startLine.append(bucketHeight * i)

		return startLine, bucketHeight

	def getOrderKey(self,elem):
		return elem[0]

	def run(self):
		processCnt = multiprocessing.cpu_count()
		print("Available Processors: " + str(processCnt))

		startLine,bucketHeight = self.getBucket(processCnt)
		jobs = []
		jobsQueue = multiprocessing.Queue()

		for i in range(processCnt):
			job = RenderProcess(jobsQueue,self.width,self.height,0,startLine[i],bucketHeight,self.scene,self.cam)
			jobs.append(job)

		timerStart = datetime.now()
		for each in jobs:
			each.start()

		bucketData = [jobsQueue.get() for each in jobs]
		#This has to be after Queue.get() or simply don't join
		#Update: join() --- wait till all the processes finish, then move on
		for each in jobs:
			each.join()

		timerEnd = datetime.now()
		renderTime = timerEnd - timerStart
		print("Total Render Time: " + str(renderTime))

		# bucketArrays.sort(key = self.getOrderKey)
		# bucketArrays = [r[1] for r in bucketArrays]
		for eachData in bucketData:
			#print("----till here")
			dataX = eachData[0]
			dataY = eachData[1]
			self.canvas[dataY:dataY+bucketHeight,dataX:600] += bucketData[2]

		"""
		#merge the arrays into one
		#mergedArrays = np.vstack(bucketArrays) #merged along second axis
		#np.require(mergedArrays,np.float32,"C")

		#Apply 2.2 gamma correction and convert sRGB, in order to convert it to Qimage, array type has to be uint8
		self.canvas = (np.power(self.canvas,1/2.2) * 255).astype(np.uint8)

		#convert array to QImage
		newImage = QImage(self.canvas.data,self.width,self.height,self.canvas.strides[0],QImage.Format_RGB888)
		newImage.save("test.png") #Image has to be save in this thread
		self.updateImgSignal.emit(newImage)
		# self.update(newImage)
		"""
