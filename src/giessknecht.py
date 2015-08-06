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
        "wait_between_pumps": 1.0,
        "flowticks_per_liter": 490
    },
    "pumps" : {},
    "valves": {},
    "flowsensors": {},
    "runtimes": {}
}

class Flowcounter:
    """Threadsafe Lightweight counter class"""
    def __init__(self):
        self.lock = Lock()
        self.ticks = {}

    def incr_counter(self, pin):
        with self.lock:
            if not pin in self.ticks:
                self.ticks[pin] = { 'ticks': 0, 'starttime': time.time() }
            self.ticks[pin]['ticks'] += 1
            return self.ticks[pin]['ticks']
    
    def get_counter(self, pin):
        with self.lock:
            if pin in self.ticks:
                return self.ticks[pin]["ticks"]
            else:
                return -1
    
    def reset_counter(self, pin):
        with self.lock:
            if pin in self.ticks:
                old_values = self.ticks[pin]
            else:
                old_values = { 'ticks': -1, 'starttime': time.time() }
            self.ticks[pin] = { 'ticks': 0, 'starttime': time.time() }
            return old_values

    def get_pins(self):
        return self.ticks.keys()

# global flowcounter
flowcounter = Flowcounter()

def parse_config(filename):
    """Load configuration from json config file"""
    global config
    with open(filename) as fd:
        c = json.load(fd)
        config.update(c)
    return config

def reset_gpio(config=config):
    """Set all used GPIO pins to sensible defaults"""
    for i in config['pumps'].values():
        GPIO.setup(i, GPIO.OUT)
        GPIO.output(i, GPIO.HIGH)
    for i in config['valves'].values():
        GPIO.setup(i, GPIO.OUT)
        GPIO.output(i, GPIO.HIGH)
    for i in config['flowsensors'].values():
        GPIO.setup(i, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.input(i)

def initialize(config=config):
    global flowcounter

    # configure logging
    #logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)
    
    # address all ports using BCM order
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Configure all assigned GPIO pins
    reset_gpio()

## Run irrigation schedule
def do_schedule(config=config):
    logging.info("Starting irrigation cycle:")

    for name, runtime in config["runtimes"].items():
        port = config['pumps'][name]

        # reset flow sensor
        if name in config["flowsensors"]:
            flowcounter.reset_counter(config["flowsensors"][name])
            # add event listener
            p = config["flowsensors"][name]
            GPIO.add_event_detect(p, GPIO.RISING, callback=flowcounter.incr_counter)

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

        # reset flow counter and output volume
        if name in config["flowsensors"]:
            #pprint(flowcounter.ticks)
            counterval = flowcounter.reset_counter(config["flowsensors"][name])
            timediff = time.time() - counterval['starttime']
            logging.info("Cycle         %16s (pin %2d) did %6d ticks in %5d seconds, that's approximatly %3.2f liters", name, config['flowsensors'][name], counterval['ticks'], timediff, counterval['ticks']/config["global"]["flowticks_per_liter"])
            # remove event listener
            p = config["flowsensors"][name]
            GPIO.remove_event_detect(p)

        # wait a while before starting the next cycle
        time.sleep(config['global']['wait_between_pumps'])

    logging.info("Irrigation cycle complete.")

if __name__ == "__main__":
    # parse commendline arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--onlyreset", action='store_true', help="Set all pins of the irrigation system to HIGH.")
    parser.add_argument("configfile", default="schedule.json")
    args = parser.parse_args()

    parse_config(args.configfile)
    initialize()

    if args.onlyreset:
        sys.exit()

    try:
        do_schedule()
    finally:
        reset_gpio()
        GPIO.cleanup()
