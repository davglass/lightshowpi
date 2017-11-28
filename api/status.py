#!/usr/bin/env python

import RPi.GPIO as GPIO
import json
import subprocess
import os
import time
import math
from datetime import timedelta
import ConfigParser

wipins = (11,12,13,15,16,18,22,7,3,5,24,26,19,21,23,8,10,False,False,False,False,29,31,33,35,37,32,36,38,40)

def getPin(id):
    return wipins[id]

pins = (0, 1, 2, 3, 4, 5, 6, 7)

bootPin = 22
airPin = 25

config = ConfigParser.ConfigParser()
config.readfp(open('/home/pi/.lights.cfg'))

if config.has_section('hardware') and config.has_option('hardware', 'gpio_pins'):
    p = config.get('hardware', 'gpio_pins')
    pins = tuple(map(int, p.split(',')))

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(getPin(bootPin), GPIO.OUT)
GPIO.setup(getPin(airPin), GPIO.OUT)

path = '/home/pi/tmp/lightshow_command'

def get_size(file):
    if not os.path.isfile(file):
        return "0 B"
    size = os.path.getsize(file)
    if (size == 0):
        return '0B'
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size,1024)))
    p = math.pow(1024,i)
    s = round(size/p,2)
    return '%s %s' % (s,size_name[i])

def get_ram():
    s = subprocess.check_output(['free', '-m'])
    lines = s.split('\n') 
    return ( int(lines[1].split()[1]), int(lines[1].split()[2]), int(lines[1].split()[3]) )

def getCPUuse():
    return(str(os.popen("/usr/bin/top -b -n1 | /usr/bin/awk '/Cpu\(s\):/ {print $2}'").readline().strip()))

def getCPUtemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    return(res.replace('temp=', '').replace("'C\n",""))

def getUptime():
	with open('/proc/uptime', 'r') as f:
	    uptime_seconds = float(f.readline().split()[0])
	    uptime_string = str(timedelta(seconds = uptime_seconds))
	return uptime_string

def status():
    f = open(path, 'r')
    command = f.read().rstrip()
    f.close()
    C = int(float(getCPUtemperature()))
    F = 9.0 / 5.0 * C + 32
    ram = get_ram()
    status = {
        "cpu": getCPUuse(),
        "tmp": get_size('/tmp/audio'),
        "memory": {
            "total": "{:} MB".format(ram[0]),
            "used": "{:} MB".format(ram[1]),
            "free": "{:} MB".format(ram[2])
        },
        "temps": {
            "F": round(F, 2),
            "C": round(C, 2)
        },
        "disabled": os.path.isfile('/home/pi/tmp/lightshow_disabled'),
        'running': {
	    'uptime': getUptime(),
            'since': time.ctime(os.path.getmtime(path)),
            'command': command
        },
        'pins': {},
        'lights': {
            'boot': 'on' if GPIO.input(getPin(bootPin)) else 'off',
            'pattern': 'on' if GPIO.input(getPin(airPin)) else 'off'
        }
    }
    for id, pin in enumerate(pins):
        GPIO.setup(getPin(pin), GPIO.OUT)
        status['pins'][id+1] = 'on' if GPIO.input(getPin(pin)) else 'off'

    return status

if __name__=='__main__':
    print json.dumps(status(), indent=4, sort_keys=True)
