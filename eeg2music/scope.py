# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import numpy as np

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar2
from matplotlib.figure import Figure

import time


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
        self.mainLayout = QVBoxLayout()
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
##         self.ax.set_ylim(,1024)
        
        self.canvas.draw()
        
        

def test_SimpleScope():
    
    class FakeThreadAcquisition(QThread):
        channelCount = 4
        channelNames = ['a', 'b', 'c', 'd']
        
        
        def __init__(self, parent = None,):
            super(FakeThreadAcquisition, self).__init__()
            self.buffer = np.random.random((2048, 4))
            
        def run(self):
            while True:
                self.buffer = np.random.random((2048,4))
                time.sleep(0.1)
        
    
    app = QApplication([])
    t = FakeThreadAcquisition()
    t.start()
    w = SimpleScope(threadacquisition = t, scope_size = 1345)
    w.show()

    w1 = SimpleScope(threadacquisition = t)
    w1.show()


    app.exec_()
    



if __name__ == '__main__':
    #~ test_SimpleCanvasAndTool()
    test_SimpleScope()
    
    

    