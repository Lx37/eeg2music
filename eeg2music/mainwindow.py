# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *



from acquisition import ThreadAcquisition, FakeThreadAcquisition
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
    
    #sp = signalprocess(threadacquisition = threadAc)
    
    f1 = SlindingTimeFreq(threadacquisition = threadAc)
    f1.show()
   
    hs = HeartScope(threadacquisition = threadAc)
    hs.show()
    
    bs = BlinkScope(threadacquisition = threadAc)
    bs.show()
    
    s1 = SimpleScopefft(threadacquisition = threadAc, fft_size = 512, port = 9003)
    s1.show()
    
    s2 = SimpleScopefft(threadacquisition = threadAc, fft_size = 512, port = 9004)
    s2.show()

    app.exec_()
    


    


if __name__ == '__main__':
    startMainWindow()
    