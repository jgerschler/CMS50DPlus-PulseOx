"""This is still VERY much in progress; modified from atrask (c) 2015"""
#!/usr/bin/env python
import sys, serial, argparse, datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from dateutil import parser as dateparser

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
        return ", ".join([
##                          "Time = {0}",
##                          "Signal Strength = {1}",
##                          "Finger Out = {2}",
##                          "Dropping SpO2 = {3}",
##                          "Beep = {4}",
##                          "Pulse waveform = {5}",
##                          "Bar Graph = {6}",
##                          "Probe Error = {7}",
##                          "Searching = {8}",
                          "{9}"
##                          "SpO2 = {10}%"
                          ]).format(
                                                  self.time,
                                                  self.signalStrength,
                                                  self.fingerOut,
                                                  self.droppingSpO2,
                                                  self.beep,
                                                  self.pulseWaveform,
                                                  self.barGraph,
                                                  self.probeError,
                                                  self.searching,
                                                  self.pulseRate,
                                                  self.bloodSpO2
                                                  )

    @staticmethod
    def getCsvColumns():
        return ["Time", "PulseRate", "SpO2", "PulseWaveform", "BarGraph", 
                "SignalStrength", "Beep", "FingerOut", "Searching",
                "DroppingSpO2", "ProbeError"]

    def getCsvData(self):
        return [self.time, self.pulseRate, self.bloodSpO2, self.pulseWaveform,
                self.barGraph, self.signalStrength, self.beep,
                self.fingerOut, self.searching, self.droppingSpO2,
                self.probeError]


class CMS50Dplus(object):
    def __init__(self, port):
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
                        yield LiveDataPoint(datetime.datetime.utcnow(), packet)
                    packet = [0]*5
                    idx = 0
            
                if idx < 5:
                    packet[idx] = byte
                    idx+=1
        except:
            self.disconnect()

def dumpLiveData(port):
    fig = plt.figure()
    ax1 = fig.add_subplot(1,1,1)
    oximeter = CMS50Dplus(port)
    measurements = 0
    for liveData in oximeter.getLiveData():
        if measurements % 60 == 0:
            print liveData
            #ax1.clear()
            ax1.plot(measurements,int(str(liveData)))
            plt.show()
        measurements += 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CMS50DPlusPulse.py v1.0 - Contec CMS50D+ Plotter (c) 2016 J.J. Gerschler")
    parser.add_argument("serialport", help="Virtual serial port where pulse oximeter is connected.")

    args = parser.parse_args()

    dumpLiveData(args.serialport)

    print ""
    print "Done."
