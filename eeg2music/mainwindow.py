# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *


from acquisition import ThreadAcquisition
from scope import SimpleScope
from spectrum import SimpleSpectrum


def startMainWindow():
    app = QApplication([])
    thread = ThreadAcquisition()
    thread.start()
    
    
    w1 = SimpleScope(threadacquisition = thread, scope_size = 4096)
    w1.show()

    w2 = SimpleScope(threadacquisition = thread)
    w2.show()
    
    s1 = SimpleSpectrum(threadacquisition = thread, fft_size = 512)
    s1.show()

    app.exec_()
    
    
    
    
    



    


if __name__ == '__main__':
    startMainWindow()
    