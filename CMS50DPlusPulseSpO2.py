"""Definitely still a beta -- could work some more on error checking, thread closure...etc"""
#!/usr/bin/env python

import serial
import threading
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class CMS50Dplus(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port
        self.conn = None
        self.counter_data = []
        self.pulse_data = []
        self.spo2_data = []

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

    def decode_packet(self, data): 
        if [d & 0x80 != 0 for d in data] != [True, False, False, False, False]:
           raise ValueError("Invalid data packet.")

        pulse_rate = (data[2] & 0x40) << 1# see CommunicationProtocolDoc.pdf
        pulse_rate |= data[3] & 0x7f

        blood_spo2 = data[4] & 0x7f

        return pulse_rate, blood_spo2
    
    def run(self):
        counter = 0
        self.connect()
        packet = [0]*5
        idx = 0
        while True:
            byte = self.get_byte()
        
            if byte is None:
                break

            if byte & 0x80:
                if idx == 5 and packet[0] & 0x80:
                    pulse_rate, blood_spo2 = self.decode_packet(packet)
                    if len(self.counter_data) > 5000:
                        self.counter_data.pop(0)
                        self.pulse_data.pop(0)
                        self.spo2_data.pop(0)
                        self.counter_data.append(counter)
                        self.pulse_data.append(pulse_rate)
                        self.spo2_data.append(blood_spo2)
                    else:
                        self.counter_data.append(counter)
                        self.pulse_data.append(pulse_rate)
                        self.spo2_data.append(blood_spo2)
                    counter += 1
                packet = [0]*5
                idx = 0
        
            if idx < 5:
                packet[idx] = byte
                idx+=1

def animate(i):
    ax1.clear()
    ax1.plot(CMS50Dplus_1.counter_data, CMS50Dplus_1.pulse_data, 'blue', CMS50Dplus_1.counter_data, CMS50Dplus_1.spo2_data, 'green')
    ax1.set_title("Pulse and SpO2 Tracker")
    ax1.set_autoscaley_on(False)
    ax1.set_ylim([40,140])
    text_pulse = "Pulse: {}".format(str(CMS50Dplus_1.pulse_data[-1]))
    text_spo2 = "SpO2: {}".format(str(CMS50Dplus_1.spo2_data[-1]))
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax1.text(0.05, 0.95, text_pulse, transform=ax1.transAxes, fontsize=14, color='blue', verticalalignment='top', bbox=props)
    ax1.text(0.05, 0.85, text_spo2, transform=ax1.transAxes, fontsize=14, color='green', verticalalignment='top', bbox=props)

CMS50Dplus_1 = CMS50Dplus("COM3")# adjust COM port as needed
CMS50Dplus_1.start()
time.sleep(1)

fig = plt.figure()
ax1 = fig.add_subplot(1, 1, 1)
ani = animation.FuncAnimation(fig, animate, 1000)
plt.show()
