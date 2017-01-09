#!/usr/bin/python
import sys, serial, argparse, datetime, threading, time, random
from dateutil import parser as dateparser
import matplotlib.pyplot as plt
import matplotlib.animation as animation

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
    global xArray
    global yArray
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
    
    def run(self):
        counter = 0
        try:
            self.connect()
            packet = [0]*5
            idx = 0
            while True:
                byte = self.getByte()
            
                if byte is None:
                    break

                if byte & 0x80:
                    if idx == 5 and packet[0] & 0x80:
                        if len(xArray) > 100:
                            xArray.pop(0)
                            yArray.pop(0)
                            xArray.append(counter)
                            yArray.append(int(str(LiveDataPoint(datetime.datetime.utcnow(), packet))))
                        else:
                            xArray.append(counter)
                            yArray.append(int(str(LiveDataPoint(datetime.datetime.utcnow(), packet))))
                        counter += 1
                    packet = [0]*5
                    idx = 0
            
                if idx < 5:
                    packet[idx] = byte
                    idx+=1
        except:
            self.disconnect()        

def animate(i):
    global xArray
    global yArray
    ax1.clear()
    ax1.plot(xArray, yArray)
            
# Create new threads
thread1 = CMS50Dplus("COM5")
# Start new Threads
thread1.start()
print("Thread Started\n")
time.sleep(1)
# while 1:
    # print("---------------------")
    # print("Current array values:")
    # print(xArray)
    # print(yArray)
    # print("---------------------")
    # time.sleep(1)
    
fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
ani = animation.FuncAnimation(fig, animate, 1000)
plt.show()
