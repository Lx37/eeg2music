# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import numpy as np
import time

from util import *

import udp


class SimpleScopefft(QWidget):
    def __init__(self, threadacquisition=None, parent = None,
                        scope_size = 512, fft_size = 512, port = 9001):
        super(SimpleScopefft, self).__init__(parent)
        
        self.port = port
        
        self.threadacquisition = threadacquisition
        self.scope_size = scope_size
        self.fft_size = fft_size
        
        self.mainlayout = QGridLayout()
        self.setLayout(self.mainlayout)
        self.setWindowTitle("Channel scope, fft and power band")

        self.combo = QComboBox()
        self.mainlayout.addWidget(QLabel('Channels'))
        self.mainlayout.addWidget(self.combo)
        
        #Time representation
        self.canvas_time = SimpleCanvas()
        self.mainlayout.addWidget(self.canvas_time, 2, 0)
        self.ax_time = self.canvas_time.fig.add_subplot(1,1,1)
        
        #Power spectrum
        self.canvas_fft = SimpleCanvas()
        self.mainlayout.addWidget(self.canvas_fft, 2, 1)
        self.ax_fft = self.canvas_fft.fig.add_subplot(1,1,1)
        
        self.comboBand = QComboBox()
        self.mainlayout.addWidget(QLabel('Select the power band to send'))
        self.mainlayout.addWidget(self.comboBand,4,0)
        
        #Power in frequency band
        self.band_name=['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma']
        #self.freqs = arange(p['f_start'],p['f_stop'],p['deltafreq'])
        self.ialpha = 0
        self.band = np.zeros((5,self.scope_size), dtype = 'f')
        #self.beta = np.zeros((self.scope_size), dtype = 'f')
        #self.gamma = np.zeros((self.scope_size), dtype = 'f')
        
        #display selected band
        self.canvas_select_powband = SimpleCanvas()
        self.mainlayout.addWidget(self.canvas_select_powband, 5, 0)
        self.ax_select_powband = self.canvas_select_powband.fig.add_subplot(1,1,1)
        
        #display all band
        self.canvas_powband = SimpleCanvas()
        self.mainlayout.addWidget(self.canvas_powband,5, 1)
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
        
        if self.comboBand.count()==0:
            self.comboBand.addItems(self.band_name)
        id_band = self.comboBand.currentIndex()
  
  
        #Time representation
        s_time = self.threadacquisition.buffer[-self.scope_size:, channel]
        self.ax_time.clear()
        self.ax_time.set_title('Signal over samples')
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
        #Delta
        ind = (self.freqs>1.) & (self.freqs<=4.)
        self.idelta = np.sum([f[ind]])
        #Theta
        ind = (self.freqs>4.) & (self.freqs<=8.)
        self.itheta = np.sum([f[ind]])
        #Alpha
        ind = (self.freqs>8.) & (self.freqs<=12.)
        self.ialpha = np.sum([f[ind]])
        #Beta
        ind = (self.freqs>12.) & (self.freqs<=24.)
        self.ibeta = np.sum([f[ind]])
        #Gamma
        ind = (self.freqs>24.) & (self.freqs<=45.)
        self.igamma = np.sum([f[ind]])
        
        b = np.array([[self.idelta, self.itheta, self.ialpha, self.ibeta, self.igamma]])
        self.band = np.concatenate( [self.band, b.T], axis = 1)
        self.band = self.band[-self.scope_size:] 
        
        color_band = ['r','b','g','y','m']
        self.ax_powband.clear()

        for i in range (0,len(self.band)):
            self.ax_powband.plot(self.band[i,-20:], color = color_band[i])
        self.ax_powband.set_title('Pow in Delta(red)-Theta(blue)-Alpha(green)-Beta(yellow)-Gamma(magenta)')
        self.ax_powband.set_ylabel('Power')
        self.ax_powband.set_xlabel('Windows')
        
        self.canvas_powband.draw()
        
        #Selected band
        self.ax_select_powband.clear()
        self.ax_select_powband.plot(self.band[id_band,-20:], color = color_band[id_band])
        self.canvas_select_powband.draw()
        
        udp.send(self.port, str(int(b[0,id_band])))


        

def test_SimpleScopefft():
    from acquisition import FakeThreadAcquisition
    
    app = QApplication([])
    t = FakeThreadAcquisition()
    t.start()
   # w = SimpleScopefft(threadacquisition = t, scope_size = 1345)
   # w.show()
    
    w1 = SimpleScopefft(threadacquisition = t)
    w1.show()

    app.exec_()
    
    




if __name__ == '__main__':
    test_SimpleScopefft()
    
    

    