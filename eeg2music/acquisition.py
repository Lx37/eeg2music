# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *




import socket
import struct

import numpy as np 
import time



class Marker:
    def __init__(self):
        self.position = 0
        self.points = 0
        self.channel = -1
        self.type = ""
        self.description = ""




class ThreadAcquisition(QThread):
    
    new_buffer = pyqtSignal()
    
    def __init__(self, parent = None,
                        host = "localhost",
                        port = 51244,
                        buffer_size = 2**16,
                        
                        ):
        super(ThreadAcquisition, self).__init__()
        
        self.host = host
        self.port = port
        
        self.buffer_size= buffer_size
        
        self.buffer = None
        
    def run(self):

        self.con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.con.connect((self.host, self.port))
        self.lastBlock = -1
        
        self.do_finish = False
        
        
        
        while  not self.do_finish:
            buf_header = self.recv_data(24)

            # Split array into usefull information id1 to id4 are constants
            (id1, id2, id3, id4, msgsize, msgtype) = struct.unpack('<llllLL', buf_header)
            
            # Get data part of message, which is of variable size
            rawdata = self.recv_data( msgsize - 24)

            # Perform action dependend on the message type
            if msgtype == 1:
                # Start message, extract eeg properties and display them

                self.channelCount, self.samplingInterval = struct.unpack('<Ld', rawdata[:12])
                self.samplingInterval *= 1e-6
                
                n = self.channelCount
                # Extract resolutions
                self.resolutions = np.array(struct.unpack('<'+'d'*n, rawdata[12:12+8*n]), dtype = 'f') 
                # Extract channel names
                self.channelNames = rawdata[12+8*n:].tostring().split('\x00')[:-1]
                
                self.buffer = np.zeros((self.buffer_size,n), dtype = 'f')
                
                print "Start"
                print "Number of channels: ",self.channelCount
                print "Sampling interval: ", self.samplingInterval
                print "Resolutions: ",self.resolutions
                print "Channel Names: ", self.channelNames


            elif msgtype == 4:
                # Data message, extract data and markers
                block, self.sigs, self.markers = self.get_signal_and_markers(rawdata)
                
                self.sigs[:,:] *= self.resolutions[np.newaxis, :]

                # Check for overflow
                if self.lastBlock != -1 and block > self.lastBlock + 1:
                    print "*** Overflow with " + str(block - self.lastBlock) + " datablocks ***" 
                self.lastBlock = block
                
                
                self.buffer = np.concatenate( [ self.buffer, self.sigs], axis = 0)[-self.buffer_size:, :]
                
                self.new_buffer.emit()
                
                
            
            elif msgtype == 3:
                # Stop message, terminate program
                print "Stop"
                finish = True            
        
    def recv_data(self, requestedSize):
        buf = np.empty( requestedSize, dtype = np.uint8)
        n = 0
        while n < requestedSize:
            databytes = self.con.recv(requestedSize - n)
            if databytes == '':
                raise RuntimeError, "connection broken"
            buf[n:n+len(databytes)] = np.frombuffer(databytes, dtype = np.uint8)
            n += len(databytes)
        return buf
    
    def get_signal_and_markers(self, rawdata):
        
        hs = 12
        dt = np.dtype(np.float32)
        
        # Extract numerical data
        (block, points, markerCount) = struct.unpack('<LLL', rawdata[:hs])
        n = self.channelCount
        sigs = (rawdata[hs:hs+points*n*dt.itemsize]).view(dt)
        sigs = sigs.reshape(points, n)

        # Extract markers
        # TODO : optimize!!!
        markers = [ ]
        index = 12 + 4 * points * n
        for m in range(markerCount):
            markersize, = struct.unpack('<L', rawdata[index:index+4])
            
            ma = Marker()
            ma.position, ma.points, ma.channel = struct.unpack('<LLl', rawdata[index+4:index+16])
            ma.type, ma.description = rawdata[index+16:index+markersize].split('\x00')[:-1]
            markers.append(ma)
            
            index = index + markersize

        return block, sigs, markers


def test_ThreadAcquisition1():
    
    def get_buffer():
        print 'sigs', t.buffer.shape, 'markers', len(t.markers)
    
    app = QApplication([])
    t = ThreadAcquisition(buffer_size = 1024)
    
    t.new_buffer.connect(get_buffer)
    
    t.start()
    app.exec_()
 

class FakeThreadAcquisition(QThread):
    channelCount = 5
    channelNames = ['random', 'random_50', 'random-blink', 'random_heart']
    samplingInterval = 0.002
    
    new_buffer = pyqtSignal()
    def __init__(self, parent = None,buffer_size = 1024):
        super(FakeThreadAcquisition, self).__init__()
        self.buffer = np.random.random((2048, 4))
        
    def run(self):
        i=0
        while True:
            if i > len(self.buffer)/4 :
                i=0
            self.buffer = np.random.random((2048,4))
            self.buffer[:,1] += np.sin(np.arange(2048)*0.002*2*np.pi*50.)*0.8
            self.buffer[-20-i:,2] *= 3
            self.buffer[-i:,2] *= 0.3
            if i > 250:
                self.buffer[260-i:,2] *= 3
                self.buffer[280-i:,2] *= 0.3
            self.buffer[-10-i,3] = 3
            self.buffer[-6-i,3] = -3

            if i > 210:
                self.buffer[220-i,3] = 3
                self.buffer[216-i,3] = -3

            #np.arange(self.buffer[-20-i,7])
            #print len(self.buffer)
            i=i+10
            time.sleep(0.1)
            self.new_buffer.emit()


def test_FakeThreadAcquisition1():
    
    def get_buffer():
        print 'sigs', t.buffer.shape
    
    app = QApplication([])
    t = FakeThreadAcquisition(buffer_size = 109)
    
    t.new_buffer.connect(get_buffer)
    
    t.start()
    app.exec_()




if __name__ == '__main__':
    #~ test_ThreadAcquisition1()
    test_FakeThreadAcquisition1()
    