#!/usr/bin/env python

import httplib
import json
from pprint import pprint
import argparse
import urllib
import os
import sys

if os.path.isfile('/home/pi/tmp/lightshow_disabled'):
    sys.exit("System is disabled, not pinging SmartThings..") 

if not os.path.isfile('/home/pi/.smartthings.json'):
    sys.exit('Failed to locate ~/.smartthings.json')

config = json.loads(open('/home/pi/.smartthings.json').read())

def switch(state, id):
    conn = httplib.HTTPSConnection("graph.api.smartthings.com")
    url = "{:s}{:s}/command/{:s}?access_token={:s}".format(config['url'], id, state, config['token'])
    conn.request("POST", url)
    data = conn.getresponse().read()
    pprint(json.loads(data))
    conn.close()

def deviceOff(id):
    switch('off', id)

def deviceOn(id):
    switch('on', id)

def setMode(mode):
    conn = httplib.HTTPSConnection("graph.api.smartthings.com")
    url = "{:s}location/{:s}?access_token={:s}".format(config['url'], urllib.quote_plus(mode), config['token'])
    conn.request("POST", url)
    data = conn.getresponse().read()
    pprint(json.loads(data))
    conn.close()

def toggleDevices(state):
    if 'devices' in config:
        if state in config['devices']:
            if 'off' in config['devices'][state]:
                for id in config['devices'][state]['off']:
                    deviceOff(config['devices'][state]['off'][id])
            if 'on' in config['devices'][state]:
                for id in config['devices'][state]['on']:
                    deviceOn(config['devices'][state]['on'][id])

parser = argparse.ArgumentParser(description='SmartThings Controller')
parser.add_argument('--off', help='Turn it off', action='store_true')
args = parser.parse_args()

if args.off:
    if 'modes' in config and 'end' in config['modes']:
        setMode(config['modes']['end'])
    else:
        print "No end mode found in config"
    
    toggleDevices('end')
else:
    if 'modes' in config and 'start' in config['modes']:
        setMode(config['modes']['start'])
    else:
        print "No start mode found in config"

    toggleDevices('start')
