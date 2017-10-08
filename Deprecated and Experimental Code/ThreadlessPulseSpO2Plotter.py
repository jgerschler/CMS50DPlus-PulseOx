"""This is an attempt at a threadless version.
Plotting delays, com issues etc. affect usability."""

#!/usr/bin/env python

import serial
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class CMS50Dplus(object):
    def __init__(self, port):
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

    def decode_data(self, data): 
        if [d & 0x80 != 0 for d in data] != [True, False, False, False, False]:
           raise ValueError("Invalid data packet.")

        pulse_rate = (data[2] & 0x40) << 1 # see CommunicationsProtocolDoc.pdf
        pulse_rate |= data[3] & 0x7f
        blood_spo2 = data[4] & 0x7f

        return pulse_rate, blood_spo2

    def plot_data(self, counter, pulse_rate, blood_spo2):
        self.count_data.append(counter)
        self.pulse_data.append(pulse_rate)
        self.spo2_data.append(blood_spo2)

        xmin, xmax = self.ax.get_xlim()
        if counter >= xmax:
            self.ax.set_xlim(xmin, 2*xmax)
            self.ax.figure.canvas.draw()

        self.line.set_data(self.count_data, self.pulse_data)
        self.line2.set_data(self.count_data, self.spo2_data)

        self.ax.figure.canvas.draw()
        
        return

    def run(self):
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], color='blue', lw=1)
        self.line2, = self.ax.plot([], [], color='green', lw=1)

        self.ax.set_ylim(40, 140)
        self.ax.set_xlim(0, 10)
        
        self.fig.canvas.set_window_title('Test')
        self.ax.set_title("Pulse and SpO2 Tracker")
        self.props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        self.ax.text(0.05, 0.95, "Pulse:", transform=self.ax.transAxes, fontsize=14,
                      color='blue', verticalalignment='top', bbox=self.props)
        self.ax.text(0.05, 0.85, "SpO2:", transform=self.ax.transAxes, fontsize=14,
                      color='green', verticalalignment='top', bbox=self.props)

        self.count_data, self.pulse_data, self.spo2_data = [], [], []

        self.ax.figure.canvas.draw()
        plt.show(block=False)

        self.get_data()

    def get_data(self):
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
                    pulse_rate, blood_spo2 = self.decode_data(packet)
                    print(counter, pulse_rate, blood_spo2)
                    
                    self.plot_data(counter, pulse_rate, blood_spo2)
                    counter += 1
                    #time.sleep(1)
                packet = [0]*5
                idx = 0
        
            if idx < 5:
                packet[idx] = byte
                idx+=1


new_instance = CMS50Dplus("COM3")# adjust COM port as needed
new_instance.run()
