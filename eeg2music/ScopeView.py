# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import numpy as np
import time

from util import *

class viewScope(QWidget):
    def __init__(self, threadacquisition=None, parent = None,
                        scope_size = 512):
        super(viewScope, self).__init__(parent)

        self.threadacquisition = threadacquisition
        self.scope_size = scope_size
        
        self.mainlayout = QVBoxLayout()
        self.setLayout(self.mainlayout)
        self.setWindowTitle("View Scope")
        
        self.combo = QComboBox()
        self.mainlayout.addWidget(self.combo)
        
        self.canvas = SimpleCanvas()
        self.mainlayout.addWidget(self.canvas)
        self.ax = self.canvas.fig.add_subplot(1,1,1)
	
	self.canvas_diff = SimpleCanvas()
        self.mainlayout.addWidget(self.canvas_diff)
        self.ax_diff = self.canvas_diff.fig.add_subplot(1,1,1)

        self.timer = QTimer(singleShot = False, interval = 40)
        self.timer.timeout.connect(self.refresh)
        self.timer.start()
        
        self.refrech_Value = 50;
        self.timer = QTimer(singleShot = False, interval = self.refrech_Value)
        self.timer.timeout.connect(self.refresh)
        self.timer.start()
        
    
    def refresh(self):
        if self.combo.count()==0:
            self.combo.addItems(self.threadacquisition.channelNames)
        channel = self.combo.currentIndex ()
        
        s = self.threadacquisition.buffer[-self.scope_size:, channel]
        self.ax.clear()
        self.ax.set_title('Signal over samples')
        self.ax.set_ylabel('Amplitude')
        self.ax.set_xlabel('Samples')
        self.ax.plot(s, color = 'r')
        self.ax.set_xlim(0,self.scope_size)
        
        self.canvas.draw()
        
        #difference
        self.derive = np.diff(s)
        self.ax_diff.clear()
        self.ax_diff.set_title('Diff over sample')
        self.ax_diff.set_ylabel('Diff')
        self.ax_diff.set_xlabel('Samples')
        self.ax_diff.plot(self.derive, color = 'g')
        self.ax_diff.set_xlim(0,self.scope_size)
              
        self.canvas_diff.draw()
               
        
def test_viewScope():
    from acquisition import FakeThreadAcquisition
    app = QApplication([])
    t = FakeThreadAcquisition()
    t.start()

    w1 = viewScope(threadacquisition = t)
    w1.show()
    


    app.exec_()
    



if __name__ == '__main__':
    test_viewScope()
    
    

    