#!/usr/bin/python3

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!")

from threading import Lock
import logging
import sys
import time

FLOWSENSOR = 7

counterlock = Lock()
flowcounter = { FLOWSENSOR: 0 }

def edge_detected(chan):
    counterlock.acquire(blocking=True, timeout=-1)
    global flowcounter
    flowcounter[chan] += 1
    counterlock.release()

if __name__ == "__main__":
    # configure logging
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
    
    # address all ports using BCM order
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Configure all assigned GPIO pins as output pins and set to HIGH
    logging.info("Initializing all GPIO pins.")
    GPIO.setup(FLOWSENSOR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.input(FLOWSENSOR)

    GPIO.add_event_detect(FLOWSENSOR, GPIO.RISING, callback=edge_detected)

    try:
        while 1:
            time.sleep(1)
            counterlock.acquire(blocking=True, timeout=-1)
            ticks = flowcounter[FLOWSENSOR]
            print(ticks/60*7)
            flowcounter[FLOWSENSOR] = 0
            counterlock.release()
    except KeyboardInterrupt:
        pass

    GPIO.cleanup()
