# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import Qt

import numpy as np
#import time

from util import *

from ScopeView import viewScope

#qtA = Qt.QApplication(sys.argv)

class simpleSignalProcess(QWidget):
    def __init__(self, threadacquisition=None, parent = None,
                        scope_size = 512, fft_size = 512):
        super(simpleSignalProcess, self).__init__(parent)
                
        self.threadacquisition = threadacquisition
	self.feature = ['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma']
	self.port = np.arange(9001,9010,1)
	self.portS = map(str, self.port)
        
        self.scope_size = scope_size
        self.fft_size = fft_size
        #sels_fft = np.zeros(self.fft_size, dtype = 'f')
	
	self.setWindowTitle("Processing Scope")
        self.mainlayout = QGridLayout()
        self.setLayout(self.mainlayout)
	
	self.comboCh = [ QComboBox() for i in range(len(self.feature)) ]
	self.comboF = []
	self.comboP = []
	self.Vbutton = []
	self.Sbutton = []
	
	self.featureData = []
	
	self.config = np.zeros((len(self.feature),3))
	# configuration window : choose channel, parametre and port
	self.mainlayout.addWidget(QLabel('Channel :'),1,0)
	self.mainlayout.addWidget(QLabel('Feature :'),1,2)
	self.mainlayout.addWidget(QLabel('Port :'),1,4)
	
	for i in range (len(self.feature)):
		
		#self.mainlayout.addWidget(QLabel('Channel :'),i+1,0)
		self.mainlayout.addWidget(self.comboCh[i],i+2,0)
	
		self.comboF.append(QComboBox())
		#self.mainlayout.addWidget(QLabel('Feature :'),i+1,2)
		self.mainlayout.addWidget(self.comboF[i],i+2,2)
	
		self.comboP.append(QComboBox())
		#self.mainlayout.addWidget(QLabel('Port :'),i+1,4)
		self.mainlayout.addWidget(self.comboP[i],i+2,4)
	
		self.Vbutton.append(QPushButton("View",None))
		self.mainlayout.addWidget(self.Vbutton[i],i+2,5)
		self.Vbutton[i].connect(self.Vbutton[i],SIGNAL("clicked()"), self.view_scope)
		
		self.Sbutton.append(QPushButton("Start Sending",None))
		self.mainlayout.addWidget(self.Sbutton[i],i+2,6)
	
	self.threadacquisition.new_buffer.connect(self.refresh)
        
        
    
    def refresh(self):
	
	for i in range (len(self.feature)):
	
		if self.comboCh[i].count()==0:
			self.comboCh[i].addItems(self.threadacquisition.channelNames)
			self.comboCh[i].setCurrentIndex(i); 
		self.config[i,0]=(self.comboCh[i].currentIndex ())
	
		if self.comboF[i].count()==0:
			self.comboF[i].addItems(self.feature)
			self.comboF[i].setCurrentIndex(i); 
		self.config[i,1] = (self.comboF[i].currentIndex ())
	
		if self.comboP[i].count()==0:
			self.comboP[i].addItems(self.portS)
			self.comboP[i].setCurrentIndex(i)
		self.config[i,2] = self.comboP[i].currentIndex ()
  
        #s = self.threadacquisition.buffer[-self.scope_size:, ch1]
        #self.ax.clear()
        #self.ax.plot(s, color = 'r')
        #self.ax.set_xlim(0,self.scope_size)
        
        #self.canvas.draw()
    
        #To do Feature evaluation spectrum
        

    
    def view_scope(self,i):
	
	print "entre dans viewscop"
	#vp = viewScope(self.threadacquisition.buffer[-self.fft_size:, self.config[i,0]], self.featureData[i] )
		
	
	    
		
    

def test_signalProcess():
    from acquisition import FakeThreadAcquisition
    
    app = QApplication([])
    t = FakeThreadAcquisition()
    t.start()
   
    sp1 = simpleSignalProcess(threadacquisition = t)
    sp1.show()

    app.exec_()


if __name__ == '__main__':
    test_signalProcess()
  
    