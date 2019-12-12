#!/usr/bin/env python

import fileinput
import subprocess
import json
import os
import re

last = {
    'artist': False,
    'title': False
}
data = {}

def clean(str):
    str = str.decode('utf-8')
    str = re.sub('[\[].*?[\]]', '', str)
    str = re.sub('[\(].*?[\)]', '', str)
    str = re.sub('\s+', ' ', str).strip()
    return str.encode('utf-8')

process = subprocess.Popen(['/home/pi/bin/pipe_music_meta'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
while True:
    line = process.stdout.readline()
    if line != '':
        #print "test:", line.rstrip()
        line = line.replace('"', '').rstrip()
        if line.startswith('Artist'):
            data['artist'] = clean(line.replace('Artist: ', '')[:-1])
        if line.startswith('Title'):
            data['title'] = clean(line.replace('Title: ', '')[:-1])
        
        #print data
        if 'artist' in data and 'title' in data:
            if data['artist'] != last['artist'] or data['title'] != last['title']:
                #print "Data Changed"
                last['artist'] = data['artist']
                last['title'] = data['title']
                #print data
                f = open('/home/pi/api/html/music.json', 'w')
                f.write(json.dumps(data, indent=4, sort_keys=True))
                f.close()
    else:
        break
