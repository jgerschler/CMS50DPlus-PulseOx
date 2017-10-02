"""In progress -- still need to make several changes,
including closing thread gracefully."""
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

x_array = []# could use numpy arrays here
pulse_array = []
spo2_array = []

# packet analysis -- pulled from https://github.com/atbrask
class LiveDataPoint(object):
    def __init__(self, time, data): 
        if [d & 0x80 != 0 for d in data] != [True, False, False, False, False]:
           raise ValueError("Invalid data packet.")

        self.time = time

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

    def __str__(self):
        return str(self.pulse_rate)+","+str(self.blood_spo2)

# pulse oximeter communication thread
class CMS50Dplus(threading.Thread):
    global x_array
    global pulse_array
    global spo2_array
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
    
    def run(self):
        counter = 0
        try:
            self.connect()
            packet = [0]*5
            idx = 0
            while True:
                byte = self.get_byte()
            
                if byte is None:
                    break

                if byte & 0x80:
                    if idx == 5 and packet[0] & 0x80:
                        data = str(LiveDataPoint(datetime.datetime.utcnow(), packet)).split(',')
                        if len(x_array) > 5000:
                            x_array.pop(0)
                            pulse_array.pop(0)
                            spo2_array.pop(0)
                            x_array.append(counter)
                            pulse_array.append(int(data[0]))
                            spo2_array.append(int(data[1]))
                        else:
                            x_array.append(counter)
                            pulse_array.append(int(data[0]))
                            spo2_array.append(int(data[1]))
                        counter += 1
                    packet = [0]*5
                    idx = 0
            
                if idx < 5:
                    packet[idx] = byte
                    idx+=1
        except:
            time.sleep(0.1)# faulty cable causes occasional disconnection/connection
            pass  

def animate(i):
    global x_array
    global pulse_array
    global spo2_array
    ax1.clear()
    ax1.plot(x_array, pulse_array, 'b', x_array, spo2_array, 'g')
    ax1.set_title("Pulse and SpO2 Tracker")
    ax1.set_autoscaley_on(False)
    ax1.set_ylim([40,140])
    text_pulse = "Pulse: {}".format(str(pulse_array[-1]))
    text_spo2 = "SpO2: {}".format(str(spo2_array[-1]))
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax1.text(0.05, 0.95, text_pulse, transform=ax1.transAxes, fontsize=14, color='blue', verticalalignment='top', bbox=props)
    ax1.text(0.05, 0.85, text_spo2, transform=ax1.transAxes, fontsize=14, color='green', verticalalignment='top', bbox=props)

new_instance = CMS50Dplus("COM3")# adjust COM port as needed
new_instance.start()
time.sleep(1)

fig = plt.figure()
ax1 = fig.add_subplot(1, 1, 1)
ani = animation.FuncAnimation(fig, animate, 1000)
plt.show()
