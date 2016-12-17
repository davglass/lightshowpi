#!/usr/bin/env python

import RPi.GPIO as GPIO
import argparse

parser = argparse.ArgumentParser(description='Lights Controller')
parser.add_argument('pin', default=6, type=int, help='The PIN to light up')
parser.add_argument('--off', help='Turn it off', action='store_false')
args = parser.parse_args()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(args.pin, GPIO.OUT)
GPIO.output(args.pin, args.off)
