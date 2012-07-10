# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import numpy as np
import time

from util import *


class SimpleScope(QWidget):
    def __init__(self, threadacquisition=None, parent = None,
                        scope_size = 512):
        super(SimpleScope, self).__init__(parent)
        
        self.threadacquisition = threadacquisition
        self.scope_size = scope_size
        
        
        self.mainlayout = QVBoxLayout()
        self.setLayout(self.mainlayout)
        
        
        self.combo = QComboBox()
        self.mainlayout.addWidget(self.combo)
        
        self.canvas = SimpleCanvas()
        self.mainlayout.addWidget(self.canvas)
        self.ax = self.canvas.fig.add_subplot(1,1,1)
        
        self.timer = QTimer(singleShot = False, interval = 40)
        self.timer.timeout.connect(self.refresh)
        self.timer.start()
        
    
    def refresh(self):
        if self.combo.count()==0:
            self.combo.addItems(self.threadacquisition.channelNames)
        channel = self.combo.currentIndex ()
        
        s = self.threadacquisition.buffer[-self.scope_size:, channel]
        self.ax.clear()
        self.ax.plot(s, color = 'r')
        self.ax.set_xlim(0,self.scope_size)
        
        self.canvas.draw()
        
        

def test_SimpleScope():
    from acquisition import FakeThreadAcquisition
    app = QApplication([])
    t = FakeThreadAcquisition()
    t.start()
    w = SimpleScope(threadacquisition = t, scope_size = 1345)
    w.show()

    w1 = SimpleScope(threadacquisition = t)
    w1.show()


    app.exec_()
    



if __name__ == '__main__':
    test_SimpleScope()
    
    

    