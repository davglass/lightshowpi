#!/usr/bin/env python
# -*- coding: latin-1 -*-

import sys
import os
import time
import json
import platform
import tweepy
import random
from get_artist import find_artist

def write(str):
    sys.stdout.write(str + '\n')
    sys.stdout.flush()

def read(path):
    if os.path.isfile(fileName):
        f = open(path, 'r')
        data = f.read().rstrip()
        f.close()
        return data
    else:
        write('Could not locate: {:s}'.format(path))
        sys.exit(1)

def tweet(status, action):
    auth = tweepy.OAuthHandler(config['api']['key'], config['api']['secret'])
    auth.set_access_token(config['access']['token'], config['access']['secret'])
    api = tweepy.API(auth)
    verb = ''
    if action == 'on':
        verb = random.choice(onList)
    elif action == 'off':
        verb = random.choice(offList)
    
    finalStatus = "{:s} {:s}".format(status, verb)
    finalStatus = finalStatus[0:130] #chop to 140 characters
    finalStatus = "{:s} {:s}{:s}".format(random.choice(xIcons), finalStatus, random.choice(xIcons))
    write("Tweeting {:s}".format(finalStatus))
    try:
        if os.path.isfile('/home/pi/tmp/lightshow_disabled'):
            write("Tweeting is disabled..")
        else:
            api.update_status(status=finalStatus)
    except tweepy.TweepError, e:
        write(e)

twitter = '/home/pi/.twitter.json'
songs = '/home/pi/api/html/music.json'
commands = '/home/pi/tmp/lightshow_command'

config = json.loads(read(twitter))

songsStamp = os.stat(songs).st_mtime
commandsStamp = os.stat(commands).st_mtime

songsValue = read(songs)
commandsValue = read(commands)

xIcons = [
    '🎄',
    '🕯',
    '🔔',
    '🎁',
    '⛄',
    '❄️',
    '🎅'
]

mIcons = [
    '📻',
    '🔊',
    '🔉',
    '💿',
    '🎙',
    '🎸',
    '🎻',
    '🎤',
    '🎶',
    '🎹',
    '🎵'
]

onList = [
    'on',
    'running',
    'active',
    'up',
    'glowing',
    'shining',
    'ablaze',
    'lit',
    'toasty',
    'powered up',
    'burning',
    'alive',
    'ongoing'
]

offList = [
    'off',
    'out',
    'down',
    'extinguished',
    'no longer alight',
    'put down',
    'shut off',
    'closed down',
    'powered down',
    'asleep',
    'disabled'
]

while True:
    status = None
    music = None
    action = 'off'
    songsStampNow = os.stat(songs).st_mtime
    commandsStampNow = os.stat(commands).st_mtime
    songsValueNow = read(songs)
    commandsValueNow = read(commands)
    if songsStamp != songsStampNow and songsValue != songsValueNow:
        try:
            data = json.loads(read(songs))
        except:
            continue

        music = "🔇  No music currently playing.."
        if 'title' in data and 'artist' in data:
            music = "{:s}  {:s} by {:s}".format(random.choice(mIcons), data['title'], data['artist'])
            write("Found: {:s}".format(find_artist(data['artist'])))
        
    if commandsStamp != commandsStampNow and commandsValue != commandsValueNow:
        cmd = read(commands)
        status = 'Lights are currently'
        if cmd == 'on':
            action = 'on'
            status = 'All lights are'
        elif cmd == 'show':
            action = 'on'
            status = 'Light show is'
        elif cmd == 'cylon':
            action = 'on'
            status = 'Cylon pattern is'
        elif cmd == 'dance':
            action = 'on'
            status = 'Dance pattern is'
        elif cmd == 'flash':
            action = 'on'
            status = 'Flash pattern is'
        elif cmd == 'random_pattern':
            action = 'on'
            status = 'Random pattern is'
        
    if status:
        tweet(status, action)
    if music:
        tweet(music, None)

    songsStamp = songsStampNow
    songsValue = songsValueNow
    commandsStamp = commandsStampNow
    commandsValue = commandsValueNow
    time.sleep(.95)
