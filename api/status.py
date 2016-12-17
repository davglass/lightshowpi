#!/usr/bin/env python

import RPi.GPIO as GPIO
import json
import os.path, time

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(31, GPIO.OUT)
GPIO.setup(37, GPIO.OUT)

pins = (11, 12, 13, 15, 16, 18, 22, 29)
path = '/home/pi/tmp/lightshow_command'

def status():
    f = open(path, 'r')
    command = f.read().rstrip()
    f.close()
    status = {
        "disabled": os.path.isfile('/home/pi/tmp/lightshow_disabled'),
        'running': {
            'since': time.ctime(os.path.getmtime(path)),
            'command': command
        },
        'pins': {},
        'lights': {
            'boot': 'on' if GPIO.input(31) else 'off',
            'pattern': 'on' if GPIO.input(37) else 'off'
        }
    }
    for id, pin in enumerate(pins):
        GPIO.setup(pin, GPIO.OUT)
        status['pins'][id+1] = 'on' if GPIO.input(pin) else 'off'

    return status

if __name__=='__main__':
    print json.dumps(status(), indent=4, sort_keys=True)
