#! /usr/bin/env python3
from os import write
import time
import paho.mqtt.client as mqtt
import json

running = True
f = open('circuits.json')
circuits = json.load(f)

client = mqtt.Client()
pi = []

def on_message(client, userdata, message):
    global running
    result = str(message.payload.decode("utf-8"))
    if "alive at" not in result:
        return
    s = result.replace(", ", "_").replace("alive at ", "").split(" ")
    name = s[0]
    ip = s[1]
    timestamp = s[2]
    pi[name] = {
        "name": name,
        "ip": ip,
        "heartbeat": timestamp
    }
    with open("/home/pi/pistates.json") as write_file:
        write_file.write(json.dumps(pi))

if __name__ == "__main__":
    client.on_message = on_message
    client.connect('192.168.1.22')
    client.subscribe('pi/#')
    client.loop_start()
    while running is True:
        time.sleep(1)
    client.loop_stop()
    client.disconnect()