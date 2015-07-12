#!/usr/bin/python3

from collections import OrderedDict
import RPi.GPIO as GPIO
import argparse
import logging
import sys
import time

# CONFIGURATION
#
# Edit these maps to match your GPIO configuration.
# Pumps/relays are numbered 1..8. If pump number 1
# is connected to GPIO 17 (BCM ordering), add
#     1: 17
# to this dict.
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

# This is the irrigation schedule. This script gets called
# once a day (in the original setup, you may do things differently,
# but then you have to think for yourself *g*). To have pump number 1
# run for 12.5 seconds, add
#     1: 12.5
# to this dict.
runtimes = {
    1: 10,
    2: 8,
    3: 4,
    4: 20
}

# Wait this many seconds between switching off one pump and activating
# the next one.
waitInbetween = 0.5

# END CONFIGURATION

def initialize():
    # configure logging
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
    
    # address all ports using BCM order
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

# Configure all assigned GPIO pins as output pins and set to HIGH
def init_gpio():
    logging.info("Initializing all GPIO pins.")
    for i in pumps.values():
        GPIO.setup(i, GPIO.OUT)
        GPIO.output(i, GPIO.HIGH)

# Set all GPIOs to HIGH
def reset_gpio():
    logging.info("Setting all GPIO pins to default HIGH.")
    for i in pumps.values():
        GPIO.output(i, GPIO.HIGH)

# Run irrigation schedule
def do_schedule(sleepTime=waitInbetween):
    logging.info("Starting irrigation cycle:")
    for pump, rtime in OrderedDict(sorted(runtimes.items())).items():
        port = pumps[pump]
        logging.info("Running pump %d (%d) for %f seconds", pump, port, rtime)
        GPIO.output(port, GPIO.LOW)
        time.sleep(rtime)
        GPIO.output(port, GPIO.HIGH)
        time.sleep(sleepTime)
    logging.info("Irrigation cycle complete.")


if __name__ == "__main__":
    # parse commendline arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--onlyreset", action='store_true', help="Set all pins of the irrigation system to HIGH.")
    args = parser.parse_args()

    # setup misc stuff
    initialize()

    # initialize all ports
    init_gpio()

    if args.onlyreset:
        sys.exit()

    try:
        # run schedule
        do_schedule()

    finally:
        # reset all pins
        reset_gpio()
