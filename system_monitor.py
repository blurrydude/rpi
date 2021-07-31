#! /usr/bin/env python3
import string
import time
time.sleep(30)
import paho.mqtt.client as mqtt
import json
from datetime import datetime
import os

running = True
client = mqtt.Client()
circuits = None
motionSensors = None

def loadCircuits():
    global circuits
    f = open('/home/pi/rpi/circuits.json')
    circuits = json.load(f)
    log('circuits')
    log(circuits)

def loadMotionSensors():
    global motionSensors
    f = open('/home/pi/rpi/motionsensors.json')
    motionSensors = json.load(f)
    log('motionSensors')
    log(motionSensors)

def initializeMqtt():
    log('initializeMqtt')
    client.on_message = on_message
    client.connect('192.168.1.22')
    client.subscribe('shellies/#')
    client.subscribe('pi/#')
    client.loop_start()

def stopMqtt():
    client.loop_stop()
    client.disconnect()

def loop():
    time.sleep(0.1)

def on_message(client, userdata, message):
    try:
        topic = message.topic
        text = str(message.payload.decode("utf-8"))
        handleMessage(topic, text)
    except Exception as err:
        log(err)


def handleMessage(topic, text):
    log("handle message: "+topic+" : "+text)
    for circuit in circuits:
        if circuit["address"] in topic and "relay/"+circuit["relay"] in topic:
            handleCircuitMessage(topic, text)
            return
    for sensor in motionSensors:
        if sensor["address"] in topic:
            handleMotionSensorMessage(sensor, text)
            return
    if "pi/" in topic:
        handlePiMessage(text)

def handleCircuitMessage(topic, text):
    bits = topic.split('/')
    address = bits[1]
    relay = bits[3]
    if "power" in topic:
        with open("/home/pi/"+address+"_"+relay+"_power.state", "w") as write_file:
            log(address + " " + relay + " " + text)
            write_file.write(text)
    else:
        with open("/home/pi/"+address+"_"+relay+".state", "w") as write_file:
            log(address + " " + relay + " " + text)
            write_file.write(text)

def handleMotionSensorMessage(circuit, text):
    data = json.loads(text)
    if data["motion"] is True:
        log("motion detected")
        for sensor in motionSensors:
            if sensor["address"] in topic:
                log("address in topic")
                for circuit in circuits:
                    if circuit["label"].lower() == sensor["activate_light"]:
                        log("label in activate_light")
                        topic = "shellies/"+circuit["address"]+"/relay/"+circuit["relay"]
                        mosquittoDo(topic,"on")
    if data["motion"] is False:
        log("motion stopped")
        for sensor in motionSensors:
            if sensor["address"] in topic and sensor["auto_off"] is True:
                for circuit in circuits:
                    if circuit["label"].lower() == sensor["activate_light"]:
                        topic = "shellies/"+circuit["address"]+"/relay/"+circuit["relay"]
                        mosquittoDo(topic,"off")

def handlePiMessage(text):
    if "alive at" not in text:
        return
    s = text.replace(", ", "_").replace("-", "_").replace("alive at ", "").split(" ")
    name = s[0]
    ip = s[1]
    ts = s[2]
    log(name+" "+ip+" "+ts)
    f = open("/home/pi/pistates.json")
    pi = json.load(f)
    pi[name] = {
        "name": name,
        "ip": ip,
        "heartbeat": ts
    }
    with open("/home/pi/pistates.json", "w") as write_file:
        write_file.write(json.dumps(pi))

def mosquittoDo(topic, command):
    global received
    global result
    try:
        client.publish(topic,command)
        log("sent command "+topic+" "+command)
    except:
        log('failed')
    return 'OK'

def log(message):
    if type(message) is not string:
        message = json.dumps(message)
    timestamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    logfiledate = datetime.now().strftime("%Y%m%d")
    logfile = "/home/pi/system_monitor_log_"+logfiledate+".txt"
    entry = timestamp + ": " + message + "\n"
    print(entry)

    if os.path.exists(logfile):
        append_write = 'a' # append if already exists
    else:
        append_write = 'w' # make a new file if not

    with open(logfile, append_write) as write_file:
        write_file.write(entry)

if __name__ == "__main__":
    loadCircuits()
    loadMotionSensors()
    initializeMqtt()
    while running is True:
        loop()
    stopMqtt()