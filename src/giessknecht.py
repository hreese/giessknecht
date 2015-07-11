#!/usr/bin/python3

import time
import RPi.GPIO as GPIO
import logging
from collections import OrderedDict

# configure logging
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

# address all ports using BCM order
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# map pumps to GPIOs (BCM)
pumps = {
    1: 17,
    2: 27,
    3: 22,
    4: 10,
    5:  9,
    6: 11,
    7: 24,
    8: 25
}

# generate map of GPIOs to pumps
ports = {v:k for k,v in pumps.items()}

# schedule: which pump gets to run this many seconds
runtimes = {
    1: 10,
    2: 8,
    3: 4,
    4: 20
}

# Initialize all assigned GPIO pins to HIGH
def init_gpio():
    logging.info("Initializing all GPIO pins.")
    for i in pumps.values():
        GPIO.setup(i, GPIO.OUT)
        GPIO.output(i, GPIO.HIGH)

def reset_gpio():
    logging.info("Setting all GPIO pins to default HIGH.")
    for i in pumps.values():
        GPIO.output(i, GPIO.HIGH)

def do_schedule(sleepTime=1):
    logging.info("Starting irrigation cycle:")
    for pump, rtime in OrderedDict(sorted(runtimes.items())).items():
        port = pumps[pump]
        logging.info("Running pump %d (%d) for %f seconds", pump, port, rtime)
        GPIO.output(port, GPIO.LOW)
        time.sleep(rtime)
        GPIO.output(port, GPIO.HIGH)
        time.sleep(sleepTime)
    logging.info("Irrigation cycle complete.")

# main()

# initialize all ports
init_gpio()

# run schedule
do_schedule()

# reset all pins
reset_gpio()
