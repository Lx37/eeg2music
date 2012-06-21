# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import numpy as np

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar2
from matplotlib.figure import Figure

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



if __name__ == '__main__':
    test_SimpleCanvasAndTool()