#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import os

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(26, GPIO.OUT)

blue_active=False
red_active=False
blue_presses=0

def pause():
    time.sleep(0.2)

def start():
    os.system("/home/pi/bin/start_lights")
    pause()

def stop():
    os.system("/home/pi/bin/stop_controller")
    pause()

def lightsOn():
    os.system("/home/pi/bin/lights_on")
    pause()	

def lightsOff():
    os.system("/home/pi/bin/lights_off")
    pause()

def blueOn():
    print("Blue on")
    hardwareControl(1)
    pause()

def blueOff():
    global blue_active
    blue_active = False
    print("Blue off")
    lightsOff()
    GPIO.output(26, False)

def redOn():
    GPIO.output(26, True)
    print("Red on")
    lightsOn()
    lightsOff()
    lightsOn()
    start()

def redOff():
    print("Red off")
    stop()
    lightsOff()
    GPIO.output(26, False)

def resetBlue():
    stop()
    lightsOff()

def resetRed():
    stop()
    global blue_presses
    blue_presses=0

def flashBlue():
    GPIO.output(26, True)
    pause()
    GPIO.output(26, False)
    pause()

def hardwareControl(id):
    names = {
        1: 'on',
        2: 'cylon',
        3: 'flash',
        4: 'step',
        5: 'dance',
        6: 'random_pattern'
    }
    resetBlue()
    command = "sudo python /home/pi/lightshowpi/py/hardware_controller.py --state {:s} &".format(names[id])
    print(command)
    os.system(command)

while True:
    blue_input_state = GPIO.input(16)
    red_input_state = GPIO.input(19)
    if blue_input_state == False:
        if blue_active:
            blueOff()
            print("Presses Reset")
            blue_presses = 0
        else:
            if blue_presses == 0:
                redOff()
                pause()
                blueOn()
            blue_presses += 1
            #print("Presses made: {0}").format(blue_presses)
            if blue_presses==1:
                hardwareControl(blue_presses)
            elif blue_presses==2:
               hardwareControl(blue_presses)
                #os.system("sudo python ../lightshowpi/py/hardware_controller.py --state cylon &")
            elif blue_presses==3:
                resetBlue()	
               # os.system("sudo python ../lightshowpi/py/hardware_controller.py --state flash &")
                hardwareControl(blue_presses)
            elif blue_presses==4:
                resetBlue()
              #  os.system("sudo python ../lightshowpi/py/hardware_controller.py --state step &")
                hardwareControl(blue_presses)
            elif blue_presses==5:
                resetBlue()
             #   os.system("sudo python ../lightshowpi/py/hardware_controller.py --state dance &")
                hardwareControl(blue_presses)
            elif blue_presses==6:
                resetBlue()
            #    os.system("sudo python ../lightshowpi/py/hardware_controller.py --state random_pattern &")
                hardwareControl(blue_presses)
            else:
                resetBlue()
                blue_active=True

            #This flashes the LED 
            for i in range(0, blue_presses):
                flashBlue()

    if red_input_state == False:
        if red_active:
            red_active=False
            resetRed()
            redOff()
        else:
            red_active=True
            resetRed()
            redOn()
    pause()
    # Loop ending here

