# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import numpy as np
import time

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar2
from matplotlib.figure import Figure


import socket


theta1 = 4
theta2 = 8
alpha1 = 8
alpha2 = 12



class SimpleCanvas(FigureCanvas):
    def __init__(self, parent=None, ):
        self.fig = Figure()
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                    QSizePolicy.Expanding,
                    QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        color = self.palette().color(QPalette.Background).getRgb()
        color = [ c/255. for c in color[:3] ]
        self.fig.set_facecolor(color)
       

class SimpleCanvasAndTool(QWidget):
    def __init__(self  , parent = None , ):
        QWidget.__init__(self, parent)
        self.mainLayout = QGridLayout()
        self.setLayout(self.mainLayout)

        self.canvas = SimpleCanvas()
        self.fig = self.canvas.fig
        self.toolbar = NavigationToolbar2(self.canvas , parent = self ,  )
        
        self.mainLayout.addWidget(self.toolbar)
        self.mainLayout.addWidget(self.canvas)
    
    
def test_SimpleCanvasAndTool():
    app = QApplication([])
    w1 = SimpleCanvasAndTool()
    w1.show()
    ax = w1.fig.add_subplot(1,1,1)
    ax.plot(np.random.randn(50000))
    w1.canvas.draw()

    app.exec_()




class SimpleScopefft(QWidget):
    def __init__(self, threadacquisition=None, parent = None,
                        scope_size = 512, fft_size = 512):
        super(SimpleScopefft, self).__init__(parent)
        
        self.threadacquisition = threadacquisition
        self.scope_size = scope_size
        self.fft_size = fft_size
        
        self.mainlayout = QGridLayout()
        self.setLayout(self.mainlayout)
        
        self.setWindowTitle("Channel scope, fft and power band")

        self.combo = QComboBox()
        self.mainlayout.addWidget(self.combo)
        
        #Time representation
        self.canvas_time = SimpleCanvas()
        self.mainlayout.addWidget(self.canvas_time, 1, 0)
        self.ax_time = self.canvas_time.fig.add_subplot(1,1,1)
        
        #Power spectrum
        self.canvas_fft = SimpleCanvas()
        self.mainlayout.addWidget(self.canvas_fft, 1, 1)
        self.ax_fft = self.canvas_fft.fig.add_subplot(1,1,1)
        
        #Power in frequency band
        self.ialpha = 0
        self.alpha = np.zeros((self.scope_size), dtype = 'f')
        self.theta = np.zeros((self.scope_size), dtype = 'f')
        self.canvas_powband = SimpleCanvas()
        self.mainlayout.addWidget(self.canvas_powband, 2, 0)
        self.ax_powband = self.canvas_powband.fig.add_subplot(1,1,1)

        #Refresh
        self.timer = QTimer(singleShot = False, interval = 100)
        self.timer.timeout.connect(self.refresh)
        self.timer.start()
        
    
    def refresh(self):
        if self.combo.count()==0:
            self.combo.addItems(self.threadacquisition.channelNames)
            self.freqs = np.fft.fftfreq(self.fft_size, self.threadacquisition.samplingInterval)
        channel = self.combo.currentIndex()
  
        #Time representation
        s_time = self.threadacquisition.buffer[-self.scope_size:, channel]
        self.ax_time.clear()
        self.ax_time.set_title('Signal over time')
        self.ax_time.set_ylabel('Amplitude')
        self.ax_time.set_xlabel('Samples')
        self.ax_time.plot(s_time, color = 'r')
        self.ax_time.set_xlim(0,self.scope_size)
##         self.ax_time.set_ylim(,1024)
        
        self.canvas_time.draw()
    
        #Power spectrum
        s_fft = self.threadacquisition.buffer[-self.fft_size:, channel]
        f = abs(np.fft.fft(s_fft))
        self.ax_fft.clear()
        self.ax_fft.plot(self.freqs[1:self.fft_size//2], f[1:self.fft_size//2], color = 'g')
        self.ax_fft.set_title('Corresponding power spectrum')
        self.ax_fft.set_ylabel('Power')
        self.ax_fft.set_xlabel('Frequency (Hz)')
##         self.ax_fft.set_xlim(0,self.scope_size)
##         self.ax_fft.set_ylim(,1024)
        
        self.canvas_fft.draw()
        
        
        #Power in frequency band
        # alpha
        self.ialpha = np.sum([f[alpha1:alpha2]])/(alpha2-alpha1)
        self.alpha = np.concatenate( [self.alpha, [self.ialpha]], axis = 0)
        self.alpha = self.alpha[-self.scope_size:] 
        
        self.itheta = np.sum([f[theta1:theta2]])/(theta2-theta1)
        self.theta = np.concatenate( [self.theta, [self.itheta]], axis = 0)
        self.theta = self.theta[-self.scope_size:] 
        
        self.ax_powband.clear()
        self.ax_powband.plot(self.alpha[-20:], color = 'g')
        self.ax_powband.plot(self.theta[-20:], color = 'b' )
        self.ax_powband.set_title('Power spectrum in alpha (green) and theta (blue)')
        self.ax_powband.set_ylabel('Power')
        self.ax_powband.set_xlabel('Windows')
        
        self.canvas_powband.draw()
        

    def send(self):
    # send data to pure data

        UDP_IP = "127.0.0.1"
        UDP_PORT = self.port
        
        if self.message == "alpha":
            MESSAGE = str(int(self.ialpha))                
                
 
        print "UDP target IP:", UDP_IP
        print "UDP target port:", UDP_PORT
        print "message:", MESSAGE

        sock = socket.socket( socket.AF_INET, # Internet
                        socket.SOCK_DGRAM ) # UDP
        sock.sendto( MESSAGE, (UDP_IP, UDP_PORT) )
        

def test_SimpleScopefft():
    
    class FakeThreadAcquisition(QThread):
        channelCount = 4
        channelNames = ['a', 'b', 'c', 'd']
        samplingInterval = 0.002
        
        
        def __init__(self, parent = None,):
            super(FakeThreadAcquisition, self).__init__()
            self.buffer = np.random.random((2048, 4))
            
        def run(self):
            while True:
                self.buffer = np.random.random((2048,4))
                self.buffer[:,2] += np.sin(np.arange(2048)*0.002*2*np.pi*50.)*0.2
                self.buffer[:,3] += np.sin(np.arange(2048)*0.002*2*np.pi*10.)*0.2
                time.sleep(0.1)
        
    
    app = QApplication([])
    t = FakeThreadAcquisition()
    t.start()
   # w = SimpleScopefft(threadacquisition = t, scope_size = 1345)
   # w.show()
    
    w1 = SimpleScopefft(threadacquisition = t)
    w1.show()
    w1.port = 9001
    w1.message = "alpha" #w1.ialpha
    
    #send udp timer
    timer_udp = QTimer(singleShot = False, interval = 100)
    timer_udp.timeout.connect(w1.send)
    timer_udp.start()


    app.exec_()
    
    




if __name__ == '__main__':
    #~ test_SimpleCanvasAndTool()
    test_SimpleScopefft()
    
    

    