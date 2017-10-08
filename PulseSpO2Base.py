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

    def get_data(self, data): 
        if [d & 0x80 != 0 for d in data] != [True, False, False, False, False]:
           raise ValueError("Invalid data packet.")

        self.pulse_rate = (data[2] & 0x40) << 1 # see CommunicationsProtocolDoc.pdf
        self.pulse_rate |= data[3] & 0x7f
        self.blood_spo2 = data[4] & 0x7f

        return self.pulse_rate, self.blood_spo2

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
                        self.pulse_rate, self.blood_spo2 = self.get_data(packet)
                        print(counter, self.pulse_rate, self.blood_spo2)
                        counter += 1
                        time.sleep(1)
                    packet = [0]*5
                    idx = 0
            
                if idx < 5:
                    packet[idx] = byte
                    idx+=1
        except:
            pass  



new_instance = CMS50Dplus("COM3")# adjust COM port as needed
new_instance.run()
