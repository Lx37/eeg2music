# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import time
import numpy as np

from util import *



class SimpleSpectrum(QWidget):
    def __init__(self, threadacquisition=None, parent = None,
                        fft_size = 512):
        super(SimpleSpectrum, self).__init__(parent)
        
        self.threadacquisition = threadacquisition
        self.fft_size = fft_size
        
        
        self.mainlayout = QVBoxLayout()
        self.setLayout(self.mainlayout)
        
        
        self.combo = QComboBox()
        self.mainlayout.addWidget(self.combo)
        
        self.canvas = SimpleCanvas()
        self.mainlayout.addWidget(self.canvas)
        self.ax = self.canvas.fig.add_subplot(1,1,1)
        
        self.timer = QTimer(singleShot = False, interval = 400)
        self.timer.timeout.connect(self.refresh)
        self.timer.start()
        
    
    def refresh(self):
        if self.combo.count()==0:
            self.combo.addItems(self.threadacquisition.channelNames)
            self.freqs = np.fft.fftfreq(self.fft_size, self.threadacquisition.samplingInterval)
        channel = self.combo.currentIndex()
        
        s = self.threadacquisition.buffer[-self.fft_size:, channel]
        self.ax.clear()
        
        f = abs(np.fft.fft(s))
        
        self.ax.plot(self.freqs[1:self.fft_size//2], f[1:self.fft_size//2], color = 'b')
##         self.ax.set_xlim(0,self.scope_size)
##         self.ax.set_ylim(,1024)
        
        self.canvas.draw()
        
        

def test_SimpleSpectrum():
    from acquisition import FakeThreadAcquisition
    
    app = QApplication([])
    t = FakeThreadAcquisition()
    t.start()
    w = SimpleSpectrum(threadacquisition = t, fft_size = 512)
    w.show()


    app.exec_()
    



if __name__ == '__main__':
    test_SimpleSpectrum()


