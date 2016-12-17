#!/bin/bash

echo "none" > /home/pi/tmp/lightshow_command
chown pi:pi /home/pi/tmp/lightshow_command
chmod a+w /home/pi/tmp/lightshow_command


/usr/bin/amixer set PCM 95%
#/home/pi/bin/start_automation
/home/pi/bin/start_api
/home/pi/bin/start_tweets
/sbin/ifconfig wlan0 down

#finally turn on boot light
/usr/bin/python /home/pi/bin/light.py 6
