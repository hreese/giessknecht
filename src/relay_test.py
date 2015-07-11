#!/usr/bin/python3

import RPi.GPIO as GPIO
import time

v = { 1: 17,
      2: 27,
      3: 22,
      4: 10,
      5:  9,
      6: 11 }

GPIO.setmode(GPIO.BCM)

for i in v.values():
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, GPIO.HIGH)

sleepTime = 0.1

try:
    GPIO.output(17, GPIO.LOW)
    print("ONE")
    time.sleep(sleepTime)
    GPIO.output(27, GPIO.LOW)
    print("TWO")
    time.sleep(sleepTime)
    GPIO.output(22, GPIO.LOW)
    print("THREE")
    time.sleep(sleepTime)
    GPIO.output(10, GPIO.LOW)
    print("FOUR")
    time.sleep(sleepTime)
    GPIO.output( 9, GPIO.LOW)
    print("FIVE")
    time.sleep(sleepTime)
    GPIO.output(11, GPIO.LOW)
    print("SIX")
    time.sleep(sleepTime)

    GPIO.cleanup()
    print("done.")

except KeyboardInterrupt:
    print("Quitting...")
    GPIO.cleanup()
