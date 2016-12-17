#!/usr/bin/env python
# -*- coding: latin-1 -*-

import time
import json
import tweepy
import argparse

def read(path):
    f = open(path, 'r')
    data = f.read().rstrip()
    f.close()
    return data

def get_api():
    auth = tweepy.OAuthHandler(config['api']['key'], config['api']['secret'])
    auth.set_access_token(config['access']['token'], config['access']['secret'])
    return tweepy.API(auth)

def get_blacklist():
    return json.loads(read('/home/pi/tmp/twitter.blacklist.json').lower())
    
twitter = '/home/pi/.twitter.json'
config = json.loads(read(twitter))



def find_artist(name, expand=False):
    found=None
    print "Looking for " + name
    if name == '':
        return found
    bl = get_blacklist()
    if name.lower() in bl:
        oName = bl[name.lower()]
        if oName == False:
            print "Skipping, in Blacklist"
            return found
        if oName:
            print "normalized: {:s}".format(oName)
            return oName
    if name.lower().startswith('the'):
        name = name.replace('The', '', 1)
    
    print "normalized looking: {:s}".format(name)
    api = get_api()
    results = api.search_users(q=name)

    for i in results:
        if i.verified:
            found = i.screen_name
            if expand:
                found = "{:s} https://twitter.com/{:s}".format(i.name, i.screen_name)
            break
    
    return found

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Artist Lookup')
    parser.add_argument('artist', help='The artist name')
    args = parser.parse_args()
    print "Looking for: {:s}".format(args.artist)
    artist = find_artist(args.artist, True)
    if artist:
        print artist
    else:
        print "Nothing Found.."
