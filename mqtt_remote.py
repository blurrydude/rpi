#! /usr/bin/env python3
from datetime import datetime, timedelta
import json
import paho.mqtt.client as mqtt
import time

state = [False,False,False,False,False,False]
pressed = [False,False]
press_time = datetime.now

def on_message(client, userdata, message):
    global state
    global pressed
    global press_time
    try:
        topic = message.topic
        data = str(message.payload.decode("utf-8"))
        if "shellyuni" in topic and "input" in topic:
            i = 0
            x = int(topic.split('/')[-1])
            d = int(data)
            do = False
            if d == 1:
                pressed[x] = True
                press_time = datetime.now()
                return
            if d == 0:
                if pressed[0] is True and pressed[1] is False:
                    do = True
                if pressed[0] is False and pressed[1] is True:
                    do = True
                    i = 1
                if pressed[0] is True and pressed[1] is True:
                    do = True
                    i = 2
                pressed = [False,False]
            if do is True:
                long = "short"
                z = i
                print(str(datetime.now() - press_time))
                if press_time < datetime.now() - timedelta(seconds=2):
                    long = "long"
                    z = z + 3
                print(long)
                s = "off"
                if state[z] is True:
                    s = "on"
                    state[z] = False
                else:
                    state[z] = True
                commands = json.load(open("mqtt_remote.json"))
                for command in commands[i][long][s]:
                    client.publish("smarter_circuits/command", command)
    except:
        donothing = True

if __name__ == "__main__":
    client = mqtt.Client()
    client.on_message = on_message
    client.connect('192.168.2.200')
    client.subscribe("shellies/#")
    client.loop_start()
    while True:
        time.sleep(1)