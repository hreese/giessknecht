#!/usr/bin/python3

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!")

import logging
import sys
import time

FLOWSENSOR = 7

def edge_detected(chan):
    print(".", end="")

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

    input("Waiting")

    GPIO.cleanup()
