#! /usr/bin/env python3
import time
time.sleep(15)
import paho.mqtt.client as mqtt
import json
import requests

running = True
f = open('motionsensors.json')
#f = open('/home/pi/rpi/motionsensors.json')
sensors = json.load(f)

client = mqtt.Client()

def on_message(client, userdata, message):
    global running
    result = json.loads(str(message.payload.decode("utf-8")))
    # {
    # "motion": true,
    # "timestamp": 1627686399,
    # "active": true,
    # "vibration": false,
    # "lux": 0,
    # "bat": 94
    # }
    if result["motion"] is True:
        for sensor in sensors:
            if sensor["address"] in message.topic:
                sendCommand("turn on "+sensor["guest bathroom"])
    
def sendCommand(command):
    print("sending command: "+command)
    try:
        r =requests.get('https://api.idkline.com/control/'+command)
        print(str(r.status_code))
    except:
        print('failed to send command')

if __name__ == "__main__":
    client.on_message = on_message
    client.connect('192.168.1.22')
    for sensor in sensors:
        topic = 'shellies/'+sensor["address"]+'/relay/'+sensor["address"]+'/status'
        print('subscribing to '+topic)
        client.subscribe(topic)
    client.loop_start()
    while running is True:
        time.sleep(1)
    client.loop_stop()
    client.disconnect()