#!/usr/bin/python3

import time
import RPi.GPIO as GPIO
from collections import OrderedDict

GPIO.setmode(GPIO.BCM)

pumps = { 1: 17,
          2: 27,
          3: 22,
          4: 10,
          5:  9,
          6: 11 }

ports = {v:k for k,v in pumps.items()}

for i in pumps.values():
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, GPIO.HIGH)

sleepTime = 0.15

try:
    #while(True):
    for x in range(10):
        for pump, port in OrderedDict(sorted(pumps.items())).items():
            GPIO.output(port, GPIO.LOW)
            print(pump)
            time.sleep(sleepTime)
    
        #for pump, port in OrderedDict(reversed(sorted(pumps.items()))).items():
        for pump, port in OrderedDict(sorted(pumps.items())).items():
            GPIO.output(port, GPIO.HIGH)
            print(pump)
            time.sleep(sleepTime)

    GPIO.cleanup()
    print("done.")

except KeyboardInterrupt:
    print("Quitting...")
    GPIO.cleanup()
