# this script is incomplete and will not function yet! 

#!/usr/bin/env python
import argparse
import threading
import time
import random
import serial
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class CMS50Dplus(object):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port
        self.conn = None

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

    def plot_init(self):
        self.ax.set_ylim(40, 140)
        self.ax.set_xlim(0, 10)
        del self.time_data[:]
        del self.pulse_data[:]
        del self.spo2_data[:]
        self.line.set_data(time_data, pulse_data)
        self.line2.set_data(time_data, spo2_data)
        return self.line, self.line2,        

    def update_data(self, data):
        t, pulse, spo2 = data
        self.time_data.append(t)
        self.pulse_data.append(pulse)
        self.spo2_data.append(spo2)
        xmin, xmax = self.ax.get_xlim()

        if t >= xmax:
            self.ax.set_xlim(xmin, 2*xmax)
            self.ax.figure.canvas.draw()
        self.line.set_data(self.time_data, self.pulse_data)
        self.line2.set_data(self.time_data, self.spo2_data)

        return self.line, self.line2,

    def get_datapoint(self, data): 
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

        return self.pulse_rate, self.blood_spo2

    def data_gen(self, t=0):
        counter = 0
        try:
            self.connect()
            packet = [0]*5
            idx = 0
            byte = self.get_byte()
        
            if byte is None:
                print("byte is none")
                break

            if byte & 0x80:
                print("byte is good")
                if idx == 5 and packet[0] & 0x80:
                    pulse_data, spo2_data = self.get_datapoint(packet)                     
                    counter += 1
                    t += 1
                packet = [0]*5
                idx = 0
                
            if idx < 5:
                packet[idx] = byte
                idx += 1

            return t, pulse_data, spo2_data
        
        except:# update
            time.sleep(0.1)# faulty cable causes occasional disconnection/connection
            print("hitting except")
            pass

    def run(self):
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], lw=1)
        self.line2, = self.ax.plot([], [], lw=1)

        self.ax.set_title("Pulse and SpO2 Tracker")
        text_pulse = "Pulse:"
        text_spo2 = "SpO2:"
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        self.ax.text(0.05, 0.95, text_pulse, transform=self.ax.transAxes, fontsize=14,
                      color='blue', verticalalignment='top', bbox=props)
        self.ax.text(0.05, 0.85, text_spo2, transform=self.ax.transAxes, fontsize=14,
                      color='green', verticalalignment='top', bbox=props)

        self.time_data, self.pulse_data, self.spo2_data = [], [], []
        
        ani = animation.FuncAnimation(self.fig, self.update_data, self.data_gen, blit=False, interval=1000,
                              repeat=False, init_func=self.plot_init)
        plt.show()



new_instance = CMS50Dplus("COM3")# adjust COM port as needed
new_instance.run()
