#!/usr/bin/python3

from pprint import pprint
from threading import Lock
import RPi.GPIO as GPIO
import argparse
import json
import logging
import sys
import time

# defaults, will be updated by config file
config = {
    "global": {
        "wait_between_pumps": 1.0
    },
    "pumps" : {},
    "valves": {},
    "flowsensors": {},
    "runtimes": {}
}

flowcounter = { "_lock": Lock() }

def parse_config(filename, default=config):
    with open(filename) as fd:
        c = json.load(fd)
        config = default.update(c)
    return config

def flow_tick_handler(pin):
    global flowcounter
    with flowcounter['_lock']:
        flowcounter[pin]['ticks'] += 1

def initialize(config=config):
    global flowcounter

    # configure logging
    #logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)
    
    # address all ports using BCM order
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Configure all assigned GPIO pins
    logging.info("Initializing all GPIO pins.")
    for i in config['pumps'].values():
        GPIO.setup(i, GPIO.OUT)
        GPIO.output(i, GPIO.HIGH)
    for i in config['valves'].values():
        GPIO.setup(i, GPIO.OUT)
        GPIO.output(i, GPIO.HIGH)
    for i in config['flowsensors'].values():
        GPIO.setup(i, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.input(i)
        with flowcounter['_lock']:
            flowcounter[i] = { 'start': time.time(), 'ticks': 0 }
        GPIO.add_event_detect(i, GPIO.RISING, callback=flow_tick_handler)

## Run irrigation schedule
def do_schedule(config=config):
    logging.info("Starting irrigation cycle:")
    sleepTime = config['global']['wait_between_pumps']

    for name, runtime in config["runtimes"].items():
        port = config['pumps'][name]
        # open valve
        if name in config['valves']:
            logging.info("Opening valve %16s (pin %2d)", name, config['valves'][name])
            GPIO.output(config['valves'][name], GPIO.LOW)
        # run pump
        logging.info("Running pump  %16s (pin %2d) for %5.2f seconds", name, port, runtime)
        GPIO.output(port, GPIO.LOW)
        time.sleep(runtime)
        # stop pump
        GPIO.output(port, GPIO.HIGH)
        # close valve
        if name in config['valves']:
            logging.info("Closing valve %16s (pin %2d)", name, config['valves'][name])
            GPIO.output(config['valves'][name], GPIO.HIGH)
        time.sleep(sleepTime)
    logging.info("Irrigation cycle complete.")


if __name__ == "__main__":
    # parse commendline arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--onlyreset", action='store_true', help="Set all pins of the irrigation system to HIGH.")
    parser.add_argument("configfile", default="schedule.json")
    args = parser.parse_args()

    parse_config(args.configfile)
    initialize()

    do_schedule()
    pprint(flowcounter)

    GPIO.cleanup()
