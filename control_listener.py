#! /usr/bin/env python3
import json
import paho.mqtt.client as mqtt
import time
import datetime

client = mqtt.Client()

def on_message(client, userdata, message):
    data = str(message.payload.decode("utf-8")).lower().split(':')
    print(data)
    if data[2] != 'released':
        return
    config_data = open('control_config.json')
    config = json.load(config_data)
    client.publish('smarter_circuits/commands',config[int(data[0])][data[1]])

if __name__ == "__main__":
    client.on_message = on_message
    client.connect('192.168.2.200')
    client.subscribe('smarter_circuits/controller')
    client.loop_start()
    running = True
    while running is True:
        time.sleep(1)
        
    client.loop_stop()
    client.disconnect()