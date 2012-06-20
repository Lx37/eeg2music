# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *



from acquisition import ThreadAcquisition
from scope import SimpleScope
from spectrum import SimpleSpectrum
from scopefft import SimpleScopefft

import UDP
import time
import socket


def startMainWindow():
    app = QApplication([])
    threadAc = ThreadAcquisition()
    
    threadAc.start()
    
    
    w1 = SimpleScope(threadacquisition = thread, scope_size = 4096)
    w1.show()

    #w2 = SimpleScope(threadacquisition = thread)
    #w2.show()
    
   
    s1 = SimpleScopefft(threadacquisition = threadAc, fft_size = 512)
    s1.show()
    
    s1.port = 9001
    s1.message = "alpha"
    
    #send udp timer
    timer_udp = QTimer(singleShot = False, interval = 100)
    timer_udp.timeout.connect(s1.send)
    timer_udp.start()
    

    app.exec_()
    


    


if __name__ == '__main__':
    startMainWindow()
    