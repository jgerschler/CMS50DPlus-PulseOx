#!/usr/bin/python

import threading, time, random

xArray = []
yArray = []

class myThread (threading.Thread):
    global xArray
    global yArray
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
    def run(self):
        counter = 0
        while 1:
            if len(xArray) > 10:
                xArray.pop(0)
                yArray.pop(0)
                xArray.append(counter)
                yArray.append(random.randint(1,8))
            else:
                xArray.append(counter)
                yArray.append(random.randint(1,8))                
            print("Data Generated!")
            counter += 1
            time.sleep(2)

# Create new threads
thread1 = myThread("Thread-1")
# Start new Threads
thread1.start()
print("Thread Started\n")
time.sleep(1)
while 1:
    print("---------------------")
    print("Current array values:")
    print(xArray)
    print(yArray)
    print("---------------------")
    time.sleep(2)
