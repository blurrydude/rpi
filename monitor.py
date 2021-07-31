#! /usr/bin/env python3
import time
time.sleep(15)
import paho.mqtt.client as mqtt
import json
import requests

running = True
fs = open('/home/pi/rpi/motionsensors.json')
sensors = json.load(fs)
f = open('/home/pi/rpi/circuits.json')
circuits = json.load(f)

client = mqtt.Client()

def on_message(client, userdata, message):
    global running
    if "status" in message.topic:
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
        if result["motion"] is True:
            for sensor in sensors:
                if sensor["address"] in message.topic:
                    sendCommand("turn on "+sensor["activate_light"])
        if result["motion"] is False:
            for sensor in sensors:
                if sensor["address"] in message.topic and sensor["auto_off"] is True:
                    sendCommand("turn off "+sensor["activate_light"])
    result = str(message.payload.decode("utf-8"))
    #print("Received: "+result)
    bits = message.topic.split('/')
    address = bits[1]
    relay = bits[3]
    if "power" in message.topic:
        with open("/home/pi/"+address+"_"+relay+"_power.state", "w") as write_file:
            print(address + " " + relay + " " + result)
            write_file.write(result)
    else:
        with open("/home/pi/"+address+"_"+relay+".state", "w") as write_file:
            print(address + " " + relay + " " + result)
            write_file.write(result)
    #print(check)
    
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
    for circuit in circuits:
        relays = 1
        if "shellyswitch25" in circuit["address"]:
            relays = 2
        for i in range(relays):
            topic = 'shellies/'+circuit["address"]+'/relay/'+str(i)
            print('subscribing to '+topic)
            client.subscribe(topic)
            topic = 'shellies/'+circuit["address"]+'/relay/'+str(i)+'/power'
            print('subscribing to '+topic)
            client.subscribe(topic)
    for sensor in sensors:
        topic = 'shellies/'+sensor["address"]+'/status'
        print('subscribing to '+topic)
        client.subscribe(topic)
    client.loop_start()
    while running is True:
        time.sleep(1)
    client.loop_stop()
    client.disconnect()