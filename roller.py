#! /usr/bin/env python3
import time
time.sleep(15)
import _thread
import paho.mqtt.client as mqtt
import subprocess
import socket
import requests
import board
from adafruit_motorkit import MotorKit
import RPi.GPIO as GPIO

myname = socket.gethostname()
myip = subprocess.check_output(['hostname', '-I'])

GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)

kit = MotorKit(0x61)

running = True
client = mqtt.Client()
read_pins = [12,16,20]#,21]
motors = [
    kit.motor1,
    kit.motor2,
    kit.motor3,
    kit.motor4
]
moving = [
    False,
    False,
    False,
    False
]

def open_roller(addy):
    global moving
    if moving[addy] is True:
        return
    moving[addy] = True
    motors[addy].throttle = 1.0
    time.sleep(6)
    motors[addy].throttle = 0.0
    moving[addy] = False

def close_roller(addy):
    global moving
    if moving[addy] is True:
        return
    moving[addy] = True
    input_state = GPIO.input(read_pins[addy])
    motors[addy].throttle = -1.0
    while input_state == 1:
        input_state = GPIO.input(read_pins[addy])
    motors[addy].throttle = 0.0
    moving[addy] = False

def on_message(client, userdata, message):
    global running
    result = str(message.payload.decode("utf-8"))
    #print("Received: "+result)
    bits = result.split(':')
    addy = int(bits[0])
    state = int(bits[1])
    if addy >= len(read_pins):
        return
    input_state = GPIO.input(read_pins[addy])
    if state == input_state:
        return
    if state == 0:
        _thread.start_new_thread(close_roller, (addy))
    else:
        _thread.start_new_thread(open_roller, (addy))

def sendReport(door, state):
    try:
        r =requests.get('https://api.idkline.com/reportdoor/'+door+"-"+state)
    except:
        print('failed to send command')

if __name__ == "__main__":
    input_state = GPIO.input(read_pins[0])
    if input_state == 1:
        close_roller(0)
    else:
        open_roller(0)
        time.sleep(3)
        close_roller(0)

    client.on_message = on_message
    client.connect('192.168.1.200')
    topic = 'pi/' + myname + '/commands'
    #print('subscribing to '+topic)
    client.subscribe(topic)
    client.loop_start()
    while running is True:
        time.sleep(1)
    client.loop_stop()
    client.disconnect()