#!/usr/bin/env python
# -*- coding: latin-1 -*-

import sys
import os
import json
import tweepy

def write(str):
    sys.stdout.write(str + '\n')
    sys.stdout.flush()

def read(path):
    if os.path.isfile(path):
        f = open(path, 'r')
        data = f.read().rstrip()
        f.close()
        return data
    else:
        write('Could not locate: {:s}'.format(path))
        sys.exit(1)


twitter = '/home/pi/.twitter.json'
config = json.loads(read(twitter))

auth = tweepy.OAuthHandler(config['api']['key'], config['api']['secret'])
auth.set_access_token(config['access']['token'], config['access']['secret'])
api = tweepy.API(auth)
try:
    api.home_timeline()
    write('API Access looks good')
except:
    write('API Access FAILED..')
    sys.exit(1)
