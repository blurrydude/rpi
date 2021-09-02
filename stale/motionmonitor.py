#! /usr/bin/env python3
import time
time.sleep(15)
import paho.mqtt.client as mqtt
import json
import requests

running = True
#f = open('motionsensors.json')
f = open('/home/pi/rpi/motionsensors.json')
sensors = json.load(f)
fc = open('/home/pi/rpi/circuits.json')
#fc = open('circuits.json')
circuits = json.load(fc)

client = mqtt.Client()

def mosquittoDo(topic, command):
    global received
    global result
    try:
        client.publish(topic,command)
        print("sent command "+topic+" "+command)
    except:
        print('failed')
    return 'OK'

def on_message(client, userdata, message):
    global running
    result = json.loads(str(message.payload.decode("utf-8")))
    print(result)
    # {
    # "motion": true,
    # "timestamp": 1627686399,
    # "active": true,
    # "vibration": false,
    # "lux": 0,
    # "bat": 94
    # }
    # if result["motion"] is True:
    #     for sensor in sensors:
    #         if sensor["address"] in message.topic:
    #             sendCommand("turn on "+sensor["activate_light"])
    # if result["motion"] is False:
    #     for sensor in sensors:
    #         if sensor["address"] in message.topic and sensor["auto_off"] is True:
    #             sendCommand("turn off "+sensor["activate_light"])
    if result["motion"] is True:
        print("motion detected")
        for sensor in sensors:
            if sensor["address"] in message.topic:
                print("address in topic")
                for circuit in circuits:
                    if circuit["label"].lower() == sensor["activate_light"]:
                        print("label in activate_light")
                        topic = "shellies/"+circuit["address"]+"/relay/"+circuit["relay"]
                        mosquittoDo(topic,"on")
    if result["motion"] is False:
        print("motion stopped")
        for sensor in sensors:
            if sensor["address"] in message.topic and sensor["auto_off"] is True:
                for circuit in circuits:
                    if circuit["label"].lower() == sensor["activate_light"]:
                        topic = "shellies/"+circuit["address"]+"/relay/"+circuit["relay"]
                        mosquittoDo(topic,"off")
    
    
def sendCommand(command):
    print("sending command: "+command)
    try:
        r =requests.get('https://api.idkline.com/control/'+command)
        print(str(r.status_code))
    except:
        print('failed to send command')

if __name__ == "__main__":
    client.on_message = on_message
    client.connect('192.168.1.200')
    for sensor in sensors:
        topic = 'shellies/'+sensor["address"]+'/status'
        print('subscribing to '+topic)
        client.subscribe(topic)
    client.loop_start()
    while running is True:
        time.sleep(1)
    client.loop_stop()
    client.disconnect()