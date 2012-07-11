# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *



from acquisition import ThreadAcquisition, FakeThreadAcquisition
from signalProcess import simpleSignalProcess

from scope import SimpleScope
from spectrum import SimpleSpectrum
from scopefft import SimpleScopefft
from slidingtimefreq import SlindingTimeFreq
from scopeBlink import BlinkScope
from scopeHeart import HeartScope

#~ import UDP
import time
import socket


def startMainWindow():
    app = QApplication([])
    #threadAc = ThreadAcquisition()
    threadAc = FakeThreadAcquisition()
    
    threadAc.start()


    #process class
    sp = simpleSignalProcess(threadacquisition = threadAc)
    sp.show()
  
  
    #some possible independant views to add
    #s1 = SimpleScopefft(threadacquisition = threadAc, fft_size = 512, port = 9001)
    #s1.show()
    
    #s2 = SimpleScopefft(threadacquisition = threadAc, fft_size = 512, port = 9002)
    #s2.show()
    
    #bs = BlinkScope(threadacquisition = threadAc, port = 9003)
    #bs.show()

    #hs = HeartScope(threadacquisition = threadAc, port = 9004)
    #hs.show()
    
    #f1 = SlindingTimeFreq(threadacquisition = threadAc)
    #f1.show()

    app.exec_()
    


    


if __name__ == '__main__':
    startMainWindow()
    