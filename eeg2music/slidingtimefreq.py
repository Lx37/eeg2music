# -*- coding: utf-8 -*-
"""
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import numpy as np
from numpy import *
import time

from util import *


#~ from guiqwt.curve import CurvePlot, CurveItem#
from guiqwt.image import ImagePlot
#~ from guiqwt.styles import CurveParam
from guiqwt.builder import make
#~ from guiqwt.shapes import RectangleShape
#~ from guiqwt.styles import ShapeParam, LineStyleParam




def generate_wavelet_fourier(len_wavelet,f_start,f_stop,
                                                                deltafreq, sampling_rate, f0,
                                                                normalisation, ):
    """
    Compute the wavelet coefficients at all scales and makes its Fourier transform.
    When different signal scalograms are computed with the exact same coefficients, 
        this function can be executed only once and its result passed directly to compute_morlet_scalogram
        
    Output:
        wf : Fourier transform of the wavelet coefficients (after weighting), Fourier frequencies are the first 
    """
    # compute final map scales
    scales = f0/np.arange(f_start,f_stop,deltafreq)*sampling_rate
    # compute wavelet coeffs at all scales
    xi=arange(-len_wavelet/2.,len_wavelet/2.)
    xsd = xi[:,newaxis] / scales
    wavelet_coefs=exp(complex(1j)*2.*pi*f0*xsd)*exp(-power(xsd,2)/2.)

    weighting_function = lambda x: x**(-(1.0+normalisation))
    wavelet_coefs = wavelet_coefs*weighting_function(scales[newaxis,:])

    # Transform the wavelet into the Fourier domain
    #~ wf=fft(wavelet_coefs.conj(),axis=0) <- FALSE
    wf=np.fft.fft(wavelet_coefs,axis=0)
    wf=wf.conj() # at this point there was a mistake in the original script
    
    return wf

class ThreadComputeTF(QThread):
    finished = pyqtSignal()
    def __init__(self, sig, wf, win, parent = None, ):
        super(ThreadComputeTF, self).__init__(parent)
        self.sig = sig
        self.wf = wf
        self.win = win
        
    def run(self):
        #~ t1 = time.time()
        if self.wf.shape[1]== self.sig.size:
        #~ if 1:
            sigf=self.win*np.fft.fft(self.sig)
            #~ sigf=self.win*np.fft.fft(self.sig, n = self.wf.shape[1])
            wt_tmp=np.fft.ifft(sigf[newaxis,:]*self.wf,axis=1)
            wt = np.fft.fftshift(wt_tmp,axes=[1])
            self.parent().map = abs(wt)
        else:
            #~ print 'bad size'
            self.parent().map = zeros(self.wf.shape)
        #~ t2 = time.time()
        #~ print t2-t1
        self.finished.emit()



class SlindingTimeFreq(QWidget):
    def __init__(self, threadacquisition=None, parent = None,):
        super(SlindingTimeFreq, self).__init__(parent)
        
        self.threadacquisition = threadacquisition
        
        self.mainlayout = QHBoxLayout()
        self.setLayout(self.mainlayout)


        v = QVBoxLayout()
        self.mainlayout.addLayout(v)
        self.combo = QComboBox()
        v.addWidget(self.combo)
        self.plot = ImagePlot(yreverse=False, lock_aspect_ratio=False,)
        v.addWidget(self.plot)

        v = QVBoxLayout()
        self.mainlayout.addLayout(v)
        
        self.spinboxes = { }
        for param, value in {'xsize':2., 'f_start':1., 'f_stop':80., 'deltafreq' : .5}.items():
            spin = QDoubleSpinBox( decimals = 1, singleStep = 0.1, value = value, minimum = 0., maximum = np.inf)
            self.spinboxes[spin] = param
            v.addWidget(QLabel(param))
            v.addWidget(spin)
            v.addSpacing(10)
            spin.valueChanged.connect(self.paramChanged)
        v.addStretch(4)

        self.image = None
        self.xsize = 2.

        self.paramsTimeFreq = dict(
                                                        f_start=1.,
                                                        f_stop = 80.,
                                                        deltafreq = .5,
                                                        sampling_rate = 1./self.threadacquisition.samplingInterval,
                                                        f0 = 2.5,
                                                        normalisation = 0.,
                                                        )
        self.recreateThread = True
        self.isComputing = False
        self.initializeTimeFreq()
        
        
        self.timer = QTimer(singleShot = False, interval = 200)
        self.timer.timeout.connect(self.refresh)
        self.timer.start()

    def initializeTimeFreq(self):
        self.plot.del_all_items()
        
        self.len_wavelet = int(self.xsize/self.threadacquisition.samplingInterval)
        self.wf = generate_wavelet_fourier(len_wavelet= self.len_wavelet, ** self.paramsTimeFreq).transpose()
        
        self.win = hamming(self.len_wavelet)
        self.map = zeros(self.wf.shape)
        self.image = make.image(self.map, title='TimeFreq',interpolation ='nearest')
        self.plot.add_item(self.image)
        
        p = self.paramsTimeFreq
        self.freqs = arange(p['f_start'],p['f_stop'],p['deltafreq'])
        
    def paramChanged(self):
        spin = self.sender()
        name = self.spinboxes[spin]
        if name =='xsize':
            self.xsize = spin.value()
            self.xsize = min(30., self.xsize)
        else:
            self.paramsTimeFreq[name] = spin.value()
        
        self.initializeTimeFreq()
        self.recreateThread = True
        
        self.refresh()

    def refresh(self):
        if self.combo.count()==0:
            self.combo.addItems(self.threadacquisition.channelNames)
        channel = self.combo.currentIndex ()
        
        if self.isComputing:
            return
        
        sig = self.threadacquisition.buffer[-self.len_wavelet:, channel]
        if sig.size != self.len_wavelet:
            print 'xsize too BIG!!', sig.size, self.len_wavelet
            return
        
        self.isComputing = True
        
        if self.recreateThread:
            self.thread = ThreadComputeTF(sig, self.wf, self.win, parent = self)
            self.thread.finished.connect(self.mapComputed)
            self.recreateThread = False
        else:
            self.thread.sig = sig
        self.thread.start()

    def mapComputed(self):
        xaxis, yaxis = self.plot.get_active_axes()
        self.plot.setAxisScale(yaxis, self.freqs[0], self.freqs[-1])
        self.plot.setAxisScale(xaxis,-self.xsize, 0.)

        self.image.set_ydata(self.freqs[0], self.freqs[-1])
        self.image.set_xdata(-self.xsize, 0.)
        
        self.image.set_data(self.map)

        self.plot.replot()

        self.isComputing = False





def test_SlindingTimeFreq():
    from acquisition import FakeThreadAcquisition
    app = QApplication([])
    t = FakeThreadAcquisition()
    t.start()
    w = SlindingTimeFreq(threadacquisition = t)
    w.show()

    app.exec_()


if __name__ == '__main__':
    test_SlindingTimeFreq()
    
    