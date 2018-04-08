import sys
import shutil
import os
import glob
import traceback
import time
import numpy as np
from PyQt4 import uic
from scipy.io import wavefile
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import pyaudio

class RecorderThread(QThread):
	def __init__(self,main):
		QThread.__init__(self)
		self.main = main

	def run(self):
		self.start_time = time.time()
		while True:
			data = self.main.stream.read(1)
			i = ord(data[0]) + 256 * ord(data[1])
			if i > 32768:
				i -= 65536
			stop = self.main.add_record_data(i)
			if stop:
				break

class GUI(QMainWindow):

	def __init__(self):
		uic.loadUi("gui.ui",self)
		self.statusBar()
		self.timer.timeout.connect(self.timer_callback)
		self.enrollRecord.clicked.connect(self.start_enroll_record)
		self.stopEnrollRecord.clicked.connect(self.stop_enroll.record)
		self.enroll.clicked.connect(self._enroll)

	def start_enroll_record(self):
		self.enroll_wav = None
		self.senroll_file_name.setText("")
		self.start_record()

	def start_record(self):
		self.pyaudio = pyaudio.PyAudio()
		self.status("Recording")
		self.recordData = []
		self.stream = self.pyaudio.open(format=pyaudio.paInt16,channels=1,rate=8000,input=True,frames_per_buffer=1)
		self.stopped = False
		self.record_thread = RecorderThread(self)
		self.record_thread.start()
		self.timer.start(1000)
		self.record_time = 0
		self.update_all_timer()

	def update_all_timer(self):
		time_string = time_string(self.record_time)

	def time_string(seconds):
		minutes = int(seconds/60)
		sec = int(seconds % 60)
		return("{:02d}:{02d}".format(minutes,sec))

	def add_record_data(self,i):
		self.recordData.append(i)
		return self.stopped

	def stop_enroll_record(self):
		self.stop_record()
		print(self.recordData[:300])
		signal = np.array(self.recordData,dtype=NPDtype)
		self.enroll_wav = (8000,signal)
		write_wav("enroll.wav",*self.enroll_wav)

	def stop_record(self):
		self.stopped = True
		self.record_thread.wait()
		self.timer.stop()
		self.stream.stop_stream()
		self.stream.close()
		self.pyaudio.terminate()
		self.status("Record stopped")

	def _enroll(self):
		name = self.Username.text().trimmed()
		if not name : 
			self.warn("Please Input Name")
			return
		new_signal = self.backend.filter(*self.enroll_wav)
		print("After removed : {0} -> {1}".format(len(self.enroll_wav[1]),len(new_signal)))
		print("Enroll: {.04f} seconds".format(float(len(new_signal))/8000))
		if len(new_signal)== 0:
			print("Error! Input is silent! Please enroll again")
			return
		self.backend.enroll(name,8000,new_signal)
		
def write_wav(file_name,frames_per_second,signal):
	wavefile.write(file_name,frames_per_second,signal)

if __name__ == "__main__":
	app = QApplication(sys.argv)
	QtCore.QCoreApplication.processEvents()
	gui_app = GUI()
	app.show()
	sys.exit(app.exec_())