# this script is incomplete and will not function yet! 

#!/usr/bin/env python
import argparse
import datetime
import threading
import time
import random
import serial
import sys
from dateutil import parser as dateparser
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# pulse oximeter communication thread
class CMS50Dplus(object):
    def __init__(self, port, x_array, pulse_array, spo2_array):
        threading.Thread.__init__(self)
        self.port = port
        self.conn = None
        self.x_array = x_array
        self.pulse_array = pulse_array
        self.spo2_array = spo2_array
        print("ran init")

    def is_connected(self):
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
        elif not self.is_connected():
            self.conn.open()

    def disconnect(self):
        if self.is_connected():
            self.conn.close()

    def get_byte(self):
        char = self.conn.read()
        if len(char) == 0:
            return None
        else:
            return ord(char)

    def datapoint(self, time, data): 
        if [d & 0x80 != 0 for d in data] != [True, False, False, False, False]:
           raise ValueError("Invalid data packet.")

         # 1st byte
        self.signal_strength = data[0] & 0x0f
        self.finger_out = bool(data[0] & 0x10)
        self.dropping_spo2 = bool(data[0] & 0x20)
        self.beep = bool(data[0] & 0x40)

        # 2nd byte
        self.pulse_waveform = data[1]

        # 3rd byte
        self.bargraph = data[2] & 0x0f
        self.probe_error = bool(data[2] & 0x10)
        self.searching = bool(data[2] & 0x20)
        self.pulse_rate = (data[2] & 0x40) << 1

        # 4th byte
        self.pulse_rate |= data[3] & 0x7f

        # 5th byte
        self.blood_spo2 = data[4] & 0x7f

        return str(self.pulse_rate)+","+str(self.blood_spo2)

    def animate(self, i):# add i
        self.ax1.clear()
        self.ax1.plot(self.x_array, self.pulse_array, 'b', self.x_array, self.spo2_array, 'g')
        self.ax1.set_title("Pulse and SpO2 Tracker")
        self.ax1.set_autoscaley_on(False)
        self.ax1.set_ylim([40,140])
        text_pulse = "Pulse: {}".format(str(self.pulse_array[-1]))
        text_spo2 = "SpO2: {}".format(str(self.spo2_array[-1]))
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        self.ax1.text(0.05, 0.95, text_pulse, transform=self.ax1.transAxes, fontsize=14, color='blue', verticalalignment='top', bbox=props)
        self.ax1.text(0.05, 0.85, text_spo2, transform=self.ax1.transAxes, fontsize=14, color='green', verticalalignment='top', bbox=props)

    def run(self):
        print("entering run")
        counter = 0
        try:
            self.connect()
            packet = [0]*5
            idx = 0
            self.fig = plt.figure()# this section needs to be altered
            self.ax1 = self.fig.add_subplot(1, 1, 1)
            self.ax1.plot(self.x_array, self.pulse_array, 'b', self.x_array, self.spo2_array, 'g')
            self.ax1.set_title("Pulse and SpO2 Tracker")
            self.ax1.set_autoscaley_on(False)
            self.ax1.set_ylim([40,140])
            text_pulse = "Pulse: {}".format(str(self.pulse_array[-1]))
            text_spo2 = "SpO2: {}".format(str(self.spo2_array[-1]))
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            self.ax1.text(0.05, 0.95, text_pulse, transform=self.ax1.transAxes, fontsize=14, color='blue', verticalalignment='top', bbox=props)
            self.ax1.text(0.05, 0.85, text_spo2, transform=self.ax1.transAxes, fontsize=14, color='green', verticalalignment='top', bbox=props)
            plt.show()
            while True:
                byte = self.get_byte()
            
                if byte is None:
                    print("byte is none")
                    break

                if byte & 0x80:
                    print("byte is good")
                    if idx == 5 and packet[0] & 0x80:
                        data = str(self.datapoint(datetime.datetime.utcnow(), packet)).split(',')
                        if len(self.x_array) > 5000:
                            self.x_array.pop(0)
                            self.pulse_array.pop(0)
                            self.spo2_array.pop(0)
                            self.x_array.append(counter)
                            self.pulse_array.append(int(data[0]))
                            self.spo2_array.append(int(data[1]))
                        else:
                            self.x_array.append(counter)
                            self.pulse_array.append(int(data[0]))
                            self.spo2_array.append(int(data[1]))

                        time.sleep(1)
                        self.ax1.set_xdata# continue here!

                        #self.ax1.clear()                    
                        #self.ani = animation.FuncAnimation(self.fig, self.animate, 1000)
                        
                        counter += 1
                    packet = [0]*5
                    idx = 0
            
                if idx < 5:
                    packet[idx] = byte
                    idx += 1
            print("got to the end of byte")
        except:
            time.sleep(0.1)# faulty cable causes occasional disconnection/connection
            print("hitting except")
            pass



x_array = []# could use numpy arrays here
pulse_array = []
spo2_array = []

new_instance = CMS50Dplus("COM3", x_array, pulse_array, spo2_array)# adjust COM port as needed
new_instance.run()
