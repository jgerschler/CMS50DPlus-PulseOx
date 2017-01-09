#!/usr/bin/env python
import sys, serial, argparse, datetime, threading, time
from dateutil import parser as dateparser
import matplotlib.pyplot as plt
import matplotlib.animation as animation

c = threading.Condition()
# shared variables
xArray = []
yArray = []

# packet analysis
class LiveDataPoint(object):
    def __init__(self, time, data): 
        if [d & 0x80 != 0 for d in data] != [True, False, False, False, False]:
           raise ValueError("Invalid data packet.")

        self.time = time

        # 1st byte
        self.signalStrength = data[0] & 0x0f
        self.fingerOut = bool(data[0] & 0x10)
        self.droppingSpO2 = bool(data[0] & 0x20)
        self.beep = bool(data[0] & 0x40)

        # 2nd byte
        self.pulseWaveform = data[1]

        # 3rd byte
        self.barGraph = data[2] & 0x0f
        self.probeError = bool(data[2] & 0x10)
        self.searching = bool(data[2] & 0x20)
        self.pulseRate = (data[2] & 0x40) << 1

        # 4th byte
        self.pulseRate |= data[3] & 0x7f

        # 5th byte
        self.bloodSpO2 = data[4] & 0x7f

    def __str__(self):
        return str(self.pulseRate)

# pulse oximeter communication thread
class CMS50Dplus(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port
        self.conn = None

    def isConnected(self):
        return type(self.conn) is serial.Serial and self.conn.isOpen()

    def connect(self):
        if self.conn is None:
            self.conn = serial.Serial(port = self.port,
                                      baudrate = 19200,
                                      parity = serial.PARITY_ODD,
                                      stopbits = serial.STOPBITS_ONE,
                                      bytesize = serial.EIGHTBITS,
                                      timeout = 5,
                                      xonxoff = 1)
        elif not self.isConnected():
            self.conn.open()

    def disconnect(self):
        if self.isConnected():
            self.conn.close()

    def getByte(self):
        char = self.conn.read()
        if len(char) == 0:
            return None
        else:
            return ord(char)
    
    def getLiveData(self):
        global xArray
        global yArray
        measurements = 0
        try:
            self.connect()
            packet = [0]*5
            idx = 0
            while True:
                c.acquire()
                byte = self.getByte()
            
                if byte is None:
                    break

                if byte & 0x80:
                    if idx == 5 and packet[0] & 0x80:
                        xArray.append(measurement)
                        yArray.append(int(LiveDataPoint(datetime.datetime.utcnow(), packet)))
                        time.sleep(0.2)
                        measurement += 1
                    packet = [0]*5
                    idx = 0
                    c.notify_all()
            
                if idx < 5:
                    packet[idx] = byte
                    idx+=1
                
                else:
                    c.wait()
                c.release()
        except:
            self.disconnect()

            
class Animator(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(1,1,1)

    def animate(self,i):
        global xArray
        global yArray
        self.ax1.clear()        
        self.ax1.plot(xArray, yArray)

    def run(self):
        c.acquire()
        ani = animation.FuncAnimation(self.fig, self.animate, interval=1000)
        plt.show()
        c.notify_all() # not getting here!
        c.release()            
            
            
oximeter = CMS50Dplus('COM5')
plotter = Animator('Pulse')           

print('classes inited')

oximeter.start()
plotter.start()

print('threads started')

oximeter.join()
plotter.join()

print('threads joined')
            
# modify below this point


# def dumpLiveData(port):
    # oximeter = CMS50Dplus(port)
    # oximeter.start()
    # oximeter.join()
    # measurements = 0
    # for liveData in oximeter.getLiveData():
        # if measurements % 60 == 0:
            # print liveData
        # measurements += 1    


